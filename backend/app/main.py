from contextlib import asynccontextmanager

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy import func, select

from app.config import get_settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.database.seed import seed_demo_data
from app.database.seed_ajay_arif import ensure_ajay_arif_data
from app.models.category import Category
from app.models.product import Product
from app.repository.user_repository import UserRepository
from app.routers import auth_router, catalog_router, inventory_router, purchase_router, sale_router, expiry_router, prediction_router, search_router
from app.utils.constants import DEFAULT_ROLES

settings = get_settings()

# Static upload dir must exist at import time (tests import app).
os.makedirs("uploads/products", exist_ok=True)


def init_database() -> None:
    """Create tables and seed default roles on startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        UserRepository(db).seed_roles(DEFAULT_ROLES)
        if settings.seed_demo_data:
            result = seed_demo_data(db)
            if result.get("seeded"):
                print(f"[SEED] {result['message']} — login: {result['login']['username']} / {result['login']['password']}")
            elif result.get("message"):
                print(f"[SEED] {result['message']}")
        ajay_arif = ensure_ajay_arif_data(db)
        if ajay_arif.get("products_added", 0) > 0 or ajay_arif.get("users_added", 0) > 0:
            print(f"[SEED] Ajay & Arif: {ajay_arif['products_added']} products, {ajay_arif['users_added']} users added")
        product_count = db.execute(select(func.count()).select_from(Product)).scalar_one()
        category_count = db.execute(select(func.count()).select_from(Category)).scalar_one()
        if int(product_count) == 0:
            print("[SEED] No products in database. Run: python -m app.database.seed --force")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise inventory management with stock prediction, expiry tracking, "
        "supplier performance, and business intelligence for retail & pharmacy."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(inventory_router, prefix="/api/v1")
app.include_router(purchase_router, prefix="/api/v1")
app.include_router(sale_router, prefix="/api/v1")
app.include_router(expiry_router, prefix="/api/v1")
app.include_router(prediction_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.app_version}
