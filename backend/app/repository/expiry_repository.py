from datetime import date, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.batch import InventoryBatch
from app.models.notification import Notification, NotificationType
from app.models.product import Product


class ExpiryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_batch(self, batch_id: int) -> InventoryBatch | None:
        stmt = (
            select(InventoryBatch)
            .options(joinedload(InventoryBatch.product).joinedload(Product.category))
            .where(InventoryBatch.id == batch_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_batches(
        self,
        *,
        status: str | None,
        product_id: int | None,
        days: int,
        skip: int,
        limit: int,
    ) -> tuple[list[InventoryBatch], int]:
        today = date.today()
        base = (
            select(InventoryBatch)
            .options(joinedload(InventoryBatch.product).joinedload(Product.category))
            .where(and_(InventoryBatch.is_disposed == False, InventoryBatch.quantity > 0))  # noqa: E712
        )

        if product_id:
            base = base.where(InventoryBatch.product_id == product_id)

        if status == "expired":
            base = base.where(InventoryBatch.expiry_date < today)
        elif status == "expiring_soon":
            base = base.where(
                and_(InventoryBatch.expiry_date >= today, InventoryBatch.expiry_date <= today + timedelta(days=days))
            )
        elif status == "valid":
            base = base.where(InventoryBatch.expiry_date > today + timedelta(days=days))

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(InventoryBatch.expiry_date.asc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).unique().scalars().all()), int(total)

    def create_batch(self, batch: InventoryBatch) -> InventoryBatch:
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return self.get_batch(batch.id)  # type: ignore[return-value]

    def save_batch(self, batch: InventoryBatch) -> InventoryBatch:
        self.db.commit()
        self.db.refresh(batch)
        return self.get_batch(batch.id)  # type: ignore[return-value]

    def get_batches_for_product_fifo(self, product_id: int) -> list[InventoryBatch]:
        """FEFO — First Expiry, First Out."""
        today = date.today()
        stmt = (
            select(InventoryBatch)
            .where(
                and_(
                    InventoryBatch.product_id == product_id,
                    InventoryBatch.is_disposed == False,  # noqa: E712
                    InventoryBatch.quantity > 0,
                    InventoryBatch.expiry_date >= today,
                )
            )
            .order_by(InventoryBatch.expiry_date.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def summary(self, days: int = 30) -> dict:
        today = date.today()
        threshold = today + timedelta(days=days)
        batches = list(
            self.db.execute(
                select(InventoryBatch).where(
                    and_(InventoryBatch.is_disposed == False, InventoryBatch.quantity > 0)  # noqa: E712
                )
            ).scalars().all()
        )
        expired = expiring = valid = 0
        for b in batches:
            if b.expiry_date < today:
                expired += 1
            elif b.expiry_date <= threshold:
                expiring += 1
            else:
                valid += 1
        return {"expiring_soon": expiring, "expired": expired, "valid": valid, "expiring_within_days": days}

    # ---------- Notifications ----------
    def create_notification(self, notif: Notification) -> Notification:
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def list_notifications(self, user_id: int | None, unread_only: bool, skip: int, limit: int) -> tuple[list[Notification], int]:
        base = select(Notification)
        if user_id is not None:
            from sqlalchemy import or_
            base = base.where(or_(Notification.user_id == user_id, Notification.user_id.is_(None)))
        if unread_only:
            base = base.where(Notification.is_read == False)  # noqa: E712
        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all()), int(total)

    def mark_read(self, notif_id: int) -> Notification | None:
        notif = self.db.get(Notification, notif_id)
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def notification_exists(self, reference: str, notif_type: str) -> bool:
        stmt = select(Notification).where(
            and_(Notification.reference == reference, Notification.type == notif_type)
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None
