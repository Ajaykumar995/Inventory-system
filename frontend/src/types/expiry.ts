export interface InventoryBatch {
  id: number
  product_id: number
  batch_number: string
  expiry_date: string
  quantity: number
  received_date: string
  is_disposed: boolean
  days_to_expiry: number
  expiry_status: 'valid' | 'expiring_soon' | 'expired'
  product: { id: number; name: string; sku: string; category: { id: number; name: string } }
}

export interface ExpirySummary {
  expiring_soon: number
  expired: number
  valid: number
  expiring_within_days: number
}

export interface Notification {
  id: number
  type: string
  title: string
  message: string
  reference?: string
  is_read: boolean
  created_at: string
}

export interface Paged<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
