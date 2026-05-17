import httpx
from fastapi import HTTPException, status

from ..models import AuthenticatedUser


class UserHttpClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def verify_credentials(self, email: str, password: str) -> AuthenticatedUser:
        body = {"email": email, "password": password}
        try:
            response = httpx.post(
                f"{self._base_url}/users/auth/verify",
                json=body,
                timeout=self._timeout,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Servicio de usuarios no disponible: {exc}",
            ) from exc

        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error del servicio de usuarios",
            )

        payload = response.json()
        return AuthenticatedUser(user_id=payload["userId"], name=payload["name"])
