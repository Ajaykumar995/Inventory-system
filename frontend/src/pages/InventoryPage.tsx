import { useEffect, useState } from 'react'
import { inventoryService } from '../services/inventoryService'
import { catalogService } from '../services/catalogService'
import { MAX_PAGE_SIZE } from '../utils/constants'
import type { InventoryItem } from '../types/inventory'
import type { Product } from '../types/catalog'

const statusBadge: Record<string, string> = {
  healthy: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  low_stock: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  out_of_stock: 'bg-red-500/20 text-red-300 border-red-500/30',
  overstock: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
}

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [filter, setFilter] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [setupForm, setSetupForm] = useState({ product_id: 0, current_stock: 0, min_stock: 10, max_stock: 500 })

  const load = async () => {
    setLoading(true)
    try {
      const [stock, prods] = await Promise.all([
        inventoryService.listStock({ q: filter || undefined, status: status || undefined, page_size: 50 }),
        catalogService.listProducts({ page_size: MAX_PAGE_SIZE }),
      ])
      setItems(stock.data.items)
      setProducts(prods.data.items)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const setup = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await inventoryService.setup(setupForm)
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Setup failed')
    }
  }

  const quickAction = async (productId: number, action: 'receive' | 'issue', qty: number) => {
    setError('')
    try {
      if (action === 'receive') await inventoryService.receive(productId, { quantity: qty })
      else await inventoryService.issue(productId, { quantity: qty, reason: 'Issued' })
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Action failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
          Stock Management
        </h1>
        <p className="text-slate-400 mt-1">Track levels, receive stock, issue items, prevent shortages</p>
      </div>

      {/* Setup new inventory */}
      <form onSubmit={setup} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">Initialize Stock for Product</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <select
            className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm"
            value={setupForm.product_id || ''}
            onChange={(e) => setSetupForm({ ...setupForm, product_id: Number(e.target.value) })}
            required
          >
            <option value="">Select Product</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
          </select>
          <input type="number" placeholder="Current Stock" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={setupForm.current_stock} onChange={(e) => setSetupForm({ ...setupForm, current_stock: Number(e.target.value) })} />
          <input type="number" placeholder="Min Stock" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={setupForm.min_stock} onChange={(e) => setSetupForm({ ...setupForm, min_stock: Number(e.target.value) })} />
          <input type="number" placeholder="Max Stock" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={setupForm.max_stock} onChange={(e) => setSetupForm({ ...setupForm, max_stock: Number(e.target.value) })} />
          <button className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition">Setup</button>
        </div>
      </form>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <input className="px-4 py-2 rounded-xl glass border border-white/10 text-sm flex-1 min-w-[200px]" placeholder="Search..." value={filter} onChange={(e) => setFilter(e.target.value)} />
        <select className="px-4 py-2 rounded-xl glass border border-white/10 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All Status</option>
          <option value="healthy">Healthy</option>
          <option value="low_stock">Low Stock</option>
          <option value="out_of_stock">Out of Stock</option>
          <option value="overstock">Overstock</option>
        </select>
        <button onClick={load} className="px-5 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 text-sm transition">Search</button>
      </div>

      {/* Stock table */}
      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-white/5 text-left">
              <tr>
                <th className="px-5 py-3 text-slate-400 font-medium">Product</th>
                <th className="px-5 py-3 text-slate-400 font-medium">SKU</th>
                <th className="px-5 py-3 text-slate-400 font-medium">Stock</th>
                <th className="px-5 py-3 text-slate-400 font-medium">Min / Max</th>
                <th className="px-5 py-3 text-slate-400 font-medium">Status</th>
                <th className="px-5 py-3 text-slate-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {items.map((inv) => (
                <tr key={inv.id} className="hover:bg-white/5 transition">
                  <td className="px-5 py-3">
                    <div className="font-medium text-white">{inv.product.name}</div>
                    <div className="text-xs text-slate-500">{inv.product.category?.name}</div>
                  </td>
                  <td className="px-5 py-3 font-mono text-cyan-400">{inv.product.sku}</td>
                  <td className="px-5 py-3 text-lg font-bold">{inv.current_stock}</td>
                  <td className="px-5 py-3 text-slate-400">{inv.min_stock} / {inv.max_stock}</td>
                  <td className="px-5 py-3">
                    <span className={`px-2 py-1 rounded-lg text-xs border ${statusBadge[inv.stock_status] ?? ''}`}>
                      {inv.stock_status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex gap-2">
                      <button onClick={() => quickAction(inv.product_id, 'receive', 10)} className="px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs hover:bg-emerald-500/30 transition">+10</button>
                      <button onClick={() => quickAction(inv.product_id, 'issue', 5)} className="px-2 py-1 rounded-lg bg-red-500/20 text-red-300 text-xs hover:bg-red-500/30 transition">-5</button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && items.length === 0 && (
                <tr><td colSpan={6} className="px-5 py-8 text-center text-slate-500">No inventory records. Setup stock for a product above.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
