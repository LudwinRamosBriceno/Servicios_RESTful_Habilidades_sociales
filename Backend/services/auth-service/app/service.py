from .models import AuthenticatedUser, LoginRequest
from .repository import AuthRepository


class AuthService:
    """
    Servicio de autenticación que maneja la lógica de negocio relacionada con el 
    inicio de sesión y la creación de sesiones en servidor.
    """
    def __init__(self, repository: AuthRepository) -> None:
        """
        Inicializa el servicio de autenticación con el repositorio proporcionado.
        """
        self._repository = repository

    def login(self, payload: LoginRequest) -> AuthenticatedUser:
        """
        Recibe las credenciales del usuario, verifica su validez utilizando el repositorio.
        Si las credenciales son válidas, devuelve el usuario autenticado.
        """
        return self._repository.verify_credentials(payload.email, payload.password)
