from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Modelo para la solicitud de inicio de sesión.
    """
    email: str
    password: str


class AuthenticatedUser(BaseModel):
    """
    Modelo que representa un usuario autenticado, con su ID y nombre.
    """
    user_id: str
    name: str


class TokenResponse(BaseModel):
    """
    Modelo para la respuesta de tokens de autenticación.
    """
    access_token: str
    token_type: str = "bearer"
    user_id: str
