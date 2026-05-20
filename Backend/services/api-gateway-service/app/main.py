import asyncio
import json
import os
import queue
import threading
import uuid
from typing import Any, Dict

import httpx
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse

from .db import Base, engine
from .messaging import publish_event, start_consumer
from .models import RequestStatus
from .repository import RequestRepository
from .events import (
    EVENT_PRODUCTS_LIST_REQUESTED,
    EVENT_PRODUCTS_GET_REQUESTED,
    EVENT_USERS_LIST_REQUESTED,
    EVENT_USERS_GET_REQUESTED,
    EVENT_USERS_CREATE_REQUESTED,
    EVENT_USERS_CREATE_RESPONDED,
    EVENT_ORDERS_CREATE_REQUESTED,
    EVENT_ORDERS_CREATE_RESPONDED,
    EVENT_ORDERS_GET_REQUESTED,
    EVENT_ORDERS_LIST_BY_USER_REQUESTED,
    EVENT_ORDERS_STATUS_UPDATED,
    RESPONSE_EVENTS,
    PUSH_EVENTS,
    EVENT_TYPE_MAP,
    RESPONSE_SUCCESS_MESSAGE,
    RESPONSE_ERROR_MESSAGE,
)

# Aplicacion principal del API Gateway.
app = FastAPI(title="NovaLink API Gateway", version="1.0.0")

# Repositorio para registrar solicitudes y respuestas.
repo = RequestRepository()

# Configuracion del servicio de autenticacion y JWT.
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8004")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "auth-service")

# Mapa de suscriptores SSE por usuario/cliente.
_subscribers: Dict[str, list[queue.Queue]] = {}
_subscribers_lock = threading.Lock()


def _subscriber_key(user_id: str | None, client_id: str | None) -> str:
    """
    Determina la clave de suscripcion segun usuario o cliente.
    """
    if user_id:
        return f"user:{user_id}"
    if client_id:
        return f"client:{client_id}"
    return "anonymous"


def _add_subscriber(key: str, q: queue.Queue) -> None:
    """
    Registra un canal SSE en la lista de suscriptores.
    """
    with _subscribers_lock:
        _subscribers.setdefault(key, []).append(q)


def _remove_subscriber(key: str, q: queue.Queue) -> None:
    """
    Remueve un canal SSE cuando el cliente se desconecta.
    """
    with _subscribers_lock:
        if key not in _subscribers:
            return
        _subscribers[key] = [item for item in _subscribers[key] if item is not q]
        if not _subscribers[key]:
            del _subscribers[key]


def _notify_subscribers(key: str, event: dict) -> None:
    """
    Publica un evento de respuesta a los suscriptores SSE.
    """
    with _subscribers_lock:
        for q in _subscribers.get(key, []):
            q.put(event)


def _decode_token(token: str) -> dict:
    """
    Valid a JWT y devuelve su payload.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido") from exc

    if payload.get("iss") != JWT_ISSUER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    return payload


def get_identity(
    authorization: str | None = Header(default=None),
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
) -> dict:
    """
    Determina identidad por JWT o por client id.
    """
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
        payload = _decode_token(token)
        return {"user_id": payload.get("sub"), "client_id": None}

    if x_client_id:
        return {"user_id": None, "client_id": x_client_id}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identidad requerida")


def _create_request(event_type: str, user_id: str | None, client_id: str | None, data: dict) -> str:
    """
    Registra una solicitud y publica el evento de request.
    """
    request_id = f"req_{uuid.uuid4().hex[:10]}"
    repo.create_request(request_id, event_type, user_id, client_id)
    payload = {"requestId": request_id, "userId": user_id, "clientId": client_id, **data}
    publish_event(event_type, payload, correlation_id=request_id)
    return request_id


@app.post("/api/auth/login")
async def login(payload: dict) -> JSONResponse:
    """
    Proxy sincrono para login (unico request directo).
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/login", json=payload)
    return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/api/events")
async def events(identity: dict = Depends(get_identity)) -> StreamingResponse:
    """
    Canal SSE para recibir respuestas asincronas.
    """
    key = _subscriber_key(identity.get("user_id"), identity.get("client_id"))
    q: queue.Queue = queue.Queue()
    _add_subscriber(key, q)

    async def _stream() -> Any:
        try:
            loop = asyncio.get_running_loop()
            while True:
                event = await loop.run_in_executor(None, q.get)
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            _remove_subscriber(key, q)

    return StreamingResponse(_stream(), media_type="text/event-stream")


@app.get("/api/products")
async def list_products(identity: dict = Depends(get_identity)) -> dict:
    """
    Solicita el listado de productos via eventos.
    """
    request_id = _create_request(EVENT_PRODUCTS_LIST_REQUESTED, identity.get("user_id"), identity.get("client_id"), {})
    return {
        "type": "products-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud de lista de productos recibida",
    }


@app.get("/api/products/{product_id}")
async def get_product(product_id: str, identity: dict = Depends(get_identity)) -> dict:
    """
    Solicita el detalle de un producto via eventos.
    """
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
    """
    Solicita el listado de usuarios via eventos.
    """
    request_id = _create_request(EVENT_USERS_LIST_REQUESTED, identity.get("user_id"), identity.get("client_id"), {})
    return {
        "type": "users-loaded",
        "requestId": request_id,
        "status": RequestStatus.PENDING.value,
        "message": "Solicitud recibida",
    }


@app.get("/api/users/{user_id}")
async def get_user(user_id: str, identity: dict = Depends(get_identity)) -> dict:
    """
    Solicita el detalle de un usuario via eventos.
    """
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
async def create_user(payload: dict, identity: dict = Depends(get_identity)) -> dict:
    """
    Solicita el registro de un usuario via eventos.
    """
    request_id = _create_request(
        EVENT_USERS_CREATE_REQUESTED,
        identity.get("user_id"),
        identity.get("client_id"),
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
    """
    Solicita la creacion de una orden via eventos.
    """
    user_id = identity.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    if user_id and payload.get("userId") not in (None, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no autorizado")

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
    """
    Solicita el detalle de una orden via eventos.
    """
    if not identity.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
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
async def get_orders_by_user(user_id: str, identity: dict = Depends(get_identity)) -> dict:
    """
    Solicita el listado de ordenes por usuario via eventos.
    """
    if not identity.get("user_id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    if identity.get("user_id") and identity.get("user_id") != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario no autorizado")

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
async def get_request_status(request_id: str, identity: dict = Depends(get_identity)) -> dict:
    """
    Consulta el estado de una solicitud registrada.
    """
    record = repo.get_request(request_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request no encontrado")

    if record.user_id and identity.get("user_id") != record.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    if record.client_id and identity.get("client_id") != record.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")

    return {
        "requestId": record.id,
        "status": record.status,
        "response": json.loads(record.response_json) if record.response_json else None,
        "error": record.error,
    }


@app.on_event("startup")
def start_response_consumer() -> None:
    """
    Arranca el consumidor de respuestas del gateway.
    """
    Base.metadata.create_all(bind=engine)

    def _handle_response(payload: dict) -> None:
        """
        Maneja una respuesta recibida del servicio de órdenes.
        """
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
