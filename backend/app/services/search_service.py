from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.models.supplier import Supplier


class SearchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def search(self, q: str, *, limit: int = 8) -> dict:
        term = q.strip().lower()
        if len(term) < 2:
            return {"query": q, "results": []}

        like = f"%{term}%"
        results: list[dict] = []

        products = self.db.execute(
            select(Product).where(
                or_(
                    func.lower(Product.name).like(like),
                    func.lower(Product.sku).like(like),
                    func.lower(Product.barcode).like(like),
                )
            ).limit(limit)
        ).scalars().all()

        for p in products:
            results.append({
                "type": "product",
                "id": p.id,
                "label": p.name,
                "sublabel": p.sku,
                "path": "/products",
            })

        categories = self.db.execute(
            select(Category).where(func.lower(Category.name).like(like)).limit(limit)
        ).scalars().all()

        for c in categories:
            results.append({
                "type": "category",
                "id": c.id,
                "label": c.name,
                "sublabel": c.description,
                "path": "/categories",
            })

        suppliers = self.db.execute(
            select(Supplier).where(func.lower(Supplier.name).like(like)).limit(limit)
        ).scalars().all()

        for s in suppliers:
            results.append({
                "type": "supplier",
                "id": s.id,
                "label": s.name,
                "sublabel": s.contact_person,
                "path": "/suppliers",
            })

        return {"query": q, "results": results[:limit]}
