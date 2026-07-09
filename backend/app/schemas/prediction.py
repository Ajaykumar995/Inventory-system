from pydantic import BaseModel, Field


class ProductVelocity(BaseModel):
    product_id: int
    product_name: str
    sku: str
    category: str
    current_stock: int
    units_sold: int
    daily_velocity: float
    monthly_forecast: int
    classification: str  # fast_moving | slow_moving | normal


class ReorderRecommendation(BaseModel):
    product_id: int
    product_name: str
    sku: str
    current_stock: int
    min_stock: int
    max_stock: int
    avg_daily_sales: float
    days_of_stock_left: float | None
    recommended_qty: int
    priority: str  # critical | high | medium | low
    reason: str


class NextMonthForecast(BaseModel):
    product_id: int
    product_name: str
    sku: str
    current_stock: int
    predicted_demand: int
    projected_stock: int
    shortfall: int
    status: str  # sufficient | reorder_needed | overstock_risk


class PredictionDashboard(BaseModel):
    analysis_period_days: int
    fast_moving_count: int
    slow_moving_count: int
    reorder_needed_count: int
    total_predicted_monthly_demand: int
    fast_movers: list[ProductVelocity]
    slow_movers: list[ProductVelocity]
    reorder_recommendations: list[ReorderRecommendation]
    next_month_forecast: list[NextMonthForecast]
