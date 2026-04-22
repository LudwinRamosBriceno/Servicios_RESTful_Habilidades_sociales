from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Order, OrderStatus
from .orm_models import OrderORM


class OrderRepository:
    """
    Repositorio de órdenes persistente sobre PostgreSQL usando SQLAlchemy ORM.
    Proporciona métodos para crear una orden, encontrar una orden por su ID, y encontrar
    todas las órdenes asociadas a un usuario específico.
    """
    def __init__(self) -> None:
        """
        Inicializa el repositorio de órdenes.
        """
        self._session_factory = SessionLocal

    def create(self, order: Order) -> Order:
        """
        Crea una nueva orden y la almacena en el repositorio.
        Argumentos:
            order (Order): La orden a crear.
        Retorna:
            Order: La orden creada.
        """
        with self._session_factory() as session:
            session: Session
            session.add(
                OrderORM(
                    id=order.id,
                    user_id=order.user_id,
                    product_id=order.product_id,
                    quantity=order.quantity,
                    status=order.status.value,
                    skill_points=order.skill_points,
                    created_at=order.created_at,
                )
            )
            session.commit()
        return order

    def find_by_id(self, order_id: str) -> Order | None:
        """
        Busca una orden por su ID. Si la orden no existe, devuelve None.
        Argumentos:
            order_id (str): El ID de la orden a buscar.
        Retorna:
            Order | None: La orden encontrada o None si no existe.
        """
        statement = select(OrderORM).where(OrderORM.id == order_id)
        with self._session_factory() as session:
            session: Session
            orm_order = session.scalars(statement).first()

        if not orm_order:
            return None
        return self._orm_to_order(orm_order)

    def find_by_user_id(self, user_id: str) -> List[Order]:
        """
        Busca todas las órdenes asociadas a un usuario específico.
        Argumentos:
            user_id (str): El ID del usuario.
        Retorna:
            List[Order]: Una lista de órdenes asociadas al usuario.
        """
        statement = select(OrderORM).where(OrderORM.user_id == user_id).order_by(OrderORM.created_at.desc())
        with self._session_factory() as session:
            session: Session
            orm_orders = session.scalars(statement).all()

        return [self._orm_to_order(order) for order in orm_orders]

    @staticmethod
    def _orm_to_order(orm_order: OrderORM) -> Order:
        """
        Convierte una instancia de OrderORM a una instancia de Order.
        Argumentos:
            orm_order (OrderORM): La instancia de OrderORM a convertir.
        Retorna:
            Order: La instancia de Order resultante de la conversión.
        """
        return Order(
            id=orm_order.id,
            user_id=orm_order.user_id,
            product_id=orm_order.product_id,
            quantity=orm_order.quantity,
            status=OrderStatus(orm_order.status),
            skill_points=orm_order.skill_points,
            created_at=orm_order.created_at,
        )
