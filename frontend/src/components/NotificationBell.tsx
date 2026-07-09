import { useEffect, useState } from 'react'
import { expiryService } from '../services/expiryService'
import type { Notification } from '../types/expiry'

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState<Notification[]>([])
  const unread = items.filter((n) => !n.is_read).length

  const load = async () => {
    try {
      const { data } = await expiryService.listNotifications({ page_size: 10 })
      setItems(data.items)
    } catch { /* ignore */ }
  }

  useEffect(() => {
    load()
    expiryService.syncNotifications().then(() => load()).catch(() => {})
    const interval = setInterval(load, 60000)
    return () => clearInterval(interval)
  }, [])

  const markRead = async (id: number) => {
    await expiryService.markRead(id)
    await load()
  }

  const typeIcon: Record<string, string> = {
    expiry_alert: '⚠️',
    expired: '🚨',
    low_stock: '📦',
    out_of_stock: '❌',
  }

  return (
    <div className="relative">
      <button
        onClick={() => { setOpen(!open); if (!open) load() }}
        className="relative p-2 rounded-xl glass border border-white/10 hover:border-amber-500/30 transition"
      >
        <span className="text-lg">🔔</span>
        {unread > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-[10px] font-bold flex items-center justify-center">
            {unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 w-80 glass rounded-2xl border border-white/10 shadow-2xl z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-white/10 flex justify-between items-center">
            <span className="font-semibold text-white text-sm">Notifications</span>
            <button onClick={() => setOpen(false)} className="text-slate-400 text-xs">Close</button>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {items.map((n) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && markRead(n.id)}
                className={`px-4 py-3 border-b border-white/5 cursor-pointer hover:bg-white/5 ${!n.is_read ? 'bg-amber-500/5' : ''}`}
              >
                <div className="flex gap-2">
                  <span>{typeIcon[n.type] ?? '📢'}</span>
                  <div>
                    <p className="text-sm font-medium text-white">{n.title}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{n.message}</p>
                  </div>
                </div>
              </div>
            ))}
            {items.length === 0 && <p className="px-4 py-6 text-sm text-slate-500 text-center">No notifications</p>}
          </div>
        </div>
      )}
    </div>
  )
}
