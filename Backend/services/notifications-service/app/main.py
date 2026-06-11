from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

app = FastAPI(title="NovaLink Notifications Service", version="1.0.0")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


class NotificationRequest(BaseModel):
    orderId: str
    userId: str
    skillName: str
    skillPoints: int


@app.post("/notifications")
def create_notification(payload: NotificationRequest):
    print(
        "[NOTIFICATION] "
        f"order={payload.orderId} user={payload.userId} "
        f"skill={payload.skillName} points={payload.skillPoints}"
    )
    return {"message": "Notification processed", "orderId": payload.orderId}


@app.get("/notifications/health")
def healthcheck():
    return {"status": "ok", "service": "notifications-service"}
