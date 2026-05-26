# Mapa de Eventos EDA - Arquitectura de Publicadores y Suscriptores

## Tabla General de Eventos

| # | Evento | Tipo | Producers  | Consumers | Descripción |
|---|--------|------|-----------|---------------|-------------|
| 1 | `orders.create.requested` | Request | API Gateway | Orders Service | Solicitud para crear una nueva orden |
| 2 | `orders.create.responded` | Response | Orders Service | API Gateway | Respuesta de creación de orden (éxito/error) |
| 3 | `orders.get.requested` | Request | API Gateway | Orders Service | Solicitud para obtener una orden por ID |
| 4 | `orders.get.responded` | Response | Orders Service | API Gateway | Respuesta con datos de la orden |
| 5 | `orders.list_by_user.requested` | Request | API Gateway | Orders Service | Solicitud para listar órdenes de un usuario |
| 6 | `orders.list_by_user.responded` | Response | Orders Service | API Gateway | Respuesta con lista de órdenes del usuario |
| 7 | `products.list.requested` | Request | API Gateway | Products Service | Solicitud para listar todos los productos |
| 8 | `products.list.responded` | Response | Products Service | API Gateway | Respuesta con lista de productos |
| 9 | `products.get.requested` | Request | API Gateway | Products Service | Solicitud para obtener un producto por ID |
| 10 | `products.get.responded` | Response | Products Service | API Gateway | Respuesta con datos del producto |
| 11 | `users.list.requested` | Request | API Gateway | Users Service | Solicitud para listar todos los usuarios |
| 12 | `users.list.responded` | Response | Users Service | API Gateway | Respuesta con lista de usuarios |
| 13 | `users.get.requested` | Request | API Gateway | Users Service | Solicitud para obtener un usuario por ID |
| 14 | `users.get.responded` | Response | Users Service | API Gateway | Respuesta con datos del usuario |
| 15 | `users.create.requested` | Request | API Gateway | Users Service | Solicitud para crear un nuevo usuario |
| 16 | `users.create.responded` | Response | Users Service | API Gateway | Respuesta de creación de usuario (éxito/error) |
| 17 | `pedido.creado` | Event | Orders Service | Products Service | Una orden fue creada exitosamente, inicia validación de inventario |
| 18 | `inventario.confirmado` | Event | Products Service | Orders Service<br/>Users Service | Stock disponible confirmado, orden procede, usuario gana habilidades |
| 19 | `inventario.rechazado` | Event | Products Service | Orders Service | Stock insuficiente o producto no disponible, orden rechazada |
| 20 | `orders.status.updated` | Event | Orders Service | API Gateway | Notificación en tiempo real de cambio de estado de orden (SSE push) |
| 21 | `usuario.actualizado` | Event | Users Service | Notifications Service | Usuario obtuvo nuevas habilidades, notificación al usuario |

---

## Topología de Conexiones por Servicio

### API Gateway
**Publica:**
- `orders.create.requested`
- `orders.get.requested`
- `orders.list_by_user.requested`
- `products.list.requested`
- `products.get.requested`
- `users.list.requested`
- `users.get.requested`
- `users.create.requested`

**Consume:**
- `orders.create.responded`
- `orders.get.responded`
- `orders.list_by_user.responded`
- `products.list.responded`
- `products.get.responded`
- `users.list.responded`
- `users.get.responded`
- `users.create.responded`
- `orders.status.updated` ← **Push SSE en tiempo real**

---

### Orders Service
**Publica:**
- `pedido.creado`
- `orders.status.updated`
- `orders.create.responded`
- `orders.get.responded`
- `orders.list_by_user.responded`

**Consume:**
- `orders.create.requested`
- `orders.get.requested`
- `orders.list_by_user.requested`
- `inventario.confirmado`
- `inventario.rechazado`

---

### Products Service
**Publica:**
- `inventario.confirmado`
- `inventario.rechazado`
- `products.list.responded`
- `products.get.responded`

**Consume:**
- `products.list.requested`
- `products.get.requested`
- `pedido.creado`

---

### Users Service
**Publica:**
- `usuario.actualizado`
- `users.list.responded`
- `users.get.responded`
- `users.create.responded`

**Consume:**
- `users.list.requested`
- `users.get.requested`
- `users.create.requested`
- `inventario.confirmado`

---

### Notifications Service
**Consume:**
- `usuario.actualizado`

---