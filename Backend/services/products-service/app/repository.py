from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Product
from .orm_models import ProductORM


class ProductRepository:
    def __init__(self) -> None:
        self._session_factory = SessionLocal

    def save(self, product: Product) -> Product:
        with self._session_factory() as session:
            session: Session
            existing = session.get(ProductORM, product.id)
            if existing:
                existing.name = product.name
                existing.description = product.description
                existing.stock = product.stock
                existing.active = product.active
            else:
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
        statement = select(ProductORM)
        with self._session_factory() as session:
            session: Session
            orm_products = session.scalars(statement).all()
        return [self._orm_to_product(p) for p in orm_products]

    def find_by_id(self, product_id: str) -> Product | None:
        statement = select(ProductORM).where(ProductORM.id == product_id)
        with self._session_factory() as session:
            session: Session
            orm_product = session.scalars(statement).first()

        if not orm_product:
            return None
        return self._orm_to_product(orm_product)

    def delete(self, product_id: str) -> None:
        with self._session_factory() as session:
            session: Session
            existing = session.get(ProductORM, product_id)
            if not existing:
                return
            session.delete(existing)
            session.commit()

    @staticmethod
    def _orm_to_product(orm_product: ProductORM) -> Product:
        return Product(
            id=orm_product.id,
            name=orm_product.name,
            description=orm_product.description,
            stock=orm_product.stock,
            active=orm_product.active,
        )
