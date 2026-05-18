from fastapi import FastAPI

from .controller import router as product_router
from .messaging import start_consumer
from .repository import ProductRepository
from .service import ProductService, EVENT_ORDER_CREATED

app = FastAPI(title="NovaLink Products Service", version="1.0.0")
app.include_router(product_router)


@app.on_event("startup")
def start_event_consumers() -> None:
    """
    Arranca consumidores de eventos para validar inventario.
    """
    service = ProductService(ProductRepository())

    def _handle_order_created(payload: dict) -> None:
        """
        Maneja el evento de orden creada para validar inventario y publicar eventos de confirmación o rechazo.
        """
        if payload.get("event_type") != EVENT_ORDER_CREATED:
            return
        service.process_order_created(payload)

    start_consumer(
        queue_name="products-service",
        routing_keys=[EVENT_ORDER_CREATED],
        handler=_handle_order_created,
    )


@app.get("/health")
def healthcheck():
    """
    Endpoint para verificar que el servicio de productos está funcionando correctamente.
    """
    return {"status": "ok", "service": "products-service"}
