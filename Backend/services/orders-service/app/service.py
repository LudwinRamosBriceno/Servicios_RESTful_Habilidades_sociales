import uuid

from fastapi import HTTPException, status

from .clients.notification_http_client import NotificationHttpClient
from .clients.product_http_client import ProductHttpClient
from .clients.user_http_client import UserHttpClient
from .models import Order, OrderRequest, OrderResult, OrderStatus, utc_now_iso
from .repository import OrderRepository


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        user_client: UserHttpClient,
        product_client: ProductHttpClient,
        notification_client: NotificationHttpClient,
    ) -> None:
        self._repository = repository
        self._user_client = user_client
        self._product_client = product_client
        self._notification_client = notification_client

    def create_order(self, payload: OrderRequest) -> tuple[OrderResult, int]:
        if payload.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantity must be > 0")

        self._user_client.get_user(payload.userId)
        product = self._product_client.get_product(payload.productId)

        if product.stock < payload.quantity:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient stock")

        self._product_client.discount_stock(payload.productId, payload.quantity)

        xp_gained = product.xpPoints * payload.quantity
        order = Order(
            id=f"ord_{uuid.uuid4().hex[:8]}",
            user_id=payload.userId,
            product_id=payload.productId,
            quantity=payload.quantity,
            status=OrderStatus.COMPLETED,
            xp_gained=xp_gained,
            created_at=utc_now_iso(),
        )
        self._repository.create(order)

        already_owned = self._user_client.add_skill(payload.userId, payload.productId, xp_gained)
        self._notification_client.send_order_completed(order.id, payload.userId, product.name, xp_gained)

        http_status = status.HTTP_202_ACCEPTED if already_owned else status.HTTP_201_CREATED
        message = "Skill already owned, XP added" if already_owned else "Order completed successfully"

        return self._to_result(order, message), http_status

    def get_order(self, order_id: str) -> OrderResult:
        order = self._repository.find_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return self._to_result(order, "Order fetched")

    def get_orders_by_user(self, user_id: str) -> list[OrderResult]:
        return [self._to_result(order, "Order fetched") for order in self._repository.find_by_user_id(user_id)]

    @staticmethod
    def _to_result(order: Order, message: str) -> OrderResult:
        return OrderResult(
            orderId=order.id,
            userId=order.user_id,
            productId=order.product_id,
            status=order.status,
            message=message,
            xpGained=order.xp_gained,
            createdAt=order.created_at,
        )
