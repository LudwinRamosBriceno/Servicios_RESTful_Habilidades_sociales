"""Constantes de eventos para el API Gateway."""

EVENT_PRODUCTS_LIST_REQUESTED = "products.list.requested"
EVENT_PRODUCTS_GET_REQUESTED = "products.get.requested"
EVENT_USERS_LIST_REQUESTED = "users.list.requested"
EVENT_USERS_GET_REQUESTED = "users.get.requested"
EVENT_USERS_CREATE_REQUESTED = "users.create.requested"
EVENT_ORDERS_CREATE_REQUESTED = "orders.create.requested"
EVENT_ORDERS_GET_REQUESTED = "orders.get.requested"
EVENT_ORDERS_LIST_BY_USER_REQUESTED = "orders.list_by_user.requested"

# Eventos de response
EVENT_PRODUCTS_LIST_RESPONDED = "products.list.responded"
EVENT_PRODUCTS_GET_RESPONDED = "products.get.responded"
EVENT_USERS_LIST_RESPONDED = "users.list.responded"
EVENT_USERS_GET_RESPONDED = "users.get.responded"
EVENT_USERS_CREATE_RESPONDED = "users.create.responded"
EVENT_ORDERS_CREATE_RESPONDED = "orders.create.responded"
EVENT_ORDERS_GET_RESPONDED = "orders.get.responded"
EVENT_ORDERS_LIST_BY_USER_RESPONDED = "orders.list_by_user.responded"
EVENT_ORDERS_STATUS_UPDATED = "orders.status.updated"

# Lista blanca de eventos de respuesta que el gateway espera recibir.
RESPONSE_EVENTS = {
    EVENT_PRODUCTS_LIST_RESPONDED,
    EVENT_PRODUCTS_GET_RESPONDED,
    EVENT_USERS_LIST_RESPONDED,
    EVENT_USERS_GET_RESPONDED,
    EVENT_USERS_CREATE_RESPONDED,
    EVENT_ORDERS_CREATE_RESPONDED,
    EVENT_ORDERS_GET_RESPONDED,
    EVENT_ORDERS_LIST_BY_USER_RESPONDED,
}

# Eventos de notificacion que se envian por SSE sin alterar el registro.
PUSH_EVENTS = {
    EVENT_ORDERS_STATUS_UPDATED,
}

# Mapeo de eventos a tipos amigables para el frontend.
EVENT_TYPE_MAP = {
    EVENT_PRODUCTS_LIST_RESPONDED: "products-loaded",
    EVENT_PRODUCTS_GET_RESPONDED: "product-loaded",
    EVENT_USERS_LIST_RESPONDED: "users-loaded",
    EVENT_USERS_GET_RESPONDED: "user-loaded",
    EVENT_USERS_CREATE_RESPONDED: "user-created",
    EVENT_ORDERS_CREATE_RESPONDED: "order-created",
    EVENT_ORDERS_GET_RESPONDED: "order-loaded",
    EVENT_ORDERS_LIST_BY_USER_RESPONDED: "orders-loaded",
    EVENT_ORDERS_STATUS_UPDATED: "order-status-updated",
}

# Mensajes de confirmacion por tipo de evento.
RESPONSE_SUCCESS_MESSAGE = {
    EVENT_PRODUCTS_LIST_RESPONDED: "Lista de productos actualizada",
    EVENT_PRODUCTS_GET_RESPONDED: "Producto cargado",
    EVENT_USERS_LIST_RESPONDED: "Usuarios cargados",
    EVENT_USERS_GET_RESPONDED: "Informacion de usuario cargada",
    EVENT_ORDERS_GET_RESPONDED: "Orden cargada",
    EVENT_ORDERS_LIST_BY_USER_RESPONDED: "Ordenes cargadas",
}

# Mensajes de error por tipo de evento.
RESPONSE_ERROR_MESSAGE = {
    EVENT_PRODUCTS_LIST_RESPONDED: "Error al cargar la lista de productos",
    EVENT_PRODUCTS_GET_RESPONDED: "Error al cargar el producto",
    EVENT_USERS_LIST_RESPONDED: "Error al cargar los usuarios",
    EVENT_USERS_GET_RESPONDED: "Error al cargar la informacion del usuario",
    EVENT_ORDERS_GET_RESPONDED: "Error al cargar la orden",
    EVENT_ORDERS_LIST_BY_USER_RESPONDED: "Error al cargar las ordenes",
}
