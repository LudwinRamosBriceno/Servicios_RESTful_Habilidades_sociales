import uuid

from fastapi import HTTPException, status

from .clients.notification_http_client import NotificationHttpClient
from .clients.product_http_client import ProductHttpClient
from .clients.user_http_client import UserHttpClient
from .models import Order, OrderRequest, OrderResult, OrderStatus, utc_now_iso
from .repository import OrderRepository


class OrderService:
    """
    Servicio de órdenes que maneja la lógica de negocio relacionada con la creación y recuperación de órdenes.
    Utiliza un repositorio para almacenar las órdenes y clientes HTTP para comunicarse con los servicios de usuarios, 
    productos y notificaciones.
    Proporciona métodos para crear una orden, obtener una orden por su ID, y obtener todas las órdenes asociadas 
    a un usuario específico.
    """

    def __init__(
        self,
        repository: OrderRepository,
        user_client: UserHttpClient,
        product_client: ProductHttpClient,
        notification_client: NotificationHttpClient,
    ) -> None:
        """
        Inicializa el servicio de órdenes con el repositorio y los clientes HTTP proporcionados.
        Argumentos:
            repository (OrderRepository): Repositorio para almacenar las órdenes.
            user_client (UserHttpClient): Cliente HTTP para comunicarse con el servicio de usuarios.
            product_client (ProductHttpClient): Cliente HTTP para comunicarse con el servicio de productos.
            notification_client (NotificationHttpClient): Cliente HTTP para comunicarse con el servicio de notificaciones.
        """
        self._repository = repository
        self._user_client = user_client
        self._product_client = product_client
        self._notification_client = notification_client

    def create_order(self, payload: OrderRequest) -> tuple[OrderResult, int]:
        """
        Crea una nueva orden, manejando la lógica de negocio relacionada con la validación de la solicitud,
        la verificación de la existencia del usuario y el producto, la actualización del stock del producto,
        la creación de la orden, la adición de puntos de habilidad al usuario, y el envío de una notificación 
        de orden completada.
        Argumentos:
            payload (OrderRequest): Datos de la orden a crear, incluyendo el ID del usuario, el ID del producto y la cantidad.
        Retorna:
            tuple[OrderResult, int]: El resultado de la creación de la orden y el código de estado HTTP correspondiente.
        """
        if payload.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La cantidad debe ser mayor que 0")

        self._user_client.get_user(payload.userId)
        product = self._product_client.get_product(payload.productId)

        if product.stock < payload.quantity:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Stock insuficiente")

        self._product_client.discount_stock(payload.productId, payload.quantity)

        skill_points = payload.quantity
        order = Order(
            id=f"ord_{uuid.uuid4().hex[:8]}",
            user_id=payload.userId,
            product_id=payload.productId,
            quantity=payload.quantity,
            status=OrderStatus.COMPLETED,
            skill_points=skill_points,
            created_at=utc_now_iso(),
        )
        self._repository.create(order)

        already_owned = self._user_client.add_skill(payload.userId, payload.productId, skill_points)
        self._notification_client.send_order_completed(order.id, payload.userId, product.name, skill_points)

        http_status = status.HTTP_202_ACCEPTED if already_owned else status.HTTP_201_CREATED
        message = "La habilidad ya estaba asignada, se sumaron puntos" if already_owned else "Orden completada exitosamente"

        return self._to_result(order, message), http_status

    def get_order(self, order_id: str) -> OrderResult:
        """
        Obtiene los detalles de una orden específica por su ID, manejando la lógica de negocio relacionada con la
        recuperación de la orden y la generación del resultado.
        Argumentos:
            order_id (str): ID de la orden a recuperar.
        Retorna:
            OrderResult: El resultado de la recuperación de la orden, que incluye detalles de la orden y un mensaje.
        """
        order = self._repository.find_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
        return self._to_result(order, "Orden obtenida")

    def get_orders_by_user(self, user_id: str) -> list[OrderResult]:
        """
        Obtiene todas las órdenes asociadas a un usuario específico, manejando la lógica de negocio 
        relacionada con la recuperación de las órdenes y la generación del resultado.
        Argumentos:
            user_id (str): ID del usuario.
        Retorna:
            list[OrderResult]: Una lista de resultados de las órdenes asociadas al usuario.
        """
        return [self._to_result(order, "Orden obtenida") for order in self._repository.find_by_user_id(user_id)]

    @staticmethod
    def _to_result(order: Order, message: str) -> OrderResult:
        """
        Convierte una orden en un resultado de orden, incluyendo un mensaje personalizado.
        Argumentos:
            order (Order): La orden a convertir.
            message (str): El mensaje personalizado para incluir en el resultado.
        Retorna:
            OrderResult: El resultado de la orden con el mensaje incluido.
        """
        return OrderResult(
            orderId=order.id,
            userId=order.user_id,
            productId=order.product_id,
            status=order.status,
            message=message,
            skillPoints=order.skill_points,
            createdAt=order.created_at,
        )
