import httpx
from fastapi import HTTPException, status


class NotificationHttpClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url
        self._timeout = timeout_seconds

    def send_order_completed(self, order_id: str, user_id: str, skill_name: str, xp_gained: int) -> None:
        body = {
            "orderId": order_id,
            "userId": user_id,
            "skillName": skill_name,
            "xpGained": xp_gained,
        }

        try:
            response = httpx.post(f"{self._base_url}/notifications", json=body, timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Notifications service unavailable: {exc}") from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Notifications service error")
