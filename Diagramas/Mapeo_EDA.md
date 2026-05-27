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


# Colas y Eventos de RabbitMQ

## Exchange principal

| Elemento | Valor |
|---|---|
| Exchange | `novalink.events` |
| Tipo | `topic` |
| Durable | `true` |
| Uso | Todos los servicios publican y consumen eventos usando el `event_type` como `routing_key`. |

Todos los servicios utilizan el mismo exchange. RabbitMQ enruta los mensajes hacia las colas correspondientes según la `routing_key` de cada evento.

---

## Cola: `api-gateway-service`

| Aspecto | Descripción |
|---|---|
| Consumidor | `api-gateway` |
| Eventos que consume | `#.responded`, `orders.status.updated` |
| Quién publica esos eventos | `products-service`, `users-service`, `orders-service` |
| Para qué sirve | Recibir respuestas de operaciones asincrónicas y eventos push de actualización de órdenes. |
| Qué hace al consumir | Actualiza la tabla `requests` en `gateway-db` y notifica al frontend mediante SSE. |
| Qué publica después | No publica otro evento como respuesta directa; envía la actualización al frontend por SSE. |

### Eventos recibidos

```txt
products.list.responded
products.get.responded
users.list.responded
users.get.responded
users.create.responded
orders.create.responded
orders.get.responded
orders.list_by_user.responded
orders.status.updated
```

### Contexto de uso

Esta cola permite que el API Gateway reciba las respuestas de los microservicios después de que estos procesan una solicitud asincrónica.

Cuando llega una respuesta, el Gateway usa el `requestId` para actualizar el estado de la solicitud en `gateway-db` y luego envía la información al frontend mediante SSE.

---

## Cola: `products-requests`

| Aspecto | Descripción |
|---|---|
| Consumidor | `products-service` |
| Eventos que consume | `products.list.requested`, `products.get.requested` |
| Quién publica esos eventos | `api-gateway` |
| Para qué sirve | Procesar consultas de productos solicitadas desde el frontend. |
| Qué hace al consumir | Consulta la base de datos `products-db`. |
| Qué publica después | `products.list.responded`, `products.get.responded` |

### Flujo de consulta de productos

```txt
Frontend solicita productos
→ API Gateway publica products.list.requested
→ products-service consume desde products-requests
→ products-service consulta products-db
→ products-service publica products.list.responded
→ api-gateway-service consume la respuesta
→ API Gateway notifica al frontend por SSE
```

---

## Cola: `products-service`

| Aspecto | Descripción |
|---|---|
| Consumidor | `products-service` |
| Evento que consume | `pedido.creado` |
| Quién publica ese evento | `orders-service` |
| Para qué sirve | Validar inventario cuando se crea un pedido. |
| Qué hace al consumir | Verifica disponibilidad del producto o habilidad y descuenta stock si corresponde. |
| Qué publica después | `inventario.confirmado` o `inventario.rechazado` |

### Contexto de uso

Cuando `orders-service` crea una orden, publica el evento `pedido.creado`.

El `products-service` consume ese evento para validar si existe inventario suficiente. Si la validación es exitosa, publica `inventario.confirmado`; si falla, publica `inventario.rechazado`.

---

## Cola: `users-requests`

| Aspecto | Descripción |
|---|---|
| Consumidor | `users-service` |
| Eventos que consume | `users.list.requested`, `users.get.requested`, `users.create.requested` |
| Quién publica esos eventos | `api-gateway` |
| Para qué sirve | Procesar operaciones asincrónicas relacionadas con usuarios. |
| Qué hace al consumir | Consulta, obtiene o crea usuarios en `users-db`. |
| Qué publica después | `users.list.responded`, `users.get.responded`, `users.create.responded` |

### Contexto de uso

Esta cola atiende solicitudes de usuario iniciadas desde el frontend a través del API Gateway.

El Gateway publica eventos de solicitud y `users-service` devuelve eventos de respuesta para que el Gateway actualice el estado de la solicitud y notifique al frontend.

---

## Cola: `users-service`

| Aspecto | Descripción |
|---|---|
| Consumidor | `users-service` |
| Evento que consume | `inventario.confirmado` |
| Quién publica ese evento | `products-service` |
| Para qué sirve | Actualizar el perfil del usuario después de confirmar inventario. |
| Qué hace al consumir | Suma o asigna puntos de habilidad al usuario en `users-db`. |
| Qué publica después | `usuario.actualizado` |

### Contexto de uso

Después de que `products-service` confirma inventario, `users-service` consume `inventario.confirmado` para actualizar las habilidades sociales del usuario.

Cuando termina la actualización, publica `usuario.actualizado`, evento que será consumido por `notifications-service`.

---

## Cola: `orders-requests`

| Aspecto | Descripción |
|---|---|
| Consumidor | `orders-service` |
| Eventos que consume | `orders.create.requested`, `orders.get.requested`, `orders.list_by_user.requested` |
| Quién publica esos eventos | `api-gateway` |
| Para qué sirve | Procesar operaciones asincrónicas relacionadas con pedidos. |
| Qué hace al consumir | Crea pedidos, consulta pedidos o lista pedidos por usuario en `orders-db`. |
| Qué publica después | `orders.create.responded`, `orders.get.responded`, `orders.list_by_user.responded` |

### Evento adicional publicado

Cuando se crea un pedido correctamente, `orders-service` también publica:

```txt
pedido.creado
```

Ese evento es consumido por `products-service`.

### Contexto de uso

Esta cola recibe las solicitudes de pedidos enviadas por el API Gateway.

En el caso de creación de pedido, `orders-service` registra la orden y luego inicia el flujo de inventario publicando `pedido.creado`.

---

## Cola: `orders-service`

| Aspecto | Descripción |
|---|---|
| Consumidor | `orders-service` |
| Eventos que consume | `inventario.confirmado`, `inventario.rechazado` |
| Quién publica esos eventos | `products-service` |
| Para qué sirve | Actualizar el estado final de una orden según el resultado del inventario. |
| Qué hace al consumir | Cambia el estado del pedido en `orders-db`. |
| Qué publica después | `orders.status.updated` |

### Contexto de uso

Cuando `products-service` valida inventario, publica `inventario.confirmado` o `inventario.rechazado`.

`orders-service` consume esos eventos para actualizar el estado de la orden y publica `orders.status.updated`, el cual es recibido por el API Gateway y enviado al frontend mediante SSE.

---

## Cola: `notifications-service`

| Aspecto | Descripción |
|---|---|
| Consumidor | `notifications-service` |
| Evento que consume | `usuario.actualizado` |
| Quién publica ese evento | `users-service` |
| Para qué sirve | Generar una notificación cuando el usuario recibe la habilidad. |
| Qué hace al consumir | Imprime o registra la notificación en consola. |
| Qué publica después | Actualmente no publica ningún evento. |

### Contexto de uso

El servicio de notificaciones funciona como consumidor final del flujo de eventos.

Cuando `users-service` actualiza la habilidad de un usuario, publica `usuario.actualizado`.

`notifications-service` consume ese evento y genera un log de confirmación.


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
