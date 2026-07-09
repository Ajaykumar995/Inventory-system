from datetime import date, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.sale import Sale, SaleItem, SaleStatus


class SaleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_invoice_number(self) -> str:
        count = self.db.execute(select(func.count()).select_from(Sale)).scalar_one()
        return f"INV-{date.today().strftime('%Y%m%d')}-{int(count) + 1:04d}"

    def get_sale(self, sale_id: int) -> Sale | None:
        stmt = (
            select(Sale)
            .options(joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category))
            .where(Sale.id == sale_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_invoice(self, invoice_number: str) -> Sale | None:
        stmt = (
            select(Sale)
            .options(joinedload(Sale.items).joinedload(SaleItem.product).joinedload(Product.category))
            .where(Sale.invoice_number == invoice_number)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_sales(
        self,
        *,
        q: str | None,
        from_date: date | None,
        to_date: date | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Sale], int]:
        base = select(Sale).options(joinedload(Sale.items).joinedload(SaleItem.product))

        filters = [Sale.status == SaleStatus.COMPLETED.value]
        if q:
            like = f"%{q.strip().lower()}%"
            base = base.where(
                or_(
                    func.lower(func.coalesce(Sale.customer_name, "")).like(like),
                    func.lower(Sale.invoice_number).like(like),
                    func.coalesce(Sale.customer_phone, "").like(f"%{q.strip()}%"),
                )
            )
        if from_date:
            filters.append(Sale.sale_date >= from_date)
        if to_date:
            filters.append(Sale.sale_date <= to_date)
        if filters:
            base = base.where(and_(*filters))

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Sale.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).unique().scalars().all()), int(total)

    def create_sale(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return self.get_sale(sale.id)  # type: ignore[return-value]

    def save_sale(self, sale: Sale) -> Sale:
        self.db.commit()
        self.db.refresh(sale)
        return self.get_sale(sale.id)  # type: ignore[return-value]

    def sales_summary(self) -> dict:
        today = date.today()
        month_start = date(today.year, today.month, 1)

        def _sum_since(since: date) -> tuple[float, int]:
            stmt = select(
                func.coalesce(func.sum(Sale.total_amount), 0),
                func.count(),
            ).where(
                and_(Sale.status == SaleStatus.COMPLETED.value, Sale.sale_date >= since)
            )
            row = self.db.execute(stmt).one()
            return float(row[0]), int(row[1])

        today_total, today_count = _sum_since(today)
        monthly_total, monthly_count = _sum_since(month_start)

        return {
            "today_sales": round(today_total, 2),
            "monthly_sales": round(monthly_total, 2),
            "today_count": today_count,
            "monthly_count": monthly_count,
        }
