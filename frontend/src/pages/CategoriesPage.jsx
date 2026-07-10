import { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { useAuth } from '../hooks/useAuth';
import { MAX_PAGE_SIZE } from '../utils/constants';
const emptyForm = { name: '', description: '' };
export default function CategoriesPage() {
    const { user } = useAuth();
    const isAdmin = user?.role.name === 'admin';
    const [items, setItems] = useState([]);
    const [q, setQ] = useState('');
    const [form, setForm] = useState(emptyForm);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const load = async () => {
        setLoading(true);
        setError('');
        try {
            const { data } = await catalogService.listCategories({ q: q || undefined, page: 1, page_size: MAX_PAGE_SIZE });
            setItems(data.items);
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to load categories. Is the backend running?');
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
        try {
            if (editingId) {
                await catalogService.updateCategory(editingId, {
                    name: form.name,
                    description: form.description || undefined,
                });
            }
            else {
                await catalogService.createCategory({ name: form.name, description: form.description || undefined });
            }
            resetForm();
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to save category');
        }
    };
    const startEdit = (c) => {
        setEditingId(c.id);
        setForm({ name: c.name, description: c.description ?? '' });
        setError('');
    };
    const remove = async (id) => {
        if (!confirm('Delete this category? Products must be removed first.'))
            return;
        setError('');
        try {
            await catalogService.deleteCategory(id);
            if (editingId === id)
                resetForm();
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Cannot delete — category may have products linked');
        }
    };
    return (<div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">Categories</h1>
        <p className="text-slate-400 mt-1">Organize products into groups — create categories before adding products</p>
      </div>

      {items.length === 0 && !loading && (<div className="glass rounded-2xl border border-amber-500/30 p-4 text-amber-200 text-sm">
          No categories yet. Use the form below to add your first one (e.g. Medicines, Grocery, Personal Care).
        </div>)}

      <form onSubmit={save} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
        <h2 className="font-semibold text-white">{editingId ? 'Edit Category' : 'Add Category'}</h2>
        {error && <p className="text-sm text-red-400 bg-red-500/10 rounded-lg px-3 py-2">{error}</p>}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm" placeholder="Category name *" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required/>
          <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm md:col-span-2" placeholder="Description (optional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}/>
        </div>
        <div className="flex gap-2">
          <button type="submit" className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm transition">
            {editingId ? 'Update Category' : 'Create Category'}
          </button>
          {editingId && (<button type="button" onClick={resetForm} className="px-5 py-2 rounded-xl bg-slate-700 text-slate-300 text-sm">
              Cancel
            </button>)}
        </div>
      </form>

      <div className="flex gap-3">
        <input className="px-4 py-2 rounded-xl glass border border-white/10 text-sm text-white placeholder-slate-500 flex-1" placeholder="Search categories..." value={q} onChange={(e) => setQ(e.target.value)}/>
        <button onClick={load} className="px-5 py-2 rounded-xl bg-slate-700 text-sm text-white">Search</button>
      </div>

      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <div className="px-5 py-3 border-b border-white/10 flex justify-between">
          <span className="font-semibold text-white">All Categories</span>
          <span className="text-sm text-slate-400">{loading ? 'Loading…' : `${items.length} items`}</span>
        </div>
        <div className="divide-y divide-white/5">
          {items.map((c) => (<div key={c.id} className="px-5 py-4 flex items-center justify-between gap-4 hover:bg-white/5">
              <div>
                <div className="font-medium text-white">{c.name}</div>
                {c.description && <div className="text-sm text-slate-400 mt-0.5">{c.description}</div>}
                <div className="text-xs text-slate-500 mt-1">ID #{c.id}</div>
              </div>
              <div className="flex gap-2 shrink-0">
                <button onClick={() => startEdit(c)} className="px-3 py-1.5 rounded-lg bg-blue-600/30 text-blue-300 text-xs hover:bg-blue-600/50">
                  Edit
                </button>
                {isAdmin && (<button onClick={() => remove(c.id)} className="px-3 py-1.5 rounded-lg bg-red-600/20 text-red-300 text-xs hover:bg-red-600/40">
                    Delete
                  </button>)}
              </div>
            </div>))}
          {!loading && items.length === 0 && (<div className="px-5 py-8 text-center text-slate-500 text-sm">No categories found.</div>)}
        </div>
      </div>
    </div>);
}
