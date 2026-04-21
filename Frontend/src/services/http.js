const API_URL_BASE = import.meta.env.VITE_API_URL_BASE;

// Función para realizar solicitud HTTP a la API
async function request(path, options = {}) {
    
    // Obtiene la configuración de la solicitud
    const { method = 'GET', headers = {}, body } = options;

    // Realizar la solicitud utilizando fetch con la configuración proporcionada
    const response = await fetch(`${API_URL_BASE}${path}`, {
        // GET, POST, PUT, DELETE
        method,
        // Encabezados, indica al backend que el cuerpo es JSON
        headers: {
            'Content-Type': 'application/json',
            ...headers,
        },
        // Convertir el cuerpo a JSON si se proporciona
        body: body ? JSON.stringify(body) : undefined,
    })

    // Obtener del header de la respuesta el tipo de contenido
    const contentType = response.headers.get('Content-Type');
    // Verificar si el header indica que la respuesta es JSON
    const isJson = contentType.includes('application/json');
    // Procesar la respuesta como JSON o texto según el tipo de contenido
    const payload = isJson ? await response.json() : await response.text()

    // Manejar errores HTTP
    if (!response.ok) {
        // Construir mensaje de error
        const message =
            // Si es JSON, usar el campo "detail" o "message" como mensaje de error
            (isJson && (payload.detail || payload.message)) ||
            // Si no es JSON pero es texto, usar el texto como mensaje de error
            (typeof payload === 'string' && payload) ||
            // Si no es JSON ni texto, usar un mensaje genérico
            'Fallo en la solicitud'
        
        // Crear un error con el mensaje
        const error = new Error(message)
        // Incluir el código de estado (error)
        error.status = response.status
        // Incluir la carga de la respuesta para más contexto
        error.payload = payload
        // Lanzar el error
        throw error
    }

    // Devolver la respuesta procesada (JSON o texto)
    return payload

}

// Función para realizar solicitud HTTP GET
export async function get(path, options = {}) {
    return request(path, { ...options, method: 'GET' })
}

// Función para realizar solicitud HTTP POST
export function post(path, body, options = {}) {
  return request(path, { ...options, method: 'POST', body })
}

// Función para realizar solicitud HTTP PUT
export function put(path, body, options = {}) {
  return request(path, { ...options, method: 'PUT', body })
}

// Función para realizar solicitud HTTP DELETE
export function del(path, options = {}) {
  return request(path, { ...options, method: 'DELETE' })
}