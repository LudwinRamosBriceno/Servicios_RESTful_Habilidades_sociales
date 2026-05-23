import { useCallback, useEffect, useRef, useState } from 'react'
import { Navbar } from '@/components/navbar'
import { ToastContainer, useToasts } from '@/components/toast-notifications'
import { AuthView } from '@/views/user_auth/auth-view'
import { ProfileView } from '@/views/user_profile/profile-view'
import { CatalogView } from '@/views/skills_catalog/catalog-view'
import { OrdersView } from '@/views/skills_orders/orders-view'
import { useEventBridge } from '@/hooks/use-event-bridge'
import { login, registerUser } from '@/services/auth'
import { getUserById } from '@/services/user'
import { getAllSkills } from '@/services/products'
import { orderSkill } from '@/services/orders'
import { getToken, clearToken } from '@/services/token-storage'


// Función para decodificar el payload de un JWT sin verificar la firma, para extraer datos como el nombre del usuario y la expiración.
function parseJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

function App() {

  // ----- Estados globales de la aplicación -----
  
  const [isAuthenticated, setIsAuthenticated] = useState(false)           // Indica si el usuario está autenticado
  const [isRestoringSession, setIsRestoringSession] = useState(true)      // Indica si la aplicación está intentando restaurar una sesión existente
  const [user, setUser] = useState(null)                                  // Datos del usuario autenticado (id, name, etc.)
  const [currentView, setCurrentView] = useState('auth')                  // Vista actual: 'auth', 'profile', 'catalog', 'orders'
  const [skills, setSkills] = useState([])                                // Catálogo de habilidades cargado desde el backend 
  const [preSelectedSkillId, setPreSelectedSkillId] = useState(undefined) // ID de habilidad preseleccionada al navegar desde el catálogo a órdenes

  const [token, setToken] = useState(() => getToken())                    // Token de autenticación JWT, inicializado desde el almacenamiento local
  const { toasts, addToast, dismiss } = useToasts()                       // Manejo de notificaciones tipo toast para mostrar mensajes al usuario


  // ----- Refs y callbacks para evitar problemas de dependencias en useEffect y useEventBridge por SSE -----

  // Ref para mostrar notificaciones desde callbacks por SSE
  const addToastRef = useRef(addToast)
  useEffect(() => { addToastRef.current = addToast }, [addToast])

  // ----- Callbacks para  -----
  const stableAddToast = useCallback((...args) => addToastRef.current(...args), [])
  const stableSetSkills = useCallback((val) => setSkills(val), [])
  const stableSetUser = useCallback((val) => setUser(val), [])

  // Refs para que refreshSkills/refreshUserData puedan llamar a registerPendingRequest
  const registerPendingRequestRef = useRef(null)


  // ----- Funciones para recargar datos, utilizadas por SSE -----

  // Función para recargar el catálogo de habilidades, utilizada por SSE
  const refreshSkills = useCallback(async () => {
    try {
      const ack = await getAllSkills()
      if (registerPendingRequestRef.current) {
        registerPendingRequestRef.current(ack, 'products-loaded')
      }
    } catch (e) {
      console.error('Error al recargar catálogo:', e)
    }
  }, [])

  // Ref de la información del usuario y recarga por SSE
  const userRef = useRef(user)
  useEffect(() => { userRef.current = user }, [user])

  // Recarga los datos del usuario después de realizar un pedido, para que el perfil se actualice con la nueva orden.
  const refreshUserData = useCallback(async () => {
    const currentUser = userRef.current
    if (!currentUser?.id) return
    try {
      const ack = await getUserById(currentUser.id)
      if (registerPendingRequestRef.current) {
        registerPendingRequestRef.current(ack, 'user-loaded')
      }
    } catch (e) {
      console.error('Error al recargar usuario:', e)
    }
  }, [])


  // ----- Configuración y manejo de SSE -----

  // Configura el SSE para recibir actualizaciones en tiempo real
  const { registerPendingRequest, clearPendingRequests } = useEventBridge({
    enabled: isAuthenticated,
    token,
    addToast: stableAddToast,
    setSkills: stableSetSkills,
    setUser: stableSetUser,
    refreshSkills,
    refreshUserData,
  })

  // Asignar registerPendingRequest al ref para que refreshSkills/refreshUserData puedan usarlo
  useEffect(() => {
    registerPendingRequestRef.current = registerPendingRequest
  }, [registerPendingRequest])

  // *** Intenta de restaurar la sesión al cargar la app, verificando el token guardado para evitar usar un token expirado o inválido. 
  // Si el token es válido, restaura la autenticación y muestra el nombre en la navbar de inmediato (los datos completos llegarán por SSE).
  useEffect(() => {
    const restoreSession = () => {
      const savedToken = getToken()
      if (!savedToken) return

      const claims = parseJwtPayload(savedToken)
      if (!claims) {
        clearToken()
        return
      }

      // Verificar que el token no haya expirado
      const nowSeconds = Math.floor(Date.now() / 1000)
      if (claims.exp && claims.exp < nowSeconds) {
        console.warn('Token expirado, cerrando sesión.')
        clearToken()
        return
      }

      // Restaurar con datos del JWT — los datos completos llegarán por SSE
      const savedView = localStorage.getItem('current_view')
      const nextView = ['profile', 'catalog', 'orders'].includes(savedView) ? savedView : 'catalog'

      setToken(savedToken)
      setIsAuthenticated(true)
      setCurrentView(nextView)
      // Establecer usuario parcial para que la navbar muestre el nombre de inmediato
      setUser({ id: claims.sub, name: claims.name })
      console.log('Sesión restaurada. Cargando datos completos...')
    }
    try {
      restoreSession()
    } finally {
      setIsRestoringSession(false)
    }
  }, [])

  // Guarda la vista actual en localStorage para restaurarla después
  useEffect(() => {
    if (!isAuthenticated) return
    if (currentView === 'auth') return
    localStorage.setItem('current_view', currentView)
  }, [currentView, isAuthenticated])


  // ----- Carga inicial de datos -----

  // Carga el catálogo de habilidades al autenticarse, registrando la solicitud pendiente para esperar la confirmación por SSE.
  useEffect(() => {
    if (!isAuthenticated) return

    const loadInitialData = async () => {
      try {
        const skillsAck = await getAllSkills()
        registerPendingRequest(skillsAck, 'products-loaded')
      } catch (error) {
        stableAddToast('error', error.message || 'No se pudo cargar las habilidades.')
        console.error('Error al cargar habilidades:', error)
      }
    }

    loadInitialData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated])

  // Carga los datos del usuario cuando se autentica o cambia el user.id.
  useEffect(() => {
    if (!isAuthenticated || !user?.id || !token) return

    const fetchUserData = async () => {
      try {
        const userAck = await getUserById(user.id)
        registerPendingRequest(userAck, 'user-loaded')
      } catch (error) {
        console.error('Error al solicitar datos del usuario:', error)
      }
    }

    fetchUserData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, isAuthenticated])


  // ----- Para acciones de usuario -----

  // Maneja el inicio de sesión, guardando el token y mostrando el nombre en la navbar de inmediato.
  const handleLogin = async (email, password) => {
    try {
      // Realizar login y obtener token
      const loginResponse = await login(email, password)

      // Verificar que se recibió un token de acceso válido
      if (!loginResponse.access_token) {
        throw new Error('No se recibió un token de acceso válido.')
      }

      // Obtiene el nombre para mostrar el nombre en la navbar inmediatamente
      const claims = parseJwtPayload(loginResponse.access_token)

      setToken(loginResponse.access_token)
      setIsAuthenticated(true)
      setCurrentView('profile')
      // Usuario parcial para que la navbar muestre el nombre antes de que llegue el SSE
      setUser({ id: loginResponse.user_id, name: claims?.name })

      stableAddToast('success', '¡Bienvenido! Cargando tu información...')
    } catch (error) {
      stableAddToast('error', error.message || 'No se pudo iniciar sesión.')
      console.error('Error al iniciar sesión:', error)
    }
  }

  // Maneja el registro de un nuevo usuario.
  const handleRegister = async (name, email, password) => {
    try {
      // Realizar el registro y registrar la solicitud pendiente para esperar la confirmación por SSE
      const ackResponse = await registerUser(name, email, password)
      registerPendingRequest(ackResponse, 'user-created')
      setCurrentView('auth')
      stableAddToast('success', '¡Usuario registrado exitosamente! Ya puedes iniciar sesión.')
    } catch (error) {
      stableAddToast('error', error.message || 'No se pudo registrar el usuario.')
      console.error('Error al registrar usuario:', error)
    }
  }

  // Maneja la realización de un pedido desde la vista de órdenes.
  const handlePlaceOrder = async (productId, quantity) => {
    try {
      if (!user?.id) {
        throw new Error('No hay usuario autenticado para realizar el pedido.')
      }
      // Realizar el pedido y registrar la solicitud pendiente para esperar la actualización por SSE
      const orderResponse = await orderSkill(user.id, productId, quantity)
      registerPendingRequest(orderResponse, 'order-status-updated')
      setPreSelectedSkillId(undefined)
      return orderResponse
    } catch (error) {
      console.error('Error al realizar el pedido:', error)
      stableAddToast('error', error.message || 'No se pudo enviar el pedido.')
      throw error
    }
  }

  // Controla el cierre de sesión del usuario, limpiando estado y localStorage
  const handleLogout = () => {
    clearToken()
    localStorage.removeItem('current_view')
    setToken(null)
    setIsAuthenticated(false)
    setUser(null)
    setSkills([])
    clearPendingRequests()
    setCurrentView('auth')
    setPreSelectedSkillId(undefined)
    stableAddToast('success', 'Has cerrado sesión exitosamente. ¡Hasta luego!')
  }

  // Maneja el clic en "Ordenar" desde el catálogo, preseleccionando la habilidad y navegando a órdenes
  const handleOrderClick = (skillId) => {
    setPreSelectedSkillId(skillId)
    setCurrentView('orders')
  }

  // Controla la navegación entre vistas
  const handleNavigate = (view) => {
    setCurrentView(isAuthenticated && view === 'auth' ? 'catalog' : view)
  }


  // ----- Componente principal -----

  return (
    <div className="min-h-screen bg-background">
      <Navbar currentView={currentView} onNavigate={handleNavigate} isAuthenticated={isAuthenticated} userName={user?.name} onLogout={handleLogout} />
      {isRestoringSession ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <p className="text-muted-foreground">Restaurando sesiÃ³n...</p>
        </div>
      ) : !isAuthenticated ? (
        <AuthView onLogin={handleLogin} onRegister={handleRegister} addToast={stableAddToast} />
      ) : currentView === 'profile' && user ? (
        <ProfileView user={user} />
      ) : currentView === 'profile' && !user ? (
        <div className="flex items-center justify-center min-h-[60vh]">
          <p className="text-muted-foreground">Cargando perfil...</p>
        </div>
      ) : currentView === 'catalog' ? (
        <CatalogView skills={skills} onOrderClick={handleOrderClick} />
      ) : currentView === 'orders' ? (
        <OrdersView skills={skills} preSelectedSkillId={preSelectedSkillId} onPlaceOrder={handlePlaceOrder} addToast={stableAddToast} />
      ) : null}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </div>
  )
}

export default App
