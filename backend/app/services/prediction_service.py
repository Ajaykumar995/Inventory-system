from sqlalchemy.orm import Session

from app.repository.prediction_repository import PredictionRepository
from app.schemas.prediction import (
    NextMonthForecast,
    PredictionDashboard,
    ProductVelocity,
    ReorderRecommendation,
)


class PredictionService:
    """
    Demand forecasting and replenishment intelligence.

    Uses sales velocity over a rolling window to:
    - identify fast/slow movers
    - predict next-month demand
    - recommend reorder quantities
    """

    def __init__(self, db: Session) -> None:
        self.repo = PredictionRepository(db)

    def _build_analysis(self, days: int, limit: int) -> dict:
        raw = self.repo.sales_velocity(days)
        classified = self.repo.classify_velocity(raw, days)
        fast = [i for i in classified if i["classification"] == "fast_moving"]
        slow = [i for i in classified if i["classification"] == "slow_moving"]
        fast.sort(key=lambda x: x["daily_velocity"], reverse=True)
        slow.sort(key=lambda x: x["daily_velocity"])
        reorder = self.repo.reorder_recommendations(classified, self.repo.DEFAULT_LEAD_TIME_DAYS)
        forecast = self.repo.next_month_forecast(classified)

        return {
            "analysis_period_days": days,
            "fast_moving_count": len(fast),
            "slow_moving_count": len(slow),
            "reorder_needed_count": len(reorder),
            "total_predicted_monthly_demand": sum(i["monthly_forecast"] for i in classified),
            "fast_movers": fast[:limit],
            "slow_movers": slow[:limit],
            "reorder_recommendations": reorder[:limit],
            "next_month_forecast": forecast[:limit],
        }

    def dashboard(self, days: int = 30, limit: int = 10) -> PredictionDashboard:
        return PredictionDashboard(**self._build_analysis(days, limit))

    def fast_moving(self, days: int = 30, limit: int = 20) -> list[ProductVelocity]:
        raw = self.repo.classify_velocity(self.repo.sales_velocity(days), days)
        items = [i for i in raw if i["classification"] == "fast_moving"]
        items.sort(key=lambda x: x["daily_velocity"], reverse=True)
        return [ProductVelocity(**i) for i in items[:limit]]

    def slow_moving(self, days: int = 30, limit: int = 20) -> list[ProductVelocity]:
        raw = self.repo.classify_velocity(self.repo.sales_velocity(days), days)
        items = [i for i in raw if i["classification"] == "slow_moving"]
        items.sort(key=lambda x: x["daily_velocity"])
        return [ProductVelocity(**i) for i in items[:limit]]

    def reorder_recommendations(self, days: int = 30, limit: int = 50) -> list[ReorderRecommendation]:
        raw = self.repo.classify_velocity(self.repo.sales_velocity(days), days)
        recs = self.repo.reorder_recommendations(raw, self.repo.DEFAULT_LEAD_TIME_DAYS)
        return [ReorderRecommendation(**r) for r in recs[:limit]]

    def next_month_forecast(self, days: int = 30, limit: int = 50) -> list[NextMonthForecast]:
        raw = self.repo.sales_velocity(days)
        forecasts = self.repo.next_month_forecast(raw)
        return [NextMonthForecast(**f) for f in forecasts[:limit]]
