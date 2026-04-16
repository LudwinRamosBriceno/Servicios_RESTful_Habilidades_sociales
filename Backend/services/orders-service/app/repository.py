from typing import Dict, List

from .models import Order


class OrderRepository:
    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def create(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def find_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def find_by_user_id(self, user_id: str) -> List[Order]:
        return [order for order in self._orders.values() if order.user_id == user_id]
