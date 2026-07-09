import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { predictionService } from '../services/predictionService'
import type { PredictionDashboard } from '../types/prediction'

const priorityStyle: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-300 border-red-500/40',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
  medium: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
  low: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
}

const statusStyle: Record<string, string> = {
  sufficient: 'text-emerald-400',
  reorder_needed: 'text-amber-400',
  overstock_risk: 'text-blue-400',
}

export default function PredictionPage() {
  const [data, setData] = useState<PredictionDashboard | null>(null)
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    predictionService.dashboard(days, 15)
      .then((r) => setData(r.data))
      .finally(() => setLoading(false))
  }, [days])

  const velocityChart = data?.fast_movers.slice(0, 8).map((p) => ({
    name: p.sku,
    velocity: p.daily_velocity,
    forecast: p.monthly_forecast,
  })) ?? []

  if (loading) return <div className="text-slate-400 animate-pulse p-8">Analyzing sales patterns...</div>

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
            Prediction Engine
          </h1>
          <p className="text-slate-400 mt-1">AI-driven demand forecasting, fast/slow movers, reorder intelligence</p>
        </div>
        <select
          className="px-4 py-2 rounded-xl glass border border-white/10 text-sm"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Fast Movers', value: data?.fast_moving_count ?? 0, color: 'text-emerald-400', icon: '🚀' },
          { label: 'Slow Movers', value: data?.slow_moving_count ?? 0, color: 'text-amber-400', icon: '🐢' },
          { label: 'Reorder Needed', value: data?.reorder_needed_count ?? 0, color: 'text-red-400', icon: '📋' },
          { label: 'Monthly Demand', value: data?.total_predicted_monthly_demand ?? 0, color: 'text-cyan-400', icon: '📈' },
        ].map((c) => (
          <div key={c.label} className="glass rounded-2xl border border-white/10 p-5">
            <div className="flex justify-between">
              <p className="text-sm text-slate-400">{c.label}</p>
              <span>{c.icon}</span>
            </div>
            <p className={`text-3xl font-bold mt-1 ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>

      {/* Velocity chart */}
      <div className="glass rounded-2xl border border-white/10 p-5">
        <h2 className="font-semibold text-white mb-4">Sales Velocity — Fast Movers</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={velocityChart}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }} />
            <Bar dataKey="velocity" name="Daily Sales" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="forecast" name="Monthly Forecast" fill="#3b82f6" radius={[4, 4, 0, 0]} opacity={0.6} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Reorder recommendations */}
        <div className="glass rounded-2xl border border-white/10 p-5">
          <h2 className="font-semibold text-white mb-4">Reorder Recommendations</h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {data?.reorder_recommendations.map((r) => (
              <div key={r.product_id} className="p-4 rounded-xl bg-slate-800/40 border border-white/5">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-white">{r.product_name}</p>
                    <p className="text-xs text-slate-500 font-mono">{r.sku}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-lg text-xs border ${priorityStyle[r.priority]}`}>{r.priority}</span>
                </div>
                <div className="flex justify-between mt-2 text-sm">
                  <span className="text-slate-400">Stock: {r.current_stock}</span>
                  <span className="text-cyan-400 font-bold">Order: {r.recommended_qty} units</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">{r.reason}</p>
              </div>
            ))}
            {!data?.reorder_recommendations.length && (
              <p className="text-slate-500 text-sm text-center py-4">All stock levels healthy — no reorders needed</p>
            )}
          </div>
        </div>

        {/* Next month forecast */}
        <div className="glass rounded-2xl border border-white/10 p-5">
          <h2 className="font-semibold text-white mb-4">Next Month Forecast</h2>
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="min-w-full text-sm">
              <thead className="text-slate-400 text-left sticky top-0 bg-slate-900/80">
                <tr>
                  <th className="pb-2">Product</th>
                  <th className="pb-2">Demand</th>
                  <th className="pb-2">Projected</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {data?.next_month_forecast.map((f) => (
                  <tr key={f.product_id}>
                    <td className="py-2">
                      <p className="text-white">{f.product_name}</p>
                      <p className="text-xs text-slate-500">{f.sku}</p>
                    </td>
                    <td className="py-2">{f.predicted_demand}</td>
                    <td className={`py-2 font-bold ${f.projected_stock < 0 ? 'text-red-400' : 'text-white'}`}>{f.projected_stock}</td>
                    <td className={`py-2 capitalize text-xs ${statusStyle[f.status]}`}>{f.status.replace('_', ' ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Slow movers */}
      <div className="glass rounded-2xl border border-white/10 p-5">
        <h2 className="font-semibold text-white mb-4">Slow Moving Products — Consider Clearance</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {data?.slow_movers.map((p) => (
            <div key={p.product_id} className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
              <p className="font-medium text-white">{p.product_name}</p>
              <p className="text-xs text-slate-500 font-mono">{p.sku}</p>
              <div className="flex justify-between mt-2 text-sm">
                <span className="text-slate-400">Sold: {p.units_sold}</span>
                <span className="text-amber-400">Stock: {p.current_stock}</span>
              </div>
            </div>
          ))}
          {!data?.slow_movers.length && <p className="text-slate-500 text-sm col-span-3 text-center py-4">No slow movers detected</p>}
        </div>
      </div>
    </div>
  )
}
