from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import MovementType, StockMovement
from app.models.sale import Sale, SaleItem, SaleStatus
from app.repository.catalog_repository import CatalogRepository
from app.repository.inventory_repository import InventoryRepository
from app.repository.sale_repository import SaleRepository
from app.services.expiry_service import ExpiryService
from app.schemas.sale import SaleCreate, SaleResponse, SalesSummary


class SaleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SaleRepository(db)
        self.catalog = CatalogRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.expiry_service = ExpiryService(db)

    def create_sale(self, body: SaleCreate, user_id: int) -> SaleResponse:
        if not body.items:
            raise HTTPException(status_code=400, detail="Sale must have at least one item")

        line_items: list[SaleItem] = []
        subtotal = 0.0

        # Validate stock and build line items
        for line in body.items:
            product = self.catalog.get_product(line.product_id)
            if product is None or not product.is_active:
                raise HTTPException(status_code=400, detail=f"Product {line.product_id} not found or inactive")

            inv = self.inventory_repo.get_by_product(line.product_id)
            if inv is None or inv.current_stock < line.quantity:
                available = inv.current_stock if inv else 0
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}. Available: {available}",
                )

            unit_price = line.unit_price if line.unit_price is not None else float(product.selling_price or 0)
            if unit_price <= 0:
                raise HTTPException(status_code=400, detail=f"Invalid price for {product.name}")

            line_total = round(unit_price * line.quantity, 2)
            subtotal += line_total
            line_items.append(
                SaleItem(
                    product_id=line.product_id,
                    quantity=line.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )

        tax_amount = round(subtotal * body.tax_percent / 100, 2)
        discount = round(body.discount, 2)
        total = round(subtotal + tax_amount - discount, 2)
        if total < 0:
            raise HTTPException(status_code=400, detail="Total cannot be negative")

        sale = Sale(
            invoice_number=self.repo.next_invoice_number(),
            customer_name=body.customer_name,
            customer_phone=body.customer_phone,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount=discount,
            total_amount=total,
            payment_method=body.payment_method,
            status=SaleStatus.COMPLETED.value,
            notes=body.notes,
            sale_date=date.today(),
            sold_by=user_id,
            items=line_items,
        )

        created = self.repo.create_sale(sale)

        # Deduct inventory after sale is persisted
        for line in created.items:
            inv = self.inventory_repo.get_by_product(line.product_id)
            if inv is None:
                continue
            prev = inv.current_stock
            inv.current_stock = prev - line.quantity
            self.inventory_repo.save(inv)
            self.inventory_repo.add_movement(
                StockMovement(
                    product_id=line.product_id,
                    movement_type=MovementType.OUT.value,
                    quantity=line.quantity,
                    previous_qty=prev,
                    new_qty=inv.current_stock,
                    reason=f"Sale: {created.invoice_number}",
                    reference=created.invoice_number,
                    created_by=user_id,
                )
            )
            self.expiry_service.deduct_from_batches_fefo(line.product_id, line.quantity)

        return SaleResponse.model_validate(created)

    def list_sales(
        self, *, q: str | None, from_date: date | None, to_date: date | None, page: int, page_size: int
    ) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_sales(q=q, from_date=from_date, to_date=to_date, skip=skip, limit=page_size)
        return {
            "items": [SaleResponse.model_validate(s) for s in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_sale(self, sale_id: int) -> SaleResponse:
        sale = self.repo.get_sale(sale_id)
        if sale is None:
            raise HTTPException(status_code=404, detail="Sale not found")
        return SaleResponse.model_validate(sale)

    def get_invoice(self, invoice_number: str) -> SaleResponse:
        sale = self.repo.get_by_invoice(invoice_number)
        if sale is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return SaleResponse.model_validate(sale)

    def cancel_sale(self, sale_id: int, user_id: int) -> SaleResponse:
        sale = self.repo.get_sale(sale_id)
        if sale is None:
            raise HTTPException(status_code=404, detail="Sale not found")
        if sale.status == SaleStatus.CANCELLED.value:
            raise HTTPException(status_code=400, detail="Sale already cancelled")

        # Restore stock
        for line in sale.items:
            inv = self.inventory_repo.get_by_product(line.product_id)
            if inv is None:
                continue
            prev = inv.current_stock
            inv.current_stock = prev + line.quantity
            self.inventory_repo.save(inv)
            self.inventory_repo.add_movement(
                StockMovement(
                    product_id=line.product_id,
                    movement_type=MovementType.IN.value,
                    quantity=line.quantity,
                    previous_qty=prev,
                    new_qty=inv.current_stock,
                    reason=f"Sale cancelled: {sale.invoice_number}",
                    reference=sale.invoice_number,
                    created_by=user_id,
                )
            )

        sale.status = SaleStatus.CANCELLED.value
        updated = self.repo.save_sale(sale)
        return SaleResponse.model_validate(updated)

    def summary(self) -> SalesSummary:
        return SalesSummary(**self.repo.sales_summary())
