from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_min_role
from app.database.session import get_db
from app.models.user import User
from app.schemas.prediction import NextMonthForecast, PredictionDashboard, ProductVelocity, ReorderRecommendation
from app.services.prediction_service import PredictionService
from app.utils.constants import UserRole

router = APIRouter(prefix="/prediction", tags=["Prediction Engine"])


@router.get("/dashboard", response_model=PredictionDashboard)
def prediction_dashboard(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
    days: int = Query(30, ge=7, le=365, description="Sales analysis window in days"),
    limit: int = Query(10, ge=1, le=50),
) -> PredictionDashboard:
    return PredictionService(db).dashboard(days, limit)


@router.get("/fast-moving", response_model=list[ProductVelocity])
def fast_moving(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
    days: int = Query(30, ge=7, le=365),
    limit: int = Query(20, ge=1, le=100),
) -> list[ProductVelocity]:
    return PredictionService(db).fast_moving(days, limit)


@router.get("/slow-moving", response_model=list[ProductVelocity])
def slow_moving(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
    days: int = Query(30, ge=7, le=365),
    limit: int = Query(20, ge=1, le=100),
) -> list[ProductVelocity]:
    return PredictionService(db).slow_moving(days, limit)


@router.get("/reorder", response_model=list[ReorderRecommendation])
def reorder_recommendations(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.INVENTORY_MANAGER))],
    days: int = Query(30, ge=7, le=365),
    limit: int = Query(50, ge=1, le=100),
) -> list[ReorderRecommendation]:
    return PredictionService(db).reorder_recommendations(days, limit)


@router.get("/next-month", response_model=list[NextMonthForecast])
def next_month_forecast(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_min_role(UserRole.STORE_MANAGER))],
    days: int = Query(30, ge=7, le=365),
    limit: int = Query(50, ge=1, le=100),
) -> list[NextMonthForecast]:
    return PredictionService(db).next_month_forecast(days, limit)
