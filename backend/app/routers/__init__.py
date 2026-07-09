from app.routers.auth import router as auth_router
from app.routers.catalog import router as catalog_router
from app.routers.inventory import router as inventory_router
from app.routers.purchase import router as purchase_router
from app.routers.sale import router as sale_router
from app.routers.expiry import router as expiry_router
from app.routers.prediction import router as prediction_router
from app.routers.search import router as search_router

__all__ = [
    "auth_router", "catalog_router", "inventory_router", "purchase_router",
    "sale_router", "expiry_router", "prediction_router", "search_router",
]