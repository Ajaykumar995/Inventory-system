import api from './api'

export interface SearchHit {
  type: 'product' | 'category' | 'supplier'
  id: number
  label: string
  sublabel?: string
  path: string
}

export const searchService = {
  search: (q: string) => api.get<{ query: string; results: SearchHit[] }>('/search', { params: { q } }),
}
