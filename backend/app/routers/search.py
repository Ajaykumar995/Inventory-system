from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.services.search_service import SearchService
from app.utils.constants import UserRole

router = APIRouter(prefix="/search", tags=["Global Search"])


@router.get("")
def global_search(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.EMPLOYEE))],
    q: str = Query(..., min_length=2),
    limit: int = Query(8, ge=1, le=20),
) -> dict:
    return SearchService(db).search(q, limit=limit)
