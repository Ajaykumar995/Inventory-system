export interface Category {
  id: number
  name: string
  description?: string
  created_at: string
}

export interface Product {
  id: number
  name: string
  sku: string
  barcode?: string
  brand?: string
  unit: string
  description?: string
  cost_price?: number
  selling_price?: number
  image_path?: string
  is_active: boolean
  created_at: string
  updated_at: string
  category: Category
}

export interface Paged<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

