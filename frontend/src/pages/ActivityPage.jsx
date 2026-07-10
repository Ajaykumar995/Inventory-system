import { useEffect, useState } from 'react';
import { inventoryService } from '../services/inventoryService';
import { catalogService } from '../services/catalogService';
import { saleService } from '../services/saleService';
import { MAX_PAGE_SIZE } from '../utils/constants';
const movementLabel = {
    in: 'Stock In',
    out: 'Stock Out',
    adjustment: 'Adjustment',
};
export default function ActivityPage() {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('all');
    const load = async () => {
        setLoading(true);
        try {
            const [movements, sales, products] = await Promise.all([
                inventoryService.listMovements({ page_size: MAX_PAGE_SIZE }),
                saleService.list({ page_size: 50 }),
                catalogService.listProducts({ page_size: MAX_PAGE_SIZE }),
            ]);
            const productMap = Object.fromEntries(products.data.items.map((p) => [p.id, p.name]));
            const movementRows = movements.data.items.map((m) => ({
                id: `m-${m.id}`,
                when: m.created_at,
                type: movementLabel[m.movement_type] ?? m.movement_type,
                detail: productMap[m.product_id] ?? `Product #${m.product_id}`,
                reference: m.reference ?? m.reason ?? '—',
                qty: `${m.movement_type === 'out' ? '-' : '+'}${m.quantity} (${m.previous_qty} → ${m.new_qty})`,
            }));
            const saleRows = sales.data.items.map((s) => ({
                id: `s-${s.id}`,
                when: s.sale_date,
                type: 'Sale',
                detail: s.customer_name ?? 'Walk-in Customer',
                reference: s.invoice_number,
                qty: `₹${s.total_amount}`,
            }));
            const merged = [...movementRows, ...saleRows].sort((a, b) => new Date(b.when).getTime() - new Date(a.when).getTime());
            setRows(merged);
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => { load(); }, []);
    const filtered = filter === 'all' ? rows : rows.filter((r) => r.type.toLowerCase().includes(filter));
    return (<div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-yellow-400 bg-clip-text text-transparent">Activity Log</h1>
          <p className="text-slate-400 mt-1">Audit trail of stock movements and sales</p>
        </div>
        <select className="px-3 py-2 rounded-xl glass border border-white/10 text-sm text-white bg-slate-900/50" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="all">All Activity</option>
          <option value="stock">Stock Movements</option>
          <option value="sale">Sales</option>
        </select>
      </div>

      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <div className="px-5 py-3 border-b border-white/10 flex justify-between">
          <span className="font-semibold text-white">Recent Activity</span>
          <span className="text-sm text-slate-400">{loading ? 'Loading…' : `${filtered.length} events`}</span>
        </div>
        <div className="divide-y divide-white/5 max-h-[600px] overflow-y-auto">
          {filtered.map((r) => (<div key={r.id} className="px-5 py-4 flex flex-wrap gap-4 items-center hover:bg-white/5">
              <div className="text-xs text-slate-500 w-36 shrink-0">
                {new Date(r.when).toLocaleString()}
              </div>
              <span className={`text-xs px-2 py-1 rounded-lg shrink-0 ${r.type === 'Sale' ? 'bg-pink-500/20 text-pink-300' :
                r.type === 'Stock Out' ? 'bg-red-500/20 text-red-300' :
                    r.type === 'Stock In' ? 'bg-emerald-500/20 text-emerald-300' :
                        'bg-amber-500/20 text-amber-300'}`}>
                {r.type}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-sm text-white">{r.detail}</div>
                <div className="text-xs text-slate-500">{r.reference}</div>
              </div>
              <div className="text-sm font-mono text-slate-300">{r.qty}</div>
            </div>))}
          {!loading && filtered.length === 0 && (<div className="px-5 py-10 text-center text-slate-500">No activity recorded yet.</div>)}
        </div>
      </div>
    </div>);
}
