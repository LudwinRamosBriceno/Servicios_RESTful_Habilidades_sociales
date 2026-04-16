import httpx
from fastapi import HTTPException, status

from ..models import UserDTO


class UserHttpClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url
        self._timeout = timeout_seconds

    def get_user(self, user_id: str) -> UserDTO:
        try:
            response = httpx.get(f"{self._base_url}/users/{user_id}", timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Users service unavailable: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Users service error")

        payload = response.json()
        return UserDTO(id=payload["id"], name=payload["name"], email=payload["email"])

    def add_skill(self, user_id: str, skill_id: str, xp_points: int) -> bool:
        body = {"skillId": skill_id, "xpPoints": xp_points}
        try:
            response = httpx.put(f"{self._base_url}/users/{user_id}/skills", json=body, timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Users service unavailable: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Users service error")

        return bool(response.json().get("alreadyOwned", False))
