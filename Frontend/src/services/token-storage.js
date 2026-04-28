// Funciones para persistir el token JWT en localStorage.
export function saveToken(token) {
    try {
        localStorage.setItem('auth_token', token)
    } catch (error) {
        console.error('Error al guardar token en localStorage:', error)
    }
}

export function getToken() {
    try {
        return localStorage.getItem('auth_token') || null
    } catch (error) {
        console.error('Error al obtener token del localStorage:', error)
        return null
    }
}

export function clearToken() {
    try {
        localStorage.removeItem('auth_token')
    } catch (error) {
        console.error('Error al limpiar token del localStorage:', error)
    }
}