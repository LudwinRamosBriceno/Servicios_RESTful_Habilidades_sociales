"""Servicio de órdenes para creación, consulta y eventos de dominio."""

import uuid

from fastapi import HTTPException, status
from app.messaging import publish_event
from app.models import Order, OrderRequest, OrderResult, OrderStatus, utc_now_iso
from app.repository import OrderRepository

# Eventos de dominio para el flujo EDA
EVENT_ORDER_CREATED = "pedido.creado"
EVENT_INVENTORY_CONFIRMED = "inventario.confirmado"
EVENT_INVENTORY_REJECTED = "inventario.rechazado"
EVENT_ORDER_STATUS_UPDATED = "orders.status.updated"


class OrderService:
    """Servicio de órdenes para creación y recuperación de órdenes."""

    def __init__(self, repository: OrderRepository) -> None:
        """Inicializa el servicio de órdenes con el repositorio."""
        self._repository = repository

    def create_order(
        self, payload: OrderRequest, user_id: str, request_id: str | None
    ) -> tuple[OrderResult, int]:
        """Crea una orden pendiente y publica el evento para el flujo EDA."""
        if payload.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La cantidad debe ser mayor que 0",
            )

        order = Order(
            id=f"ord_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            product_id=payload.productId,
            quantity=payload.quantity,
            status=OrderStatus.PENDING,
            skill_points=0,
            created_at=utc_now_iso(),
        )
        self._repository.create(order)
        publish_event(
            EVENT_ORDER_CREATED,
            {
                "requestId": request_id,
                "orderId": order.id,
                "userId": user_id,
                "productId": payload.productId,
                "quantity": payload.quantity,
            },
            correlation_id=order.id,
        )

        return (
            self._to_result(order, "Orden creada, pendiente de inventario"),
            status.HTTP_202_ACCEPTED,
        )

    def handle_inventory_confirmed(self, payload: dict) -> None:
        """Actualiza la orden a completada tras confirmacion de inventario."""
        data = payload.get("data", {})
        request_id = data.get("requestId")
        order_id = data.get("orderId")
        user_id = data.get("userId")
        if not order_id or not user_id:
            return
        skill_points = data.get("skillPoints", data.get("quantity", 0))
        self._repository.update_status(order_id, OrderStatus.COMPLETED, skill_points)
        publish_event(
            EVENT_ORDER_STATUS_UPDATED,
            {
                "requestId": request_id,
                "orderId": order_id,
                "userId": user_id,
                "status": OrderStatus.COMPLETED.value,
                "message": "Orden completada",
            },
            correlation_id=order_id,
        )

    def handle_inventory_rejected(self, payload: dict) -> None:
        """Actualiza la orden a rechazada tras rechazo de inventario."""
        data = payload.get("data", {})
        request_id = data.get("requestId")
        order_id = data.get("orderId")
        user_id = data.get("userId")
        if not order_id or not user_id:
            return
        self._repository.update_status(order_id, OrderStatus.REJECTED, 0)
        publish_event(
            EVENT_ORDER_STATUS_UPDATED,
            {
                "requestId": request_id,
                "orderId": order_id,
                "userId": user_id,
                "status": OrderStatus.REJECTED.value,
                "message": "Orden rechazada",
                "reason": data.get("reason"),
                "statusCode": data.get("statusCode"),
            },
            correlation_id=order_id,
        )

    def get_order(self, order_id: str) -> OrderResult:
        """Obtiene los detalles de una orden por su ID."""
        order = self._repository.find_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada"
            )
        return self._to_result(order, "Orden obtenida")

    def get_orders_by_user(self, user_id: str) -> list[OrderResult]:
        """Obtiene todas las órdenes asociadas a un usuario."""
        return [
            self._to_result(order, "Orden obtenida")
            for order in self._repository.find_by_user_id(user_id)
        ]

    @staticmethod
    def _to_result(order: Order, message: str) -> OrderResult:
        """Convierte una orden en un resultado de orden."""
        return OrderResult(
            orderId=order.id,
            userId=order.user_id,
            productId=order.product_id,
            status=order.status,
            message=message,
            skillPoints=order.skill_points,
            createdAt=order.created_at,
        )
