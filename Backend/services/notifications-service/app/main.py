from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="NovaLink Notifications Service", version="1.0.0")


class NotificationRequest(BaseModel):
    """
    Modelo para la solicitud de creación de una notificación.
    """
    model_config = ConfigDict(populate_by_name=True)

    orderId: str
    userId: str
    skillName: str
    skillPoints: int
    issued_by: str = Field(alias="issued_by")


@app.post("/notifications")
def create_notification(payload: NotificationRequest):
    """
    Endpoint para crear una notificación.
    """
    print(
        "[NOTIFICATION] "
        f"order={payload.orderId} user={payload.userId} "
        f"skill={payload.skillName} points={payload.skillPoints} "
        f"issued_by={payload.issued_by}"
    )
    return {"message": "Notification processed", "orderId": payload.orderId}


@app.get("/notifications/health")
def healthcheck():
    """
    Ruta de salud para verificar que el servicio de notificaciones está funcionando correctamente.
    """
    return {"status": "ok", "service": "notifications-service"}
