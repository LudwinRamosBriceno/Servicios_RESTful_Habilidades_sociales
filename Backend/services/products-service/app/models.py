from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    description: str
    stock: int
    active: bool = True


class CreateProductRequest(BaseModel):
    id: str | None = None
    name: str
    description: str
    stock: int
    active: bool = True


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    stock: int | None = None
    active: bool | None = None


class UpdateStockRequest(BaseModel):
    quantity: int

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    stock: int
    active: bool
