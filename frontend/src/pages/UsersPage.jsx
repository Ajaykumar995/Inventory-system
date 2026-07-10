import { useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { useAuth } from '../hooks/useAuth';
import { MAX_PAGE_SIZE } from '../utils/constants';
import { formatRole } from '../utils/csv';
const ROLES = ['admin', 'inventory_manager', 'store_manager', 'employee', 'supplier'];
const roleBadge = {
    admin: 'bg-red-500/20 text-red-300',
    inventory_manager: 'bg-blue-500/20 text-blue-300',
    store_manager: 'bg-violet-500/20 text-violet-300',
    employee: 'bg-slate-500/20 text-slate-300',
    supplier: 'bg-amber-500/20 text-amber-300',
};
export default function UsersPage() {
    const { user: me } = useAuth();
    const isAdmin = me?.role.name === 'admin';
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [form, setForm] = useState({
        email: '', username: '', password: '', full_name: '', phone: '', role_name: 'employee',
    });
    const load = async () => {
        setLoading(true);
        setError('');
        try {
            const { data } = await authService.listUsers({ page_size: MAX_PAGE_SIZE });
            setUsers(data.items);
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to load users');
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => { load(); }, []);
    const createUser = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await authService.createUser({
                email: form.email,
                username: form.username,
                password: form.password,
                full_name: form.full_name,
                phone: form.phone || undefined,
                role_name: form.role_name,
            });
            setForm({ email: '', username: '', password: '', full_name: '', phone: '', role_name: 'employee' });
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to create user');
        }
    };
    const updateUser = async (id, patch) => {
        setError('');
        try {
            await authService.updateUser(id, patch);
            await load();
        }
        catch (err) {
            setError(err?.response?.data?.detail ?? 'Failed to update user');
        }
    };
    return (<div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">User Management</h1>
        <p className="text-slate-400 mt-1">Manage team accounts and assign roles — Admin only for create/edit</p>
      </div>

      {error && <p className="text-sm text-red-400 bg-red-500/10 rounded-lg px-4 py-2">{error}</p>}

      {isAdmin && (<form onSubmit={createUser} className="glass rounded-2xl border border-white/10 p-5 space-y-3">
          <h2 className="font-semibold text-white">Create New User</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" placeholder="Full name *" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required/>
            <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" placeholder="Username *" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required/>
            <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" placeholder="Email *" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required/>
            <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" placeholder="Password * (min 8)" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8}/>
            <input className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}/>
            <select className="px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm" value={form.role_name} onChange={(e) => setForm({ ...form, role_name: e.target.value })}>
              {ROLES.map((r) => <option key={r} value={r}>{formatRole(r)}</option>)}
            </select>
          </div>
          <button className="px-5 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-sm">Create User</button>
        </form>)}

      <div className="glass rounded-2xl border border-white/10 overflow-hidden">
        <div className="px-5 py-3 border-b border-white/10 flex justify-between">
          <span className="font-semibold text-white">All Users</span>
          <span className="text-sm text-slate-400">{loading ? 'Loading…' : `${users.length} users`}</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900/40 text-slate-400 text-left">
              <tr>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Last Login</th>
                {isAdmin && <th className="px-4 py-3">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {users.map((u) => (<tr key={u.id} className="hover:bg-white/5">
                  <td className="px-4 py-3">
                    <div className="font-medium text-white">{u.full_name}</div>
                    <div className="text-xs text-slate-500">@{u.username} • {u.email}</div>
                  </td>
                  <td className="px-4 py-3">
                    {isAdmin && u.id !== me?.id ? (<select className="px-2 py-1 rounded-lg bg-slate-800 border border-white/10 text-xs text-white" value={u.role.name} onChange={(e) => updateUser(u.id, { role_name: e.target.value })}>
                        {ROLES.map((r) => <option key={r} value={r}>{formatRole(r)}</option>)}
                      </select>) : (<span className={`text-xs px-2 py-1 rounded-lg ${roleBadge[u.role.name] ?? ''}`}>
                        {formatRole(u.role.name)}
                      </span>)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-lg ${u.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">
                    {u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}
                  </td>
                  {isAdmin && (<td className="px-4 py-3">
                      {u.id !== me?.id && (<button onClick={() => updateUser(u.id, { is_active: !u.is_active })} className="text-xs text-amber-400 hover:text-amber-300">
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>)}
                    </td>)}
                </tr>))}
            </tbody>
          </table>
        </div>
      </div>
    </div>);
}
