import api from './api'
import type { Category, Paged, Product } from '../types/catalog'

export const catalogService = {
  listCategories: (params: { q?: string; page?: number; page_size?: number }) =>
    api.get<Paged<Category>>('/catalog/categories', { params }),

  createCategory: (data: { name: string; description?: string }) =>
    api.post<Category>('/catalog/categories', data),

  updateCategory: (id: number, data: { name?: string; description?: string }) =>
    api.put<Category>(`/catalog/categories/${id}`, data),

  deleteCategory: (id: number) =>
    api.delete(`/catalog/categories/${id}`),

  listProducts: (params: {
    q?: string
    category_id?: number
    is_active?: boolean
    sort?: string
    order?: string
    page?: number
    page_size?: number
  }) => api.get<Paged<Product>>('/catalog/products', { params }),

  createProduct: (data: {
    name: string
    sku: string
    barcode?: string
    brand?: string
    category_id: number
    unit?: string
    description?: string
    cost_price?: number
    selling_price?: number
  }) => api.post<Product>('/catalog/products', data),

  updateProduct: (id: number, data: {
    name?: string
    barcode?: string
    brand?: string
    category_id?: number
    unit?: string
    description?: string
    cost_price?: number
    selling_price?: number
    is_active?: boolean
  }) => api.put<Product>(`/catalog/products/${id}`, data),

  deleteProduct: (id: number) =>
    api.delete(`/catalog/products/${id}`),

  uploadProductImage: (productId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<Product>(`/catalog/products/${productId}/image`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

