from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.inventory import Inventory, StockMovement
from app.models.product import Product
from app.models.supplier import Supplier
from app.repository.purchase_repository import PurchaseRepository
from app.repository.sale_repository import SaleRepository
from app.repository.expiry_repository import ExpiryRepository


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_product(self, product_id: int) -> Inventory | None:
        stmt = (
            select(Inventory)
            .options(joinedload(Inventory.product).joinedload(Product.category))
            .where(Inventory.product_id == product_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, inventory_id: int) -> Inventory | None:
        stmt = (
            select(Inventory)
            .options(joinedload(Inventory.product).joinedload(Product.category))
            .where(Inventory.id == inventory_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_inventory(
        self,
        *,
        q: str | None,
        status: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Inventory], int]:
        base = select(Inventory).options(joinedload(Inventory.product).joinedload(Product.category))

        filters = []
        if q:
            like = f"%{q.strip().lower()}%"
            base = base.join(Product).where(
                or_(
                    func.lower(Product.name).like(like),
                    func.lower(Product.sku).like(like),
                )
            )
        if status:
            if status == "out_of_stock":
                filters.append(Inventory.current_stock <= 0)
            elif status == "low_stock":
                filters.append(and_(Inventory.current_stock > 0, Inventory.current_stock <= Inventory.min_stock))
            elif status == "overstock":
                filters.append(Inventory.current_stock >= Inventory.max_stock)
            elif status == "healthy":
                filters.append(
                    and_(
                        Inventory.current_stock > Inventory.min_stock,
                        Inventory.current_stock < Inventory.max_stock,
                    )
                )

        if filters:
            base = base.where(and_(*filters))

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Inventory.updated_at.desc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).unique().scalars().all())
        return items, int(total)

    def create(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        self.db.commit()
        self.db.refresh(inventory)
        return self.get_by_product(inventory.product_id)  # type: ignore[return-value]

    def save(self, inventory: Inventory) -> Inventory:
        self.db.commit()
        self.db.refresh(inventory)
        return self.get_by_product(inventory.product_id)  # type: ignore[return-value]

    def add_movement(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def list_movements(self, product_id: int | None, skip: int, limit: int) -> tuple[list[StockMovement], int]:
        base = select(StockMovement)
        if product_id:
            base = base.where(StockMovement.product_id == product_id)
        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, int(total)

    def dashboard_stats(self) -> dict:
        inv_stmt = select(Inventory).options(joinedload(Inventory.product))
        inventories = list(self.db.execute(inv_stmt).unique().scalars().all())

        total_products = self.db.execute(select(func.count()).select_from(Product)).scalar_one()
        total_categories = self.db.execute(select(func.count()).select_from(Category)).scalar_one()
        total_suppliers = self.db.execute(select(func.count()).select_from(Supplier)).scalar_one()
        monthly_purchases = PurchaseRepository(self.db).monthly_purchase_total()
        sales_data = SaleRepository(self.db).sales_summary()
        expiry_data = ExpiryRepository(self.db).summary(30)

        low = out = over = healthy = total_units = 0
        value = 0.0
        warehouse_items = []

        for inv in inventories:
            total_units += inv.current_stock
            cost = float(inv.product.cost_price or 0)
            value += inv.current_stock * cost
            st = inv.stock_status
            if st == "out_of_stock":
                out += 1
            elif st == "low_stock":
                low += 1
            elif st == "overstock":
                over += 1
            else:
                healthy += 1

            warehouse_items.append({
                "product_id": inv.product_id,
                "name": inv.product.name,
                "sku": inv.product.sku,
                "stock": inv.current_stock,
                "min_stock": inv.min_stock,
                "max_stock": inv.max_stock,
                "status": st,
            })

        return {
            "total_products": int(total_products),
            "total_categories": int(total_categories),
            "total_suppliers": int(total_suppliers),
            "monthly_purchases": round(monthly_purchases, 2),
            "today_sales": sales_data["today_sales"],
            "monthly_sales": sales_data["monthly_sales"],
            "expiring_soon": expiry_data["expiring_soon"],
            "expired": expiry_data["expired"],
            "low_stock": low,
            "out_of_stock": out,
            "overstock": over,
            "healthy_stock": healthy,
            "inventory_value": round(value, 2),
            "total_stock_units": total_units,
            "warehouse_items": warehouse_items[:24],
        }
