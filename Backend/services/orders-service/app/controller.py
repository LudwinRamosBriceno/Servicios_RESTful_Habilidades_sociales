import os

from fastapi import APIRouter, Response

from .clients.notification_http_client import NotificationHttpClient
from .clients.product_http_client import ProductHttpClient
from .clients.user_http_client import UserHttpClient
from .models import OrderRequest
from .repository import OrderRepository
from .service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

users_service_url = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
products_service_url = os.getenv("PRODUCTS_SERVICE_URL", "http://products-service:8002")
notifications_service_url = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8003")

service = OrderService(
    repository=OrderRepository(),
    user_client=UserHttpClient(users_service_url),
    product_client=ProductHttpClient(products_service_url),
    notification_client=NotificationHttpClient(notifications_service_url),
)


@router.post("")
def create_order(payload: OrderRequest, response: Response):
    result, http_status = service.create_order(payload)
    response.status_code = http_status
    return result


@router.get("/{order_id}")
def get_order(order_id: str):
    return service.get_order(order_id)


@router.get("/user/{user_id}")
def get_user_orders(user_id: str):
    return service.get_orders_by_user(user_id)
