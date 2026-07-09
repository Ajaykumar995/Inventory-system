export interface Supplier {
  id: number
  name: string
  contact_person?: string
  email?: string
  phone?: string
  address?: string
  rating: number
  is_active: boolean
  created_at: string
}

export interface SupplierPerformance {
  supplier_id: number
  supplier_name: string
  total_orders: number
  received_orders: number
  on_time_deliveries: number
  delayed_deliveries: number
  avg_delivery_days: number | null
  on_time_rate: number
}

export interface PurchaseItem {
  id: number
  product_id: number
  quantity_ordered: number
  quantity_received: number
  unit_price: number
  batch_number?: string
  product: { id: number; name: string; sku: string; category: { id: number; name: string } }
}

export interface PurchaseOrder {
  id: number
  po_number: string
  supplier_id: number
  status: string
  order_date: string
  expected_delivery?: string
  received_date?: string
  total_amount: number
  notes?: string
  created_by: number
  created_at: string
  supplier: Supplier
  items: PurchaseItem[]
}

export interface Paged<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
