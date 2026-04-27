import httpx


class ProductHttpClient:
    def __init__(self, base_url: str, timeout_seconds: float = 3.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    def get_product_name(self, product_id: str) -> str | None:
        try:
            response = httpx.get(f"{self._base_url}/products/{product_id}", timeout=self._timeout)
        except httpx.RequestError:
            return None

        if response.status_code != 200:
            return None

        payload = response.json()
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            return None
        return name
