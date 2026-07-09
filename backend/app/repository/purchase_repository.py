from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.purchase import POStatus, PurchaseItem, PurchaseOrder
from app.models.supplier import Supplier


class PurchaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- Suppliers ----------
    def get_supplier(self, supplier_id: int) -> Supplier | None:
        return self.db.get(Supplier, supplier_id)

    def get_supplier_by_name(self, name: str) -> Supplier | None:
        stmt = select(Supplier).where(func.lower(Supplier.name) == name.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def list_suppliers(self, q: str | None, skip: int, limit: int) -> tuple[list[Supplier], int]:
        base = select(Supplier)
        if q:
            like = f"%{q.strip().lower()}%"
            base = base.where(
                or_(
                    func.lower(Supplier.name).like(like),
                    func.lower(func.coalesce(Supplier.email, "")).like(like),
                    func.coalesce(Supplier.phone, "").like(f"%{q.strip()}%"),
                )
            )
        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Supplier.name.asc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all()), int(total)

    def create_supplier(self, supplier: Supplier) -> Supplier:
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def save_supplier(self, supplier: Supplier) -> Supplier:
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def count_suppliers(self) -> int:
        return int(self.db.execute(select(func.count()).select_from(Supplier)).scalar_one())

    def supplier_performance(self, supplier_id: int) -> dict:
        supplier = self.get_supplier(supplier_id)
        if supplier is None:
            return {}

        orders = list(
            self.db.execute(
                select(PurchaseOrder).where(
                    and_(
                        PurchaseOrder.supplier_id == supplier_id,
                        PurchaseOrder.status.in_([POStatus.RECEIVED.value, POStatus.PARTIAL.value]),
                    )
                )
            ).scalars().all()
        )

        total = len(orders)
        on_time = delayed = 0
        delivery_days: list[int] = []

        for po in orders:
            if po.received_date and po.order_date:
                days = (po.received_date - po.order_date).days
                delivery_days.append(days)
                if po.expected_delivery:
                    if po.received_date <= po.expected_delivery:
                        on_time += 1
                    else:
                        delayed += 1

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier.name,
            "total_orders": total,
            "received_orders": total,
            "on_time_deliveries": on_time,
            "delayed_deliveries": delayed,
            "avg_delivery_days": round(sum(delivery_days) / len(delivery_days), 1) if delivery_days else None,
            "on_time_rate": round(on_time / total * 100, 1) if total else 0.0,
        }

    # ---------- Purchase Orders ----------
    def next_po_number(self) -> str:
        count = self.db.execute(select(func.count()).select_from(PurchaseOrder)).scalar_one()
        return f"PO-{date.today().strftime('%Y%m%d')}-{int(count) + 1:04d}"

    def get_po(self, po_id: int) -> PurchaseOrder | None:
        stmt = (
            select(PurchaseOrder)
            .options(
                joinedload(PurchaseOrder.supplier),
                joinedload(PurchaseOrder.items).joinedload(PurchaseItem.product).joinedload(Product.category),
            )
            .where(PurchaseOrder.id == po_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_pos(self, status: str | None, supplier_id: int | None, skip: int, limit: int) -> tuple[list[PurchaseOrder], int]:
        base = (
            select(PurchaseOrder)
            .options(joinedload(PurchaseOrder.supplier), joinedload(PurchaseOrder.items))
        )
        filters = []
        if status:
            filters.append(PurchaseOrder.status == status)
        if supplier_id:
            filters.append(PurchaseOrder.supplier_id == supplier_id)
        if filters:
            base = base.where(and_(*filters))

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).unique().scalars().all()), int(total)

    def create_po(self, po: PurchaseOrder) -> PurchaseOrder:
        self.db.add(po)
        self.db.commit()
        self.db.refresh(po)
        return self.get_po(po.id)  # type: ignore[return-value]

    def save_po(self, po: PurchaseOrder) -> PurchaseOrder:
        self.db.commit()
        self.db.refresh(po)
        return self.get_po(po.id)  # type: ignore[return-value]

    def monthly_purchase_total(self) -> float:
        from datetime import datetime
        now = datetime.now()
        start = date(now.year, now.month, 1)
        stmt = select(func.coalesce(func.sum(PurchaseOrder.total_amount), 0)).where(
            and_(
                PurchaseOrder.status.in_([POStatus.RECEIVED.value, POStatus.PARTIAL.value]),
                PurchaseOrder.received_date >= start,
            )
        )
        return float(self.db.execute(stmt).scalar_one())
