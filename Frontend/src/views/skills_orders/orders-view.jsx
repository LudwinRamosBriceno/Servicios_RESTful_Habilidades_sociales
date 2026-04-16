import { useState, useEffect } from 'react'
import { ShoppingBag, Minus, Plus, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import './orders-view.css'

export function OrdersView({ skills, preSelectedSkill, onPlaceOrder, addToast }) {
  const [selectedSkill, setSelectedSkill] = useState(preSelectedSkill || '')
  const [points, setPoints] = useState(1)

  useEffect(() => {
    if (preSelectedSkill) {
      setSelectedSkill(preSelectedSkill)
      setPoints(1)
    }
  }, [preSelectedSkill])

  const skill = skills.find((s) => s.name === selectedSkill)
  const maxPoints = skill?.stock ?? 0

  const handleSkillChange = (name) => {
    setSelectedSkill(name)
    setPoints(1)
  }

  const handleDecrement = () => setPoints((p) => Math.max(1, p - 1))
  const handleIncrement = () => setPoints((p) => Math.min(maxPoints, p + 1))

  const handleInputChange = (e) => {
    const val = Number(e.target.value)
    if (!isNaN(val)) {
      setPoints(Math.min(maxPoints, Math.max(1, val)))
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!selectedSkill) {
      addToast('error', 'Please select a skill before ordering.')
      return
    }
    if (!skill || skill.stock === 0) {
      addToast('error', 'This skill is out of stock.')
      return
    }
    if (points < 1 || points > skill.stock) {
      addToast('error', `Please enter a value between 1 and ${skill.stock}.`)
      return
    }
    onPlaceOrder(selectedSkill, points)
    addToast('success', `Order placed! You acquired ${points} point${points > 1 ? 's' : ''} of ${selectedSkill}.`)
    setPoints(1)
  }

  const availableSkills = skills.filter((s) => s.stock > 0)
  const unavailableSkills = skills.filter((s) => s.stock === 0)

  return (
    <main className="orders-main">
      {/* Header */}
      <div className="orders-header">
        <div className="orders-header-title-row">
          <ShoppingBag className="w-5 h-5" style={{ color: '#6B3A4F' }} />
          <h2 className="orders-header-title">Place an Order</h2>
        </div>
        <p className="orders-header-subtitle">
          Select a skill and the number of points you&apos;d like to acquire.
        </p>
      </div>

      {/* Form Card */}
      <section className="orders-form-card">
        <form onSubmit={handleSubmit} className="orders-form" noValidate>
          {/* Skill Selector */}
          <div>
            <label className="orders-field-label">
              Select Skill <span className="orders-field-required">*</span>
            </label>
            <div className="orders-skill-grid">
              {availableSkills.map((s) => (
                <button
                  type="button"
                  key={s.name}
                  onClick={() => handleSkillChange(s.name)}
                  className={cn('orders-skill-button orders-skill-button-available', selectedSkill === s.name && 'orders-skill-button-selected')}
                  style={selectedSkill === s.name ? { color: '#6B3A4F' } : {}}
                >
                  {s.name}
                </button>
              ))}
              {unavailableSkills.map((s) => (
                <button
                  type="button"
                  key={s.name}
                  disabled
                  className="orders-skill-button orders-skill-button-unavailable"
                  title="Out of stock"
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>

          {/* Stock Info */}
          {selectedSkill && skill && (
            <div className="orders-stock-info">
              <AlertCircle className="orders-stock-icon" style={{ color: '#2A5F7A' }} />
              <div className="orders-stock-text">
                <span className="orders-stock-text-skill">{skill.name}</span>
                <span className="orders-stock-text-muted"> has </span>
                <span className="orders-stock-text-bold">{skill.stock} point{skill.stock !== 1 ? 's' : ''}</span>
                <span className="orders-stock-text-muted"> available in stock.</span>
              </div>
            </div>
          )}

          {/* Points Selector */}
          <div>
            <label className="orders-field-label">
              Number of Points <span className="orders-field-required">*</span>
            </label>
            <div className="orders-points-container">
              <button
                type="button"
                onClick={handleDecrement}
                disabled={!selectedSkill || points <= 1}
                className="orders-points-button"
                aria-label="Decrease points"
              >
                <Minus className="w-4 h-4" />
              </button>
              <input
                type="number"
                value={points}
                onChange={handleInputChange}
                min={1}
                max={maxPoints}
                disabled={!selectedSkill}
                className="orders-points-input"
                aria-label="Number of points"
              />
              <button
                type="button"
                onClick={handleIncrement}
                disabled={!selectedSkill || points >= maxPoints}
                className="orders-points-button"
                aria-label="Increase points"
              >
                <Plus className="w-4 h-4" />
              </button>
              {selectedSkill && (
                <span className="orders-points-hint">
                  of <span className="orders-points-hint-bold">{maxPoints}</span> available
                </span>
              )}
            </div>
            {selectedSkill && maxPoints > 0 && (
              <div className="orders-progress-wrapper">
                <div
                  className="orders-progress-bar"
                  style={{ width: `${(points / maxPoints) * 100}%` }}
                  role="progressbar"
                  aria-valuenow={points}
                  aria-valuemin={1}
                  aria-valuemax={maxPoints}
                />
              </div>
            )}
          </div>

          {/* Order Summary */}
          {selectedSkill && skill && (
            <div className="orders-summary">
              <div className="orders-summary-left">
                <p className="orders-summary-label">Order Summary</p>
                <p className="orders-summary-value">
                  {points} pt{points !== 1 ? 's' : ''} of {skill.name}
                </p>
              </div>
              <div className="orders-summary-right">
                <p className="orders-summary-label">Remaining After</p>
                <p className="orders-summary-value">{skill.stock - points} pts</p>
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={!selectedSkill || !skill || skill.stock === 0}
            className="orders-submit-button"
            style={{ color: '#6B3A4F' }}
          >
            Place Order
          </button>
        </form>
      </section>
    </main>
  )
}
