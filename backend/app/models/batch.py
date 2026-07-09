from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InventoryBatch(Base):
    """
    Batch-level stock with expiry tracking.

    Critical for pharmacies — medicines must be sold/dispensed before expiry (FEFO).
    """

    __tablename__ = "inventory_batches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    batch_number: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_disposed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship("Product", back_populates="batches")

    @property
    def days_to_expiry(self) -> int:
        return (self.expiry_date - date.today()).days

    @property
    def expiry_status(self) -> str:
        days = self.days_to_expiry
        if days < 0:
            return "expired"
        if days <= 30:
            return "expiring_soon"
        return "valid"
