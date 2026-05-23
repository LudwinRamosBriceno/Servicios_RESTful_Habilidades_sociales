import { get } from './http'

// Función para obtener la lista habilidades del catálogo y stock actual
export function getAllSkills() {
    return get('/products', { auth: true })
}
