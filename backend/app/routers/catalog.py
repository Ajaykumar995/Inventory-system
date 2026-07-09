from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.catalog import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PagedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.catalog_service import CatalogService
from app.utils.constants import UserRole

router = APIRouter(prefix="/catalog", tags=["Catalog (Products & Categories)"])


# ----------------- Categories -----------------
@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    body: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> CategoryResponse:
    return CatalogService(db).create_category(body)


@router.get("/categories", response_model=PagedResponse)
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str | None = Query(default=None, description="Search by category name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    result = CatalogService(db).list_categories(q=q, page=page, page_size=page_size)
    return PagedResponse(**result)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    body: CategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> CategoryResponse:
    return CatalogService(db).update_category(category_id, body)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.ADMIN))],
) -> None:
    CatalogService(db).delete_category(category_id)


# ----------------- Products -----------------
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> ProductResponse:
    return CatalogService(db).create_product(body)


@router.get("/products", response_model=PagedResponse)
def list_products(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str | None = Query(default=None, description="Search by name, sku, brand, barcode"),
    category_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    sort: str = Query(default="updated_at", description="name|sku|created_at|updated_at"),
    order: str = Query(default="desc", description="asc|desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    result = CatalogService(db).list_products(
        q=q,
        category_id=category_id,
        is_active=is_active,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )
    return PagedResponse(**result)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> ProductResponse:
    return CatalogService(db).get_product(product_id)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> ProductResponse:
    return CatalogService(db).update_product(product_id, body)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.ADMIN))],
) -> None:
    CatalogService(db).delete_product(product_id)


@router.post("/products/{product_id}/image", response_model=ProductResponse)
def upload_product_image(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
    file: UploadFile = File(...),
) -> ProductResponse:
    return CatalogService(db).upload_product_image(
        product_id=product_id,
        file=file,
        upload_dir="uploads/products",
    )

