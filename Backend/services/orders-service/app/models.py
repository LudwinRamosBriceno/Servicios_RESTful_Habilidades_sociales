from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel


def utc_now_iso() -> str:
    """
    Obtiene la fecha y hora actual en formato ISO 8601 con zona horaria UTC, sin microsegundos, 
    y con el sufijo 'Z' para indicar UTC.
    Retorna:
        str: La fecha y hora actual en formato ISO 8601 con zona horaria UTC.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class OrderStatus(str, Enum):
    """
    Enumeración para representar los posibles estados de una orden.
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Order(BaseModel):
    """
    Modelo de datos para representar una orden, incluyendo su ID, ID del usuario, ID del producto, 
    cantidad, estado, puntos de experiencia ganados, y fecha de creación.
    """
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: OrderStatus
    xp_gained: int
    created_at: str


class OrderRequest(BaseModel):
    """
    Modelo de datos para representar la solicitud de creación de una orden.
    """
    userId: str
    productId: str
    quantity: int


class OrderResult(BaseModel):
    """
    Modelo de datos para representar el resultado de una operación relacionada con una orden.
    """
    orderId: str
    userId: str
    productId: str
    status: OrderStatus
    message: str
    xpGained: int
    createdAt: str


class UserDTO(BaseModel):
    """
    Modelo de datos para representar un usuario.
    """
    id: str
    name: str
    email: str


class ProductDTO(BaseModel):
    """
    Modelo de datos para representar un producto.
    """
    id: str
    name: str
    stock: int
    xpPoints: int
