from pydantic import BaseModel


# Modelo para un producto
class Product(BaseModel):
    id: str
    name: str
    description: str
    stock: int
    active: bool = True

# Modelo para las solicitudes de creación de producto
class CreateProductRequest(BaseModel):
    id: str | None = None
    name: str
    description: str
    stock: int
    active: bool = True

# Modelo para las solicitudes de actualización de producto
class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    stock: int | None = None
    active: bool | None = None

# Modelo para las solicitudes de actualización de stock
class UpdateStockRequest(BaseModel):
    quantity: int

# Modelo para las respuestas de producto (respuesta del servicio al cliente)
class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    stock: int
    active: bool
