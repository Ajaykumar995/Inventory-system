import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import WarehouseSceneWrapper from '../components/WarehouseSceneWrapper'
import StatCard from '../components/StatCard'
import { inventoryService } from '../services/inventoryService'
import type { DashboardStats } from '../types/inventory'
import { useAuth } from '../hooks/useAuth'

const PIE_COLORS = ['#22c55e', '#eab308', '#ef4444', '#3b82f6']

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    inventoryService.dashboard()
      .then((r) => setStats(r.data))
      .catch(() => setStats(null))
      .finally(() => setLoading(false))
  }, [])

  const pieData = stats ? [
    { name: 'Healthy', value: stats.healthy_stock },
    { name: 'Low Stock', value: stats.low_stock },
    { name: 'Out of Stock', value: stats.out_of_stock },
    { name: 'Overstock', value: stats.overstock },
  ] : []

  const barData = stats?.warehouse_items.slice(0, 8).map((w) => ({
    name: w.sku,
    stock: w.stock,
    min: w.min_stock,
  })) ?? []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
          Operations Dashboard
        </h1>
        <p className="text-slate-400 mt-1">
          Welcome back, <span className="text-white font-medium">{user?.full_name}</span> — real-time inventory intelligence
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard label="Total Products" value={loading ? '—' : stats?.total_products ?? 0} icon="🏷️" glow="blue" />
        <StatCard label="Suppliers" value={loading ? '—' : stats?.total_suppliers ?? 0} icon="🏭" glow="blue" />
        <StatCard label="Low Stock" value={loading ? '—' : stats?.low_stock ?? 0} icon="⚠️" glow="yellow" trend="Needs reorder" />
        <StatCard label="Expiring Soon" value={loading ? '—' : stats?.expiring_soon ?? 0} icon="⏰" glow="yellow" trend="Within 30 days" />
        <StatCard label="Expired" value={loading ? '—' : stats?.expired ?? 0} icon="🚨" glow="red" trend="Dispose immediately" />
        <StatCard label="Today's Sales" value={loading ? '—' : `₹${(stats?.today_sales ?? 0).toLocaleString()}`} icon="💳" glow="green" />
        <StatCard label="Monthly Sales" value={loading ? '—' : `₹${(stats?.monthly_sales ?? 0).toLocaleString()}`} icon="📈" glow="blue" />
      </div>

      {/* 3D Warehouse + Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 glass rounded-2xl border border-white/10 overflow-hidden" style={{ height: 480 }}>
          <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-white">3D Warehouse View</h2>
              <p className="text-xs text-slate-400">Live stock levels — drag to rotate</p>
            </div>
            <div className="flex gap-3 text-xs">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-green-500" /> Healthy</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-500" /> Low</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Out</span>
            </div>
          </div>
          <div className="h-[calc(100%-52px)]">
            <WarehouseSceneWrapper items={stats?.warehouse_items ?? []} />
          </div>
        </div>

        <div className="space-y-4">
          <div className="glass rounded-2xl border border-white/10 p-5">
            <h3 className="font-semibold text-white mb-4">Stock Health</h3>
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={4} dataKey="value">
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {pieData.map((d, i) => (
                <div key={d.name} className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="w-2 h-2 rounded-full" style={{ background: PIE_COLORS[i] }} />
                  {d.name}: <span className="text-white font-medium">{d.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-2xl border border-white/10 p-5">
            <h3 className="font-semibold text-white mb-1">Total Units</h3>
            <p className="text-4xl font-bold text-cyan-400">{loading ? '—' : stats?.total_stock_units ?? 0}</p>
            <p className="text-xs text-slate-500 mt-1">{stats?.total_categories ?? 0} categories tracked</p>
          </div>
        </div>
      </div>

      {/* Bar chart */}
      <div className="glass rounded-2xl border border-white/10 p-5">
        <h3 className="font-semibold text-white mb-4">Stock Levels by SKU</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={barData}>
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
            <Bar dataKey="stock" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="min" fill="#ef4444" radius={[4, 4, 0, 0]} opacity={0.4} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
