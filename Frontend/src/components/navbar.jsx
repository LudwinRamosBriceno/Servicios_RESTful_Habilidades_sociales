import { BookOpen, ShoppingBag, User, LogOut, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import './navbar.css'

const navItems = [
  { id: 'profile', label: 'My Profile', icon: User },
  { id: 'catalog', label: 'Skills Catalog', icon: BookOpen },
  { id: 'orders', label: 'Orders', icon: ShoppingBag },
]

export function Navbar({ currentView, onNavigate, isAuthenticated, userName, onLogout }) {
  return (
    <header className="navbar-header">
      <div className="navbar-container">
        {/* Logo */}
        <button onClick={() => isAuthenticated && onNavigate('profile')} className="navbar-logo">
          <div className="navbar-logo-icon">
            <Sparkles className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="navbar-logo-text">
            Skills<span style={{ color: '#c2607a' }}>Market</span>
          </span>
        </button>

        {/* Navigation */}
        {isAuthenticated ? (
          <nav className="navbar-nav">
            {navItems.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => onNavigate(id)}
                className={cn('navbar-nav-button', currentView === id ? 'navbar-nav-button-active' : 'navbar-nav-button-inactive')}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </nav>
        ) : (
          <span className="navbar-message">Please sign in to continue</span>
        )}

        {/* User / Auth */}
        {isAuthenticated && (
          <div className="navbar-user-section">
            <span className="navbar-user-name">
              Hello, <span className="navbar-user-name-bold">{userName}</span>
            </span>
            <button onClick={onLogout} className="navbar-logout-button" aria-label="Log out">
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Log out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
