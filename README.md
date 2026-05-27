# NovaLink

> **Estudiantes:** Meibel Ceciliano Picado · Carlos Contreras Luna · Byron Mata Fuentes · Ludwin Ramos Briceño

Plataforma de microservicios REST para gestionar habilidades sociales como productos.

## Finalidad del Proyecto

NovaLink es una plataforma distribuida orientada a la gestión de habilidades sociales mediante una arquitectura de microservicios basada en eventos (Event-Driven Architecture).

El objetivo principal del proyecto es demostrar el desacoplamiento entre servicios utilizando RabbitMQ como broker de mensajería, Kubernetes para orquestación y comunicación asincrónica entre componentes independientes.

El sistema permite:

- Gestionar usuarios y habilidades sociales.
- Consultar y registrar productos/habilidades disponibles.
- Procesar pedidos de habilidades mediante eventos asincrónicos.
- Actualizar perfiles de usuario automáticamente tras la confirmación de un pedido.
- Generar notificaciones desacopladas mediante consumidores de eventos.
- Implementar autenticación centralizada basada en sesiones HTTP-only.
- Registrar solicitudes asincrónicas y sus estados mediante un API Gateway (Backend) con soporte SSE.

Además, el proyecto busca aplicar principios de:

- Arquitectura orientada a eventos (EDA).
- Arquitectura en capas.
- Desacoplamiento entre microservicios.
- Persistencia independiente por servicio.
- Orquestación con Kubernetes.
- Resiliencia básica mediante colas de mensajería.
- Automatización y despliegue containerizado.

## Tecnologías utilizadas

- Kubernetes (Minikube)
- Docker
- Python y FastAPI
- PostgreSQL
- React + Vite y Javascript
- SQLAlchemy y Alembic

## Estado del Proyecto

Actualmente el sistema implementa lo siguiente:

### Componentes principales

- API Gateway (Backend) con comunicación SSE.
- Auth Service con autenticación mediante cookies HTTP-only.
- Users Service.
- Products Service.
- Orders Service.
- Notifications Service.
- RabbitMQ como broker de eventos.
- Bases de datos PostgreSQL independientes por servicio.
- Orquestación mediante Kubernetes (Minikube).

### Funcionalidades implementadas

- Flujo completo de autenticación y validación de sesión.
- Procesamiento asincrónico de pedidos mediante RabbitMQ.
- Comunicación desacoplada entre servicios mediante eventos.
- Actualización automática de habilidades del usuario.
- Notificaciones basadas en eventos.
- Persistencia de solicitudes asincrónicas en `gateway-db`.
- Streaming de respuestas al frontend mediante SSE.
- Recuperación básica ante caída temporal de microservicios consumidores.
- Despliegue funcional en Kubernetes mediante Deployments y Services.

## Diagramas C4 y secuencia


### Diagrama de Contexto
<img src="Diagramas/Diagrama%20de%20Contexto.svg" alt="Diagrama de Contexto" width="700px" />

### Diagrama de Contenedores
<img src="Diagramas/Diagrama%20de%20Contenedores.svg" alt="Diagrama de Contenedores" width="700px" />

### Diagrama de Componentes
<img src="Diagramas/Diagrama%20de%20Componentes.svg" alt="Diagrama de Componentes" width="700px" />

### Diagrama de Secuencia
<img src="Diagramas/Diagrama de Secuencia.svg" alt="Diagrama de Secuencia" width="700px" />


### Diagrama de arquitectura EDA

El siguiente link lo redirige al mapa de Producers y Consumers y a la Topología de Conexiones especificadas por servicio.

[Mapeo EDA](/Diagramas/Mapeo_EDA.md)

---

# Manual de API RESTful

[Manual de los endpoints expuestos por el API Gateway (Backend) en formato OpenAPI](/Backend/OpenAPI/api-gateway.openapi.json)

# Architecture Decision Records

---

## Tabla de contenidos

- [ADR 001 — Arquitectura orientada completamente a eventos para comunicación entre servicios](#adr-001)
- [ADR 002 — Kubernetes (Minikube) para orquestación de contenedores](#adr-002)
- [ADR 003 — Bases de datos separadas con volúmenes dedicados](#adr-003)
- [ADR 004 — Uso de cookie `HttpOnly` para `session_id` e invalidación de sesiones tras caída o reinicio del `auth-service`](#adr-004)

---

## ADR 001

### Arquitectura orientada completamente a eventos para comunicación entre servicios

**Estado:** `Accepted`

### Contexto

Durante la fase de diseño del proyecto, se realizó una consulta formal sobre el alcance esperado del uso de mensajería y eventos dentro de la arquitectura de microservicios. La interpretación confirmada inicialmente indicó que la comunicación entre servicios debía implementarse utilizando eventos y colas de mensajería como mecanismo principal de interacción.

Con base en dicha aclaración, el sistema fue diseñado bajo un enfoque completamente orientado a eventos, incluyendo operaciones tradicionalmente síncronas como consultas de información (`GET`), las cuales fueron modeladas mediante intercambio de eventos y respuestas asincrónicas.

Posteriormente, durante sesión de dudas en vivo del proyecto, se aclaró que las operaciones `GET` no necesariamente requerían implementarse mediante eventos y que podían resolverse mediante comunicación HTTP síncrona. Sin embargo, dado que la arquitectura ya se encontraba implementada y funcional bajo el modelo orientado a eventos, se decidió mantener el diseño original justificando sus beneficios arquitectónicos y académicos.

### Decisión

Toda la comunicación entre microservicios se implementará mediante RabbitMQ y eventos asincrónicos, incluyendo:

- Operaciones de creación y actualización (`POST`, `PUT`, etc.).
- Consultas de información equivalentes a operaciones `GET`.
- Intercambio de respuestas mediante colas de respuesta temporales o patrones request-response asincrónicos.

El API Gateway (Backend) actúa como punto de entrada único y coordina la publicación y recepción de eventos hacia los servicios internos.

### Consecuencias

#### Positivas

- Se mantiene una arquitectura uniforme basada completamente en eventos.
- Se reduce el acoplamiento directo entre servicios.
- Permite demostrar el uso práctico de mensajería asincrónica más allá de eventos simples.
- Facilita tolerancia a fallos temporales mediante desacoplamiento temporal.
- Cumple con la interpretación inicial validada de los requerimientos del proyecto.

#### Negativas

- Incrementa considerablemente la complejidad para operaciones simples de consulta.
- Introduce mayor latencia respecto a consultas HTTP directas.
- El patrón request-response asincrónico requiere manejo adicional de correlación y timeouts.
- No representa la implementación más común para operaciones `GET` en arquitecturas de microservicios tradicionales.
- La depuración y trazabilidad de consultas resulta más compleja.

---

## ADR 002

### Uso de Kubernetes (Minikube) para orquestación de contenedores

**Estado:** `Accepted`

### Contexto

Se requiere que todos los servicios del sistema sean containerizados con Docker y ejecutados en un entorno que simule una infraestructura cloud real. El sistema está compuesto por múltiples microservicios y componentes de soporte:

- API Gateway (Backend)
- Auth Service
- Users Service
- Products Service
- Orders Service
- Notifications Service
- RabbitMQ
- Bases de datos PostgreSQL independientes

Se debe orquestar la infraestructura utilizando Kubernetes, específicamente **Minikube**, mediante manifiestos YAML (`Deployment`, `Service` y `PersistentVolumeClaim`) para garantizar despliegue, descubrimiento de servicios y resiliencia básica.

### Decisión

Se utilizará **Minikube** como clúster Kubernetes local de un solo nodo para desplegar toda la plataforma:

- Cada microservicio y base de datos se desplegará mediante un **Deployment**.
- Los microservicios internos y bases de datos se expondrán mediante **Services tipo `ClusterIP`**.
- El API Gateway (Backend) se expondrá mediante un **Service tipo `NodePort`** para permitir acceso desde el frontend y herramientas externas como Postman.
- RabbitMQ se desplegará como servicio interno del clúster para gestionar comunicación asincrónica basada en eventos.
- Kubernetes manejará el reinicio automático de Pods en caso de fallos.
- Los Services de Kubernetes proveerán descubrimiento de servicios mediante DNS interno del clúster.

### Consecuencias

#### Positivas

- Cumple con el requisito de utilizar Kubernetes y Minikube para orquestación.
- Permite desplegar múltiples servicios desacoplados dentro del mismo clúster.
- Kubernetes proporciona descubrimiento de servicios mediante DNS interno.
- RabbitMQ y las bases de datos pueden comunicarse internamente sin exponer puertos externos innecesarios.
- Los Deployments permiten recuperación automática de Pods ante fallos.
- Los manifiestos YAML pueden adaptarse posteriormente a un entorno cloud real.
- Facilita pruebas de resiliencia y desacoplamiento entre servicios.

#### Negativas

- El equipo debe aprender conceptos de Kubernetes (`Pods`, `Deployments`, `Services`, `PVCs`, `kubectl`).
- Mayor consumo de recursos locales debido a Minikube y múltiples contenedores simultáneos.
- Cada modificación requiere reconstrucción de imágenes Docker y reinicio de Pods.
- Minikube está orientado a desarrollo y pruebas, no a producción escalable.
- El debugging distribuido entre múltiples Pods y RabbitMQ aumenta la complejidad operativa.

---

## ADR 003

### Bases de datos separadas por servicio con persistencia mediante volúmenes

**Estado:** `Accepted`

### Contexto

La arquitectura del sistema sigue un enfoque de microservicios desacoplados, donde cada servicio es responsable de sus propios datos. Además, el sistema utiliza comunicación asincrónica mediante eventos, por lo que se requiere persistencia tanto para los datos de negocio como para el seguimiento de solicitudes procesadas por el API Gateway (Backend).

Debido a que los contenedores Docker pierden sus datos al reiniciarse, es necesario utilizar almacenamiento persistente dentro del clúster Kubernetes.

### Decisión

Cada microservicio mantendrá su propia base de datos PostgreSQL independiente utilizando un **PersistentVolumeClaim (PVC)** para persistencia de datos en Minikube.

Las bases de datos definidas son:

| Servicio | Base de Datos | Almacenamiento |
|----------|---------------|---------------|
| Users Service | users-db | 1 GB |
| Products Service | products-db | 1 GB |
| Orders Service | orders-db | 2 GB |
| API Gateway (Backend) | gateway-db | 1 GB |

Los volúmenes persistentes serán montados dentro de cada contenedor PostgreSQL para evitar pérdida de información ante reinicios de Pods o contenedores.

El `gateway-db` será utilizado para registrar solicitudes asincrónicas, incluyendo:

- requestId
- estado (`PENDING`, `COMPLETED`, `FAILED`)
- respuestas
- errores
- timestamps

### Consecuencias

#### Positivas

- Cada microservicio mantiene independencia de datos y bajo acoplamiento.
- Los datos persisten aunque los Pods sean reiniciados o recreados.
- El API Gateway (Backend) puede almacenar el estado de solicitudes asincrónicas y correlacionar respuestas provenientes de RabbitMQ.
- Permite escalar servicios y bases de datos de forma independiente en el futuro.
- PostgreSQL es un motor conocido por el equipo y adecuado para relaciones transaccionales.

#### Negativas

- Incrementa el consumo de almacenamiento y recursos del clúster.
- El manejo de múltiples bases de datos aumenta la complejidad operativa.
- Las sesiones actuales del Auth Service permanecen en memoria y no sobreviven reinicios del servicio.
- Los PVCs de Minikube utilizan almacenamiento local, por lo que no existe tolerancia real a fallos físicos del nodo.
- No existe actualmente un mecanismo automatizado de backup o replicación.

---

## ADR 004

### Uso de cookie `HttpOnly` para manejo de sesiones centralizadas en el `auth-service`

**Estado:** `Accepted`

### Contexto

Inicialmente, el sistema utilizaba autenticación basada en tokens enviados por el cliente en cada solicitud. Posteriormente, se identificó que dicho enfoque exponía las credenciales de autenticación al entorno del navegador, aumentando el riesgo ante ataques XSS o accesos desde scripts del cliente.

Adicionalmente, la arquitectura del sistema ya dependía de un `auth-service` centralizado encargado de validar identidades antes de permitir operaciones protegidas en el API Gateway (Backend). Debido a esto, se decidió adoptar un modelo de sesiones centralizadas utilizando cookies `HttpOnly`.

Actualmente, las sesiones activas se almacenan temporalmente en memoria dentro del `auth-service`. Por esta razón, si el servicio se reinicia o falla, las sesiones activas se pierden y los usuarios deben autenticarse nuevamente.

### Decisión

- El sistema utilizará autenticación basada en sesiones centralizadas gestionadas por el `auth-service`.
- El cliente recibirá únicamente un identificador de sesión (`session_id`) almacenado en una cookie `HttpOnly`.
- La cookie no contendrá información sensible del usuario ni tokens JWT.
- La información de autenticación permanecerá almacenada únicamente en memoria dentro del `auth-service`.
- El API Gateway (Backend) validará cada solicitud protegida consultando al `auth-service` mediante el endpoint de validación de sesión.
- Si el `auth-service` se reinicia o falla, las sesiones almacenadas en memoria serán invalidadas automáticamente.

### Consecuencias

#### Positivas

- Se reduce la exposición de credenciales frente a ataques XSS al utilizar cookies `HttpOnly`.
- El cliente no necesita almacenar tokens en `localStorage` o `sessionStorage`.
- El control de sesiones y autenticación permanece centralizado en el `auth-service`.
- El cierre de sesión puede invalidarse inmediatamente desde el servidor.
- El navegador maneja automáticamente el envío de cookies en solicitudes autenticadas.

#### Negativas

- Las sesiones activas se pierden si el `auth-service` se reinicia o falla.
- El API Gateway (Backend) depende del `auth-service` para validar autenticación en cada solicitud protegida.
- No existe persistencia distribuida de sesiones; actualmente las sesiones viven únicamente en memoria.
- La experiencia de usuario puede verse afectada durante despliegues o reinicios del `auth-service`.
- Escalar múltiples instancias del `auth-service` requeriría un almacenamiento compartido de sesiones (por ejemplo Redis o base de datos distribuida).
