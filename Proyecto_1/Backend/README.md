# NovaLink

Plataforma de microservicios REST para gestionar habilidades sociales como productos.

## Servicios

- users-service:8001
- products-service:8002
- orders-service:8000
- notifications-service:8003

## Acceso local recomendado en Windows con driver Docker:

```bash
kubectl port-forward service/api-gateway 8080:8080
```

