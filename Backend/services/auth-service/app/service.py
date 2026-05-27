"""Servicio de autenticación para inicio de sesión y creación de sesiones."""

from app.models import AuthenticatedUser, LoginRequest
from app.repository import AuthRepository


class AuthService:
    """Servicio de autenticación para inicio de sesión y creación de sesiones."""

    def __init__(self, repository: AuthRepository) -> None:
        """Inicializa el servicio de autenticación con el repositorio."""
        self._repository = repository

    def login(self, payload: LoginRequest) -> AuthenticatedUser:
        """Verifica credenciales y devuelve el usuario autenticado."""
        return self._repository.verify_credentials(payload.email, payload.password)
