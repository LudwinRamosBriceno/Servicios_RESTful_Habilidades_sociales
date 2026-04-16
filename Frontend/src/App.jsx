import { useState } from 'react'
import { Navbar } from '@/components/navbar'
import { ToastContainer, useToasts } from '@/components/toast-notifications'
import { AuthView } from '@/views/user_auth/auth-view'
import { ProfileView } from '@/views/user_profile/profile-view'
import { CatalogView } from '@/views/skills_catalog/catalog-view'
import { OrdersView } from '@/views/skills_orders/orders-view'
import { INITIAL_SKILLS } from '@/lib/data'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [currentView, setCurrentView] = useState('auth')
  const [skills, setSkills] = useState(INITIAL_SKILLS)
  const [preSelectedSkill, setPreSelectedSkill] = useState(undefined)

  const { toasts, addToast, dismiss } = useToasts()

  const handleLogin = (name, email) => {
    setUser({ name, email, acquiredSkills: [] })
    setIsAuthenticated(true)
    setCurrentView('profile')
  }

  const handleRegister = (name, email) => {
    setUser({ name, email, acquiredSkills: [] })
    setIsAuthenticated(true)
    setCurrentView('profile')
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUser(null)
    setCurrentView('auth')
    setPreSelectedSkill(undefined)
    addToast('success', 'You have been signed out. See you soon!')
  }

  const handleUpdateName = (newName) => {
    setUser((prev) => (prev ? { ...prev, name: newName } : prev))
  }

  const handleOrderClick = (skillName) => {
    setPreSelectedSkill(skillName)
    setCurrentView('orders')
  }

  const handlePlaceOrder = (skillName, points) => {
    setSkills((prev) =>
      prev.map((s) => (s.name === skillName ? { ...s, stock: s.stock - points } : s)),
    )

    setUser((prev) => {
      if (!prev) return prev
      const existing = prev.acquiredSkills.find((s) => s.name === skillName)
      const updatedSkills = existing
        ? prev.acquiredSkills.map((s) =>
            s.name === skillName ? { ...s, points: s.points + points } : s,
          )
        : [...prev.acquiredSkills, { name: skillName, points }]
      return { ...prev, acquiredSkills: updatedSkills }
    })

    setPreSelectedSkill(undefined)
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        currentView={currentView}
        onNavigate={setCurrentView}
        isAuthenticated={isAuthenticated}
        userName={user?.name}
        onLogout={handleLogout}
      />

      {!isAuthenticated || currentView === 'auth' ? (
        <AuthView onLogin={handleLogin} onRegister={handleRegister} addToast={addToast} />
      ) : currentView === 'profile' && user ? (
        <ProfileView
          userName={user.name}
          email={user.email}
          acquiredSkills={user.acquiredSkills}
          onUpdateName={handleUpdateName}
          addToast={addToast}
        />
      ) : currentView === 'catalog' ? (
        <CatalogView skills={skills} onOrderClick={handleOrderClick} />
      ) : currentView === 'orders' ? (
        <OrdersView
          skills={skills}
          preSelectedSkill={preSelectedSkill}
          onPlaceOrder={handlePlaceOrder}
          addToast={addToast}
        />
      ) : null}

      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </div>
  )
}

export default App
