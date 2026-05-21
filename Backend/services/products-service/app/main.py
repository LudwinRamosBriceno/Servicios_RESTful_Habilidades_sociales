from fastapi import FastAPI, HTTPException

from .controller import router as product_router
from .messaging import publish_event, start_consumer
from .repository import ProductRepository
from .service import ProductService, EVENT_ORDER_CREATED

# Eventos de request/response para el gateway.
EVENT_PRODUCTS_LIST_REQUESTED = "products.list.requested"
EVENT_PRODUCTS_GET_REQUESTED = "products.get.requested"
EVENT_PRODUCTS_LIST_RESPONDED = "products.list.responded"
EVENT_PRODUCTS_GET_RESPONDED = "products.get.responded"

# Aplicacion principal del microservicio de productos.
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

    # Suscribe el consumidor al evento de orden creada para validar inventario.
    start_consumer(
        queue_name="products-service",
        routing_keys=[EVENT_ORDER_CREATED],
        handler=_handle_order_created,
    )


@app.on_event("startup")
def start_request_consumers() -> None:
    """
    Consume requests del gateway y publica respuestas.
    """
    service = ProductService(ProductRepository())

    def _respond(
        event_type: str,
        request_id: str,
        user_id: str | None,
        result: dict | list | None,
        error: str | None,
        status_code: int,
    ) -> None:
        """
        Publica un evento de respuesta con el resultado o error del procesamiento de un request.
        """
        publish_event(
            event_type,
            {
                "requestId": request_id,
                "userId": user_id,
                "ok": error is None,
                "result": result,
                "error": error,
                "statusCode": status_code,
            },
            correlation_id=request_id,
        )

    def _handle_request(payload: dict) -> None:
        """
        Maneja los eventos de request para listar o obtener productos, 
        y publica eventos de respuesta con el resultado o error.
        """
        data = payload.get("data", {})
        event_type = payload.get("event_type")
        request_id = data.get("requestId")
        user_id = data.get("userId")

        # Si no hay requestId, no se puede responder, así que se ignora el mensaje.
        if not request_id:
            return

        # Intenta procesar el request según su tipo.
        try:
            # Si el request es para listar productos, obtiene la lista de productos y responde con el resultado.
            if event_type == EVENT_PRODUCTS_LIST_REQUESTED:
                results = service.list_products()
                _respond(
                    EVENT_PRODUCTS_LIST_RESPONDED,
                    request_id,
                    user_id,
                    [item.model_dump() for item in results],
                    None,
                    200,
                )
                return

            # Si el request es para obtener un producto, obtiene el producto por su ID y responde con el resultado.
            if event_type == EVENT_PRODUCTS_GET_REQUESTED:
                product_id = data.get("productId")
                result = service.get_product(product_id)
                _respond(EVENT_PRODUCTS_GET_RESPONDED, request_id, user_id, result.model_dump(), None, 200)
        
        # Si ocurre cualquier error en el procesamiento del request, responde con el error y el código de estado correspondiente.
        except Exception as exc:
            response_type = {
                EVENT_PRODUCTS_LIST_REQUESTED: EVENT_PRODUCTS_LIST_RESPONDED,
                EVENT_PRODUCTS_GET_REQUESTED: EVENT_PRODUCTS_GET_RESPONDED,
            }.get(event_type)

            # Si se pudo determinar el tipo de respuesta, responde con el mensaje de error y el código de estado.
            if response_type:
                status_code = exc.status_code if isinstance(exc, HTTPException) else 500
                _respond(response_type, request_id, user_id, None, str(exc), status_code)
    
    # Suscribe el consumidor a los eventos de request para listar y obtener productos.
    start_consumer(
        queue_name="products-requests",
        routing_keys=[EVENT_PRODUCTS_LIST_REQUESTED, EVENT_PRODUCTS_GET_REQUESTED],
        handler=_handle_request,
    )


@app.get("/health")
def healthcheck():
    """
    Endpoint para verificar que el servicio de productos está funcionando correctamente.
    """
    return {"status": "ok", "service": "products-service"}
