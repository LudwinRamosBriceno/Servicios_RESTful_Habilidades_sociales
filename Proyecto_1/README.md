# NovaLink

> **Estudiantes:** Meibel Ceciliano Picado · Carlos Contreras Luna · Byron Mata Fuentes · Ludwin Ramos Briceño

Plataforma de microservicios REST para gestionar habilidades sociales como productos.

## Tecnologías utilizadas

- Kubernetes (Minikube)
- Docker
- Python y FastAPI
- PostgreSQL
- React + Vite y Javascript
- SQLAlchemy y Alembic
- Nginx

## Diagramas C4 y secuencia


### Diagrama de Contexto
<img src="Diagramas/Diagrama%20de%20Contexto.svg" alt="Diagrama de Contexto" width="700px" />

### Diagrama de Contenedores
<img src="Diagramas/Diagrama%20de%20Contenedores.svg" alt="Diagrama de Contenedores" width="700px" />

### Diagrama de Componentes
<img src="Diagramas/Diagrama%20de%20Componentes.svg" alt="Diagrama de Componentes" width="700px" />

### Diagrama de Secuencia
<img src="Diagramas/Diagrama%20de%20Secuencia.svg" alt="Diagrama de Secuencia" width="700px" />

---

# Manual de API RESTful


## Tabla de contenidos

- [Users](#users)
- [Products](#products)
- [Orders](#orders)

---

## Users

### Descripción general

El servicio **users** permite crear, obtener y modificar los usuarios que utilizan NovaLink.

- **Puerto del servicio (directo):** `8001`
- **Directo al microservicio (dentro del clúster):** `http://localhost:8001/users`
- **A través del API Gateway:** `http://localhost:8080/api/users`

### Modelo base

Esquema utilizado tanto para crear un usuario como para actualizarlo _(todos los campos son opcionales en actualización)_.

```json
{
  "name": "string",
  "email": "usuario@correo.com",
  "password": "string"
}
```

### Endpoints

| Método | URL | Descripción | Parámetros | Respuesta |
|--------|-----|-------------|------------|-----------|
| `GET` | `/api/users` | Retorna una lista de todos los usuarios registrados | — | `200 OK` · `404` No hay usuarios registrados |
| `GET` | `/api/users/{user_id}` | Obtener la información de un usuario específico | — | `200 OK` · `404` No hay usuarios registrados |
| `POST` | `/api/users` | Permite crear un nuevo usuario | `name`: string · `email`: string · `password`: string | `200 OK` · `409` Nombre ya existente · `422` Faltan campos o email inválido |
| `PUT` | `/api/users/{user_id}` | Actualizar un usuario existente | _(Campos opcionales)_ `name`: string · `email`: string · `password`: string | `200 OK` · `404` Usuario no encontrado · `409` Nombre ya existente · `422` Faltan campos o email inválido |

---

## Products

### Descripción general

El servicio **products** permite crear, obtener y modificar los productos en stock que ofrece NovaLink.

- **Puerto del servicio (directo):** `8002`
- **Directo al microservicio (dentro del clúster):** `http://localhost:8002/products`
- **A través del API Gateway:** `http://localhost:8080/api/products`

### Modelo base

Esquema utilizado tanto para crear un producto como para actualizarlo _(obligatorio solo para estas acciones)_.

```json
{
  "name": "string",
  "description": "string",
  "stock": integer,
  "active": Boolean
}
```

### Endpoints

| Método | URL | Descripción | Parámetros | Respuesta |
|--------|-----|-------------|------------|-----------|
| `GET` | `/api/products` | Retorna una lista de todos los productos registrados | — | `200 OK` |
| `GET` | `/api/products/{product_id}` | Obtener un producto por id | — | `200 OK` · `404` Producto no encontrado |
| `POST` | `/api/products` | Crear un nuevo producto | `name`: string · `description`: string · `stock`: integer · `active`: boolean | `200 OK` · `409` Producto ya existe |
| `PUT` | `/api/products/{product_id}` | Actualizar un producto existente por id | `name`: string · `description`: string · `stock`: integer · `active`: boolean | `200 OK` · `404` Producto no encontrado |
| `DELETE` | `/api/products/{product_id}` | Eliminar un producto por id | — | `200 OK` · `404` Producto no encontrado |
| `PUT` | `/api/products/{product_id}/stock` | Descontar stock de un producto por id | `quantity`: integer | `200 OK` · `404` Producto no encontrado · `422` Cantidad debe ser > 0 · `422` Stock insuficiente |

---

## Orders

### Descripción general

El servicio **orders** permite crear pedidos de productos asociados a un usuario existente.

- **Puerto del servicio (directo):** `8000`
- **Directo al microservicio (dentro del clúster):** `http://localhost:8000/orders`
- **A través del API Gateway:** `http://localhost:8080/api/orders`

### Modelo base

Esquema utilizado tanto para crear una orden como para actualizarla _(obligatorio solo para estas acciones)_.

```json
{
  "user_id": "string",
  "product_id": "string",
  "quantity": integer,
  "status": "string",
  "skill_points": integer,
  "created_at": "string"
}
```

### Endpoints

| Método | URL | Descripción | Parámetros | Respuesta |
|--------|-----|-------------|------------|-----------|
| `POST` | `/api/orders` | Creación de una orden | `user_id`: string · `product_id`: string · `quantity`: integer · `status`: string · `skill_points`: integer · `created_at`: string | `201` Orden completada con éxito · `202` Habilidad en propiedad, puntos agregados · `422` Cantidad debe ser > 0 · `422` Stock insuficiente |
| `GET` | `/api/orders/{order_id}` | Obtener detalles de una orden por id | — | `200 OK` · `404` Orden no encontrada |
| `GET` | `/api/orders/user/{user_id}` | Obtener órdenes asociadas a un usuario por id de usuario | — | `200 OK` · `404` Usuario no encontrado |

# Architecture Decision Records

---

## Tabla de contenidos

- [ADR 001 — Arquitectura híbrida con API Gateway](#adr-001)
- [ADR 002 — Kubernetes (Minikube) para orquestación de contenedores](#adr-002)
- [ADR 003 — Bases de datos separadas con volúmenes dedicados](#adr-003)

---

## ADR 001

### Arquitectura híbrida con API Gateway simple y comunicación síncrona directa entre microservicios

**Estado:** `Accepted`

### Contexto

La plataforma a diseñar e implementar debe seguir un ecosistema de microservicios RESTful, con una interfaz de usuario, un backend con la lógica de negocio y almacenamiento en base de datos. El sistema contiene tres microservicios independientes: **Usuarios**, **Productos** y **Pedidos**.

El proyecto tiene una duración de 3 semanas y el equipo de desarrollo tiene experiencia y conocimiento limitado en arquitecturas de microservicios.

### Decisión

Se utilizará una arquitectura híbrida fácil de implementar, depurar y desplegar en un clúster, considerando que solo se tendrán tres servicios y el volumen de transacciones será bajo. Se usará:

- **Un API Gateway simple** (sin lógica adicional) que actuará únicamente como _reverse proxy_ o punto de entrada para enrutar peticiones HTTP provenientes del frontend hacia los servicios correspondientes: Usuarios, Productos y Pedidos.
- **Comunicación síncrona directa** mediante HTTP client entre servicios. El servicio de Pedidos se comunica con Usuarios y Productos; el servicio de Usuarios tiene contacto con Productos.

### Consecuencias

####  Positivas

- Simplicidad y rapidez de implementación.
- El API Gateway expone solo ciertos endpoints hacia el exterior, consumidos por el frontend, y enruta a los servicios internos del clúster.
- El Gateway incorpora una capa de seguridad al no revelar las URIs internas de los microservicios.
- La comunicación síncrona por HTTP es fácil de depurar con logs y herramientas como Postman.
- Menor latencia en el flujo de pedido al no introducir mediadores.
- Cada microservicio mantiene su propia base de datos (autonomía de datos).
- Si el API Gateway falla, los servicios pueden seguir funcionando independientemente.

####  Negativas

- **Acoplamiento temporal:** si Productos o Usuarios falla, Pedidos no puede completar la operación, generando errores en cascada.
- **Mayor latencia en cadenas largas:** un pedido implica 3 llamadas HTTP internas (validar usuario, validar producto, actualizar perfil).
- **Acoplamiento en Pedidos:** si en el futuro se añaden más servicios (como facturación), Pedidos se volvería un "orquestador" acoplado.
- Si el API Gateway falla, el cliente no puede consumir los servicios.

---

## ADR 002

### Uso de Kubernetes (Minikube) para orquestación de contenedores

**Estado:** `Accepted`

### Contexto

Se requiere que todos los servicios (Usuarios, Productos, Pedidos y sus respectivas bases de datos) sean containerizados con Docker y ejecutados en un entorno que simule una infraestructura cloud real. Se debe orquestar los contenedores usando Kubernetes, específicamente **Minikube** para generar un clúster local, y escribir los manifiestos YAML necesarios (Deployments y Services) para que la aplicación sea resiliente y accesible dentro del clúster.

El equipo tiene 3 semanas de desarrollo y experiencia limitada en orquestación.

### Decisión

Se usará **Minikube** para crear un clúster Kubernetes de un solo nodo en el entorno local de desarrollo:

- Cada servicio y base de datos será desplegado mediante un **Deployment** (define réplicas, imagen Docker y puertos).
- Cada servicio será expuesto internamente mediante un **Service de tipo `ClusterIP`**.
- El API Gateway tendrá un **Service de tipo `NodePort`** para acceso desde el frontend o desde fuera del clúster (pruebas con Postman).
- El API Gateway será un servicio independiente, de modo que si falla, los demás servicios sigan funcionando y viceversa.

### Consecuencias

####  Positivas

- Cumple con el requisito explícito de orquestar contenedores con Kubernetes y Minikube.
- Minikube es gratuito, se ejecuta localmente y no requiere recursos cloud ni cuentas de pago.
- Los Services de Kubernetes proveen descubrimiento de servicio por nombre DNS, resolviendo el problema de IPs dinámicas.
- Si un contenedor falla, Kubernetes lo reinicia automáticamente gracias al Deployment.
- Los manifiestos YAML pueden adaptarse fácilmente a un clúster cloud real en el futuro.

####  Negativas

- El equipo debe aprender conceptos de Kubernetes (Pods, Deployments, Services, `kubectl`) y escribir YAMLs, lo que consume tiempo de investigación.
- Mayor consumo de recursos locales: Minikube requiere al menos **2 CPUs y 4 GB de RAM**, lo que puede ser limitante en equipos no especializados.
- Cada cambio en el código requiere reconstruir la imagen Docker, actualizarla en Minikube y reiniciar los Pods.
- Minikube está diseñado para desarrollo y pruebas, no para entornos escalables.

---

## ADR 003

### Bases de datos separadas por servicio con volúmenes dedicados para persistencia

**Estado:** `Accepted`

### Contexto

Los requerimientos establecen que cada microservicio debe tener su propia base de datos para demostrar la autonomía del sistema. Como los contenedores Docker pierden datos al reiniciarse, es necesario garantizar la persistencia de la información.

### Decisión

Cada base de datos usará un **PersistentVolumeClaim (PVC)** que solicita almacenamiento persistente en Minikube. Las capacidades asignadas son:

| Servicio | Almacenamiento | Justificación |
|----------|---------------|---------------|
| Usuarios | 1 GB | Volumen de datos estable |
| Productos | 1 GB | Volumen de datos estable |
| Pedidos | 2 GB | Mayor tasa de crecimiento por transacciones |

Los datos se almacenarán en el volumen montado en una ruta concreta dentro de cada contenedor de base de datos. Se utilizará **PostgreSQL** como motor de base de datos relacional, dado el conocimiento del equipo y la naturaleza relacional de los datos.

### Consecuencias

####  Positivas

- Cumple con el requisito de que cada servicio gestiona su propia base de datos (independencia de datos).
- Los volúmenes persistentes evitan la pérdida de datos cuando los contenedores o Pods se reinician o eliminan.
- La asignación de 2 GB a Pedidos anticipa un mayor volumen sin desperdiciar recursos en los otros servicios.
- Los PVCs de Minikube utilizan el almacenamiento local del nodo, suficiente para un MVP.
- Separar las bases de datos permite escalar cada servicio de forma independiente en el futuro.

####  Negativas

- Implica mayor consumo de recursos físicos.
- Si el volumen se corrompe, los datos de las tres bases de datos se pierden (a menos que se configuren backups).
- Mayor complejidad de orquestación: se deben crear 3 deployments de bases de datos y 4 servicios (incluyendo el API Gateway).