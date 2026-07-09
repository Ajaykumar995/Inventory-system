import api from './api'
import type { InventoryBatch, ExpirySummary, Notification, Paged } from '../types/expiry'

export const expiryService = {
  summary: (days?: number) => api.get<ExpirySummary>('/expiry/summary', { params: { days } }),
  listBatches: (params?: { status?: string; product_id?: number; days?: number; page?: number; page_size?: number }) =>
    api.get<Paged<InventoryBatch>>('/expiry/batches', { params }),
  addBatch: (data: { product_id: number; batch_number: string; expiry_date: string; quantity: number }) =>
    api.post<InventoryBatch>('/expiry/batches', data),
  dispose: (batchId: number, reason?: string) =>
    api.post<InventoryBatch>(`/expiry/batches/${batchId}/dispose`, { reason }),
  syncNotifications: () => api.post<{ created: number }>('/expiry/notifications/sync'),
  listNotifications: (params?: { unread_only?: boolean; page?: number; page_size?: number }) =>
    api.get<Paged<Notification>>('/expiry/notifications', { params }),
  markRead: (id: number) => api.put<Notification>(`/expiry/notifications/${id}/read`),
}
