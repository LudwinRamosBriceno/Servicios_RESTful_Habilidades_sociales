import { get, post, put, del } from './http'
import { saveToken } from './token-storage'

// Función para iniciar sesión con email y contraseña
export async function login(email, password) {
    if (!email || !password) {
        throw new Error('Error: Email y contraseña son obligatorios')
    }
    const response = await post('/auth/login', { email, password })
    // Guardar el token en localStorage
    if (response.access_token) {
        saveToken(response.access_token)
    }
    return response
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
    return post('/users', { name, email, password })
}
