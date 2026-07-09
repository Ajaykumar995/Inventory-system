from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import ProductResponse


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float | None = Field(default=None, ge=0, description="Defaults to product selling_price")


class SaleCreate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    payment_method: str = Field(default="cash", description="cash|card|upi|credit")
    tax_percent: float = Field(default=0, ge=0, le=100)
    discount: float = Field(default=0, ge=0)
    notes: str | None = None
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float
    line_total: float
    product: ProductResponse


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    customer_name: str | None = None
    customer_phone: str | None = None
    subtotal: float
    tax_amount: float
    discount: float
    total_amount: float
    payment_method: str
    status: str
    notes: str | None = None
    sale_date: date
    sold_by: int
    created_at: datetime
    items: list[SaleItemResponse]


class SalesSummary(BaseModel):
    today_sales: float
    monthly_sales: float
    today_count: int
    monthly_count: int
