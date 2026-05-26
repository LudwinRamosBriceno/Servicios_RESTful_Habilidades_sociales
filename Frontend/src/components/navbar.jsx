import { BookOpen, ShoppingBag, User, LogOut, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import './navbar.css'

const navItems = [
  { id: 'profile', label: 'Perfil', icon: <User className="w-4 h-4" /> },
  { id: 'catalog', label: 'Catalogo', icon: <BookOpen className="w-4 h-4" /> },
  { id: 'orders', label: 'Pedidos', icon: <ShoppingBag className="w-4 h-4" /> },
]

export function Navbar({ currentView, onNavigate, isAuthenticated, userName, onLogout }) {
  return (
    <header className="navbar-header">
      <div className="navbar-container">
        <button onClick={() => isAuthenticated && onNavigate('profile')} className="navbar-logo">
          <div className="navbar-logo-icon">
            <Sparkles className="w-4 h-4 text-primary-foreground" />
          </div>
          <span className="navbar-logo-text">
            Skills<span style={{ color: '#c2607a' }}>Market</span>
          </span>
        </button>

        {isAuthenticated ? (
          <nav className="navbar-nav">
            {navItems.map(({ id, label, icon }) => (
              <button
                key={id}
                onClick={() => onNavigate(id)}
                className={cn('navbar-nav-button', currentView === id ? 'navbar-nav-button-active' : 'navbar-nav-button-inactive')}
              >
                {icon}
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </nav>
        ) : (
          <span className="navbar-message">SkillsMarket by NovaLink</span>
        )}

        {isAuthenticated && (
          <div className="navbar-user-section">
            <span className="navbar-user-name">
              Hola, <span className="navbar-user-name-bold">{userName}!</span>
            </span>
            <button onClick={onLogout} className="navbar-logout-button" aria-label="Log out">
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Salir</span>
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
