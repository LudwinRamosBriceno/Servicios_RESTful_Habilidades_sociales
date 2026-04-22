import uuid
import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import ProgrammingError

from .models import CreateProductRequest, Product, ProductResponse, UpdateProductRequest, UpdateStockRequest
from .repository import ProductRepository


logger = logging.getLogger(__name__)

# Servicio de productos con logica de negocio
class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository # instancia del repositorio para acceder a la base de datos
        self._seed_products() # Se colocan en la base de datos productos de prueba al iniciar el servicio

    # Metodo para listar todos los productos
    def list_products(self) -> list[ProductResponse]:
        return [self._to_response(product) for product in self._repository.find_all()]

    # Metodo para obtener un producto por su id
    def get_product(self, product_id: str) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return self._to_response(product)

    # Metodo para crear un nuevo producto
    def create_product(self, payload: CreateProductRequest) -> ProductResponse:
        product_id = payload.id or f"hab_{uuid.uuid4().hex[:6]}"
        product = Product(
            id=product_id,
            name=payload.name,
            description=payload.description,
            stock=payload.stock,
            active=payload.active,
        )
        self._repository.save(product)
        return self._to_response(product)

    # Metodo para actualizar un producto existente
    def update_product(self, product_id: str, payload: UpdateProductRequest) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        if payload.name is not None:
            product.name = payload.name
        if payload.description is not None:
            product.description = payload.description
        if payload.stock is not None:
            product.stock = payload.stock
        if payload.active is not None:
            product.active = payload.active

        self._repository.save(product)
        return self._to_response(product)

    # Metodo para eliminar un producto por su id
    def delete_product(self, product_id: str) -> None:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        
        self._repository.delete(product_id)

    # Metodo para descontar stock de un producto
    def discount_stock(self, product_id: str, payload: UpdateStockRequest) -> ProductResponse:
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        if payload.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La cantidad debe ser > 0")
        if product.stock < payload.quantity:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Stock insuficiente")

        product.stock -= payload.quantity
        self._repository.save(product)
        return self._to_response(product)

    # Metodo para convertir un objeto de producto a un objeto de respuesta (para el cliente)
    @staticmethod
    def _to_response(product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            stock=product.stock,
            active=product.active,
        )

    # Metodo para insertar productos de prueba en la base de datos al inciar el servicio
    def _seed_products(self) -> None:
        try:
            if self._repository.find_all():
                return
        except ProgrammingError:
            # If schema is missing, keep the service alive and migrate DB first.
            logger.warning("Products table is missing. Skipping seed until migrations are applied.")
            return

        seed_data = [
            Product(id="hab_001", name="empatia", description="Comprender emociones ajenas", stock=100, active=True),
            Product(id="hab_002", name="amistad", description="Crear vinculos positivos", stock=100, active=True),
            Product(id="hab_003", name="liderazgo", description="Guiar equipos", stock=80, active=True),
            Product(id="hab_004", name="creatividad", description="Generar ideas nuevas", stock=90, active=True),
            Product(id="hab_005", name="resiliencia", description="Superar adversidad", stock=70, active=True),
            Product(id="hab_006", name="comunicacion", description="Transmitir ideas claramente", stock=100, active=True),
            Product(id="hab_007", name="colaboracion", description="Trabajar en equipo", stock=110, active=True),
            Product(id="hab_008", name="sagacidad", description="Percibir con agudeza", stock=60, active=True),
            Product(id="hab_009", name="paciencia", description="Mantener calma", stock=120, active=True),
            Product(id="hab_010", name="respeto", description="Valorar a los demas", stock=120, active=True),
            Product(id="hab_011", name="confianza", description="Seguridad personal y social", stock=90, active=True),
            Product(id="hab_012", name="humor", description="Usar humor apropiado", stock=100, active=True),
            Product(id="hab_013", name="adaptabilidad", description="Ajustarse al cambio", stock=80, active=True),
            Product(id="hab_014", name="escucha activa", description="Escuchar con atencion", stock=95, active=True),
            Product(id="hab_015", name="iniciativa", description="Actuar de forma proactiva", stock=85, active=True),
        ]

        # Se insertan los productos de prueba en la base de datos
        for product in seed_data:
            self._repository.save(product)
