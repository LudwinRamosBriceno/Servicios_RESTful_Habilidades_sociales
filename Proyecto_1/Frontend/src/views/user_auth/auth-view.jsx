import { useState } from 'react'
import { Eye, EyeOff, Sparkles } from 'lucide-react'
import './auth-view.css'

// Componente de selección y registro de usuarios.
export function AuthView({ users = [], onLogin, onRegister, addToast }) {
  const [mode, setMode] = useState('select')
  const [form, setForm] = useState({ name: '', email: ''})
  const usersList = Array.isArray(users) ? users : []

  // Generar mensaje de bienvenida al ingresar.
  const handleUserSelect = async (user) => {
    try {
      await onLogin(user)
    } catch {
      // El manejo de errores se centraliza en App.
    }
  }

  // Validar campos de registro
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.email) {
      addToast('error', 'Por favor, completa todos los campos requeridos.')
      return
    }
    if (!form.name) {
      addToast('error', 'Por favor, ingresa tu nombre completo.')
      return
    }
    try {
      await onRegister(form.name, form.email)
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
            {mode === 'select' ? '¿Quien está usando SkillsMarket?' : 'Crea tu cuenta'}
          </h1>
          <p className="auth-header-subtitle">
            {mode === 'select'
              ? 'Elige tu perfil para continuar'
              : 'Únete a SkillsMarket y comienza a mejorar tus habilidades sociales hoy mismo'}
          </p>
        </div>

        {/* Selector de usuario / Formulario de registro */}
        {mode === 'select' ? (
          
          /* Selector de usuario */
          <div className="auth-user-grid" role="list">
            <div className="auth-user-track">
              {usersList.length === 0 ? (
                // No hay usuarios registrados
                <p className="auth-empty-users">No hay usuarios registrados.</p>
              ) : (
                // Mostrar lista de usuarios registrados para seleccionar
                usersList.map((user, index) => (
                  <button key={`${user.id || user.email || user.name}-${index}`} className="auth-user-card" role="listitem" onClick={() => handleUserSelect(user)} >
                    <div className="auth-user-avatar">
                      <span className="auth-user-initials">{(user.name || '?').slice(0, 2).toUpperCase()}</span>
                    </div>
                    <span className="auth-user-name">{user.name}</span>
                  </button>
                ))
              )}
            </div>
          </div>

        ) : (

          /* Formulario de registro */
          <div className="auth-form-container">
            <form onSubmit={handleSubmit} className="auth-form" noValidate>
              
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
                <label htmlFor="email" className="auth-label">Dirección de email</label>
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

              <button type="submit" className="auth-submit-button" style={{ color: '#6B3A4F' }}>
                Crear cuenta
              </button>

            </form>
          </div>
        )}

        {/* Enlace para cambiar entre modos */}
        <p className="auth-footer">
          {mode === 'select' ? '¿Nuevo aquí?  ' : '¿Ya tienes un perfil? '}
          <button
            onClick={() => setMode(mode === 'select' ? 'register' : 'select')}
            className="auth-footer-link"
          >
            {mode === 'select' ? 'Registrarse' : 'Seleccionar usuario'}
          </button>
        </p>

      </div>
    </main>
  )
}
