import { Outlet, Link, useLocation } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

import { useTheme } from '../hooks/useTheme'

import NotificationBell from '../components/NotificationBell'

import GlobalSearch from '../components/GlobalSearch'

import { formatRole } from '../utils/csv'



const ROLE_LEVEL: Record<string, number> = {

  supplier: 1, employee: 2, store_manager: 3, inventory_manager: 4, admin: 5,

}



const nav = [

  { to: '/', label: 'Dashboard', icon: '📊', minRole: 'employee' },

  { to: '/inventory', label: 'Stock', icon: '📦', minRole: 'employee' },

  { to: '/expiry', label: 'Expiry', icon: '⏰', minRole: 'employee' },

  { to: '/prediction', label: 'Predictions', icon: '🔮', minRole: 'store_manager' },

  { to: '/purchases', label: 'Purchases', icon: '🛒', minRole: 'employee' },

  { to: '/sales', label: 'Sales', icon: '💳', minRole: 'employee' },

  { to: '/suppliers', label: 'Suppliers', icon: '🏭', minRole: 'employee' },

  { to: '/products', label: 'Products', icon: '🏷️', minRole: 'employee' },

  { to: '/categories', label: 'Categories', icon: '📁', minRole: 'employee' },

  { to: '/activity', label: 'Activity', icon: '📋', minRole: 'employee' },

  { to: '/reports', label: 'Reports', icon: '📥', minRole: 'store_manager' },

  { to: '/users', label: 'Users', icon: '👥', minRole: 'store_manager' },

  { to: '/profile', label: 'Profile', icon: '👤', minRole: 'employee' },

]



export default function MainLayout() {

  const { user, logout } = useAuth()

  const { dark, toggle } = useTheme()

  const location = useLocation()

  const userLevel = ROLE_LEVEL[user?.role.name ?? 'employee'] ?? 0



  const visibleNav = nav.filter((item) => userLevel >= (ROLE_LEVEL[item.minRole] ?? 0))



  return (

    <div className="min-h-screen gradient-mesh text-slate-100 flex">

      <aside className="w-64 glass border-r border-white/10 flex flex-col fixed h-full z-20">

        <div className="p-6 border-b border-white/10">

          <div className="flex items-center gap-3">

            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-lg font-bold shadow-lg shadow-blue-500/30">

              SI

            </div>

            <div>

              <h1 className="font-bold text-sm leading-tight">Smart Inventory</h1>

              <p className="text-[10px] text-slate-400">Stock Prediction System</p>

            </div>

          </div>

        </div>



        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">

          {visibleNav.map((item) => {

            const active = location.pathname === item.to

            return (

              <Link

                key={item.to}

                to={item.to}

                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all ${

                  active

                    ? 'bg-blue-600/30 text-blue-300 border border-blue-500/30 shadow-lg shadow-blue-500/10'

                    : 'text-slate-400 hover:text-white hover:bg-white/5'

                }`}

              >

                <span>{item.icon}</span>

                {item.label}

              </Link>

            )

          })}

        </nav>



        <div className="p-4 border-t border-white/10 space-y-3">

          <button

            onClick={toggle}

            className="w-full px-4 py-2 rounded-xl glass text-sm text-slate-300 hover:text-white transition"

          >

            {dark ? '☀️ Light Mode' : '🌙 Dark Mode'}

          </button>

          <Link to="/profile" className="flex items-center gap-3 px-2 hover:bg-white/5 rounded-xl py-1 transition">

            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-xs font-bold">

              {user?.full_name?.[0]}

            </div>

            <div className="flex-1 min-w-0">

              <p className="text-sm font-medium truncate">{user?.full_name}</p>

              <p className="text-[10px] text-slate-400">{formatRole(user?.role.name ?? '')}</p>

            </div>

          </Link>

          <button onClick={logout} className="w-full px-4 py-2 rounded-xl bg-red-500/20 text-red-300 text-sm hover:bg-red-500/30 transition border border-red-500/20">

            Sign Out

          </button>

        </div>

      </aside>



      <main className="flex-1 ml-64 min-h-screen">

        <div className="flex items-center justify-between gap-4 px-8 pt-4">

          <GlobalSearch />

          <NotificationBell />

        </div>

        <div className="p-8 pt-4">

          <Outlet />

        </div>

      </main>

    </div>

  )

}

