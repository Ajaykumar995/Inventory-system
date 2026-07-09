export interface WarehouseItem {
  product_id: number
  name: string
  sku: string
  stock: number
  min_stock: number
  max_stock: number
  status: 'healthy' | 'low_stock' | 'out_of_stock' | 'overstock'
}

export interface DashboardStats {
  total_products: number
  total_categories: number
  total_suppliers: number
  low_stock: number
  out_of_stock: number
  overstock: number
  healthy_stock: number
  inventory_value: number
  total_stock_units: number
  monthly_purchases: number
  today_sales: number
  monthly_sales: number
  expiring_soon: number
  expired: number
  warehouse_items: WarehouseItem[]
}

export interface InventoryItem {
  id: number
  product_id: number
  current_stock: number
  min_stock: number
  max_stock: number
  location?: string
  stock_status: string
  updated_at: string
  product: {
    id: number
    name: string
    sku: string
    brand?: string
    category: { id: number; name: string }
  }
}

export interface StockMovement {
  id: number
  product_id: number
  movement_type: string
  quantity: number
  previous_qty: number
  new_qty: number
  reason?: string
  reference?: string
  created_by: number
  created_at: string
}

export interface Paged<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
