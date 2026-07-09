from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=220)
    sku: str = Field(min_length=2, max_length=80)
    barcode: str | None = Field(default=None, max_length=64)
    brand: str | None = Field(default=None, max_length=120)
    category_id: int
    unit: str = Field(default="unit", max_length=40)
    description: str | None = None
    cost_price: float | None = Field(default=None, ge=0)
    selling_price: float | None = Field(default=None, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=220)
    barcode: str | None = Field(default=None, max_length=64)
    brand: str | None = Field(default=None, max_length=120)
    category_id: int | None = None
    unit: str | None = Field(default=None, max_length=40)
    description: str | None = None
    cost_price: float | None = Field(default=None, ge=0)
    selling_price: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    barcode: str | None = None
    brand: str | None = None
    unit: str
    description: str | None = None
    cost_price: float | None = None
    selling_price: float | None = None
    image_path: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    category: CategoryResponse


class PagedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int

