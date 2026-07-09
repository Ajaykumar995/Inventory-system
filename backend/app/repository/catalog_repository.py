from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.product import Product


class CatalogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- Categories ----------
    def get_category(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_category_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(func.lower(Category.name) == name.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def list_categories(self, q: str | None, skip: int, limit: int) -> tuple[list[Category], int]:
        base = select(Category)
        if q:
            like = f"%{q.strip().lower()}%"
            base = base.where(func.lower(Category.name).like(like))

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(Category.name.asc()).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).scalars().all())
        return items, int(total)

    def create_category(self, name: str, description: str | None) -> Category:
        category = Category(name=name.strip(), description=description)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(self, category: Category, *, name: str | None, description: str | None) -> Category:
        if name is not None:
            category.name = name.strip()
        if description is not None:
            category.description = description
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category: Category) -> None:
        self.db.delete(category)
        self.db.commit()

    # ---------- Products ----------
    def get_product(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id == product_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_product_by_sku(self, sku: str) -> Product | None:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(func.lower(Product.sku) == sku.strip().lower())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_product_by_barcode(self, barcode: str) -> Product | None:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.barcode == barcode.strip())
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_products(
        self,
        *,
        q: str | None,
        category_id: int | None,
        is_active: bool | None,
        sort: str,
        order: str,
        skip: int,
        limit: int,
    ) -> tuple[list[Product], int]:
        base = select(Product).options(joinedload(Product.category))

        filters = []
        if category_id is not None:
            filters.append(Product.category_id == category_id)
        if is_active is not None:
            filters.append(Product.is_active == is_active)
        if q:
            like = f"%{q.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(Product.name).like(like),
                    func.lower(Product.sku).like(like),
                    func.lower(func.coalesce(Product.brand, "")).like(like),
                    func.coalesce(Product.barcode, "").like(f"%{q.strip()}%"),
                )
            )
        if filters:
            base = base.where(and_(*filters))

        sort_map = {
            "name": Product.name,
            "sku": Product.sku,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at,
        }
        sort_col = sort_map.get(sort, Product.updated_at)
        sort_col = sort_col.desc() if order.lower() == "desc" else sort_col.asc()

        total = self.db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        stmt = base.order_by(sort_col).offset(skip).limit(limit)
        items = list(self.db.execute(stmt).unique().scalars().all())
        return items, int(total)

    def create_product(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return self.get_product(product.id)  # type: ignore[return-value]

    def update_product(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return self.get_product(product.id)  # type: ignore[return-value]

    def delete_product(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()

