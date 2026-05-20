import uuid
import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import ProgrammingError

from .models import CreateProductRequest, Product, ProductResponse, UpdateProductRequest, UpdateStockRequest
from .repository import ProductRepository
from .messaging import publish_event

# Eventos de dominio para el flujo EDA
EVENT_ORDER_CREATED = "pedido.creado" 
EVENT_INVENTORY_CONFIRMED = "inventario.confirmado"
EVENT_INVENTORY_REJECTED = "inventario.rechazado"

# Configuración de logging para el servicio de productos
logger = logging.getLogger(__name__)

class ProductService:
    """
    Servicio de productos con logica de negocio relacionada con la gestión de productos y validación de inventario.
    """
    def __init__(self, repository: ProductRepository) -> None:
        """
        Inicializa el servicio de productos.
        """
        self._repository = repository # instancia del repositorio para acceder a la base de datos
        self._seed_products() # Se colocan en la base de datos productos de prueba al iniciar el servicio

    def list_products(self) -> list[ProductResponse]:
        """
        Metodo para listar todos los productos disponibles en la base de datos, incluso aquellos sin stock.
        """
        return [self._to_response(product) for product in self._repository.find_all()]

    def get_product(self, product_id: str) -> ProductResponse:
        """
        Metodo para obtener un producto por su id. Si el producto no existe, se lanza una excepcion HTTP 404.
        """
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return self._to_response(product)

    def create_product(self, payload: CreateProductRequest) -> ProductResponse:
        """
        Metodo para crear un nuevo producto en la base de datos. Si el ID ya existe, se actualiza el producto existente.
        """
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

    def update_product(self, product_id: str, payload: UpdateProductRequest) -> ProductResponse:
        """
        Metodo para actualizar un producto existente por su id. Si el producto no existe, se lanza una excepcion HTTP 404.
        """
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

    def delete_product(self, product_id: str) -> None:
        """
        Metodo para eliminar un producto por su id. Si el producto no existe, se lanza una excepcion HTTP 404.
        """
        product = self._repository.find_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        
        self._repository.delete(product_id)

    def discount_stock(self, product_id: str, payload: UpdateStockRequest) -> ProductResponse:
        """
        Metodo para descontar stock de un producto por su id. 
        Si el producto no existe, se lanza una excepcion HTTP 404. 
        Si la cantidad a descontar es mayor al stock disponible, se lanza una excepcion HTTP 422.
        """
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

    def process_order_created(self, payload: dict) -> None:
        """
        Valida inventario y publica el evento correspondiente.
        """
        data = payload.get("data", {})
        request_id = data.get("requestId")
        order_id = data.get("orderId")
        user_id = data.get("userId")
        product_id = data.get("productId")
        quantity = data.get("quantity")

        # Si falta información esencial en el payload, se lanza un error 
        # y se publica un evento de rechazo de inventario.
        if not order_id or not user_id or not product_id or not isinstance(quantity, int):
            raise ValueError("Invalid order.created payload")

        # Se busca el producto en la base de datos para validar su disponibilidad y stock.
        product = self._repository.find_by_id(product_id)

        # Si el producto no existe o no está activo, se publica un evento de rechazo de 
        # inventario con el motivo y código de estado 404.
        if not product or not product.active:
            publish_event(
                EVENT_INVENTORY_REJECTED,
                {
                    "requestId": request_id,
                    "orderId": order_id,
                    "userId": user_id,
                    "productId": product_id,
                    "quantity": quantity,
                    "reason": "Producto no disponible",
                    "statusCode": 404,
                },
                correlation_id=order_id,
            )
            return

        # Si el stock es insuficiente para cubrir la cantidad solicitada, 
        # se publica un evento de rechazo de inventario
        if product.stock < quantity:
            publish_event(
                EVENT_INVENTORY_REJECTED,
                {
                    "requestId": request_id,
                    "orderId": order_id,
                    "userId": user_id,
                    "productId": product_id,
                    "quantity": quantity,
                    "reason": "Stock insuficiente",
                    "statusCode": 422,
                },
                correlation_id=order_id,
            )
            return

        # Si el producto está disponible y hay stock suficiente, se descuenta el stock.
        product.stock -= quantity

        # Se guarda el producto actualizado en la base de datos. 
        self._repository.save(product)

        # Se publica un evento de confirmación de inventario con los detalles del pedido y el producto.
        publish_event(
            EVENT_INVENTORY_CONFIRMED,
            {
                "requestId": request_id,
                "orderId": order_id,
                "userId": user_id,
                "productId": product_id,
                "quantity": quantity,
                "productName": product.name,
                "skillPoints": quantity,
            },
            correlation_id=order_id,
        )

    @staticmethod
    def _to_response(product: Product) -> ProductResponse:
        """
        Metodo para convertir un objeto de producto a un objeto de respuesta (para el cliente).
        """
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            stock=product.stock,
            active=product.active,
        )

    def _seed_products(self) -> None:
        """
        Coloca en la base de datos productos de prueba si no existen. 
        Si la tabla de productos no existe, se omite el proceso (asumiendo que las migraciones se aplicarán después).
        """
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
