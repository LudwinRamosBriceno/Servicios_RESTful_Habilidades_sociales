import { get, post, put, del } from './http'

// Función para obtener la lista de usuarios registrados
export function getUsers() {
    return get('/users')
}

// Función para registrar un nuevo usuario
export function registerUser(name, email, password) { 
    if (!name || !email || !password) {
        throw new Error('[Frontend] Error: Todos los campos son obligatorios')
    }
    return post('/users', { name, email, password })
}
