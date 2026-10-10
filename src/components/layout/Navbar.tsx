import { Menu, ShieldCheck, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { navItems } from '../../data/mockData'
import { Button } from '../common/Button'

export function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { isAuthenticated, user, logout } = useAuth()
  const planningRole = user?.role === 'GOVERNMENT' || user?.role === 'ADMIN'
  const familyRole = user?.role === 'CITIZEN' || user?.role === 'NGO_WORKER' || user?.role === 'ADMIN'
  const dashboardPath = planningRole ? '/government/dashboard' : familyRole ? '/dashboard' : '/map'
  const dashboardLabel = planningRole ? 'Planning dashboard' : familyRole ? 'Dashboard' : 'Service directory'

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-sm">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8" aria-label="Main navigation">
        <Link to="/" className="flex items-center gap-3" aria-label="Sahaayak home">
          <span className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-emerald-100 ring-1 ring-emerald-200">
            <ShieldCheck className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full border border-white bg-sky-600 text-[10px] font-bold text-white">C</span>
          </span>
          <span className="leading-tight">
            <span className="block text-xl font-bold tracking-tight text-slate-900">Sahaayak</span>
            <span className="block text-[10px] font-medium uppercase tracking-[0.18em] text-slate-500">Child Service Continuity Platform</span>
          </span>
        </Link>

        <div className="hidden items-center gap-2 lg:flex">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>

        <div className="hidden items-center gap-3 lg:flex">
          {isAuthenticated ? (
            <>
              {familyRole && <Button variant="outline" to="/family">Family</Button>}
              <Button variant="outline" to={dashboardPath}>
                {dashboardLabel}
              </Button>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </>
          ) : (
            <>
              <Button variant="outline" to="/login">Login</Button>
              <Button to="/register">Register</Button>
            </>
          )}
        </div>

        <button
          type="button"
          aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 text-slate-700 lg:hidden"
          onClick={() => setMenuOpen((open) => !open)}
        >
          {menuOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
        </button>
      </nav>

      {menuOpen ? (
        <div className="border-t border-slate-200 bg-white px-4 py-4 lg:hidden">
          <div className="flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-lg px-3 py-2 text-sm font-medium ${
                    isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
                onClick={() => setMenuOpen(false)}
              >
                {item.label}
              </NavLink>
            ))}
            <div className={`mt-3 grid ${isAuthenticated ? (familyRole ? 'grid-cols-3' : 'grid-cols-2') : 'grid-cols-2'} gap-2 pt-2`}>
              {isAuthenticated ? (
                <>
                  {familyRole && (
                    <Button variant="outline" to="/family" className="w-full" onClick={() => setMenuOpen(false)}>
                      Family
                    </Button>
                  )}
                  <Button variant="outline" to={dashboardPath} className="w-full" onClick={() => setMenuOpen(false)}>
                    {planningRole ? 'Planning' : familyRole ? 'Dashboard' : 'Directory'}
                  </Button>
                  <Button className="w-full" onClick={() => {
                    setMenuOpen(false)
                    logout()
                  }}>
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="outline" to="/login" className="w-full" onClick={() => setMenuOpen(false)}>
                    Login
                  </Button>
                  <Button to="/register" className="w-full" onClick={() => setMenuOpen(false)}>
                    Register
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </header>
  )
}
