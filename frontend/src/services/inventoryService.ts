import api from './api'
import type { DashboardStats, InventoryItem, Paged } from '../types/inventory'

export const inventoryService = {
  dashboard: () => api.get<DashboardStats>('/inventory/dashboard'),
  listStock: (params?: { q?: string; status?: string; page?: number; page_size?: number }) =>
    api.get<Paged<InventoryItem>>('/inventory/stock', { params }),
  setup: (data: { product_id: number; current_stock?: number; min_stock?: number; max_stock?: number; location?: string }) =>
    api.post<InventoryItem>('/inventory/setup', data),
  receive: (productId: number, data: { quantity: number; reason?: string }) =>
    api.post<InventoryItem>(`/inventory/stock/${productId}/receive`, data),
  issue: (productId: number, data: { quantity: number; reason?: string }) =>
    api.post<InventoryItem>(`/inventory/stock/${productId}/issue`, data),
  adjust: (productId: number, data: { quantity: number; reason: string }) =>
    api.post<InventoryItem>(`/inventory/stock/${productId}/adjust`, data),
  listMovements: (params?: { product_id?: number; page?: number; page_size?: number }) =>
    api.get<Paged<import('../types/inventory').StockMovement>>('/inventory/movements', { params }),
}
