import { get, post, put, del } from './http'

// Función para información de un usuario
export function getUserById(id) {
    return get(`/users/${id}`)
}
