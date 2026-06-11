"""API Gateway que enruta solicitudes y expone canal SSE para respuestas."""

import asyncio
import json
import os
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from .db import Base, SessionLocal, engine
from .events import (
    EVENT_ORDERS_CREATE_REQUESTED,
    EVENT_ORDERS_CREATE_RESPONDED,
    EVENT_ORDERS_GET_REQUESTED,
    EVENT_ORDERS_LIST_BY_USER_REQUESTED,
    EVENT_ORDERS_STATUS_UPDATED,
    EVENT_PRODUCTS_GET_REQUESTED,
    EVENT_PRODUCTS_LIST_REQUESTED,
    EVENT_TYPE_MAP,
    EVENT_USERS_CREATE_REQUESTED,
    EVENT_USERS_CREATE_RESPONDED,
    EVENT_USERS_GET_REQUESTED,
    EVENT_USERS_LIST_REQUESTED,
    PUSH_EVENTS,
    RESPONSE_ERROR_MESSAGE,
    RESPONSE_EVENTS,
    RESPONSE_SUCCESS_MESSAGE,
)
from .messaging import publish_event, start_consumer
from .models import RequestStatus
from .repository import RequestRepository

# Aplicacion principal del API Gateway.
app = FastAPI(title="NovaLink API Gateway", version="1.0.0")

# Repositorio para registrar solicitudes y respuestas.
repo = RequestRepository(SessionLocal)

# Configuracion del servicio de autenticacion y JWT.
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8004")


@dataclass
class SseSubscriber:
    """Canal SSE asociado al event loop que atiende la conexion."""

    queue: asyncio.Queue
    loop: asyncio.AbstractEventLoop


# Mapa de suscriptores SSE por usuario/cliente.
_subscribers: Dict[str, list[SseSubscriber]] = {}
_subscribers_lock = threading.Lock()


def _subscriber_key(user_id: str | None, client_id: str | None) -> str:
    """Determina la clave de suscripcion segun usuario o cliente."""
    if user_id:
        return f"user:{user_id}"
    if client_id:
        return f"client:{client_id}"
    return "anonymous"


def _add_subscriber(key: str, subscriber: SseSubscriber) -> None:
    """Registra un canal SSE en la lista de suscriptores."""
    with _subscribers_lock:
        _subscribers.setdefault(key, []).append(subscriber)


def _remove_subscriber(key: str, subscriber: SseSubscriber) -> None:
    """Remueve un canal SSE cuando el cliente se desconecta."""
    with _subscribers_lock:
        if key not in _subscribers:
            return
        _subscribers[key] = [
            item for item in _subscribers[key] if item is not subscriber
        ]
        if not _subscribers[key]:
            del _subscribers[key]


def _notify_subscribers(key: str, event: dict) -> None:
    """Publica un evento de respuesta a los suscriptores SSE."""
    with _subscribers_lock:
        subscribers = list(_subscribers.get(key, []))

    for subscriber in subscribers:
        if subscriber.loop.is_closed():
            _remove_subscriber(key, subscriber)
            continue

        def _enqueue(target: SseSubscriber = subscriber, payload: dict = event) -> None:
            try:
                target.queue.put_nowait(payload)
            except asyncio.QueueFull:
                print(f"[gateway] SSE queue full for {key}; dropping event")

        subscriber.loop.call_soon_threadsafe(_enqueue)


async def _validate_session(request: Request) -> dict | None:
    """Valida la sesion usando el auth-service."""
    # Validación centralizada: el gateway depende del auth-service para sesiones.
    cookie_header = request.headers.get("cookie")
    if not cookie_header:
        return None

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/session",
                headers={"cookie": cookie_header},
            )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticacion no respondio a tiempo",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio de autenticacion no disponible: {exc}",
        ) from exc

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion invalida"
        )
    if response.status_code >= 500:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de autenticacion no disponible",
        )

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Respuesta invalida del servicio de autenticacion",
        )


async def get_identity(
    request: Request,
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
) -> dict:
    """Determina identidad por sesion o por client id."""
    session = await _validate_session(request)
    if session and session.get("user_id"):
        return {"user_id": session.get("user_id"), "client_id": None}

    if x_client_id:
        return {"user_id": None, "client_id": x_client_id}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Identidad requerida"
    )


def _create_request(
    event_type: str, user_id: str | None, client_id: str | None, data: dict
) -> str:
    """Registra una solicitud y publica el evento de request."""
    request_id = f"req_{uuid.uuid4().hex[:10]}"
    repo.create_request(request_id, event_type, user_id, client_id)
    payload = {
        "requestId": request_id,
        "userId": user_id,
        "clientId": client_id,
        **data,
    }
    publish_event(event_type, payload, correlation_id=request_id)
    return request_id


@app.post("/api/auth/login")
async def login(payload: dict) -> JSONResponse:
    """Proxy sincrono para el inicio de sesion (unico request directo)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{AUTH_SERVICE_URL}/login", json=payload)
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Servicio de autenticacion no respondio a tiempo"},
        )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Servicio de autenticacion no disponible: {exc}"},
        )

    try:
        content = response.json()
    except ValueError:
        content = {
            "detail": response.text
            or "Respuesta invalida del servicio de autenticacion"
        }

    gateway_response = JSONResponse(status_code=response.status_code, content=content)
    for value in response.headers.get_list("set-cookie"):
        gateway_response.headers.append("set-cookie", value)
    return gateway_response


@app.get("/api/auth/session")
async def session(request: Request) -> JSONResponse:
    """Proxy para validar la sesion actual."""
    cookie_header = request.headers.get("cookie", "")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/session",
                headers={"cookie": cookie_header},
            )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Servicio de autenticacion no respondio a tiempo"},
        )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Servicio de autenticacion no disponible: {exc}"},
        )

    try:
        content = response.json()
    except ValueError:
        content = {
            "detail": response.text
            or "Respuesta invalida del servicio de autenticacion"
        }

    return JSONResponse(status_code=response.status_code, content=content)


@app.post("/api/auth/logout")
async def logout(request: Request) -> JSONResponse:
    """Proxy para cerrar sesion."""
    cookie_header = request.headers.get("cookie", "")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/logout",
                headers={"cookie": cookie_header},
            )
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Servicio de autenticacion no respondio a tiempo"},
        )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Servicio de autenticacion no disponible: {exc}"},
        )

    try:
        content = response.json()
    except ValueError:
        content = {
            "detail": response.text
            or "Respuesta invalida del servicio de autenticacion"
        }

    gateway_response = JSONResponse(status_code=response.status_code, content=content)
    for value in response.headers.get_list("set-cookie"):
        gateway_response.headers.append("set-cookie", value)
    return gateway_response


@app.get("/api/events")
async def events(
    request: Request, identity: dict = Depends(get_identity)
) -> StreamingResponse:
    """Canal SSE para recibir respuestas asincronas."""
    key = _subscriber_key(identity.get("user_id"), identity.get("client_id"))
    subscriber = SseSubscriber(
        queue=asyncio.Queue(maxsize=100), loop=asyncio.get_running_loop()
    )
    _add_subscriber(key, subscriber)

    async def _stream() -> Any:
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(subscriber.queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            _remove_subscriber(key, subscriber)

    return StreamingResponse(_stream(), media_type="text/event-stream")


@app.get("/health")
def healthcheck() -> dict:
    """Endpoint de salud para Kubernetes y diagnostico local."""
    return {"status": "ok", "service": "api-gateway"}


@app.get("/api/products")
async def list_products(identity: dict = Depends(get_identity)) -> dict:
    """Solicita el listado de productos via eventos."""
    request_id = _create_request(
        EVENT_PRODUCTS_LIST_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {},
    )
    return {
        "type": "products-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de lista de productos recibida",
    }


@app.get("/api/products/{product_id}")
async def get_product(product_id: str, identity: dict = Depends(get_identity)) -> dict:
    """Solicita el detalle de un producto via eventos."""
    request_id = _create_request(
        EVENT_PRODUCTS_GET_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {"productId": product_id},
    )
    return {
        "type": "product-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de detalle de producto recibida",
    }


@app.get("/api/users")
async def list_users(identity: dict = Depends(get_identity)) -> dict:
    """Solicita el listado de usuarios via eventos."""
    request_id = _create_request(
        EVENT_USERS_LIST_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {},
    )
    return {
        "type": "users-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud recibida",
    }


@app.get("/api/users/{user_id}")
async def get_user(user_id: str, identity: dict = Depends(get_identity)) -> dict:
    """Solicita el detalle de un usuario via eventos."""
    request_id = _create_request(
        EVENT_USERS_GET_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {"targetUserId": user_id},
    )
    return {
        "type": "user-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de informacion de usuario recibida",
    }


@app.post("/api/users")
async def create_user(payload: dict) -> dict:
    """Solicita el registro de un usuario via eventos."""
    request_id = _create_request(
        EVENT_USERS_CREATE_REQUESTED,
        None,
        None,
        payload,
    )
    return {
        "type": "user-created",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Usuario creado, pendiente de confirmacion",
    }


@app.post("/api/orders")
async def create_order(payload: dict, identity: dict = Depends(get_identity)) -> dict:
    """Solicita la creacion de una orden via eventos."""
    user_id = identity.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido"
        )
    if user_id and payload.get("userId") not in (None, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no autorizado"
        )

    if user_id:
        payload = {**payload, "userId": user_id}

    request_id = _create_request(
        EVENT_ORDERS_CREATE_REQUESTED,
        user_id,
        identity.get("client_id"),
        payload,
    )
    return {
        "type": "order-created",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Orden creada, pendiente de inventario",
    }


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str, identity: dict = Depends(get_identity)) -> dict:
    """Solicita el detalle de una orden via eventos."""
    if not identity.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido"
        )
    request_id = _create_request(
        EVENT_ORDERS_GET_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {"orderId": order_id},
    )
    return {
        "type": "order-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de informacion de pedido recibida",
    }


@app.get("/api/orders/user/{user_id}")
async def get_orders_by_user(
    user_id: str, identity: dict = Depends(get_identity)
) -> dict:
    """Solicita el listado de ordenes por usuario via eventos."""
    if not identity.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido"
        )
    if identity.get("user_id") and identity.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no autorizado"
        )

    request_id = _create_request(
        EVENT_ORDERS_LIST_BY_USER_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
        {"targetUserId": user_id},
    )
    return {
        "type": "orders-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de lista de ordenes recibida",
    }


@app.get("/api/requests/{request_id}")
async def get_request_status(
    request_id: str, identity: dict = Depends(get_identity)
) -> dict:
    """Consulta el estado de una solicitud registrada."""
    record = repo.get_request(request_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request no encontrado"
        )

    if record.user_id and identity.get("user_id") != record.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado"
        )

    if record.client_id and identity.get("client_id") != record.client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado"
        )

    return {
        "requestId": record.id,
        "status": record.status,
        "response": json.loads(record.response_json) if record.response_json else None,
        "error": record.error,
    }


@app.on_event("startup")
def start_response_consumer() -> None:
    """Arranca el consumidor de respuestas del gateway."""
    last_error: Exception | None = None
    for attempt in range(1, 13):
        try:
            Base.metadata.create_all(bind=engine)
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            print(f"[gateway] database not ready, retry {attempt}/12: {exc}")
            time.sleep(5)

    if last_error is not None:
        raise last_error

    def _handle_response(payload: dict) -> None:
        """Maneja una respuesta recibida del servicio de ordenes."""
        event_type = payload.get("event_type")
        # Si el evento es un push event, notifica a los suscriptores correspondientes sin actualizar el estado de la solicitud.
        if event_type in PUSH_EVENTS:
            data = payload.get("data", {})
            user_id = data.get("userId")
            request_id = data.get("requestId")
            status_code = data.get("statusCode")

            # Si no hay userId, no se puede notificar, así que se ignora el mensaje.
            if not user_id:
                return
            message = data.get("message")

            # Si el mensaje de respuesta incluye un código de estado, se agrega al mensaje para mayor claridad.
            if status_code:
                message = f"{message} ({status_code})"
            key = _subscriber_key(user_id, None)
            _notify_subscribers(
                key,
                {
                    "type": EVENT_TYPE_MAP.get(event_type, event_type),
                    "requestId": request_id,
                    "status": data.get("status"),
                    "message": message,
                },
            )
            return

        # Si el evento no es un evento de respuesta esperado, se ignora el mensaje.
        if event_type not in RESPONSE_EVENTS:
            return

        # Si el evento es una actualización de estado de orden, se notifica a los suscriptores correspondientes sin actualizar el
        # estado de la solicitud, ya que este evento no corresponde a una respuesta directa a una solicitud del gateway.
        data = payload.get("data", {})
        request_id = data.get("requestId")

        # Si no hay requestId, no se puede actualizar ni notificar, así que se ignora el mensaje.
        if not request_id:
            return

        # Si el evento es una actualización de estado de orden, se notifica a los suscriptores correspondientes sin actualizar el estado de la solicitud.
        ok = data.get("ok", True)
        status_value = RequestStatus.COMPLETED if ok else RequestStatus.FAILED
        response_payload = data.get("result")
        error = data.get("error")

        # Actualiza el estado de la solicitud en el repositorio y obtiene el registro actualizado para determinar a quién notificar.
        repo.update_request(request_id, status_value, response_payload, error)
        record = repo.get_request(request_id)

        # Si no se encuentra el registro de la solicitud, no se puede notificar, así que se ignora el mensaje.
        if not record:
            return

        # Si el evento es una respuesta a la creación de usuario, se notifica a los suscriptores correspondientes con un mensaje específico para esta acción.
        if event_type == EVENT_USERS_CREATE_RESPONDED:
            status_code = data.get("statusCode")
            message = "Usuario creado" if ok else (error or "Error al crear usuario")

            # Si el mensaje de respuesta incluye un código de estado, se agrega al mensaje para mayor claridad.
            if not ok and status_code:
                message = f"{message} ({status_code})"
            _notify_subscribers(
                _subscriber_key(record.user_id, record.client_id),
                {
                    "type": EVENT_TYPE_MAP.get(event_type, event_type),
                    "requestId": request_id,
                    "status": status_value.value,
                    "message": message,
                },
            )
            return

        # Si el evento es una respuesta a la creación de orden, no se notifica a los suscriptores ya que esta acción tiene un flujo de comunicación diferente y se maneja principalmente a través de eventos de actualización de estado de orden.
        if event_type == EVENT_ORDERS_CREATE_RESPONDED:
            return

        key = _subscriber_key(record.user_id, record.client_id)
        status_code = data.get("statusCode")

        # Si la respuesta indica éxito, se utiliza un mensaje de éxito específico para el tipo de evento;
        # si indica error, se utiliza el mensaje de error proporcionado o un mensaje genérico según el tipo de evento.
        # Si el mensaje de error incluye un código de estado, se agrega al mensaje para mayor claridad.
        if ok:
            message = RESPONSE_SUCCESS_MESSAGE.get(event_type, "Completado")
            result_payload = response_payload
        else:
            message = error or RESPONSE_ERROR_MESSAGE.get(event_type, "Error")
            if status_code:
                message = f"{message} ({status_code})"
            result_payload = None
        _notify_subscribers(
            key,
            {
                "type": EVENT_TYPE_MAP.get(event_type, event_type),
                "requestId": request_id,
                "status": status_value.value,
                "result": result_payload,
                "message": message,
            },
        )

    # Inicia el consumidor para procesar las respuestas entrantes de los servicios en la cola "api-gateway-service" con los routing keys correspondientes.
    start_consumer(
        queue_name="api-gateway-service",
        routing_keys=["#.responded", EVENT_ORDERS_STATUS_UPDATED],
        handler=_handle_response,
    )
