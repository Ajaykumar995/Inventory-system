from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):
    """
    Product master data (not stock).

    This captures identifiers used in real operations:
    - SKU: internal unique identifier for procurement + warehouse picking
    - Barcode: retail scanning at POS / receiving
    - Brand: reporting and supplier negotiations
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)

    unit: Mapped[str] = mapped_column(String(40), default="unit", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Used later for inventory valuation and reorder suggestions.
    cost_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    selling_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    inventory: Mapped["Inventory | None"] = relationship("Inventory", back_populates="product", uselist=False)
    movements: Mapped[list["StockMovement"]] = relationship("StockMovement", back_populates="product")
    batches: Mapped[list["InventoryBatch"]] = relationship("InventoryBatch", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku='{self.sku}', name='{self.name}')>"

