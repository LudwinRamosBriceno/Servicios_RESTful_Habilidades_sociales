import os

from fastapi import APIRouter, Cookie, HTTPException, Response, status

from .clients.user_http_client import UserHttpClient
from .models import LoginRequest, LoginResponse, SessionResponse
from .repository import AuthRepository
from .service import AuthService
from .session_store import SESSION_COOKIE_NAME, SESSION_TTL_SECONDS, create_session, delete_session, get_session

# Configuración del router y del servicio de autenticación.
router = APIRouter(tags=["auth"])

# Configuración de la URL del servicio de usuarios.
users_service_url = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
service = AuthService(AuthRepository(UserHttpClient(users_service_url)))


_cookie_secure = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response):
    """
    Ruta para iniciar sesión, recibiendo el correo 
    y la contraseña en el cuerpo de la solicitud.
    """
    user = service.login(payload)
    session_id, _expires_at = create_session(user.user_id, user.name)
    # La sesión se mantiene en el backend; la cookie solo guarda el session_id.
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_id,
        httponly=True,
        samesite="lax",
        secure=_cookie_secure,
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )
    return LoginResponse(user_id=user.user_id, name=user.name)


@router.get("/session", response_model=SessionResponse)
def validate_session(session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    """
    Ruta para validar la sesión almacenada en cookie.
    """
    # Si la sesión no existe en memoria, se considera inválida.
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion invalida")
    return SessionResponse(user_id=session["user_id"], name=session.get("name"))


@router.post("/logout")
def logout(response: Response, session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    """
    Ruta para cerrar sesión y eliminar la cookie.
    """
    delete_session(session_id)
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return {"ok": True}
