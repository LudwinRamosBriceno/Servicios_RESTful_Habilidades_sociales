import { useState, useEffect } from 'react'
import { ShoppingBag, Minus, Plus } from 'lucide-react'
import { cn } from '@/lib/utils'
import './orders-view.css'

// Componente de vista para realizar pedidos de habilidades.
export function OrdersView({ skills, preSelectedSkillId, onPlaceOrder, addToast }) {
  const [selectedSkillId, setSelectedSkillId] = useState(preSelectedSkillId || '')
  const [points, setPoints] = useState(1)

  // Si desde el catálogo se preselecciona una habilidad, actualizar el estado local para reflejarlo.
  useEffect(() => {
    if (preSelectedSkillId) {
      setSelectedSkillId(preSelectedSkillId)
      setPoints(1)
    }
  }, [preSelectedSkillId])

  // Obtener la habilidad seleccionada para determinar el stock disponible.
  const skill = skills.find((s) => s.id === selectedSkillId)

  // El máximo de puntos que se pueden ordenar es el stock disponible de la habilidad seleccionada.
  const maxPoints = skill?.stock ?? 0

  // Manejar el cambio de habilidad seleccionada. Al cambiar, resetear los puntos a 1.
  const handleSkillChange = (skillId) => {
    setSelectedSkillId(skillId)
    setPoints(1)
  }

  // Manejar incremento y decremento de puntos, asegurando que se mantengan dentro de los límites permitidos.
  const handleDecrement = () => setPoints((p) => Math.max(1, p - 1))
  const handleIncrement = () => setPoints((p) => Math.min(maxPoints, p + 1))

  // Validar el input de puntos (que sea un número y esté dentro de los límites permitidos).
  const handleInputChange = (e) => {
    const val = Number(e.target.value)
    if (!isNaN(val)) {
      setPoints(Math.min(maxPoints, Math.max(1, val)))
    }
  }

  // Validar el formulario antes de enviar el pedido.
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!selectedSkillId) {
      addToast('error', 'Por favor, selecciona una habilidad para ordenar.')
      return
    }
    if (!skill || skill.stock === 0) {
      addToast('error', 'Esta habilidad está fuera de stock.')
      return
    }
    if (points < 1 || points > skill.stock) {
      addToast('error', `Por favor, introduce un valor entre 1 y ${skill.stock}.`)
      return
    }
    try {
      await onPlaceOrder(selectedSkillId, points)
      addToast('success', `Pedido realizado! Has adquirido ${points} punto${points > 1 ? 's' : ''} de ${skill.name}.`)
      setPoints(1)
    } catch {
      // El manejo de errores se centraliza en App.
    }
  }

  // Separar las habilidades disponibles de las que no lo están.
  const availableSkills = skills.filter((s) => s.stock > 0)
  const unavailableSkills = skills.filter((s) => s.stock === 0)

  return (
    <main className="orders-main">
      
      {/* Encabezado */}
      <div className="orders-header">
        <div className="orders-header-title-row">
          <h2 className="orders-header-title">Realizar un pedido</h2>
        </div>
        <p className="orders-header-subtitle">
          Selecciona una habilidad y la cantidad de puntos que deseas adquirir.
        </p>
      </div>

      {/* Formulario de pedido */}
      <section className="orders-form-card">
        <form onSubmit={handleSubmit} className="orders-form" noValidate>
          
          {/* Seleccionar habilidad */}
          <div>

            <label className="orders-field-label">
              Seleccionar habilidad <span className="orders-field-required">*</span>
            </label>
            
            <div className="orders-skill-grid">
              {// Habilidades disponibles para ordenar
              availableSkills.map((s) => (
                <button
                  type="button"
                  key={s.id}
                  onClick={() => handleSkillChange(s.id)}
                  className={cn('orders-skill-button orders-skill-button-available', selectedSkillId === s.id && 'orders-skill-button-selected')}
                  style={selectedSkillId === s.id ? { color: '#6B3A4F' } : {}}
                >
                  {s.name}
                </button>
              ))} 
              
              {// Habilidades no disponibles (sin stock)
              unavailableSkills.map((s) => (
                <button
                  type="button"
                  key={s.id}
                  disabled
                  className="orders-skill-button orders-skill-button-unavailable"
                  title="Out of stock"
                >
                  {s.name}
                </button>
              ))}
            </div>

          </div>


          {/* Selector de puntos */}
          <div>
            
            <label className="orders-field-label">
              Cantidad de Puntos <span className="orders-field-required">*</span>
            </label>

            <div className="orders-points-container">
              
              {/* Botone de decrementar puntos */}
              <button
                type="button"
                onClick={handleDecrement}
                disabled={!selectedSkillId || points <= 1}
                className="orders-points-button"
              >
                <Minus className="w-4 h-4" />
              </button>

              {/* Input para ingresar cantidad de puntos */}
              <input 
                type="number"
                value={points}
                onChange={handleInputChange}
                min={1}
                max={maxPoints}
                disabled={!selectedSkillId}
                className="orders-points-input"
              />

              {/* Botón de incrementar puntos */}
              <button
                type="button"
                onClick={handleIncrement}
                disabled={!selectedSkillId || points >= maxPoints}
                className="orders-points-button"
              >
                <Plus className="w-4 h-4" />
              </button>

              {/* Indicador de puntos disponibles para la habilidad seleccionada */}
              {selectedSkillId && (
                <span className="orders-points-hint">
                  de <span className="orders-points-hint-bold">{maxPoints}</span> disponibles
                </span>
              )}

            </div>
          </div>

          {/* Botón de enviar pedido */}
          <button
            type="submit"
            disabled={!selectedSkillId || !skill || skill.stock === 0}
            className="orders-submit-button"
            style={{ color: '#6B3A4F' }}
          >
            Realizar pedido
          </button>

        </form>
      </section>
    </main>
  )
}
