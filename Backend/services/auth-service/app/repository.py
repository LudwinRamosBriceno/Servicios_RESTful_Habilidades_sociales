"""Repositorio de autenticación que usa un cliente HTTP de usuarios."""

from clients.user_http_client import UserHttpClient
from models import AuthenticatedUser


class AuthRepository:
    """Repositorio de autenticación que usa un cliente HTTP de usuarios."""

    def __init__(self, user_client: UserHttpClient) -> None:
        """Inicializa el repositorio con el cliente de usuarios."""
        self._user_client = user_client

    def verify_credentials(self, name: str, password: str) -> AuthenticatedUser:
        """Verifica las credenciales del usuario."""
        return self._user_client.verify_credentials(name, password)
