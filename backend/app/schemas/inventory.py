from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import ProductResponse


class InventoryCreate(BaseModel):
    product_id: int
    current_stock: int = Field(default=0, ge=0)
    min_stock: int = Field(default=10, ge=0)
    max_stock: int = Field(default=500, ge=1)
    location: str | None = None


class InventoryUpdate(BaseModel):
    min_stock: int | None = Field(default=None, ge=0)
    max_stock: int | None = Field(default=None, ge=1)
    location: str | None = None


class StockAdjustment(BaseModel):
    quantity: int = Field(description="Positive to add, negative to remove")
    reason: str = Field(min_length=2, max_length=500)
    reference: str | None = None


class StockReceive(BaseModel):
    quantity: int = Field(gt=0)
    reason: str = "Stock received"
    reference: str | None = None


class StockIssue(BaseModel):
    quantity: int = Field(gt=0)
    reason: str = "Stock issued"
    reference: str | None = None


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    current_stock: int
    min_stock: int
    max_stock: int
    location: str | None = None
    stock_status: str
    updated_at: datetime
    product: ProductResponse


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    movement_type: str
    quantity: int
    previous_qty: int
    new_qty: int
    reason: str | None = None
    reference: str | None = None
    created_by: int
    created_at: datetime


class DashboardStats(BaseModel):
    total_products: int
    total_categories: int
    total_suppliers: int
    low_stock: int
    out_of_stock: int
    overstock: int
    healthy_stock: int
    inventory_value: float
    total_stock_units: int
    monthly_purchases: float = 0
    today_sales: float = 0
    monthly_sales: float = 0
    expiring_soon: int = 0
    expired: int = 0
    warehouse_items: list[dict]
