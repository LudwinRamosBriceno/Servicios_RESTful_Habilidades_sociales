import { get, post } from './http'
import { getClientId } from './token-storage'

// Función para iniciar sesión con email y contraseña (cookie HttpOnly).
export async function login(email, password) {
    if (!email || !password) {
        throw new Error('Error: Email y contraseña son obligatorios')
    }
    return post('/auth/login', { email, password })
}

// Función para obtener la lista de usuarios registrados
export function getUsers() {
    return get('/users')
}

// Función para registrar un nuevo usuario
export function registerUser(name, email, password) {
    if (!name || !email || !password) {
        throw new Error('Error: Todos los campos son obligatorios')
    }
    // Para registro anónimo, enviar X-Client-Id según contrato del gateway
    const clientId = getClientId()
    return post('/users', { name, email, password }, { headers: { 'X-Client-Id': clientId }, omitCredentials: true })
}

// Función para validar sesión actual (cookie HttpOnly).
export function getSession() {
    return get('/auth/session')
}

// Función para cerrar sesión.
export function logout() {
    return post('/auth/logout')
}
