import { useEffect, useState } from 'react'
import { catalogService } from '../services/catalogService'
import { inventoryService } from '../services/inventoryService'
import { saleService } from '../services/saleService'
import { MAX_PAGE_SIZE } from '../utils/constants'
import type { Sale, CartLine } from '../types/sale'
import type { Product } from '../types/catalog'

export default function SalesPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [stockMap, setStockMap] = useState<Record<number, number>>({})
  const [cart, setCart] = useState<CartLine[]>([])
  const [sales, setSales] = useState<Sale[]>([])
  const [invoice, setInvoice] = useState<Sale | null>(null)
  const [error, setError] = useState('')
  const [customer, setCustomer] = useState({ name: '', phone: '' })
  const [payment, setPayment] = useState('cash')
  const [taxPercent, setTaxPercent] = useState(5)

  const load = async () => {
    const [prods, stock, history] = await Promise.all([
      catalogService.listProducts({ page_size: MAX_PAGE_SIZE, is_active: true }),
      inventoryService.listStock({ page_size: MAX_PAGE_SIZE }),
      saleService.list({ page_size: 20 }),
    ])
    setProducts(prods.data.items)
    const sm: Record<number, number> = {}
    stock.data.items.forEach((i) => { sm[i.product_id] = i.current_stock })
    setStockMap(sm)
    setSales(history.data.items)
  }

  useEffect(() => { load() }, [])

  const addToCart = (p: Product) => {
    const available = stockMap[p.id] ?? 0
    if (available <= 0) { setError(`No stock for ${p.name}`); return }
    setError('')
    const existing = cart.find((c) => c.product_id === p.id)
    if (existing) {
      if (existing.quantity >= available) { setError('Not enough stock'); return }
      setCart(cart.map((c) => c.product_id === p.id ? { ...c, quantity: c.quantity + 1 } : c))
    } else {
      setCart([...cart, {
        product_id: p.id, name: p.name, sku: p.sku,
        quantity: 1, unit_price: p.selling_price ?? 0,
      }])
    }
  }

  const subtotal = cart.reduce((s, c) => s + c.unit_price * c.quantity, 0)
  const tax = subtotal * taxPercent / 100
  const total = subtotal + tax

  const checkout = async () => {
    if (!cart.length) return
    setError('')
    try {
      const { data } = await saleService.create({
        customer_name: customer.name || undefined,
        customer_phone: customer.phone || undefined,
        payment_method: payment,
        tax_percent: taxPercent,
        items: cart.map((c) => ({ product_id: c.product_id, quantity: c.quantity, unit_price: c.unit_price })),
      })
      setInvoice(data)
      setCart([])
      setCustomer({ name: '', phone: '' })
      await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Checkout failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-pink-400 to-orange-400 bg-clip-text text-transparent">Point of Sale</h1>
        <p className="text-slate-400 mt-1">Record sales, generate invoices, auto-deduct inventory</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Product picker */}
        <div className="xl:col-span-2 glass rounded-2xl border border-white/10 p-5">
          <h2 className="font-semibold text-white mb-4">Products</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-[420px] overflow-y-auto">
            {products.map((p) => {
              const stock = stockMap[p.id] ?? 0
              return (
                <button
                  key={p.id}
                  onClick={() => addToCart(p)}
                  disabled={stock <= 0}
                  className="text-left p-4 rounded-xl bg-slate-800/50 border border-white/10 hover:border-pink-500/40 transition disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <p className="font-medium text-white text-sm truncate">{p.name}</p>
                  <p className="text-xs text-slate-500 font-mono">{p.sku}</p>
                  <div className="flex justify-between mt-2">
                    <span className="text-pink-400 font-bold">₹{p.selling_price ?? 0}</span>
                    <span className={`text-xs ${stock <= 5 ? 'text-red-400' : 'text-slate-500'}`}>Stock: {stock}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Cart / Checkout */}
        <div className="glass rounded-2xl border border-white/10 p-5 flex flex-col">
          <h2 className="font-semibold text-white mb-4">Cart ({cart.length})</h2>
          {error && <p className="text-sm text-red-400 mb-3">{error}</p>}

          <div className="flex-1 space-y-2 overflow-y-auto max-h-48 mb-4">
            {cart.map((c) => (
              <div key={c.product_id} className="flex justify-between items-center text-sm bg-slate-800/40 rounded-lg px-3 py-2">
                <div>
                  <p className="text-white">{c.name}</p>
                  <p className="text-xs text-slate-500">{c.quantity} × ₹{c.unit_price}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">₹{(c.quantity * c.unit_price).toFixed(0)}</span>
                  <button onClick={() => setCart(cart.filter((x) => x.product_id !== c.product_id))} className="text-red-400 text-xs">✕</button>
                </div>
              </div>
            ))}
            {cart.length === 0 && <p className="text-slate-500 text-sm text-center py-4">Tap products to add</p>}
          </div>

          <input className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm mb-2" placeholder="Customer name (optional)" value={customer.name} onChange={(e) => setCustomer({ ...customer, name: e.target.value })} />
          <div className="flex gap-2 mb-3">
            <select className="flex-1 px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={payment} onChange={(e) => setPayment(e.target.value)}>
              <option value="cash">Cash</option>
              <option value="card">Card</option>
              <option value="upi">UPI</option>
              <option value="credit">Credit</option>
            </select>
            <input type="number" className="w-20 px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={taxPercent} onChange={(e) => setTaxPercent(Number(e.target.value))} title="Tax %" />
          </div>

          <div className="border-t border-white/10 pt-3 space-y-1 text-sm mb-4">
            <div className="flex justify-between text-slate-400"><span>Subtotal</span><span>₹{subtotal.toFixed(2)}</span></div>
            <div className="flex justify-between text-slate-400"><span>Tax ({taxPercent}%)</span><span>₹{tax.toFixed(2)}</span></div>
            <div className="flex justify-between text-lg font-bold text-white"><span>Total</span><span>₹{total.toFixed(2)}</span></div>
          </div>

          <button onClick={checkout} disabled={!cart.length} className="w-full py-3 rounded-xl bg-gradient-to-r from-pink-600 to-orange-600 text-white font-medium disabled:opacity-50 transition hover:from-pink-500 hover:to-orange-500">
            Complete Sale
          </button>
        </div>
      </div>

      {/* Invoice modal */}
      {invoice && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={() => setInvoice(null)}>
          <div className="glass rounded-2xl border border-white/20 p-8 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
            <div className="text-center mb-6">
              <p className="text-xs text-slate-400 uppercase tracking-widest">Invoice</p>
              <h2 className="text-2xl font-bold text-white font-mono">{invoice.invoice_number}</h2>
              <p className="text-sm text-slate-400">{invoice.sale_date}</p>
            </div>
            {invoice.customer_name && <p className="text-sm text-slate-300 mb-4">Customer: {invoice.customer_name}</p>}
            <div className="space-y-2 mb-4">
              {invoice.items.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span className="text-white">{item.product?.name} × {item.quantity}</span>
                  <span>₹{item.line_total}</span>
                </div>
              ))}
            </div>
            <div className="border-t border-white/10 pt-3 space-y-1 text-sm">
              <div className="flex justify-between text-slate-400"><span>Subtotal</span><span>₹{invoice.subtotal}</span></div>
              <div className="flex justify-between text-slate-400"><span>Tax</span><span>₹{invoice.tax_amount}</span></div>
              <div className="flex justify-between text-xl font-bold text-white"><span>Total</span><span>₹{invoice.total_amount}</span></div>
              <p className="text-xs text-slate-500 capitalize">Paid via {invoice.payment_method}</p>
            </div>
            <button onClick={() => setInvoice(null)} className="w-full mt-6 py-2 rounded-xl bg-slate-700 text-white text-sm">Close</button>
          </div>
        </div>
      )}

      {/* Sales history */}
      <div className="glass rounded-2xl border border-white/10 p-5">
        <h2 className="font-semibold text-white mb-4">Recent Sales</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-slate-400 text-left">
              <tr>
                <th className="pb-2">Invoice</th>
                <th className="pb-2">Customer</th>
                <th className="pb-2">Items</th>
                <th className="pb-2">Payment</th>
                <th className="pb-2">Total</th>
                <th className="pb-2">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {sales.map((s) => (
                <tr key={s.id} className="hover:bg-white/5 cursor-pointer" onClick={() => setInvoice(s)}>
                  <td className="py-2 font-mono text-pink-400">{s.invoice_number}</td>
                  <td className="py-2">{s.customer_name ?? 'Walk-in'}</td>
                  <td className="py-2">{s.items.length}</td>
                  <td className="py-2 capitalize">{s.payment_method}</td>
                  <td className="py-2 font-bold text-white">₹{s.total_amount}</td>
                  <td className="py-2 text-slate-500">{s.sale_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
