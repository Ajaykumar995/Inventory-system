export interface ProductVelocity {
  product_id: number
  product_name: string
  sku: string
  category: string
  current_stock: number
  units_sold: number
  daily_velocity: number
  monthly_forecast: number
  classification: string
}

export interface ReorderRecommendation {
  product_id: number
  product_name: string
  sku: string
  current_stock: number
  min_stock: number
  max_stock: number
  avg_daily_sales: number
  days_of_stock_left: number | null
  recommended_qty: number
  priority: string
  reason: string
}

export interface NextMonthForecast {
  product_id: number
  product_name: string
  sku: string
  current_stock: number
  predicted_demand: number
  projected_stock: number
  shortfall: number
  status: string
}

export interface PredictionDashboard {
  analysis_period_days: number
  fast_moving_count: number
  slow_moving_count: number
  reorder_needed_count: number
  total_predicted_monthly_demand: number
  fast_movers: ProductVelocity[]
  slow_movers: ProductVelocity[]
  reorder_recommendations: ReorderRecommendation[]
  next_month_forecast: NextMonthForecast[]
}
