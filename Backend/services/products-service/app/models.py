from pydantic import BaseModel

class Product(BaseModel):
    """
    Modelo de datos para representar un producto, incluyendo su ID, nombre, descripción, stock y estado activo.
    """
    id: str
    name: str
    description: str
    stock: int
    active: bool = True

class CreateProductRequest(BaseModel):
    """
    Modelo para las solicitudes de creación de producto
    """
    id: str | None = None
    name: str
    description: str
    stock: int
    active: bool = True

class UpdateProductRequest(BaseModel):
    """
    Modelo para las solicitudes de actualización de producto
    """
    name: str | None = None
    description: str | None = None
    stock: int | None = None
    active: bool | None = None

class UpdateStockRequest(BaseModel):
    """
    Modelo para las solicitudes de actualización de stock
    """
    quantity: int

class ProductResponse(BaseModel):
    """
    Modelo para las respuestas de producto (respuesta del servicio al cliente)
    """
    id: str
    name: str
    description: str
    stock: int
    active: bool
