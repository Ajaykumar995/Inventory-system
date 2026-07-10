const glowMap = {
    green: 'stat-glow-green border-emerald-500/30',
    yellow: 'stat-glow-yellow border-amber-500/30',
    red: 'stat-glow-red border-red-500/30',
    blue: 'stat-glow-blue border-blue-500/30',
};
export default function StatCard({ label, value, icon, glow = 'blue', trend }) {
    return (<div className={`glass rounded-2xl p-5 border ${glowMap[glow]} transition-transform hover:scale-[1.02]`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400 font-medium">{label}</p>
          <p className="text-3xl font-bold mt-1 text-white">{value}</p>
          {trend && <p className="text-xs text-slate-500 mt-1">{trend}</p>}
        </div>
        <div className="text-2xl opacity-80">{icon}</div>
      </div>
    </div>);
}
