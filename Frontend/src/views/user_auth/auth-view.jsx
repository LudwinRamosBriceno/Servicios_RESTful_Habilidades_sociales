import { useState } from 'react'
import { Eye, EyeOff, Sparkles } from 'lucide-react'
import './auth-view.css'

// Componente de selección y registro de usuarios.
export function AuthView({ onLogin, onRegister, addToast }) {
  const [mode, setMode] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [form, setForm] = useState({ email: '', password: '', name: '', confirmPassword: '' })

  // Manejar inicio de sesión con credenciales reales.
  const handleLoginSubmit = async (e) => {
    e.preventDefault()
    if (!form.email) {
      addToast('error', 'Por favor, ingresa tu correo electrónico.')
      return
    }
    if (!form.password) {
      addToast('error', 'Por favor, ingresa tu contraseña.')
      return
    }
    try {
      await onLogin(form.email, form.password)
      setForm({ email: '', password: '', name: '', confirmPassword: '' })
    } catch {
      // El manejo de errores se centraliza en App.
    }
  }

  // Validar campos de registro
  const handleRegisterSubmit = async (e) => {
    e.preventDefault()
    if (!form.email) {
      addToast('error', 'Por favor, completa todos los campos requeridos.')
      return
    }
    if (!form.name) {
      addToast('error', 'Por favor, ingresa tu nombre completo.')
      return
    }
    if (!form.password) {
      addToast('error', 'Por favor, ingresa tu contraseña.')
      return
    }
    if (form.password !== form.confirmPassword) {
      addToast('error', 'Las contraseñas no coinciden.')
      return
    }
    try {
      await onRegister(form.name, form.email, form.password)
      setForm({ email: '', password: '', name: '', confirmPassword: '' })
    } catch {
      // El manejo de errores se centraliza en App.
    }
  }

  // Actualizar estado del formulario
  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  // Renderizar la vista de selección/registro de usuarios
  return (
    <main className="auth-main">
      <div className="auth-container">
        
        {/* Encabezado */}
        <div className="auth-header">
          <div className="auth-header-icon">
            <Sparkles className="w-7 h-7 text-primary-foreground" style={{ color: '#6B3A4F' }} />
          </div>
          <h1 className="auth-header-title">
            {mode === 'login' ? 'Inicia sesión en SkillsMarket' : 'Crea tu cuenta'}
          </h1>
          <p className="auth-header-subtitle">
            {mode === 'login'
              ? 'Ingresa con tu correo y contraseña para continuar'
              : 'Únete a SkillsMarket y comienza a mejorar tus habilidades sociales hoy mismo'}
          </p>
        </div>

        {/* Login / Formulario de registro */}
        {mode === 'login' ? (

          /* Formulario de inicio de sesión */
          <div className="auth-form-container">
            <form onSubmit={handleLoginSubmit} className="auth-form" noValidate>
              
              {/* Dirección de email */}
              <div className="auth-field">
                <label htmlFor="email" className="auth-label">Correo electrónico</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="usuario@correo.com"
                  value={form.email}
                  onChange={handleChange}
                  className="auth-input"
                />
              </div>

              {/* Contraseña */}
              <div className="auth-field">
                <label htmlFor="password" className="auth-label">Contraseña</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={handleChange}
                  className="auth-input pr-11"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="auth-password-toggle"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Botón de envío de inicio de sesión */}
              <button type="submit" className="auth-submit-button" style={{ color: '#6B3A4F' }}>
                Iniciar sesión
              </button>

            </form>
          </div>

        ) : (

          /* Formulario de registro */
          <div className="auth-form-container">
            <form onSubmit={handleRegisterSubmit} className="auth-form" noValidate>
              
              {/* Nombre completo */}
              <div className="auth-field">
                <label htmlFor="name" className="auth-label">Nombre Completo</label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  placeholder="Winona Ryder"
                  value={form.name}
                  onChange={handleChange}
                  className="auth-input"
                />
              </div>

              {/* Dirección de email */}
              <div className="auth-field">
                <label htmlFor="email" className="auth-label">Correo electrónico</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  placeholder="winona@example.com"
                  value={form.email}
                  onChange={handleChange}
                  className="auth-input"
                />
              </div>

              {/* Contraseña */}
              <div className="auth-field">
                <label htmlFor="password" className="auth-label">Contraseña</label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={handleChange}
                  className="auth-input pr-11"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="auth-password-toggle"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Confirmar contraseña */}
              <div className="auth-field">
                <label htmlFor="confirmPassword" className="auth-label">Confirmar contraseña</label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  className="auth-input pr-11"
                />
                <button type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="auth-password-toggle"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              <button type="submit" className="auth-submit-button" style={{ color: '#6B3A4F' }}>
                Crear cuenta
              </button>

            </form>
          </div>
        )}

        {/* Enlace para cambiar entre modos */}
        <p className="auth-footer">
          {mode === 'login' ? '¿Nuevo aquí?  ' : '¿Ya tienes un perfil? '}
          <button
            onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
            className="auth-footer-link"
          >
            {mode === 'login' ? 'Registrarse' : 'Iniciar sesión'}
          </button>
        </p>

      </div>
    </main>
  )
}
