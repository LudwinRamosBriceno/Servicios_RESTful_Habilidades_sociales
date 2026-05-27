"""Cliente HTTP para obtener productos desde products-service."""

import httpx


class ProductHttpClient:
    """Cliente HTTP para consultas a products-service."""

    def __init__(self, base_url: str, timeout_seconds: float = 3.0) -> None:
        """Inicializa el cliente con base URL y timeout."""
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def get_product_name(self, product_id: str) -> str | None:
        """Obtiene el nombre de un producto por su ID."""
        try:
            response = httpx.get(
                f"{self._base_url}/products/{product_id}", timeout=self._timeout
            )
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        payload = response.json()
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return None
        return name
