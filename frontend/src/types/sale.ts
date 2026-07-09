export interface SaleItem {
  id: number
  product_id: number
  quantity: number
  unit_price: number
  line_total: number
  product: { id: number; name: string; sku: string; selling_price?: number; category: { id: number; name: string } }
}

export interface Sale {
  id: number
  invoice_number: string
  customer_name?: string
  customer_phone?: string
  subtotal: number
  tax_amount: number
  discount: number
  total_amount: number
  payment_method: string
  status: string
  notes?: string
  sale_date: string
  sold_by: number
  created_at: string
  items: SaleItem[]
}

export interface SalesSummary {
  today_sales: number
  monthly_sales: number
  today_count: number
  monthly_count: number
}

export interface Paged<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface CartLine {
  product_id: number
  name: string
  sku: string
  quantity: number
  unit_price: number
}
