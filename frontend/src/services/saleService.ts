import api from './api'
import type { Sale, SalesSummary, Paged } from '../types/sale'

export const saleService = {
  create: (data: {
    customer_name?: string
    customer_phone?: string
    payment_method?: string
    tax_percent?: number
    discount?: number
    notes?: string
    items: { product_id: number; quantity: number; unit_price?: number }[]
  }) => api.post<Sale>('/sales', data),

  list: (params?: { q?: string; page?: number; page_size?: number }) =>
    api.get<Paged<Sale>>('/sales', { params }),

  get: (id: number) => api.get<Sale>(`/sales/${id}`),

  getInvoice: (invoiceNumber: string) => api.get<Sale>(`/sales/invoice/${invoiceNumber}`),

  summary: () => api.get<SalesSummary>('/sales/summary'),

  cancel: (id: number) => api.post<Sale>(`/sales/${id}/cancel`),
}
