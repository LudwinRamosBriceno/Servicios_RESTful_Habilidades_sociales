from .clients.user_http_client import UserHttpClient
from .models import AuthenticatedUser


class AuthRepository:
    def __init__(self, user_client: UserHttpClient) -> None:
        """
        Repositorio de autenticación que utiliza un cliente HTTP para comunicarse con el servicio de usuarios.
        """
        self._user_client = user_client

    def verify_credentials(self, name: str, password: str) -> AuthenticatedUser:
        """
        Verifica las credenciales del usuario.
        """
        return self._user_client.verify_credentials(name, password)
