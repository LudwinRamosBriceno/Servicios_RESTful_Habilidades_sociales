import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """
    Modelo que representa un usuario autenticado, con su ID, nombre y token JWT.
    """
    user_id: str
    name: str | None = None
    token: str


# Seguridad HTTP para extraer el token JWT de las solicitudes entrantes.
_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> AuthenticatedUser:
    
    """
    Dependencia de FastAPI que se utiliza para proteger rutas que requieren autenticación.
    Esta función extrae el token JWT de las credenciales proporcionadas, lo decodifica y valida.
    Devuelve un objeto AuthenticatedUser con la información del usuario autenticado.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")

    token = credentials.credentials
    secret = os.getenv("JWT_SECRET_KEY", "dev-secret")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    issuer = os.getenv("JWT_ISSUER", "auth-service")

    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    if payload.get("iss") != issuer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    return AuthenticatedUser(user_id=user_id, name=payload.get("name"), token=token)
