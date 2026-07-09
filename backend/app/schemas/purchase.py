from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import ProductResponse


class SupplierCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    rating: float
    is_active: bool
    created_at: datetime


class SupplierPerformance(BaseModel):
    supplier_id: int
    supplier_name: str
    total_orders: int
    received_orders: int
    on_time_deliveries: int
    delayed_deliveries: int
    avg_delivery_days: float | None
    on_time_rate: float


class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity_ordered: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    batch_number: str | None = None


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    expected_delivery: date | None = None
    notes: str | None = None
    items: list[PurchaseItemCreate] = Field(min_length=1)


class PurchaseItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_price: float
    batch_number: str | None = None
    product: ProductResponse


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    po_number: str
    supplier_id: int
    status: str
    order_date: date
    expected_delivery: date | None = None
    received_date: date | None = None
    total_amount: float
    notes: str | None = None
    created_by: int
    created_at: datetime
    supplier: SupplierResponse
    items: list[PurchaseItemResponse]


class ReceiveItemRequest(BaseModel):
    purchase_item_id: int
    quantity: int = Field(gt=0)
    batch_number: str | None = None
    expiry_date: date | None = None


class ReceivePORequest(BaseModel):
    items: list[ReceiveItemRequest]
    received_date: date | None = None
