// Client ID handling for anonymous identification (X-Client-Id)
export function saveClientId(clientId) {
    try {
        localStorage.setItem('client_id', clientId)
    } catch (error) {
        console.error('Error al guardar clientId en localStorage:', error)
    }
}

export function getClientId() {
    try {
        let id = localStorage.getItem('client_id')
        if (!id) {
            // Crear un client id simple, persistirlo y retornarlo
            id = `client-${Math.random().toString(36).slice(2, 10)}`
            localStorage.setItem('client_id', id)
        }
        return id
    } catch (error) {
        console.error('Error al obtener clientId del localStorage:', error)
        return null
    }
}

export function clearClientId() {
    try {
        localStorage.removeItem('client_id')
    } catch (error) {
        console.error('Error al limpiar clientId del localStorage:', error)
    }
}
