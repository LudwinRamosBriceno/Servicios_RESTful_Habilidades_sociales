import { useEffect, useState } from 'react'
import { Navbar } from '@/components/navbar'
import { ToastContainer, useToasts } from '@/components/toast-notifications'
import { AuthView } from '@/views/user_auth/auth-view'
import { ProfileView } from '@/views/user_profile/profile-view'
import { CatalogView } from '@/views/skills_catalog/catalog-view'
import { OrdersView } from '@/views/skills_orders/orders-view'
import { getUsers, registerUser } from '@/services/auth'
import { getUserById } from '@/services/user'
import { getAllSkills } from '@/services/products'
import { orderSkill } from '@/services/orders'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)           // Controlar si el usuario está autenticado
  const [users, setUsers] = useState([])                                  // Almacenar lista de usuarios disponibles para seleccionar
  const [user, setUser] = useState(null)                                  // Almacenar la información del usuario autenticado
  const [currentView, setCurrentView] = useState('auth')                  // Controlar la vista actual (auth, profile, catalog, orders)
  const [skills, setSkills] = useState([])                                // Almacenar las habilidades disponibles en el catálogo
  const [preSelectedSkillId, setPreSelectedSkillId] = useState(undefined) // Almacenar la habilidad preseleccionada en el catálogo

  // Manejar las notificaciones de toast
  const { toasts, addToast, dismiss } = useToasts()

  // Cargar datos iniciales para selector de usuarios y catálogo.
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [usersResponse, skillsResponse] = await Promise.all([getUsers(), getAllSkills()])
        setUsers(Array.isArray(usersResponse) ? usersResponse : [])
        setSkills(skillsResponse)
        if (!Array.isArray(usersResponse)) {
          // Si la respuesta de usuarios no es un array, mostrar un error específico.
        }
      } catch (error) {
        addToast('error', error.message || 'No se pudo cargar la información inicial.')
        console.error('Error al cargar datos iniciales:', error)
      }
    }

    loadInitialData()
  }, [addToast])

  // Controlar el ingreso del usuario
  const handleLogin = async (selectedUser) => {
    try {
      if (!selectedUser?.id) {
        setUser(selectedUser)
        setIsAuthenticated(true)
        setCurrentView('profile')
        addToast('success', `Bienvenido, ${selectedUser?.name || 'usuario'}!`)
        console.log('Usuario autenticado exitosamente:', selectedUser)
        return
      }

      // Obtener datos completos del usuario para mostrarlos en perfil.
      const userResponse = await getUserById(selectedUser.id)
      setUser(userResponse)
      setIsAuthenticated(true)
      setCurrentView('profile')
      addToast('success', `Bienvenido, ${userResponse.name}!`)
      console.log('Usuario autenticado exitosamente:', userResponse)
    } catch (error) {
      addToast('error', error.message || 'No se pudo obtener la información del usuario.')
      console.error('Error al obtener información del usuario:', error)
    }
  }

  // Controlar el registro del usuario
  const handleRegister = async (name, email) => {
    try {
      // Registrar el usuario y usar la respuesta del backend directamente. (debe cambiar de estado si backend responde ok)
      const userResponse = await registerUser(name, email, 'default123')
      setUser(userResponse)
      setUsers((prev) => [...prev, userResponse])
      setIsAuthenticated(true)
      setCurrentView('profile')
      addToast('success', `Bienvenido a SkillsMarket, ${userResponse.name}!`)
      console.log('Usuario registrado exitosamente:', userResponse)
    } catch (error) {
      addToast('error', error.message || 'No se pudo registrar el usuario.')
      console.error('Error al registrar usuario:', error)
    }
  }

  // Controlar el cierre de sesión del usuario
  const handleLogout = () => {
    // Actualiza el estado de autenticación (Llamada al backend para cerrar la sesión del usuario y limpiar cualquier token o cookie de autenticación)
    setIsAuthenticated(false)
    // Limpiar la información del usuario
    setUser(null)
    // Actualizar la vista actual a "seleccionar usuario" luego de cerrar sesión
    setCurrentView('auth')
    // Limpiar cualquier habilidad preseleccionada
    setPreSelectedSkillId(undefined)
    // Mostrar una notificación de éxito al cerrar sesión
    addToast('success', 'Has cerrado sesión exitosamente. ¡Hasta luego!')
  }

  // Controlar el clic en "Ordenar" desde el catálogo
  const handleOrderClick = (skillId) => {
    // Establecer la habilidad preseleccionada para que se muestre en la vista de órdenes
    setPreSelectedSkillId(skillId)
    // Actualizar la vista actual a "orders" para mostrar la vista de órdenes con la habilidad preseleccionada
    setCurrentView('orders')
  }

  // Controlar la colocación de una orden desde la vista de órdenes
  const handlePlaceOrder = async (productId, quantity) => {
    try {
      if (!user?.id) {
        console.error('Intento de realizar pedido sin usuario autenticado.')
        throw new Error('No hay usuario autenticado para realizar el pedido.')
      }

      await orderSkill(user.id, productId, quantity)

      // Refrescar información desde backend para mantener datos consistentes.
      const [skillsResponse, userResponse] = await Promise.all([getAllSkills(), getUserById(user.id)])
      setSkills(skillsResponse)
      setUser(userResponse)

      // Limpiar la habilidad preseleccionada después de colocar la orden
      setPreSelectedSkillId(undefined)
    } catch (error) {
      console.error('Error al realizar el pedido:', error)
      addToast('error', error.message || 'No se pudo realizar el pedido.')
      throw error
    }
  }

  return (
    <div className="min-h-screen bg-background">
      
      {/* Barra de navegación*/}
      <Navbar
        currentView={currentView}
        onNavigate={setCurrentView}
        isAuthenticated={isAuthenticated}
        userName={user?.name}
        onLogout={handleLogout}
      />


      {!isAuthenticated || currentView === 'auth' ? (

        // Mostrar la vista de autenticación si el usuario no está autenticado
        <AuthView users={users} onLogin={handleLogin} onRegister={handleRegister} addToast={addToast} />

      ) : currentView === 'profile' && user ? (
        
        // Mostrar la vista de perfil si el usuario está autenticado y ha seleccionado la vista de perfil
        <ProfileView
          user={user}
        />

      ) : currentView === 'catalog' ? (
        
        // Mostrar la vista de catálogo si el usuario está autenticado y ha seleccionado la vista de catálogo
        <CatalogView skills={skills} onOrderClick={handleOrderClick} />

      ) : currentView === 'orders' ? (
        
        // Mostrar la vista de órdenes si el usuario está autenticado y ha seleccionado la vista de órdenes
        <OrdersView
          skills={skills}
          preSelectedSkillId={preSelectedSkillId}
          onPlaceOrder={handlePlaceOrder}
          addToast={addToast}
        />
        
      ) : null}

      {/* Contenedor de notificaciones de toast */}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </div>
  )
}

// Exportar el componente principal de la aplicación
export default App
