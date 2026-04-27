import os

from fastapi import APIRouter, Response

from .clients.notification_http_client import NotificationHttpClient
from .clients.product_http_client import ProductHttpClient
from .clients.user_http_client import UserHttpClient
from .models import OrderRequest
from .repository import OrderRepository
from .service import OrderService

# Enrutador de FastAPI para manejar las rutas relacionadas con las órdenes. 
router = APIRouter(prefix="/orders", tags=["orders"])

# Configuración de los clientes HTTP para comunicarse con los servicios de usuarios, productos y notificaciones,
# utilizando las URLs obtenidas de las variables de entorno o valores predeterminados.
users_service_url = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
products_service_url = os.getenv("PRODUCTS_SERVICE_URL", "http://products-service:8002")
notifications_service_url = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8003")

# Inicialización del servicio de órdenes, proporcionando el repositorio y los clientes HTTP configurados.
service = OrderService(
    repository=OrderRepository(),
    user_client=UserHttpClient(users_service_url),
    product_client=ProductHttpClient(products_service_url),
    notification_client=NotificationHttpClient(notifications_service_url),
)

@router.post("")
def create_order(payload: OrderRequest, response: Response):
    """
    Ruta para crear una nueva orden, recibiendo los datos de la orden en el cuerpo de la solicitud.
    El servicio de órdenes se encarga de procesar la creación de la orden, manejar la lógica de negocio, 
    y devolver el resultado junto con el código de estado HTTP adecuado.
    Argumentos:
        payload (OrderRequest): Datos de la orden a crear, incluyendo el ID del usuario, el ID 
        del producto y la cantidad.
        response (Response): Objeto de respuesta de FastAPI para configurar el código de estado HTTP de la respuesta.
    Retorna:
        El resultado de la creación de la orden, que puede incluir detalles de la orden creada o un mensaje de error.
    """
    result, http_status = service.create_order(payload)
    response.status_code = http_status
    return result


@router.get("/{order_id}")
def get_order(order_id: str):
    """
    Ruta para obtener los detalles de una orden específica por su ID. 
    El servicio de órdenes se encarga de recuperar la información de la orden, manejar la lógica 
    de negocio, y devolver el resultado junto con el código de estado HTTP adecuado.
    Argumentos:
        order_id (str): ID de la orden a recuperar.
    Retorna:
        El resultado de la recuperación de la orden, que puede incluir detalles de la orden o un mensaje de error.
    """
    return service.get_order(order_id)


@router.get("/user/{user_id}")
def get_user_orders(user_id: str):
    """
    Ruta para obtener todas las órdenes asociadas a un usuario específico por su ID.
    El servicio de órdenes se encarga de recuperar la información de las órdenes del usuario, manejar la lógica 
    de negocio, y devolver el resultado junto con el código de estado HTTP adecuado.
    Argumentos:
        user_id (str): ID del usuario cuyas órdenes se desean recuperar.
    Retorna:
        El resultado de la recuperación de las órdenes del usuario, que puede incluir una lista de órdenes o un mensaje de error.
    """
    return service.get_orders_by_user(user_id)
