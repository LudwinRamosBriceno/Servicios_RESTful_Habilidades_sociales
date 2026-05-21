from fastapi import FastAPI, HTTPException

from .controller import router as user_router
from .messaging import publish_event, start_consumer
from .repository import UserRepository
from .service import UserService, EVENT_INVENTORY_CONFIRMED
from .models import CreateUserRequest

# Eventos de request/response para el gateway.
EVENT_USERS_LIST_REQUESTED = "users.list.requested"
EVENT_USERS_GET_REQUESTED = "users.get.requested"
EVENT_USERS_CREATE_REQUESTED = "users.create.requested"
EVENT_USERS_LIST_RESPONDED = "users.list.responded"
EVENT_USERS_GET_RESPONDED = "users.get.responded"
EVENT_USERS_CREATE_RESPONDED = "users.create.responded"

# Aplicacion principal del microservicio de usuarios.
app = FastAPI(title="NovaLink Users Service", version="1.0.0")
# Registra endpoints funcionales bajo el prefijo definido en el controller.
app.include_router(user_router)


@app.on_event("startup")
def start_event_consumers() -> None:
    """
    Arranca consumidores de eventos para asignar habilidades.
    En este caso, escucha eventos de inventario confirmado para otorgar puntos al usuario.
    """
    service = UserService(UserRepository())

    def _handle_inventory_confirmed(payload: dict) -> None:
        if payload.get("event_type") != EVENT_INVENTORY_CONFIRMED:
            return
        service.process_inventory_confirmed(payload)

    start_consumer(
        queue_name="users-service",
        routing_keys=[EVENT_INVENTORY_CONFIRMED],
        handler=_handle_inventory_confirmed,
    )


@app.on_event("startup")
def start_request_consumers() -> None:
    """
    Consume requests del gateway y publica respuestas.
    """
    service = UserService(UserRepository())

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
        Maneja los eventos de request para listar, obtener o crear usuarios, 
        y publica eventos de respuesta con el resultado o error.
        """
        data = payload.get("data", {})
        event_type = payload.get("event_type")
        request_id = data.get("requestId")
        user_id = data.get("userId")

        # Si no hay requestId, no se puede responder, así que se ignora el mensaje.
        if not request_id:
            return
        
        # Intenta procesar el request según su tipo y responde con el resultado o error.
        try:
            # Procesa request de listar usuarios.
            if event_type == EVENT_USERS_LIST_REQUESTED:
                results = service.list_users()
                _respond(
                    EVENT_USERS_LIST_RESPONDED,
                    request_id,
                    user_id,
                    [item.model_dump() for item in results],
                    None,
                    200,
                )
                return
            # Procesa request de obtener un usuario específico.
            if event_type == EVENT_USERS_GET_REQUESTED:
                target_user_id = data.get("targetUserId")
                result = service.get_user(target_user_id)
                _respond(EVENT_USERS_GET_RESPONDED, request_id, user_id, result.model_dump(), None, 200)
                return
            # Procesa request de crear un nuevo usuario.
            if event_type == EVENT_USERS_CREATE_REQUESTED:
                create_payload = {
                    "name": data.get("name"),
                    "email": data.get("email"),
                    "password": data.get("password"),
                }
                result = service.create_user(CreateUserRequest(**create_payload))
                _respond(EVENT_USERS_CREATE_RESPONDED, request_id, user_id, result.model_dump(), None, 200)
        
        # Si ocurre cualquier error durante el procesamiento, responde con el mensaje de error y código correspondiente.
        except Exception as exc:
            response_type = {
                EVENT_USERS_LIST_REQUESTED: EVENT_USERS_LIST_RESPONDED,
                EVENT_USERS_GET_REQUESTED: EVENT_USERS_GET_RESPONDED,
                EVENT_USERS_CREATE_REQUESTED: EVENT_USERS_CREATE_RESPONDED,
            }.get(event_type)

            if response_type:
                status_code = exc.status_code if isinstance(exc, HTTPException) else 500
                _respond(response_type, request_id, user_id, None, str(exc), status_code)

    # Arranca el consumidor para manejar los eventos de request relacionados con usuarios.
    start_consumer(
        queue_name="users-requests",
        routing_keys=[EVENT_USERS_LIST_REQUESTED, EVENT_USERS_GET_REQUESTED, EVENT_USERS_CREATE_REQUESTED],
        handler=_handle_request,
    )


@app.get("/health")
def healthcheck():
    """
    Endpoint para verificar disponibilidad del servicio.
    """
    return {"status": "ok", "service": "users-service"}
