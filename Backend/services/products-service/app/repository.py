"""Repositorio de productos persistente con SQLAlchemy ORM."""

from typing import List

from models import Product
from orm_models import ProductORM
from sqlalchemy import select
from sqlalchemy.orm import Session  # para manejar las sesiones de base de datos


class ProductRepository:
    """Repositorio para crear, leer, actualizar y eliminar productos."""

    def __init__(self, session_factory):
        """Crea nuevas sesiones de base de datos para cada operación."""
        self._session_factory = session_factory

    def save(self, product: Product) -> Product:
        """Guarda un producto en la base de datos."""
        with self._session_factory() as session:
            session: Session
            existing = session.get(
                ProductORM, product.id
            )  # verifica si el producto ya existe en la base de datos

            # Si el producto existe, actualiza sus campos.
            if existing:
                existing.name = product.name
                existing.description = product.description
                existing.stock = product.stock
                existing.active = product.active
            else:
                # Si el producto no existe, lo agrega como un nuevo registro.
                session.add(
                    ProductORM(
                        id=product.id,
                        name=product.name,
                        description=product.description,
                        stock=product.stock,
                        active=product.active,
                    )
                )
            session.commit()
        return product

    def find_all(self) -> List[Product]:
        """Devuelve una lista de todos los productos en la base de datos."""
        # Se crea la consulta SQL mediante SQLAlchemy para seleccionar todos los productos de la tabla products
        statement = select(ProductORM)

        with self._session_factory() as session:
            session: Session
            orm_products = session.scalars(
                statement
            ).all()  # ejecuta la consulta y obtiene todos los productos como objetos ORM
        return [self._orm_to_product(p) for p in orm_products]

    def find_by_id(self, product_id: str) -> Product | None:
        """Devuelve un producto por su ID, o None si no se encuentra."""
        # Se crea la consulta SQL mediante SQLAlchemy para seleccionar el producto con el ID especificado
        statement = select(ProductORM).where(ProductORM.id == product_id)

        with self._session_factory() as session:
            session: Session
            orm_product = session.scalars(
                statement
            ).first()  # ejecuta la consulta y obtiene el primer resultado (o None si no se encuentra)

        if not orm_product:
            return None
        return self._orm_to_product(orm_product)

    def delete(self, product_id: str) -> None:
        """Elimina un producto por su ID si existe."""
        with self._session_factory() as session:
            session: Session
            existing = session.get(
                ProductORM, product_id
            )  # verifica si el producto existe en la base de datos
            if not existing:
                return
            session.delete(existing)
            session.commit()

    @staticmethod
    def _orm_to_product(orm_product: ProductORM) -> Product:
        """Convierte un objeto ORM a un objeto Product."""
        return Product(
            id=orm_product.id,
            name=orm_product.name,
            description=orm_product.description,
            stock=orm_product.stock,
            active=orm_product.active,
        )
