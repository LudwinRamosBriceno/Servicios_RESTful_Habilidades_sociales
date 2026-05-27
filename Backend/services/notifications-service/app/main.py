"""Servicio de notificaciones para crear y enviar notificaciones."""

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .messaging import start_consumer

EVENT_USER_UPDATED = "usuario.actualizado"

app = FastAPI(title="NovaLink Notifications Service", version="1.0.0")


class NotificationRequest(BaseModel):
    """Modelo para la solicitud de creación de una notificación."""

    model_config = ConfigDict(populate_by_name=True)

    orderId: str
    userId: str
    skillName: str
    skillPoints: int
    issued_by: str = Field(alias="issued_by")


@app.post("/notifications")
def create_notification(payload: NotificationRequest):
    """Endpoint para crear una notificación."""
    print(
        "[NOTIFICATION] "
        f"order={payload.orderId} user={payload.userId} "
        f"skill={payload.skillName} points={payload.skillPoints} "
        f"issued_by={payload.issued_by}"
    )
    return {"message": "Notification processed", "orderId": payload.orderId}


@app.on_event("startup")
def start_event_consumers() -> None:
    """Arranca consumidores de eventos para generar notificaciones."""

    def _handle_user_updated(payload: dict) -> None:
        if payload.get("event_type") != EVENT_USER_UPDATED:
            return
        data = payload.get("data", {})
        print(
            "[NOTIFICATION] "
            f"order={data.get('orderId')} user={data.get('userId')} "
            f"skill={data.get('productName')} points={data.get('skillPoints')} "
            "issued_by=events",
            flush=True,
        )

    start_consumer(
        queue_name="notifications-service",
        routing_keys=[EVENT_USER_UPDATED],
        handler=_handle_user_updated,
    )


@app.get("/notifications/health")
def healthcheck():
    """Ruta de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "notifications-service"}
