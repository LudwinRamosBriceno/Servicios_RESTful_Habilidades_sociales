import { get, post, put, del } from './http'

// Función para realizar un pedido de habilidad
export function orderSkill(userId, productId, quantity) {
    return post('/orders', { userId, productId, quantity }, { auth: true })
}