"""Controlador de FastAPI para rutas de órdenes."""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .auth import AuthenticatedUser, get_current_user
from .db import SessionLocal
from .models import OrderRequest
from .repository import OrderRepository
from .service import OrderService

# Enrutador de FastAPI para manejar las rutas relacionadas con las órdenes.
router = APIRouter(prefix="/orders", tags=["orders"])

# Inicialización del servicio de órdenes con su repositorio.
repository = OrderRepository(
    SessionLocal
)  # se le pasa la sesión de base de datos al repositorio
service = OrderService(repository=repository)


@router.post("")
def create_order(
    payload: OrderRequest,
    response: Response,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """Ruta para crear una nueva orden."""
    if payload.userId != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no autorizado"
        )

    result, http_status = service.create_order(payload, current_user.user_id)
    response.status_code = http_status
    return result


@router.get("/{order_id}")
def get_order(order_id: str):
    """Ruta para obtener los detalles de una orden por ID."""
    return service.get_order(order_id)


@router.get("/user/{user_id}")
def get_user_orders(user_id: str):
    """Ruta para obtener órdenes asociadas a un usuario por ID."""
    return service.get_orders_by_user(user_id)
