import os

from fastapi import APIRouter

from .clients.user_http_client import UserHttpClient
from .models import LoginRequest, TokenResponse
from .repository import AuthRepository
from .service import AuthService

# Configuración del router y del servicio de autenticación.
router = APIRouter(tags=["auth"])

# Configuración de la URL del servicio de usuarios.
users_service_url = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
service = AuthService(AuthRepository(UserHttpClient(users_service_url)))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """
    Ruta para iniciar sesión, recibiendo el correo 
    y la contraseña en el cuerpo de la solicitud.
    """
    return service.login(payload)
