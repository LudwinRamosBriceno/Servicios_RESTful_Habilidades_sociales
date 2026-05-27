"""Repositorio de órdenes persistente sobre PostgreSQL con SQLAlchemy ORM."""

from typing import List

from models import Order, OrderStatus
from orm_models import OrderORM
from sqlalchemy import select
from sqlalchemy.orm import Session


class OrderRepository:
    """Repositorio de órdenes persistente sobre PostgreSQL con SQLAlchemy ORM."""

    def __init__(self, session_factory):
        """Inicializa el repositorio con una fábrica de sesiones."""
        self._session_factory = session_factory  # sesión de base de datos

    def create(self, order: Order) -> Order:
        """Crea una nueva orden y la almacena en el repositorio."""
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
        """Busca una orden por su ID y devuelve None si no existe."""
        statement = select(OrderORM).where(OrderORM.id == order_id)
        with self._session_factory() as session:
            session: Session
            orm_order = session.scalars(statement).first()

        if not orm_order:
            return None
        return self._orm_to_order(orm_order)

    def find_by_user_id(self, user_id: str) -> List[Order]:
        """Busca todas las órdenes asociadas a un usuario."""
        statement = (
            select(OrderORM)
            .where(OrderORM.user_id == user_id)
            .order_by(OrderORM.created_at.desc())
        )
        with self._session_factory() as session:
            session: Session
            orm_orders = session.scalars(statement).all()

        return [self._orm_to_order(order) for order in orm_orders]

    def update_status(
        self, order_id: str, status: OrderStatus, skill_points: int
    ) -> Order | None:
        """Actualiza el estado y los puntos de habilidad de una orden."""
        with self._session_factory() as session:
            session: Session
            existing = session.get(OrderORM, order_id)
            if not existing:
                return None

            existing.status = status.value
            existing.skill_points = skill_points
            session.commit()
            session.refresh(existing)
            return self._orm_to_order(existing)

    @staticmethod
    def _orm_to_order(orm_order: OrderORM) -> Order:
        """Convierte una instancia de OrderORM a una instancia de Order."""
        return Order(
            id=orm_order.id,
            user_id=orm_order.user_id,
            product_id=orm_order.product_id,
            quantity=orm_order.quantity,
            status=OrderStatus(orm_order.status),
            skill_points=orm_order.skill_points,
            created_at=orm_order.created_at,
        )
