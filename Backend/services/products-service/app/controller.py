from fastapi import APIRouter

from .models import CreateProductRequest, UpdateProductRequest, UpdateStockRequest
from .repository import ProductRepository
from .service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
service = ProductService(ProductRepository())

# Endpoint para obtener la lista de productos
@router.get("")
def list_products():
    return service.list_products()

# Endpoint para obtener un producto por su ID
@router.get("/{product_id}")
def get_product(product_id: str):
    return service.get_product(product_id)

# Endpoint para crear un nuevo producto
@router.post("")
def create_product(payload: CreateProductRequest):
    return service.create_product(payload)

# Endpoint para actualizar un producto existente (toda la info o parcial)
@router.put("/{product_id}")
def update_product(product_id: str, payload: UpdateProductRequest):
    return service.update_product(product_id, payload)

# Endpoint para eliminar un producto
@router.delete("/{product_id}")
def delete_product(product_id: str):
    service.delete_product(product_id)
    return {"message": "Product deleted"}

# Endpoint para descontar stock de un producto
@router.put("/{product_id}/stock")
def discount_stock(product_id: str, payload: UpdateStockRequest):
    return service.discount_stock(product_id, payload)
