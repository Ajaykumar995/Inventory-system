import { useEffect, useState } from 'react';
import { purchaseService } from '../services/purchaseService';
import { catalogService } from '../services/catalogService';
import { MAX_PAGE_SIZE } from '../utils/constants';
const statusColor = {
    ordered: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    partial: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    received: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    cancelled: 'bg-red-500/20 text-red-300 border-red-500/30',
    draft: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
};
export default function PurchaseOrdersPage() {
    const [orders, setOrders] = useState([]);
    const [suppliers, setSuppliers] = useState([]);
    const [products, setProducts] = useState([]);
    const [error, setError] = useState('');
    const [form, setForm] = useState({
        supplier_id: 0,
        product_id: 0,
        quantity: 50,
        unit_price: 0,
        expected_delivery: '',
    });
    const load = async () => {
        const [ords, sups, prods] = await Promise.all([
            purchaseService.listOrders({ page_size: 50 }),
            purchaseService.listSuppliers({ page_size: 100 }),
            catalogService.listProducts({ page_size: MAX_PAGE_SIZE }),
        ]);
        setOrders(ords.data.items);
        setSuppliers(sups.data.items);
        setProducts(prods.data.items);
    };
    useEffect(() => { load(); }, []);
    const createPO = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await purchaseService.createOrder({
                supplier_id: form.supplier_id,
                expected_delivery: form.expected_delivery || undefined,
                items: [{ product_id: form.product_id, quantity_ordered: form.quantity, unit_price: form.unit_price }],
            });
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to create PO');
        }
    };
    const receiveAll = async (po) => {
        setError('');
        try {
            const items = po.items
                .filter((i) => i.quantity_received < i.quantity_ordered)
                .map((i) => ({ purchase_item_id: i.id, quantity: i.quantity_ordered - i.quantity_received }));
            if (!items.length)
                return;
            await purchaseService.receiveOrder(po.id, items);
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Receive failed');
        }
    };
    return (<div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">Purchase Orders</h1>
        <p className="text-slate-400 mt-1">Create POs, receive stock, track purchase history</p>
      </div>

      <form onSubmit={createPO} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">Create Purchase Order</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <select className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.supplier_id || ''} onChange={(e) => setForm({ ...form, supplier_id: Number(e.target.value) })} required>
            <option value="">Select Supplier</option>
            {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.product_id || ''} onChange={(e) => setForm({ ...form, product_id: Number(e.target.value) })} required>
            <option value="">Select Product</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
          </select>
          <input type="number" placeholder="Quantity" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })}/>
          <input type="number" placeholder="Unit Price ₹" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.unit_price || ''} onChange={(e) => setForm({ ...form, unit_price: Number(e.target.value) })} required/>
          <input type="date" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.expected_delivery} onChange={(e) => setForm({ ...form, expected_delivery: e.target.value })}/>
        </div>
        <button className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm transition">Create PO</button>
      </form>

      <div className="space-y-4">
        {orders.map((po) => (<div key={po.id} className="glass rounded-2xl border border-white/10 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
              <div>
                <h3 className="font-semibold text-white font-mono">{po.po_number}</h3>
                <p className="text-sm text-slate-400">{po.supplier.name} • {po.order_date}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-3 py-1 rounded-lg text-xs border ${statusColor[po.status] ?? ''}`}>{po.status}</span>
                <span className="text-lg font-bold text-white">₹{po.total_amount.toLocaleString()}</span>
                {(po.status === 'ordered' || po.status === 'partial') && (<button onClick={() => receiveAll(po)} className="px-4 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs transition">
                    Receive Stock
                  </button>)}
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead className="text-slate-400 text-left">
                  <tr>
                    <th className="pb-2">Product</th>
                    <th className="pb-2">Ordered</th>
                    <th className="pb-2">Received</th>
                    <th className="pb-2">Unit Price</th>
                    <th className="pb-2">Line Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {po.items.map((item) => (<tr key={item.id}>
                      <td className="py-2 text-white">{item.product?.name ?? `Product #${item.product_id}`}</td>
                      <td className="py-2">{item.quantity_ordered}</td>
                      <td className="py-2 text-cyan-400">{item.quantity_received}</td>
                      <td className="py-2">₹{item.unit_price}</td>
                      <td className="py-2 font-medium">₹{(item.quantity_ordered * item.unit_price).toLocaleString()}</td>
                    </tr>))}
                </tbody>
              </table>
            </div>
          </div>))}
        {orders.length === 0 && <p className="text-center text-slate-500 py-8">No purchase orders yet.</p>}
      </div>
    </div>);
}
