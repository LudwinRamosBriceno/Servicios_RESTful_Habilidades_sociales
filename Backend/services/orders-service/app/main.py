"""Punto de entrada principal para el servicio de órdenes."""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException

from .controller import router as orders_router
from .db import SessionLocal
from .messaging import publish_event, start_consumer
from .models import OrderRequest
from .repository import OrderRepository
from .service import (
    EVENT_INVENTORY_CONFIRMED,
    EVENT_INVENTORY_REJECTED,
    EVENT_ORDER_STATUS_UPDATED,
    OrderService,
)

# Eventos de request/response para el gateway.
EVENT_ORDERS_CREATE_REQUESTED = "orders.create.requested"
EVENT_ORDERS_GET_REQUESTED = "orders.get.requested"
EVENT_ORDERS_LIST_BY_USER_REQUESTED = "orders.list_by_user.requested"
EVENT_ORDERS_CREATE_RESPONDED = "orders.create.responded"
EVENT_ORDERS_GET_RESPONDED = "orders.get.responded"
EVENT_ORDERS_LIST_BY_USER_RESPONDED = "orders.list_by_user.responded"

# Evento de notificacion de cambio de estado.
EVENT_ORDERS_STATUS_UPDATED = EVENT_ORDER_STATUS_UPDATED

# Inicialización de la aplicación FastAPI y registro del enrutador de órdenes.
app = FastAPI(title="NovaLink Orders Service", version="1.0.0")
app.include_router(orders_router)


@app.on_event("startup")
def run_db_migrations() -> None:
    """Ejecuta las migraciones de Alembic al iniciar el servicio."""
    # Si la variable de entorno RUN_DB_MIGRATIONS_ON_STARTUP no está configurada como "true", se omiten las migraciones.
    if os.getenv("RUN_DB_MIGRATIONS_ON_STARTUP", "false").lower() != "true":
        print(
            "[orders-service] Startup migrations disabled (RUN_DB_MIGRATIONS_ON_STARTUP!=true)."
        )
        return

    # Configura Alembic para ejecutar las migraciones desde el directorio raíz del proyecto.
    root_dir = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))

    # Intenta ejecutar las migraciones y captura cualquier error que ocurra durante el proceso.
    try:
        command.upgrade(alembic_cfg, "head")
    # Si Alembic lanza un SystemExit, se captura la excepción y se imprime un mensaje, pero se continúa con el inicio del servicio.
    except SystemExit as exc:
        print(
            f"[orders-service] Alembic exited during startup with code={exc.code}; continuing."
        )


@app.on_event("startup")
def start_event_consumers() -> None:
    """Arranca consumidores de eventos para actualizar estados de ordenes."""
    service = OrderService(OrderRepository(SessionLocal))

    def _handle_event(payload: dict) -> None:
        """Maneja eventos de confirmación y rechazo de inventario."""
        event_type = payload.get("event_type")
        if event_type == EVENT_INVENTORY_CONFIRMED:
            service.handle_inventory_confirmed(payload)
        elif event_type == EVENT_INVENTORY_REJECTED:
            service.handle_inventory_rejected(payload)

    # Suscribe el consumidor a los eventos de confirmación y rechazo de inventario
    # para actualizar el estado de las órdenes en consecuencia.
    start_consumer(
        queue_name="orders-service",
        routing_keys=[EVENT_INVENTORY_CONFIRMED, EVENT_INVENTORY_REJECTED],
        handler=_handle_event,
    )


@app.on_event("startup")
def start_request_consumers() -> None:
    """Consume requests del gateway y publica respuestas."""
    service = OrderService(OrderRepository(SessionLocal))

    def _respond(
        event_type: str,
        request_id: str,
        user_id: str | None,
        result: dict | list | None,
        error: str | None,
        status_code: int,
    ) -> None:
        """Publica un evento de respuesta con resultado o error del request."""
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
        """Maneja solicitudes entrantes del gateway."""
        data = payload.get("data", {})
        event_type = payload.get("event_type")
        request_id = data.get("requestId")
        user_id = data.get("userId")

        # Si no hay requestId, no se puede responder, así que se ignora el mensaje.
        if not request_id:
            return

        # Intenta procesar la solicitud según el tipo de evento.
        try:
            # Si el evento es de creación de orden, se procesa la solicitud de creación y se responde con el resultado o error.
            if event_type == EVENT_ORDERS_CREATE_REQUESTED:
                order_request = OrderRequest(
                    userId=data.get("userId"),
                    productId=data.get("productId"),
                    quantity=data.get("quantity", 0),
                )
                result, _ = service.create_order(order_request, user_id, request_id)
                _respond(
                    EVENT_ORDERS_CREATE_RESPONDED,
                    request_id,
                    user_id,
                    result.model_dump(),
                    None,
                    202,
                )
                return

            # Si el evento es de obtención de orden, se procesa la solicitud de obtención y se responde con el resultado o error.
            if event_type == EVENT_ORDERS_GET_REQUESTED:
                order_id = data.get("orderId")
                result = service.get_order(order_id)
                _respond(
                    EVENT_ORDERS_GET_RESPONDED,
                    request_id,
                    user_id,
                    result.model_dump(),
                    None,
                    200,
                )
                return

            # Si el evento es de listado de órdenes por usuario, se procesa la solicitud y se responde con el resultado o error.
            if event_type == EVENT_ORDERS_LIST_BY_USER_REQUESTED:
                target_user_id = data.get("targetUserId")
                results = service.get_orders_by_user(target_user_id)
                _respond(
                    EVENT_ORDERS_LIST_BY_USER_RESPONDED,
                    request_id,
                    user_id,
                    [item.model_dump() for item in results],
                    None,
                    200,
                )

        # Si ocurre cualquier error durante el procesamiento de la solicitud, se captura la excepción y se responde
        # con un evento de respuesta que contiene el error.
        except Exception as exc:
            response_type = {
                EVENT_ORDERS_CREATE_REQUESTED: EVENT_ORDERS_CREATE_RESPONDED,
                EVENT_ORDERS_GET_REQUESTED: EVENT_ORDERS_GET_RESPONDED,
                EVENT_ORDERS_LIST_BY_USER_REQUESTED: EVENT_ORDERS_LIST_BY_USER_RESPONDED,
            }.get(event_type)

            # Si se pudo determinar un tipo de respuesta para el evento, se responde con el error y el código de estado correspondiente.
            if response_type:
                status_code = exc.status_code if isinstance(exc, HTTPException) else 500
                _respond(
                    response_type, request_id, user_id, None, str(exc), status_code
                )

    # Inicia el consumidor para procesar las solicitudes entrantes del gateway en la cola "orders-requests" con los routing keys correspondientes.
    start_consumer(
        queue_name="orders-requests",
        routing_keys=[
            EVENT_ORDERS_CREATE_REQUESTED,
            EVENT_ORDERS_GET_REQUESTED,
            EVENT_ORDERS_LIST_BY_USER_REQUESTED,
        ],
        handler=_handle_request,
    )


@app.get("/health")
def healthcheck():
    """Ruta de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "orders-service"}
