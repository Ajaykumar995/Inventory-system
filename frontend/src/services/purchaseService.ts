import api from './api'
import type { PurchaseOrder, Paged, Supplier, SupplierPerformance } from '../types/purchase'

export const purchaseService = {
  listSuppliers: (params?: { q?: string; page?: number; page_size?: number }) =>
    api.get<Paged<Supplier>>('/purchases/suppliers', { params }),
  createSupplier: (data: { name: string; contact_person?: string; email?: string; phone?: string; address?: string }) =>
    api.post<Supplier>('/purchases/suppliers', data),
  supplierPerformance: (id: number) =>
    api.get<SupplierPerformance>(`/purchases/suppliers/${id}/performance`),

  listOrders: (params?: { status?: string; supplier_id?: number; page?: number; page_size?: number }) =>
    api.get<Paged<PurchaseOrder>>('/purchases/orders', { params }),
  createOrder: (data: {
    supplier_id: number
    expected_delivery?: string
    notes?: string
    items: { product_id: number; quantity_ordered: number; unit_price: number; batch_number?: string }[]
  }) => api.post<PurchaseOrder>('/purchases/orders', data),
  receiveOrder: (poId: number, items: { purchase_item_id: number; quantity: number }[]) =>
    api.post<PurchaseOrder>(`/purchases/orders/${poId}/receive`, { items }),
  cancelOrder: (poId: number) =>
    api.post<PurchaseOrder>(`/purchases/orders/${poId}/cancel`),
}
