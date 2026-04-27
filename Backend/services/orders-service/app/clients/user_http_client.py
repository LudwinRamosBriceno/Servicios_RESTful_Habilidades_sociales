import httpx
from fastapi import HTTPException, status

from ..models import UserDTO


class UserHttpClient:
    """
    Cliente HTTP que se comunica con el servicio de usuarios para obtener información 
    sobre los usuarios y agregar habilidades a los usuarios.
    Atributos:
    base_url (str): URL base del servicio de usuarios
    timeout (float): Tiempo de espera para las solicitudes HTTP
    """
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        """
        Inicializa el cliente con la URL base del servicio de usuarios y un tiempo de espera opcional.
        """
        self._base_url = base_url
        self._timeout = timeout_seconds

    def get_user(self, user_id: str) -> UserDTO:
        """
        Obtiene la información de un usuario por su ID, manejando errores de conexión, usuario no encontrado
        y respuestas no exitosas.
        """
        try:
            response = httpx.get(f"{self._base_url}/users/{user_id}", timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Servicio de usuarios no disponible: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error del servicio de usuarios")

        payload = response.json()
        return UserDTO(id=payload["id"], name=payload["name"], email=payload["email"])

    def add_skill(self, user_id: str, skill_id: str, skill_points: int) -> bool:
        """
        Agrega una habilidad a un usuario, proporcionando el ID del usuario, el ID de la habilidad 
        y los puntos de experiencia a agregar.
        Maneja errores de conexión, usuario no encontrado, y respuestas no exitosas. Devuelve
        """
        body = {"skillId": skill_id, "skillPoints": skill_points}
        try:
            response = httpx.put(f"{self._base_url}/users/{user_id}/skills", json=body, timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Servicio de usuarios no disponible: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error del servicio de usuarios")

        return bool(response.json().get("alreadyOwned", False))
