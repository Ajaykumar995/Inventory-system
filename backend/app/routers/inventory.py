from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.catalog import PagedResponse
from app.schemas.inventory import (
    DashboardStats,
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
    StockAdjustment,
    StockIssue,
    StockReceive,
)
from app.services.inventory_service import InventoryService
from app.utils.constants import UserRole

router = APIRouter(prefix="/inventory", tags=["Inventory & Stock"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> DashboardStats:
    return InventoryService(db).dashboard()


@router.post("/setup", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def setup_inventory(
    body: InventoryCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> InventoryResponse:
    return InventoryService(db).setup_inventory(body)


@router.get("/stock", response_model=PagedResponse)
def list_stock(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str | None = Query(default=None),
    status: str | None = Query(default=None, description="out_of_stock|low_stock|overstock|healthy"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**InventoryService(db).list_inventory(q=q, status=status, page=page, page_size=page_size))


@router.put("/stock/{product_id}/thresholds", response_model=InventoryResponse)
def update_thresholds(
    product_id: int,
    body: InventoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> InventoryResponse:
    return InventoryService(db).update_thresholds(product_id, body)


@router.post("/stock/{product_id}/receive", response_model=InventoryResponse)
def receive_stock(
    product_id: int,
    body: StockReceive,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> InventoryResponse:
    return InventoryService(db).receive_stock(product_id, body, current_user.id)


@router.post("/stock/{product_id}/issue", response_model=InventoryResponse)
def issue_stock(
    product_id: int,
    body: StockIssue,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> InventoryResponse:
    return InventoryService(db).issue_stock(product_id, body, current_user.id)


@router.post("/stock/{product_id}/adjust", response_model=InventoryResponse)
def adjust_stock(
    product_id: int,
    body: StockAdjustment,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> InventoryResponse:
    return InventoryService(db).adjust_stock(product_id, body, current_user.id)


@router.get("/movements", response_model=PagedResponse)
def list_movements(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    product_id: int | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**InventoryService(db).list_movements(product_id, page, page_size))
