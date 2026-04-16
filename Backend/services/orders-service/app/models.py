from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class Order(BaseModel):
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: OrderStatus
    xp_gained: int
    created_at: str


class OrderRequest(BaseModel):
    userId: str
    productId: str
    quantity: int


class OrderResult(BaseModel):
    orderId: str
    userId: str
    productId: str
    status: OrderStatus
    message: str
    xpGained: int
    createdAt: str


class UserDTO(BaseModel):
    id: str
    name: str
    email: str


class ProductDTO(BaseModel):
    id: str
    name: str
    stock: int
    xpPoints: int
