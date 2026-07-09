from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.catalog import PagedResponse
from app.schemas.expiry import BatchCreate, BatchResponse, DisposeBatchRequest, ExpirySummary, NotificationResponse
from app.services.expiry_service import ExpiryService
from app.utils.constants import UserRole

router = APIRouter(prefix="/expiry", tags=["Expiry Management"])


@router.get("/summary", response_model=ExpirySummary)
def expiry_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    days: int = Query(30, ge=1, le=365),
) -> ExpirySummary:
    return ExpiryService(db).summary(days)


@router.get("/batches", response_model=PagedResponse)
def list_batches(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    status: str | None = Query(default=None, description="expired|expiring_soon|valid"),
    product_id: int | None = Query(default=None),
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**ExpiryService(db).list_batches(
        status=status, product_id=product_id, days=days, page=page, page_size=page_size
    ))


@router.post("/batches", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def add_batch(
    body: BatchCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> BatchResponse:
    return ExpiryService(db).add_batch(body, current_user.id)


@router.post("/batches/{batch_id}/dispose", response_model=BatchResponse)
def dispose_batch(
    batch_id: int,
    body: DisposeBatchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
) -> BatchResponse:
    """Dispose expired stock — removes from inventory with audit trail."""
    return ExpiryService(db).dispose_batch(batch_id, body, current_user.id)


@router.post("/notifications/sync")
def sync_notifications(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    days: int = Query(30, ge=1, le=365),
) -> dict:
    count = ExpiryService(db).sync_expiry_notifications(days)
    return {"created": count}


@router.get("/notifications", response_model=PagedResponse)
def list_notifications(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    unread_only: bool = Query(default=False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**ExpiryService(db).list_notifications(
        current_user.id, unread_only, page, page_size
    ))


@router.put("/notifications/{notif_id}/read", response_model=NotificationResponse)
def mark_read(
    notif_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> NotificationResponse:
    return ExpiryService(db).mark_notification_read(notif_id)
