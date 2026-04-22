import { get, post, put, del } from './http'

// Función para obtener la lista habilidades del catálogo y stock actual
export function getAllSkills() {
    return get('/products')
}