import { useEffect, useMemo, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { useAuth } from '../hooks/useAuth';
import { MAX_PAGE_SIZE } from '../utils/constants';
const emptyForm = {
    name: '',
    sku: '',
    barcode: '',
    brand: '',
    category_id: 0,
    unit: 'unit',
    cost_price: '',
    selling_price: '',
    description: '',
};
export default function ProductsPage() {
    const { user } = useAuth();
    const isAdmin = user?.role.name === 'admin';
    const [categories, setCategories] = useState([]);
    const [items, setItems] = useState([]);
    const [q, setQ] = useState('');
    const [categoryId, setCategoryId] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [form, setForm] = useState(emptyForm);
    const canSubmit = useMemo(() => form.name.trim() && form.sku.trim() && form.category_id > 0, [form]);
    const load = async () => {
        setLoading(true);
        setError('');
        try {
            const [cats, prods] = await Promise.all([
                catalogService.listCategories({ page: 1, page_size: MAX_PAGE_SIZE }),
                catalogService.listProducts({
                    q: q || undefined,
                    category_id: categoryId === '' ? undefined : categoryId,
                    page: 1,
                    page_size: MAX_PAGE_SIZE,
                    sort: 'updated_at',
                    order: 'desc',
                }),
            ]);
            setCategories(cats.data.items);
            setItems(prods.data.items);
        }
        catch (err) {
            const detail = err?.response?.data?.detail;
            setError(Array.isArray(detail) ? detail.map((d) => d.msg).join(', ') : (detail ?? 'Failed to load products. Is the backend running?'));
            setItems([]);
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => { load(); }, []);
    const resetForm = () => {
        setForm(emptyForm);
        setEditingId(null);
    };
    const save = async (e) => {
        e.preventDefault();
        setError('');
        const payload = {
            name: form.name.trim(),
            sku: form.sku.trim(),
            barcode: form.barcode.trim() || undefined,
            brand: form.brand.trim() || undefined,
            category_id: form.category_id,
            unit: form.unit.trim() || 'unit',
            description: form.description.trim() || undefined,
            cost_price: form.cost_price ? Number(form.cost_price) : undefined,
            selling_price: form.selling_price ? Number(form.selling_price) : undefined,
        };
        try {
            if (editingId) {
                await catalogService.updateProduct(editingId, payload);
            }
            else {
                await catalogService.createProduct(payload);
            }
            resetForm();
            await load();
        }
        catch (err) {
            const detail = err?.response?.data?.detail;
            setError(typeof detail === 'string' ? detail : (detail?.[0]?.msg ?? 'Failed to save product'));
        }
    };
    const startEdit = (p) => {
        setEditingId(p.id);
        setForm({
            name: p.name,
            sku: p.sku,
            barcode: p.barcode ?? '',
            brand: p.brand ?? '',
            category_id: p.category.id,
            unit: p.unit,
            cost_price: p.cost_price != null ? String(p.cost_price) : '',
            selling_price: p.selling_price != null ? String(p.selling_price) : '',
            description: p.description ?? '',
        });
        setError('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    const toggleActive = async (p) => {
        setError('');
        try {
            await catalogService.updateProduct(p.id, { is_active: !p.is_active });
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to update product');
        }
    };
    const remove = async (id) => {
        if (!confirm('Delete this product permanently?'))
            return;
        setError('');
        try {
            await catalogService.deleteProduct(id);
            if (editingId === id)
                resetForm();
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to delete product');
        }
    };
    const uploadImage = async (productId, file) => {
        setError('');
        try {
            await catalogService.uploadProductImage(productId, file);
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Image upload failed');
        }
    };
    return (<div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">Products</h1>
          <p className="text-slate-400 mt-1">Full catalog — add, edit, price, barcode, and product images</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <input className="px-3 py-2 rounded-xl glass border border-white/10 text-sm text-white placeholder-slate-500" placeholder="Search name / SKU / barcode..." value={q} onChange={(e) => setQ(e.target.value)}/>
          <select className="px-3 py-2 rounded-xl glass border border-white/10 text-sm text-white bg-slate-900/50" value={categoryId} onChange={(e) => setCategoryId(e.target.value ? Number(e.target.value) : '')}>
            <option value="">All Categories</option>
            {categories.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
          </select>
          <button onClick={load} className="px-4 py-2 rounded-xl bg-slate-700 text-sm text-white">Search</button>
        </div>
      </div>

      {categories.length === 0 && !loading && (<div className="glass rounded-2xl border border-amber-500/30 p-4 text-amber-200 text-sm">
          Create at least one <strong>Category</strong> first (sidebar → Categories), then come back here to add products.
        </div>)}

      <form onSubmit={save} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">{editingId ? 'Edit Product' : 'Add New Product'}</h2>
        {error && <p className="text-sm text-red-400 bg-red-500/10 rounded-lg px-3 py-2">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Product name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm font-mono" placeholder="SKU *" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} required disabled={!!editingId}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm font-mono" placeholder="Barcode" value={form.barcode} onChange={(e) => setForm({ ...form, barcode: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Brand" value={form.brand} onChange={(e) => setForm({ ...form, brand: e.target.value })}/>

          <select className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" value={form.category_id || ''} onChange={(e) => setForm({ ...form, category_id: Number(e.target.value) })} required>
            <option value="" disabled>Select category *</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Unit (strip, bottle, kg...)" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Cost price ₹" type="number" min="0" step="0.01" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Selling price ₹" type="number" min="0" step="0.01" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })}/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm md:col-span-4" placeholder="Description (optional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}/>
        </div>
        <div className="flex gap-2">
          <button type="submit" disabled={!canSubmit || categories.length === 0} className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm disabled:opacity-40 transition">
            {editingId ? 'Update Product' : 'Create Product'}
          </button>
          {editingId && (<button type="button" onClick={resetForm} className="px-5 py-2 rounded-xl bg-slate-700 text-slate-300 text-sm">Cancel</button>)}
        </div>
      </form>

      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <div className="px-5 py-3 border-b border-white/10 flex justify-between">
          <span className="font-semibold text-white">Product Catalog</span>
          <span className="text-sm text-slate-400">{loading ? 'Loading…' : `${items.length} products`}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900/40 text-left text-slate-400">
              <tr>
                <th className="px-4 py-3">Product</th>
                <th className="px-4 py-3">SKU</th>
                <th className="px-4 py-3">Barcode</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Prices</th>
                <th className="px-4 py-3">Image</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {items.map((p) => (<tr key={p.id} className="hover:bg-white/5">
                  <td className="px-4 py-3">
                    <div className="font-medium text-white">{p.name}</div>
                    <div className="text-xs text-slate-500">{p.brand ?? '—'} • {p.unit}</div>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${p.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'}`}>
                      {p.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-cyan-300">{p.sku}</td>
                  <td className="px-4 py-3 font-mono text-slate-400">{p.barcode ?? '—'}</td>
                  <td className="px-4 py-3 text-slate-300">{p.category?.name}</td>
                  <td className="px-4 py-3 text-slate-300">
                    <div>₹{p.selling_price ?? '—'}</div>
                    <div className="text-xs text-slate-500">cost ₹{p.cost_price ?? '—'}</div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {p.image_path ? (<img src={p.image_path} alt={p.name} className="h-10 w-10 rounded-lg object-cover border border-white/10"/>) : (<div className="h-10 w-10 rounded-lg bg-slate-800 border border-white/10"/>)}
                      <label className="text-xs px-2 py-1 rounded-lg bg-slate-700 text-slate-300 cursor-pointer hover:bg-slate-600">
                        Upload
                        <input type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f)
            uploadImage(p.id, f); }}/>
                      </label>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-col gap-1">
                      <button onClick={() => startEdit(p)} className="text-xs text-blue-400 hover:text-blue-300 text-left">Edit</button>
                      <button onClick={() => toggleActive(p)} className="text-xs text-amber-400 hover:text-amber-300 text-left">
                        {p.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                      {isAdmin && (<button onClick={() => remove(p.id)} className="text-xs text-red-400 hover:text-red-300 text-left">Delete</button>)}
                    </div>
                  </td>
                </tr>))}
              {!loading && items.length === 0 && (<tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-500">
                    No products yet. Add categories first, then use the form above.
                  </td>
                </tr>)}
            </tbody>
          </table>
        </div>
      </div>
    </div>);
}
