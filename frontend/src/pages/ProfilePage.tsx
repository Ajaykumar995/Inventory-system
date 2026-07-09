import { useState } from 'react'
import { authService } from '../services/authService'
import { useAuth } from '../hooks/useAuth'
import { formatRole } from '../utils/csv'

export default function ProfilePage() {
  const { user } = useAuth()
  const [form, setForm] = useState({
    full_name: user?.full_name ?? '',
    email: user?.email ?? '',
    phone: user?.phone ?? '',
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setMessage('')
    try {
      await authService.updateMe(form)
      setMessage('Profile updated successfully')
      window.location.reload()
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (!user) return null

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">My Profile</h1>
        <p className="text-slate-400 mt-1">Update your account details</p>
      </div>

      <div className="glass rounded-2xl border border-white/10 p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-2xl font-bold">
          {user.full_name[0]}
        </div>
        <div>
          <h2 className="text-xl font-semibold text-white">{user.full_name}</h2>
          <p className="text-slate-400">@{user.username}</p>
          <span className="text-xs px-2 py-1 rounded-lg bg-blue-500/20 text-blue-300 mt-1 inline-block">
            {formatRole(user.role.name)}
          </span>
        </div>
      </div>

      <form onSubmit={save} className="glass rounded-2xl border border-white/10 p-5 space-y-4">
        {message && <p className="text-sm text-emerald-400 bg-emerald-500/10 rounded-lg px-3 py-2">{message}</p>}
        {error && <p className="text-sm text-red-400 bg-red-500/10 rounded-lg px-3 py-2">{error}</p>}

        <div className="space-y-3">
          <label className="block text-sm text-slate-400">Full Name</label>
          <input className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
        </div>
        <div className="space-y-3">
          <label className="block text-sm text-slate-400">Email</label>
          <input className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        </div>
        <div className="space-y-3">
          <label className="block text-sm text-slate-400">Phone</label>
          <input className="w-full px-3 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </div>
        <div className="text-xs text-slate-500">
          Last login: {user.last_login ? new Date(user.last_login).toLocaleString() : '—'}
        </div>
        <button disabled={saving} className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-sm disabled:opacity-50">
          {saving ? 'Saving…' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
