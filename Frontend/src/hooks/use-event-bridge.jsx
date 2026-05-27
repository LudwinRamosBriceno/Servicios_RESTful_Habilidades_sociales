import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchEventSource } from '@microsoft/fetch-event-source'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const DEFAULT_SSE_URL = `${API_BASE_URL}/events`

// Hook para manejar la comunicación asíncrona (SSE) entre el frontend y el backend, ademas del estado de solicitudes pendientes
export function useEventBridge({ enabled, addToast, setSkills, setUser, refreshUserData, refreshSkills }) {

    const [pendingRequests, setPendingRequests] = useState([])      // Lista de solicitudes pendientes realizadas por el frontend y esperan respuesta

    // Cuando SSE llega, ejecuta las ref para actualizar App.jsx
    const addToastRef = useRef(addToast)                            // Apunta a addToast para mostrar notificaciones
    const setSkillsRef = useRef(setSkills)                          // Apunta a setSkills para actualizar el catálogo de habilidades
    const setUserRef = useRef(setUser)                              // Apunta a setUser para actualizar los datos del usuario

    // Para refrescar los estados actualizados ↑
    const refreshUserDataRef = useRef(refreshUserData)              // Apunta a refreshUserData para recargar los datos del usuario desde el servidor
    const refreshSkillsRef = useRef(refreshSkills)                  // Apunta a refreshSkills para recargar el catálogo de habilidades desde el servidor
    const handlePayloadRef = useRef(null)                           // Apunta a handlePayload para procesar los payloads recibidos por SSE

    const resolvedRequestIdsRef = useRef(new Set())                 // Conjunto de IDs de solicitudes ya resueltas, evita procesar el mismo evento SSE varias veces
    const pollTimerIdsRef = useRef(new Map())                       // Mapa de requestId → timerId del polling, permite cancelar el timer cuando SSE responde primero

    // Sincroniza las refs cuando App.jsx se re-renderiza y entrega versiones nuevas de sus funciones
    useEffect(() => { addToastRef.current = addToast }, [addToast])
    useEffect(() => { setSkillsRef.current = setSkills }, [setSkills])
    useEffect(() => { setUserRef.current = setUser }, [setUser])
    useEffect(() => { refreshUserDataRef.current = refreshUserData }, [refreshUserData])
    useEffect(() => { refreshSkillsRef.current = refreshSkills }, [refreshSkills])

    // ------------------------------------------------------------------

    // Función para limpiar el timer del polling de una solicitud cuando se resuelve o se cancela
    const clearPollTimer = useCallback((requestId) => {
        // Busca el timerId asociado al requestId
        const timerId = pollTimerIdsRef.current.get(requestId)
        // Si existe un timer activo, lo limpia y lo elimina del mapa
        if (timerId) {
            clearTimeout(timerId)
            pollTimerIdsRef.current.delete(requestId)
        }
    }, [])

    // Función para iniciar el polling del estado de una solicitud asíncrona, se llama cuando se registra una nueva solicitud pendiente
    const pollRequestStatus = useCallback((requestId, type) => {

        // Si no hay requestId o la solicitud ya fue resuelta, no hace nada
        if (!requestId || resolvedRequestIdsRef.current.has(requestId)) return

        // Función recursiva para programar intentos de polling con retraso incremental (termina después de 10 intentos o si la solicitud se resuelve)
        const schedulePoll = (attempt) => {

            // Configura un timer para consultar el estado de la solicitud
            const timerId = setTimeout(async () => {

            // Verifica nuevamente si la solicitud ya fue resuelta antes de hacer la consulta
            if (resolvedRequestIdsRef.current.has(requestId)) return

            // Consulta el estado de la solicitud al backend
            try {
                // Realiza una petición al backend para obtener el estado de la solicitud (NO HAY ALGO EN EL BACKEND RECIBA ESTA CONSULTA O SI?)
                const response = await fetch(`${API_BASE_URL}/requests/${requestId}`, {
                    credentials: 'include',
                })
                // Si la respuesta es exitosa, procesa el payload como se haría con un evento SSE normal
                if (response.ok) {
                    const payload = await response.json()
                    if (payload.status === 'COMPLETED' || payload.status === 'FAILED') {
                        handlePayloadRef.current?.({
                            type,
                            requestId,
                            status: payload.status,
                            result: payload.response,
                            message: payload.error,
                        })
                        return
                    }
                }
            } catch (error) {
                console.warn('No se pudo consultar estado de solicitud:', error)
            }
            // Si la solicitud no se ha resuelto en el tiempo asignado, programa otro intento de polling con un retraso incremental
            if (attempt < 10) {
                schedulePoll(attempt + 1)
            }
            }, attempt === 1 ? 4000 : 2500) // Retraso inicial de 4 segundos, luego 2.5 segundos para cada intento adicional
            // Guarda el timerId en el mapa para poder cancelarlo si llega un SSE con la respuesta antes de que el timer se ejecute
            pollTimerIdsRef.current.set(requestId, timerId)
        }
        // Inicia el siguiente intento de polling
        schedulePoll(1)
    }, [])

    // Función para registrar una nueva solicitud pendiente, se llama cuando el frontend envía una solicitud asíncrona al backend
    const registerPendingRequest = useCallback((response, type) => {

        // Extrae el requestId de la respuesta sincrona del backend (ACK)
        const requestId = response?.requestId || response?.id

        // Si no se recibe un requestId, muestra una advertencia y no registra la solicitud como pendiente
        if (!requestId) {
            console.warn('ACK recibido sin requestId. No se pudo registrar como pendiente.')
            return null
        }

        // Agrega la solicitud pendiente a la lista de pendingRequests
        setPendingRequests((prev) => [ ...prev, { requestId, type, createdAt: new Date().toISOString(), }, ])

        // Muestra un notificación de que la solicitud fue recibida
        try {
            const ackMessage = response?.message || `Solicitud recibida (${type})`
            console.log(ackMessage, 'ID:', requestId)
            addToastRef.current( 'info', requestId ? `${ackMessage} - id: ${requestId}` : ackMessage, { className: 'toast-item-info' } )
        } catch (err) {
            console.warn('No se pudo mostrar toast para ACK:', err)
        }

        // Elimina el requestId (ACK) del conjunto de solicitudes resueltas
        resolvedRequestIdsRef.current.delete(requestId)

        // Inicia el polling para esta solicitud
        pollRequestStatus(requestId, type)

        return requestId
    }, [pollRequestStatus])

    // Función para resolver una solicitud pendiente cuando llega respuesta por SSE
    const resolvePendingRequest = useCallback((requestId) => {
        // Si no se recibe un requestId, no hace nada
        if (!requestId) return
        // Agrega el requestId al conjunto de solicitudes resueltas
        resolvedRequestIdsRef.current.add(requestId)
        // Limpia el timer de polling asociado
        clearPollTimer(requestId)
        // Elimina la solicitud pendiente de la lista de pendingRequests
        setPendingRequests((prev) => prev.filter((item) => item.requestId !== requestId))
    }, [clearPollTimer])

    // Función para limpiar todas las solicitudes pendientes
    const clearPendingRequests = useCallback(() => {
        // Limpia todos los timers de polling activos
        for (const timerId of pollTimerIdsRef.current.values()) {
            clearTimeout(timerId)
        }
        // Limpia los mapas y conjuntos relacionados con las solicitudes pendientes
        pollTimerIdsRef.current.clear()
        // Agrega todos los requestIds pendientes al conjunto de resueltos
        resolvedRequestIdsRef.current.clear()
        // Limpia la lista de solicitudes pendientes en el estado
        setPendingRequests([])
    }, [])

    const resolvePendingRequestRef = useRef(resolvePendingRequest)  // Apunta a resolvePendingRequest para resolver solicitudes pendientes cuando llega un SSE con la respuesta
    useEffect(() => { resolvePendingRequestRef.current = resolvePendingRequest }, [resolvePendingRequest])

    // Función para procesar los payloads recibidos por SSE
    const handlePayload = useCallback((payload) => {
        // Extrae la información relevante del payload recibido por SSE
        const { requestId, type, status, message } = payload || {}
        // Si tiene un requestId, marca esa solicitud como resuelta, la elimina de pendingRequests y cancela su timer de polling si existe
        if (requestId) {
            resolvePendingRequestRef.current(requestId)
        }

        // Determina el estado de la transacción y muestra una notificación (re-renderiza App.jsx)
        const showByStatus = (defaults) => {
            if (status === 'FAILED') {
                addToastRef.current('error', message || defaults.fail)
            } else if (status === 'COMPLETED') {
                addToastRef.current('success', message || defaults.success)
            } else if (message) {
                addToastRef.current('info', message)
            }
        }

        // Si el tipo de evento es 'products-loaded', actualiza el catálogo de habilidades en App.jsx usando setSkillsRef (re-renderiza App.jsx)
        if (type === 'products-loaded') {
            const skillsPayload = payload.result
            if (Array.isArray(skillsPayload)) {
                setSkillsRef.current(skillsPayload)
            }
            showByStatus({ success: 'Catalogo de habilidades actualizado', fail: 'Fallo al actualizar catalogo' })  // Muestra notificación del resultado
        }

        // Si el tipo de evento es 'user-loaded' o 'user-created', actualiza los datos del usuario en App.jsx usando setUserRef (re-renderiza App.jsx)
        if (type === 'user-loaded' || type === 'user-created') {
            const userPayload = payload.result
            if (userPayload) {
                setUserRef.current(userPayload)
            }
            showByStatus({ success: 'Informacion del usuario actualizada', fail: 'Fallo al cargar informacion del usuario' })   // Muestra notificación del resultado
        }

        // Si el tipo de evento es 'order-status-updated', muestra una notificación del estado de la orden y refresca los datos del usuario y el catálogo de habilidades si la orden se completó o falló (re-renderiza App.jsx)
        if (type === 'order-status-updated') {
            showByStatus({ success: 'Orden procesada correctamente', fail: 'Error en la orden' })   // Muestra notificación del resultado
            if (status === 'COMPLETED' || status === 'FAILED') {
                refreshSkillsRef.current?.()
                refreshUserDataRef.current?.()
            }
        }
    }, [])

    // Sincroniza la ref de handlePayload
    useEffect(() => { handlePayloadRef.current = handlePayload }, [handlePayload])

    useEffect(() => {
        if (!enabled) return

        const controller = new AbortController()

        // Función para conectar al backend usando SSE y manejar los eventos recibidos
        const connect = async () => {
            try {
                // Conecta al backend usando fetchEventSource para recibir eventos SSE
                await fetchEventSource(DEFAULT_SSE_URL, {
                    method: 'GET',
                    // La cookie de sesión se coloca automáticamente.
                    credentials: 'include',
                    signal: controller.signal,

                    // Maneja la respuesta de conexión para verificar que es un stream SSE válido
                    onopen(response) {
                        if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
                            console.log('SSE conectado')
                            return
                        }
                        throw new Error(`Respuesta SSE inesperada: ${response.status}`)
                    },

                    // Maneja los eventos SSE recibidos, procesa el payload usando handlePayloadRef para actualizar App.jsx sin reiniciar la conexión SSE
                    onmessage(event) {
                        if (!event.data) return
                        try {
                            handlePayloadRef.current?.(JSON.parse(event.data))
                        } catch {
                            console.warn('Evento SSE no JSON:', event.data)
                        }
                    },

                    // Maneja errores de la conexión SSE, muestra un error en consola si la conexión falla
                    onerror(error) {
                        console.error('Error SSE:', error)
                    },
                })
            } catch (error) {
                if (!controller.signal.aborted) {
                    console.error('Fallo al conectar SSE:', error)
                }
            }
        }

        connect()

        return () => {
            controller.abort()
        }
    }, [enabled])

    return { pendingRequests, registerPendingRequest, clearPendingRequests }
}


/* Flujo cuando backend responde por SSE:
1. SSE llega
2. Se ejecuta ejecuta setSkillsRef.current(array), lo que llama a setSkills(array) en App.jsx (setter de useState) es un cambio de estado en App.jsx
3. React detecta el cambio de estado y re-renderiza App.jsx
4. addToast nace con nuevo contexto (función nueva en memoria)
5. useEffect detecta que addToast cambió y actualiza addToastRef.current = addToast (ref se actualiza)
6. addToastRef.current se usa para mostrar notificaciones con el nuevo contexto de App.jsx, evitando reconexiones SSE

En respuestas posteriores del backend:
El ciclo se repite:
                     SSE llega → refs del hook ejecutan funciones actualizadas de App.jsx
                     Las refs siempre apuntan a las versiones más recientes gracias a los useEffect
                     El SSE nunca se reinicia, solo consume las refs actualizadas en cada respuesta */
