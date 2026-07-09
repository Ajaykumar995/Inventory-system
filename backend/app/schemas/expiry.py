from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import ProductResponse


class BatchCreate(BaseModel):
    product_id: int
    batch_number: str = Field(min_length=1, max_length=80)
    expiry_date: date
    quantity: int = Field(gt=0)


class BatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    batch_number: str
    expiry_date: date
    quantity: int
    received_date: date
    is_disposed: bool
    days_to_expiry: int
    expiry_status: str
    product: ProductResponse


class ExpirySummary(BaseModel):
    expiring_soon: int
    expired: int
    valid: int
    expiring_within_days: int


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    message: str
    reference: str | None = None
    is_read: bool
    created_at: datetime


class DisposeBatchRequest(BaseModel):
    reason: str = Field(default="Expired stock disposed", min_length=2)
