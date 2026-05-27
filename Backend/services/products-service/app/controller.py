"""Controlador de FastAPI para rutas relacionadas con productos."""

from fastapi import APIRouter

from .db import SessionLocal
from .models import CreateProductRequest, UpdateProductRequest, UpdateStockRequest
from .repository import ProductRepository
from .service import ProductService

# Se define el router con la url base del servicio
router = APIRouter(prefix="/products", tags=["products"])

# Inicialización del servicio de productos con su repositorio.
repository = ProductRepository(
    SessionLocal
)  # se le pasa la sesión de base de datos al repositorio
service = ProductService(repository=repository)


@router.get("")
def list_products():
    """Obtiene la lista de todos los productos."""
    return service.list_products()


@router.get("/{product_id}")
def get_product(product_id: str):
    """Obtiene los detalles de un producto por su ID."""
    return service.get_product(product_id)


# Endpoint para crear un nuevo producto
@router.post("")
def create_product(payload: CreateProductRequest):
    """Crea un nuevo producto."""
    return service.create_product(payload)


@router.put("/{product_id}")
def update_product(product_id: str, payload: UpdateProductRequest):
    """Actualiza un producto existente por su ID."""
    return service.update_product(product_id, payload)


@router.delete("/{product_id}")
def delete_product(product_id: str):
    """Elimina un producto por su ID."""
    service.delete_product(product_id)
    return {"message": "Product deleted"}


@router.put("/{product_id}/stock")
def discount_stock(product_id: str, payload: UpdateStockRequest):
    """Descuenta stock de un producto por su ID."""
    return service.discount_stock(product_id, payload)
