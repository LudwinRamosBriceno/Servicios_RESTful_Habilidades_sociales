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


class LoginResponse(BaseModel):
    """
    Modelo para la respuesta de inicio de sesión.
    """
    user_id: str
    name: str | None = None


class SessionResponse(BaseModel):
    """
    Modelo para la validación de sesión.
    """
    user_id: str
    name: str | None = None
