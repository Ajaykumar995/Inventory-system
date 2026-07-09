import os
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repository.catalog_repository import CatalogRepository
from app.schemas.catalog import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.utils.constants import UserRole


class CatalogService:
    """
    Business logic for product & category master data.

    Master data quality directly impacts:
    - replenishment / reorder accuracy
    - expiry compliance (batch + category later)
    - BI reports and supplier negotiations
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CatalogRepository(db)

    # ---------- Categories ----------
    def create_category(self, body: CategoryCreate) -> CategoryResponse:
        if self.repo.get_category_by_name(body.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
        category = self.repo.create_category(body.name, body.description)
        return CategoryResponse.model_validate(category)

    def list_categories(self, *, q: str | None, page: int, page_size: int) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_categories(q=q, skip=skip, limit=page_size)
        return {
            "items": [CategoryResponse.model_validate(c) for c in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update_category(self, category_id: int, body: CategoryUpdate) -> CategoryResponse:
        category = self.repo.get_category(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if body.name is not None:
            existing = self.repo.get_category_by_name(body.name)
            if existing is not None and existing.id != category_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name already exists")

        updated = self.repo.update_category(category, name=body.name, description=body.description)
        return CategoryResponse.model_validate(updated)

    def delete_category(self, category_id: int) -> None:
        category = self.repo.get_category(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        # Real business rule: disallow deleting a category if products exist.
        if category.products:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete category with products",
            )

        self.repo.delete_category(category)

    # ---------- Products ----------
    def create_product(self, body: ProductCreate) -> ProductResponse:
        if self.repo.get_product_by_sku(body.sku):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="SKU already exists")
        if body.barcode and self.repo.get_product_by_barcode(body.barcode):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Barcode already exists")

        category = self.repo.get_category(body.category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")

        product = Product(
            name=body.name.strip(),
            sku=body.sku.strip().upper(),
            barcode=body.barcode.strip() if body.barcode else None,
            brand=body.brand.strip() if body.brand else None,
            category_id=body.category_id,
            unit=body.unit.strip(),
            description=body.description,
            cost_price=body.cost_price,
            selling_price=body.selling_price,
        )

        try:
            created = self.repo.create_product(product)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate product field") from exc

        return ProductResponse.model_validate(created)

    def list_products(
        self,
        *,
        q: str | None,
        category_id: int | None,
        is_active: bool | None,
        sort: str,
        order: str,
        page: int,
        page_size: int,
    ) -> dict:
        skip = (page - 1) * page_size
        items, total = self.repo.list_products(
            q=q,
            category_id=category_id,
            is_active=is_active,
            sort=sort,
            order=order,
            skip=skip,
            limit=page_size,
        )
        return {
            "items": [ProductResponse.model_validate(p) for p in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_product(self, product_id: int) -> ProductResponse:
        product = self.repo.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductResponse.model_validate(product)

    def update_product(self, product_id: int, body: ProductUpdate) -> ProductResponse:
        product = self.repo.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if body.barcode is not None and body.barcode != "":
            existing = self.repo.get_product_by_barcode(body.barcode)
            if existing is not None and existing.id != product_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Barcode already exists")

        if body.category_id is not None:
            category = self.repo.get_category(body.category_id)
            if category is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category_id")
            product.category_id = body.category_id

        for attr in ("name", "brand", "unit", "description"):
            val = getattr(body, attr)
            if val is not None:
                setattr(product, attr, val.strip() if isinstance(val, str) else val)

        if body.barcode is not None:
            product.barcode = body.barcode.strip() if body.barcode else None

        if body.cost_price is not None:
            product.cost_price = body.cost_price
        if body.selling_price is not None:
            product.selling_price = body.selling_price
        if body.is_active is not None:
            product.is_active = body.is_active

        updated = self.repo.update_product(product)
        return ProductResponse.model_validate(updated)

    def delete_product(self, product_id: int) -> None:
        product = self.repo.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        self.repo.delete_product(product)

    def upload_product_image(self, product_id: int, file: UploadFile, upload_dir: str) -> ProductResponse:
        product = self.repo.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PNG, JPEG, or WEBP images are supported",
            )

        ext = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
        }[file.content_type]

        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        filename = f"product_{product_id}{ext}"
        dest = os.path.join(upload_dir, filename)

        with open(dest, "wb") as f:
            f.write(file.file.read())

        product.image_path = f"/uploads/products/{filename}"
        updated = self.repo.update_product(product)
        return ProductResponse.model_validate(updated)

