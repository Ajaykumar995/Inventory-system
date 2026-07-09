from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.catalog import PagedResponse
from app.schemas.purchase import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    ReceivePORequest,
    SupplierCreate,
    SupplierPerformance,
    SupplierResponse,
    SupplierUpdate,
)
from app.services.purchase_service import PurchaseService
from app.utils.constants import UserRole

router = APIRouter(prefix="/purchases", tags=["Purchases & Suppliers"])


# ---------- Suppliers ----------
@router.post("/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    body: SupplierCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> SupplierResponse:
    return PurchaseService(db).create_supplier(body)


@router.get("/suppliers", response_model=PagedResponse)
def list_suppliers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**PurchaseService(db).list_suppliers(q, page, page_size))


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    body: SupplierUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> SupplierResponse:
    return PurchaseService(db).update_supplier(supplier_id, body)


@router.get("/suppliers/{supplier_id}/performance", response_model=SupplierPerformance)
def supplier_performance(
    supplier_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
) -> SupplierPerformance:
    return PurchaseService(db).supplier_performance(supplier_id)


# ---------- Purchase Orders ----------
@router.post("/orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_po(
    body: PurchaseOrderCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> PurchaseOrderResponse:
    return PurchaseService(db).create_po(body, current_user.id)


@router.get("/orders", response_model=PagedResponse)
def list_pos(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    status: str | None = Query(default=None),
    supplier_id: int | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**PurchaseService(db).list_pos(status, supplier_id, page, page_size))


@router.get("/orders/{po_id}", response_model=PurchaseOrderResponse)
def get_po(
    po_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> PurchaseOrderResponse:
    return PurchaseService(db).get_po(po_id)


@router.post("/orders/{po_id}/receive", response_model=PurchaseOrderResponse)
def receive_po(
    po_id: int,
    body: ReceivePORequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> PurchaseOrderResponse:
    """Receive stock from PO — auto-updates inventory and stock movements."""
    return PurchaseService(db).receive_po(po_id, body, current_user.id)


@router.post("/orders/{po_id}/cancel", response_model=PurchaseOrderResponse)
def cancel_po(
    po_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> PurchaseOrderResponse:
    return PurchaseService(db).cancel_po(po_id)
