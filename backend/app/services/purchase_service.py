from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.inventory import Inventory, MovementType, StockMovement
from app.models.purchase import POStatus, PurchaseItem, PurchaseOrder
from app.models.supplier import Supplier
from app.repository.catalog_repository import CatalogRepository
from app.repository.inventory_repository import InventoryRepository
from app.repository.purchase_repository import PurchaseRepository
from app.services.expiry_service import ExpiryService
from app.schemas.purchase import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    ReceivePORequest,
    SupplierCreate,
    SupplierPerformance,
    SupplierResponse,
    SupplierUpdate,
)


class PurchaseService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PurchaseRepository(db)
        self.catalog = CatalogRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.expiry_service = ExpiryService(db)

    # ---------- Suppliers ----------
    def create_supplier(self, body: SupplierCreate) -> SupplierResponse:
        if self.repo.get_supplier_by_name(body.name):
            raise HTTPException(status_code=409, detail="Supplier already exists")
        supplier = Supplier(
            name=body.name.strip(),
            contact_person=body.contact_person,
            email=body.email,
            phone=body.phone,
            address=body.address,
        )
        return SupplierResponse.model_validate(self.repo.create_supplier(supplier))

    def list_suppliers(self, q: str | None, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_suppliers(q, skip, limit=page_size)
        return {
            "items": [SupplierResponse.model_validate(s) for s in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update_supplier(self, supplier_id: int, body: SupplierUpdate) -> SupplierResponse:
        supplier = self.repo.get_supplier(supplier_id)
        if supplier is None:
            raise HTTPException(status_code=404, detail="Supplier not found")
        if body.name is not None:
            existing = self.repo.get_supplier_by_name(body.name)
            if existing and existing.id != supplier_id:
                raise HTTPException(status_code=409, detail="Supplier name already exists")
            supplier.name = body.name.strip()
        for field in ("contact_person", "email", "phone", "address"):
            val = getattr(body, field)
            if val is not None:
                setattr(supplier, field, val)
        if body.rating is not None:
            supplier.rating = body.rating
        if body.is_active is not None:
            supplier.is_active = body.is_active
        return SupplierResponse.model_validate(self.repo.save_supplier(supplier))

    def supplier_performance(self, supplier_id: int) -> SupplierPerformance:
        data = self.repo.supplier_performance(supplier_id)
        if not data:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return SupplierPerformance(**data)

    # ---------- Purchase Orders ----------
    def create_po(self, body: PurchaseOrderCreate, user_id: int) -> PurchaseOrderResponse:
        supplier = self.repo.get_supplier(body.supplier_id)
        if supplier is None or not supplier.is_active:
            raise HTTPException(status_code=400, detail="Invalid or inactive supplier")

        items: list[PurchaseItem] = []
        total = 0.0
        for line in body.items:
            product = self.catalog.get_product(line.product_id)
            if product is None:
                raise HTTPException(status_code=400, detail=f"Product {line.product_id} not found")
            line_total = line.quantity_ordered * line.unit_price
            total += line_total
            items.append(
                PurchaseItem(
                    product_id=line.product_id,
                    quantity_ordered=line.quantity_ordered,
                    unit_price=line.unit_price,
                    batch_number=line.batch_number,
                )
            )

        po = PurchaseOrder(
            po_number=self.repo.next_po_number(),
            supplier_id=body.supplier_id,
            status=POStatus.ORDERED.value,
            order_date=date.today(),
            expected_delivery=body.expected_delivery,
            total_amount=total,
            notes=body.notes,
            created_by=user_id,
            items=items,
        )
        created = self.repo.create_po(po)
        return PurchaseOrderResponse.model_validate(created)

    def list_pos(self, status: str | None, supplier_id: int | None, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_pos(status, supplier_id, skip, limit=page_size)
        return {
            "items": [PurchaseOrderResponse.model_validate(po) for po in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_po(self, po_id: int) -> PurchaseOrderResponse:
        po = self.repo.get_po(po_id)
        if po is None:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        return PurchaseOrderResponse.model_validate(po)

    def _ensure_inventory(self, product_id: int) -> Inventory:
        inv = self.inventory_repo.get_by_product(product_id)
        if inv is None:
            inv = Inventory(product_id=product_id, current_stock=0, min_stock=10, max_stock=500)
            inv = self.inventory_repo.create(inv)
        return inv

    def receive_po(self, po_id: int, body: ReceivePORequest, user_id: int) -> PurchaseOrderResponse:
        po = self.repo.get_po(po_id)
        if po is None:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        if po.status == POStatus.CANCELLED.value:
            raise HTTPException(status_code=400, detail="Cannot receive a cancelled PO")
        if po.status == POStatus.RECEIVED.value:
            raise HTTPException(status_code=400, detail="PO already fully received")

        item_map = {i.id: i for i in po.items}
        received_date = body.received_date or date.today()

        for recv in body.items:
            item = item_map.get(recv.purchase_item_id)
            if item is None:
                raise HTTPException(status_code=400, detail=f"Invalid item {recv.purchase_item_id}")
            remaining = item.quantity_ordered - item.quantity_received
            if recv.quantity > remaining:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot receive {recv.quantity} for {item.product_id}, only {remaining} remaining",
                )

            inv = self._ensure_inventory(item.product_id)
            prev = inv.current_stock
            inv.current_stock = prev + recv.quantity
            self.inventory_repo.save(inv)

            self.inventory_repo.add_movement(
                StockMovement(
                    product_id=item.product_id,
                    movement_type=MovementType.IN.value,
                    quantity=recv.quantity,
                    previous_qty=prev,
                    new_qty=inv.current_stock,
                    reason=f"PO received: {po.po_number}",
                    reference=po.po_number,
                    created_by=user_id,
                )
            )
            item.quantity_received += recv.quantity

            # Create batch if expiry info provided (pharmacy compliance)
            if recv.expiry_date:
                from app.models.batch import InventoryBatch
                batch_num = recv.batch_number or item.batch_number or f"BATCH-{po.po_number}-{item.id}"
                self.expiry_service.repo.create_batch(
                    InventoryBatch(
                        product_id=item.product_id,
                        batch_number=batch_num,
                        expiry_date=recv.expiry_date,
                        quantity=recv.quantity,
                        received_date=received_date,
                    )
                )

        all_received = all(i.quantity_received >= i.quantity_ordered for i in po.items)
        any_received = any(i.quantity_received > 0 for i in po.items)

        if all_received:
            po.status = POStatus.RECEIVED.value
            po.received_date = received_date
        elif any_received:
            po.status = POStatus.PARTIAL.value
            po.received_date = received_date

        # Update supplier rating based on delivery timeliness
        if po.received_date and po.expected_delivery:
            supplier = po.supplier
            if po.received_date <= po.expected_delivery:
                supplier.rating = min(5.0, supplier.rating + 0.1)
            else:
                supplier.rating = max(1.0, supplier.rating - 0.2)

        saved = self.repo.save_po(po)
        return PurchaseOrderResponse.model_validate(saved)

    def cancel_po(self, po_id: int) -> PurchaseOrderResponse:
        po = self.repo.get_po(po_id)
        if po is None:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        if po.status in (POStatus.RECEIVED.value, POStatus.PARTIAL.value):
            raise HTTPException(status_code=400, detail="Cannot cancel a received PO")
        po.status = POStatus.CANCELLED.value
        return PurchaseOrderResponse.model_validate(self.repo.save_po(po))
