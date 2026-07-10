import { useEffect, useState } from 'react';
import { purchaseService } from '../services/purchaseService';
export default function SuppliersPage() {
    const [items, setItems] = useState([]);
    const [perf, setPerf] = useState(null);
    const [q, setQ] = useState('');
    const [error, setError] = useState('');
    const [form, setForm] = useState({ name: '', contact_person: '', phone: '', email: '' });
    const load = async () => {
        const { data } = await purchaseService.listSuppliers({ q: q || undefined, page_size: 50 });
        setItems(data.items);
    };
    useEffect(() => { load(); }, []);
    const create = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await purchaseService.createSupplier({
                name: form.name,
                contact_person: form.contact_person || undefined,
                phone: form.phone || undefined,
                email: form.email || undefined,
            });
            setForm({ name: '', contact_person: '', phone: '', email: '' });
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed');
        }
    };
    const showPerf = async (id) => {
        const { data } = await purchaseService.supplierPerformance(id);
        setPerf(data);
    };
    return (<div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">Suppliers</h1>
        <p className="text-slate-400 mt-1">Track vendor performance, delivery times, and contact details</p>
      </div>

      <form onSubmit={create} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">Add Supplier</h2>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Company Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Contact Person" value={form.contact_person} onChange={(e) => setForm({ ...form, contact_person: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-sm" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}/>
        </div>
        <button className="px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm transition">Create Supplier</button>
      </form>

      <div className="flex gap-3">
        <input className="px-4 py-2 rounded-xl glass border border-white/10 text-sm flex-1" placeholder="Search suppliers..." value={q} onChange={(e) => setQ(e.target.value)}/>
        <button onClick={load} className="px-5 py-2 rounded-xl bg-slate-700 text-sm">Search</button>
      </div>

      {perf && (<div className="glass rounded-2xl border border-violet-500/30 p-5">
          <h3 className="font-semibold text-white mb-3">Performance: {perf.supplier_name}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span className="text-slate-400">Total Orders</span><p className="text-xl font-bold text-white">{perf.total_orders}</p></div>
            <div><span className="text-slate-400">On-Time Rate</span><p className="text-xl font-bold text-emerald-400">{perf.on_time_rate}%</p></div>
            <div><span className="text-slate-400">Avg Delivery</span><p className="text-xl font-bold text-cyan-400">{perf.avg_delivery_days ?? '—'} days</p></div>
            <div><span className="text-slate-400">Delayed</span><p className="text-xl font-bold text-red-400">{perf.delayed_deliveries}</p></div>
          </div>
          <button onClick={() => setPerf(null)} className="mt-3 text-xs text-slate-400 hover:text-white">Close</button>
        </div>)}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((s) => (<div key={s.id} className="glass rounded-2xl border border-white/10 p-5 hover:border-violet-500/30 transition">
            <div className="flex justify-between items-start">
              <h3 className="font-semibold text-white">{s.name}</h3>
              <span className="text-xs px-2 py-1 rounded-lg bg-amber-500/20 text-amber-300">★ {s.rating.toFixed(1)}</span>
            </div>
            {s.contact_person && <p className="text-sm text-slate-400 mt-2">{s.contact_person}</p>}
            {s.phone && <p className="text-sm text-slate-500">{s.phone}</p>}
            {s.email && <p className="text-sm text-slate-500">{s.email}</p>}
            <button onClick={() => showPerf(s.id)} className="mt-3 text-xs text-violet-400 hover:text-violet-300">View Performance →</button>
          </div>))}
      </div>
    </div>);
}
