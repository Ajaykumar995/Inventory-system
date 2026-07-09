from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.catalog import PagedResponse
from app.schemas.sale import SaleCreate, SaleResponse, SalesSummary
from app.services.sale_service import SaleService
from app.utils.constants import UserRole

router = APIRouter(prefix="/sales", tags=["Sales & Invoicing"])


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    body: SaleCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> SaleResponse:
    """Record a sale — validates stock, deducts inventory, generates invoice."""
    return SaleService(db).create_sale(body, current_user.id)


@router.get("", response_model=PagedResponse)
def list_sales(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str | None = Query(default=None, description="Search invoice, customer"),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PagedResponse:
    return PagedResponse(**SaleService(db).list_sales(q=q, from_date=from_date, to_date=to_date, page=page, page_size=page_size))


@router.get("/summary", response_model=SalesSummary)
def sales_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> SalesSummary:
    return SaleService(db).summary()


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> SaleResponse:
    return SaleService(db).get_sale(sale_id)


@router.get("/invoice/{invoice_number}", response_model=SaleResponse)
def get_invoice(
    invoice_number: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
) -> SaleResponse:
    return SaleService(db).get_invoice(invoice_number)


@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
    sale_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
) -> SaleResponse:
    """Cancel sale and restore inventory (Store Manager+)."""
    return SaleService(db).cancel_sale(sale_id, current_user.id)
