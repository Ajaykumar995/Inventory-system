import { useEffect, useState } from 'react';
import { expiryService } from '../services/expiryService';
import { catalogService } from '../services/catalogService';
import { MAX_PAGE_SIZE } from '../utils/constants';
const statusStyle = {
    valid: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    expiring_soon: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    expired: 'bg-red-500/20 text-red-300 border-red-500/30',
};
export default function ExpiryPage() {
    const [summary, setSummary] = useState(null);
    const [batches, setBatches] = useState([]);
    const [products, setProducts] = useState([]);
    const [filter, setFilter] = useState('');
    const [error, setError] = useState('');
    const [form, setForm] = useState({ product_id: 0, batch_number: '', expiry_date: '', quantity: 0 });
    const load = async () => {
        const [sum, batchData, prods] = await Promise.all([
            expiryService.summary(30),
            expiryService.listBatches({ status: filter || undefined, page_size: 50 }),
            catalogService.listProducts({ page_size: MAX_PAGE_SIZE }),
        ]);
        setSummary(sum.data);
        setBatches(batchData.data.items);
        setProducts(prods.data.items);
    };
    useEffect(() => { load(); }, [filter]);
    const addBatch = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await expiryService.addBatch(form);
            setForm({ product_id: 0, batch_number: '', expiry_date: '', quantity: 0 });
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed');
        }
    };
    const dispose = async (id) => {
        try {
            await expiryService.dispose(id, 'Expired stock disposed');
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Dispose failed');
        }
    };
    const syncAlerts = async () => {
        await expiryService.syncNotifications();
        await load();
    };
    return (<div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-red-400 bg-clip-text text-transparent">Expiry Management</h1>
          <p className="text-slate-400 mt-1">Track batch expiry, prevent losses, comply with pharmacy regulations</p>
        </div>
        <button onClick={syncAlerts} className="px-4 py-2 rounded-xl bg-amber-600/30 border border-amber-500/30 text-amber-300 text-sm hover:bg-amber-600/40 transition">
          Sync Alerts
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
            { label: 'Valid', value: summary?.valid ?? 0, color: 'text-emerald-400', border: 'border-emerald-500/30' },
            { label: 'Expiring Soon', value: summary?.expiring_soon ?? 0, color: 'text-amber-400', border: 'border-amber-500/30' },
            { label: 'Expired', value: summary?.expired ?? 0, color: 'text-red-400', border: 'border-red-500/30' },
        ].map((c) => (<div key={c.label} className={`glass rounded-2xl border ${c.border} p-5 text-center`}>
            <p className="text-sm text-slate-400">{c.label}</p>
            <p className={`text-4xl font-bold ${c.color}`}>{c.value}</p>
          </div>))}
      </div>

      {/* Add batch */}
      <form onSubmit={addBatch} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">Register Batch with Expiry</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <select className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.product_id || ''} onChange={(e) => setForm({ ...form, product_id: Number(e.target.value) })} required>
            <option value="">Product</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Batch Number" value={form.batch_number} onChange={(e) => setForm({ ...form, batch_number: e.target.value })} required/>
          <input type="date" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} required/>
          <input type="number" className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Quantity" value={form.quantity || ''} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} required/>
          <button className="px-4 py-2 rounded-xl bg-amber-600 text-white text-sm">Add Batch</button>
        </div>
      </form>

      {/* Filters */}
      <div className="flex gap-2">
        {['', 'expiring_soon', 'expired', 'valid'].map((s) => (<button key={s} onClick={() => setFilter(s)} className={`px-4 py-2 rounded-xl text-sm transition ${filter === s ? 'bg-amber-600/30 border border-amber-500/30 text-amber-300' : 'glass border border-white/10 text-slate-400'}`}>
            {s ? s.replace('_', ' ') : 'All'}
          </button>))}
      </div>

      {/* Batch table */}
      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-white/5 text-slate-400 text-left">
            <tr>
              <th className="px-5 py-3">Product</th>
              <th className="px-5 py-3">Batch</th>
              <th className="px-5 py-3">Expiry</th>
              <th className="px-5 py-3">Days Left</th>
              <th className="px-5 py-3">Qty</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {batches.map((b) => (<tr key={b.id} className="hover:bg-white/5">
                <td className="px-5 py-3 text-white">{b.product?.name}</td>
                <td className="px-5 py-3 font-mono text-cyan-400">{b.batch_number}</td>
                <td className="px-5 py-3">{b.expiry_date}</td>
                <td className={`px-5 py-3 font-bold ${b.days_to_expiry <= 0 ? 'text-red-400' : b.days_to_expiry <= 30 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {b.days_to_expiry <= 0 ? 'EXPIRED' : `${b.days_to_expiry}d`}
                </td>
                <td className="px-5 py-3">{b.quantity}</td>
                <td className="px-5 py-3">
                  <span className={`px-2 py-1 rounded-lg text-xs border ${statusStyle[b.expiry_status]}`}>{b.expiry_status.replace('_', ' ')}</span>
                </td>
                <td className="px-5 py-3">
                  {!b.is_disposed && b.quantity > 0 && (<button onClick={() => dispose(b.id)} className="px-2 py-1 rounded-lg bg-red-500/20 text-red-300 text-xs hover:bg-red-500/30">Dispose</button>)}
                </td>
              </tr>))}
          </tbody>
        </table>
      </div>
    </div>);
}
