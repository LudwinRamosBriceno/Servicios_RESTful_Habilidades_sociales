"""Modelos de datos para órdenes, solicitudes y resultados."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel


def utc_now_iso() -> str:
    """Obtiene la fecha y hora actual en ISO 8601 UTC sin microsegundos."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class OrderStatus(str, Enum):
    """Enumeración para los posibles estados de una orden."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Order(BaseModel):
    """Modelo de datos para representar una orden."""

    id: str
    user_id: str
    product_id: str
    quantity: int
    status: OrderStatus
    skill_points: int
    created_at: str


class OrderRequest(BaseModel):
    """Modelo de datos para la solicitud de creación de una orden."""

    userId: str
    productId: str
    quantity: int


class OrderResult(BaseModel):
    """Modelo de datos para el resultado de una operación de orden."""

    orderId: str
    userId: str
    productId: str
    status: OrderStatus
    message: str
    skillPoints: int
    createdAt: str
