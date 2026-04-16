import uuid

from fastapi import HTTPException, status

from .models import CreateProductRequest, Product, ProductResponse, UpdateProductRequest, UpdateStockRequest
from .repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository
        self._seed_products()

    def list_products(self) -> list[ProductResponse]:
        return [self._to_response(product) for product in self._repository.find_all()]

    def get_product(self, product_id: str) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return self._to_response(product)

    def create_product(self, payload: CreateProductRequest) -> ProductResponse:
        product_id = payload.id or f"hab_{uuid.uuid4().hex[:6]}"
        product = Product(
            id=product_id,
            name=payload.name,
            description=payload.description,
            difficulty=payload.difficulty,
            xp_points=payload.xpPoints,
            stock=payload.stock,
            active=payload.active,
        )
        self._repository.save(product)
        return self._to_response(product)

    def update_product(self, product_id: str, payload: UpdateProductRequest) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if payload.name is not None:
            product.name = payload.name
        if payload.description is not None:
            product.description = payload.description
        if payload.difficulty is not None:
            product.difficulty = payload.difficulty
        if payload.xpPoints is not None:
            product.xp_points = payload.xpPoints
        if payload.stock is not None:
            product.stock = payload.stock
        if payload.active is not None:
            product.active = payload.active

        self._repository.save(product)
        return self._to_response(product)

    def delete_product(self, product_id: str) -> None:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        self._repository.delete(product_id)

    def discount_stock(self, product_id: str, payload: UpdateStockRequest) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if payload.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantity must be > 0")
        if product.stock < payload.quantity:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient stock")

        product.stock -= payload.quantity
        self._repository.save(product)
        return self._to_response(product)

    @staticmethod
    def _to_response(product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            difficulty=product.difficulty,
            xpPoints=product.xp_points,
            stock=product.stock,
            active=product.active,
        )

    def _seed_products(self) -> None:
        if self._repository.find_all():
            return

        seed_data = [
            Product(id="hab_001", name="empatia", description="Comprender emociones ajenas", difficulty=1, xp_points=50, stock=100, active=True),
            Product(id="hab_002", name="amistad", description="Crear vinculos positivos", difficulty=1, xp_points=45, stock=100, active=True),
            Product(id="hab_003", name="liderazgo", description="Guiar equipos", difficulty=2, xp_points=80, stock=80, active=True),
            Product(id="hab_004", name="creatividad", description="Generar ideas nuevas", difficulty=2, xp_points=70, stock=90, active=True),
            Product(id="hab_005", name="resiliencia", description="Superar adversidad", difficulty=3, xp_points=100, stock=70, active=True),
            Product(id="hab_006", name="comunicacion", description="Transmitir ideas claramente", difficulty=2, xp_points=60, stock=100, active=True),
            Product(id="hab_007", name="colaboracion", description="Trabajar en equipo", difficulty=1, xp_points=55, stock=110, active=True),
            Product(id="hab_008", name="sagacidad", description="Percibir con agudeza", difficulty=3, xp_points=95, stock=60, active=True),
            Product(id="hab_009", name="paciencia", description="Mantener calma", difficulty=1, xp_points=40, stock=120, active=True),
            Product(id="hab_010", name="respeto", description="Valorar a los demas", difficulty=1, xp_points=50, stock=120, active=True),
            Product(id="hab_011", name="confianza", description="Seguridad personal y social", difficulty=2, xp_points=65, stock=90, active=True),
            Product(id="hab_012", name="humor", description="Usar humor apropiado", difficulty=1, xp_points=35, stock=100, active=True),
            Product(id="hab_013", name="adaptabilidad", description="Ajustarse al cambio", difficulty=2, xp_points=75, stock=80, active=True),
            Product(id="hab_014", name="escucha activa", description="Escuchar con atencion", difficulty=2, xp_points=70, stock=95, active=True),
            Product(id="hab_015", name="iniciativa", description="Actuar de forma proactiva", difficulty=2, xp_points=85, stock=85, active=True),
        ]

        for product in seed_data:
            self._repository.save(product)
