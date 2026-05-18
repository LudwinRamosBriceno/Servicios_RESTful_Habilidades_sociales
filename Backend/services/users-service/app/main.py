from fastapi import FastAPI

from .controller import router as user_router
from .messaging import start_consumer
from .repository import UserRepository
from .service import UserService, EVENT_INVENTORY_CONFIRMED

# Aplicacion principal del microservicio de usuarios.
app = FastAPI(title="NovaLink Users Service", version="1.0.0")
# Registra endpoints funcionales bajo el prefijo definido en el controller.
app.include_router(user_router)


@app.on_event("startup")
def start_event_consumers() -> None:
    """
    Arranca consumidores de eventos para asignar habilidades.
    En este caso, escucha eventos de inventario confirmado para otorgar puntos al usuario.
    """
    service = UserService(UserRepository())

    def _handle_inventory_confirmed(payload: dict) -> None:
        if payload.get("event_type") != EVENT_INVENTORY_CONFIRMED:
            return
        service.process_inventory_confirmed(payload)

    start_consumer(
        queue_name="users-service",
        routing_keys=[EVENT_INVENTORY_CONFIRMED],
        handler=_handle_inventory_confirmed,
    )


@app.get("/health")
def healthcheck():
    """
    Endpoint para verificar disponibilidad del servicio.
    """
    return {"status": "ok", "service": "users-service"}
