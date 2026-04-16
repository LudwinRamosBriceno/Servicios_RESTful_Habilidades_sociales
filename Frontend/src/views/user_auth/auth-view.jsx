import { useState } from 'react'
import { Eye, EyeOff, Sparkles } from 'lucide-react'
import './auth-view.css'

export function AuthView({ onLogin, onRegister, addToast }) {
  const [mode, setMode] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '', confirmPassword: '' })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.email || !form.password) {
      addToast('error', 'Please fill in all required fields.')
      return
    }
    if (mode === 'register') {
      if (!form.name) {
        addToast('error', 'Please enter your full name.')
        return
      }
      if (form.password !== form.confirmPassword) {
        addToast('error', 'Passwords do not match.')
        return
      }
      onRegister(form.name, form.email)
      addToast('success', `Welcome to SkillsMarket, ${form.name}!`)
    } else {
      const displayName = form.email.split('@')[0]
      onLogin(displayName, form.email)
      addToast('success', 'Signed in successfully. Welcome back!')
    }
  }

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  return (
    <main className="auth-main">
      <div className="auth-container">
        {/* Brand header */}
        <div className="auth-header">
          <div className="auth-header-icon">
            <Sparkles className="w-7 h-7 text-primary-foreground" style={{ color: '#6B3A4F' }} />
          </div>
          <h1 className="auth-header-title">
            {mode === 'login' ? 'Welcome back' : 'Create your account'}
          </h1>
          <p className="auth-header-subtitle">
            {mode === 'login'
              ? 'Sign in to access your skills dashboard'
              : 'Join SkillsMarket and start growing'}
          </p>
        </div>

        {/* Toggle tabs */}
        <div className="auth-tabs">
          {['login', 'register'].map((tab) => (
            <button
              key={tab}
              onClick={() => setMode(tab)}
              className={`auth-tab-button ${mode === tab ? 'auth-tab-button-active' : 'auth-tab-button-inactive'}`}
            >
              {tab === 'login' ? 'Sign In' : 'Register'}
            </button>
          ))}
        </div>

        {/* Card */}
        <div className="auth-card">
          <form onSubmit={handleSubmit} className="auth-form" noValidate>
            {mode === 'register' && (
              <div className="auth-field">
                <label htmlFor="name" className="auth-label">Full Name</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  placeholder="Jane Doe"
                  value={form.name}
                  onChange={handleChange}
                  className="auth-input"
                />
              </div>
            )}

            <div className="auth-field">
              <label htmlFor="email" className="auth-label">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="jane@example.com"
                value={form.email}
                onChange={handleChange}
                className="auth-input"
              />
            </div>

            <div className="auth-field">
              <label htmlFor="password" className="auth-label">Password</label>
              <div className="auth-password-wrapper">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={handleChange}
                  className="auth-input pr-11"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="auth-password-toggle"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {mode === 'register' && (
              <div className="auth-field">
                <label htmlFor="confirmPassword" className="auth-label">Confirm Password</label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  className="auth-input"
                />
              </div>
            )}

            <button type="submit" className="auth-submit-button" style={{ color: '#6B3A4F' }}>
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <p className="auth-footer">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
              className="auth-footer-link"
            >
              {mode === 'login' ? 'Register' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>
    </main>
  )
}
