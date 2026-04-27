import os
from datetime import datetime, timedelta, timezone

import jwt

from .models import AuthenticatedUser, LoginRequest, TokenResponse
from .repository import AuthRepository


class AuthService:
    """
    Servicio de autenticación que maneja la lógica de negocio relacionada con el 
    inicio de sesión y la generación de tokens JWT.
    """
    def __init__(self, repository: AuthRepository) -> None:
        """
        Inicializa el servicio de autenticación con el repositorio proporcionado.
        """
        self._repository = repository

    def login(self, payload: LoginRequest) -> TokenResponse:
        """
        Recibe las credenciales del usuario, verifica su validez utilizando el repositorio.
        Si las credenciales son válidas, genera un token JWT para el usuario autenticado.
        """
        user = self._repository.verify_credentials(payload.email, payload.password)
        token = self._generate_token(user)
        return TokenResponse(access_token=token, user_id=user.user_id)

    @staticmethod
    def _generate_token(user: AuthenticatedUser) -> str:
        """
        Genera un token JWT para el usuario autenticado, utilizando una clave secreta y configuraciones de expiración.
        """
        secret = os.getenv("JWT_SECRET_KEY", "dev-secret")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        issuer = os.getenv("JWT_ISSUER", "auth-service")
        expires_seconds = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user.user_id,
            "name": user.name,
            "iss": issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=expires_seconds)).timestamp()),
        }
        return jwt.encode(payload, secret, algorithm=algorithm)
