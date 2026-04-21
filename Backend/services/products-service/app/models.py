from pydantic import BaseModel


class Product(BaseModel):
    id: str
    name: str
    description: str
    #difficulty: int
    #xp_points: int
    stock: int
    active: bool = True


class CreateProductRequest(BaseModel):
    id: str | None = None
    name: str
    description: str
    #difficulty: int
    #xpPoints: int
    stock: int
    active: bool = True


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    #difficulty: int | None = None
    #xpPoints: int | None = None
    stock: int | None = None
    active: bool | None = None


class UpdateStockRequest(BaseModel):
    quantity: int

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    #difficulty: int
    #xpPoints: int
    stock: int
    active: bool
