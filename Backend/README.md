# NovaLink

Plataforma de microservicios REST para gestionar habilidades sociales como productos.

## Servicios

- users-service:8001
- products-service:8002
- orders-service:8000
- notifications-service:8003

## Ejecutar en local con Docker Compose

```bash
docker compose up --build
```

## API Gateway

Se agrego un API Gateway basado en Nginx en `gateway/`.

Cuando levantas el stack con Docker Compose, el frontend o cualquier cliente puede usar un unico punto de entrada:

- `http://localhost:8080/api/orders`
- `http://localhost:8080/api/users`
- `http://localhost:8080/api/products`
- `http://localhost:8080/api/notifications`

Ejemplos:

- `GET http://localhost:8080/api/products`
- `POST http://localhost:8080/api/orders`
- `GET http://localhost:8080/api/users/{user_id}`

Health checks disponibles via gateway:

- `GET http://localhost:8080/api/orders-health`
- `GET http://localhost:8080/api/notifications-health`

## Endpoints principales

- POST /orders
- GET /orders/{id}
- GET /orders/user/{userId}

## Kubernetes

Los manifiestos se encuentran en `k8s/`.

Para desplegar el gateway en Minikube:

```bash
docker build -t api-gateway:latest ./gateway
minikube image load api-gateway:latest
kubectl apply -f k8s/api-gateway.yaml
```

Acceso local recomendado en Windows con driver Docker:

```bash
kubectl port-forward service/api-gateway 8080:8080
```
