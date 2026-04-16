from typing import Dict, List

from .models import Product


class ProductRepository:
    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}

    def save(self, product: Product) -> Product:
        self._products[product.id] = product
        return product

    def find_all(self) -> List[Product]:
        return list(self._products.values())

    def find_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)

    def delete(self, product_id: str) -> None:
        if product_id in self._products:
            del self._products[product_id]
