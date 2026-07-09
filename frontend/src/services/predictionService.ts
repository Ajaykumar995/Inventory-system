import api from './api'
import type { PredictionDashboard, ProductVelocity, ReorderRecommendation, NextMonthForecast } from '../types/prediction'

export const predictionService = {
  dashboard: (days?: number, limit?: number) =>
    api.get<PredictionDashboard>('/prediction/dashboard', { params: { days, limit } }),
  fastMoving: (days?: number) =>
    api.get<ProductVelocity[]>('/prediction/fast-moving', { params: { days } }),
  slowMoving: (days?: number) =>
    api.get<ProductVelocity[]>('/prediction/slow-moving', { params: { days } }),
  reorder: (days?: number) =>
    api.get<ReorderRecommendation[]>('/prediction/reorder', { params: { days } }),
  nextMonth: (days?: number) =>
    api.get<NextMonthForecast[]>('/prediction/next-month', { params: { days } }),
}
