import httpx
from fastapi import HTTPException, status


class NotificationHttpClient:
    """
    Cliente HTTP que se comunica con el servicio de notificaciones para enviar eventos relacionados con las órdenes.
    Atributos: 
    base_url (str): URL base del servicio de notificaciones 
    timeout (float): Tiempo de espera para las solicitudes HTTP
    """
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        """
        Inicializa el cliente con la URL base del servicio de notificaciones y un tiempo de espera opcional.
        """
        self._base_url = base_url
        self._timeout = timeout_seconds

    
    def send_order_completed(self, order_id: str, user_id: str, skill_name: str, skill_points: int) -> None:
        """
        Envia una notificación de que una orden ha sido completada.
        """
        body = {
            "orderId": order_id,
            "userId": user_id,
            "skillName": skill_name,
            "skillPoints": skill_points,
        }
        
        try:
            response = httpx.post(f"{self._base_url}/notifications", json=body, timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Servicio de notificaciones no disponible: {exc}") from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error del servicio de notificaciones")
