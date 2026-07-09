from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.batch import InventoryBatch
from app.models.inventory import MovementType, StockMovement
from app.models.notification import Notification, NotificationType
from app.repository.catalog_repository import CatalogRepository
from app.repository.expiry_repository import ExpiryRepository
from app.repository.inventory_repository import InventoryRepository
from app.schemas.expiry import BatchCreate, BatchResponse, DisposeBatchRequest, ExpirySummary, NotificationResponse


class ExpiryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ExpiryRepository(db)
        self.catalog = CatalogRepository(db)
        self.inventory_repo = InventoryRepository(db)

    def _batch_response(self, batch: InventoryBatch) -> BatchResponse:
        data = BatchResponse.model_validate(batch)
        data.days_to_expiry = batch.days_to_expiry
        data.expiry_status = batch.expiry_status
        return data

    def add_batch(self, body: BatchCreate, user_id: int) -> BatchResponse:
        product = self.catalog.get_product(body.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if body.expiry_date < date.today():
            raise HTTPException(status_code=400, detail="Cannot add batch with past expiry date")

        inv = self.inventory_repo.get_by_product(body.product_id)
        if inv is None:
            from app.models.inventory import Inventory
            inv = Inventory(product_id=body.product_id, current_stock=0, min_stock=10, max_stock=500)
            inv = self.inventory_repo.create(inv)

        prev = inv.current_stock
        inv.current_stock = prev + body.quantity
        self.inventory_repo.save(inv)

        batch = InventoryBatch(
            product_id=body.product_id,
            batch_number=body.batch_number.strip(),
            expiry_date=body.expiry_date,
            quantity=body.quantity,
            received_date=date.today(),
        )
        created = self.repo.create_batch(batch)

        self.inventory_repo.add_movement(
            StockMovement(
                product_id=body.product_id,
                movement_type=MovementType.IN.value,
                quantity=body.quantity,
                previous_qty=prev,
                new_qty=inv.current_stock,
                reason=f"Batch received: {body.batch_number}",
                reference=body.batch_number,
                created_by=user_id,
            )
        )
        return self._batch_response(created)

    def list_batches(
        self, *, status: str | None, product_id: int | None, days: int, page: int, page_size: int
    ) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_batches(
            status=status, product_id=product_id, days=days, skip=skip, limit=page_size
        )
        return {
            "items": [self._batch_response(b) for b in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def summary(self, days: int = 30) -> ExpirySummary:
        return ExpirySummary(**self.repo.summary(days))

    def dispose_batch(self, batch_id: int, body: DisposeBatchRequest, user_id: int) -> BatchResponse:
        batch = self.repo.get_batch(batch_id)
        if batch is None:
            raise HTTPException(status_code=404, detail="Batch not found")
        if batch.is_disposed:
            raise HTTPException(status_code=400, detail="Batch already disposed")

        inv = self.inventory_repo.get_by_product(batch.product_id)
        if inv is None:
            raise HTTPException(status_code=400, detail="No inventory for product")

        qty = batch.quantity
        prev = inv.current_stock
        inv.current_stock = max(0, prev - qty)
        self.inventory_repo.save(inv)

        batch.quantity = 0
        batch.is_disposed = True
        updated = self.repo.save_batch(batch)

        self.inventory_repo.add_movement(
            StockMovement(
                product_id=batch.product_id,
                movement_type=MovementType.OUT.value,
                quantity=qty,
                previous_qty=prev,
                new_qty=inv.current_stock,
                reason=body.reason,
                reference=batch.batch_number,
                created_by=user_id,
            )
        )
        return self._batch_response(updated)

    def sync_expiry_notifications(self, days: int = 30) -> int:
        """Generate notifications for expiring/expired batches (idempotent by reference)."""
        created = 0
        batches, _ = self.repo.list_batches(status=None, product_id=None, days=days, skip=0, limit=500)

        for batch in batches:
            ref = f"batch-{batch.id}"
            if batch.expiry_status == "expired":
                if not self.repo.notification_exists(ref, NotificationType.EXPIRED.value):
                    self.repo.create_notification(
                        Notification(
                            type=NotificationType.EXPIRED.value,
                            title="Expired Product",
                            message=f"{batch.product.name} (Batch {batch.batch_number}) expired on {batch.expiry_date}",
                            reference=ref,
                        )
                    )
                    created += 1
            elif batch.expiry_status == "expiring_soon":
                if not self.repo.notification_exists(ref, NotificationType.EXPIRY_ALERT.value):
                    self.repo.create_notification(
                        Notification(
                            type=NotificationType.EXPIRY_ALERT.value,
                            title="Expiring Soon",
                            message=f"{batch.product.name} (Batch {batch.batch_number}) expires in {batch.days_to_expiry} days",
                            reference=ref,
                        )
                    )
                    created += 1
        return created

    def list_notifications(self, user_id: int, unread_only: bool, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_notifications(user_id, unread_only, skip, limit=page_size)
        return {
            "items": [NotificationResponse.model_validate(n) for n in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def mark_notification_read(self, notif_id: int) -> NotificationResponse:
        notif = self.repo.mark_read(notif_id)
        if notif is None:
            raise HTTPException(status_code=404, detail="Notification not found")
        return NotificationResponse.model_validate(notif)

    def deduct_from_batches_fefo(self, product_id: int, quantity: int) -> None:
        """Deduct sale quantity from batches using FEFO."""
        remaining = quantity
        batches = self.repo.get_batches_for_product_fifo(product_id)
        for batch in batches:
            if remaining <= 0:
                break
            take = min(batch.quantity, remaining)
            batch.quantity -= take
            remaining -= take
            self.repo.save_batch(batch)
        # If no batches tracked, skip (inventory still deducted at aggregate level)
