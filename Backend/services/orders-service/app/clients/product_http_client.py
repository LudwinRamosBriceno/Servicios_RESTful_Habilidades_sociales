import httpx
from fastapi import HTTPException, status

from ..models import ProductDTO


class ProductHttpClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self._base_url = base_url
        self._timeout = timeout_seconds

    def get_product(self, product_id: str) -> ProductDTO:
        try:
            response = httpx.get(f"{self._base_url}/products/{product_id}", timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Products service unavailable: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Products service error")

        payload = response.json()
        return ProductDTO(
            id=payload["id"],
            name=payload["name"],
            stock=payload["stock"],
            xpPoints=payload["xpPoints"],
        )

    def discount_stock(self, product_id: str, quantity: int) -> None:
        body = {"quantity": quantity}
        try:
            response = httpx.put(f"{self._base_url}/products/{product_id}/stock", json=body, timeout=self._timeout)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Products service unavailable: {exc}") from exc

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Insufficient stock")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Products service error")
