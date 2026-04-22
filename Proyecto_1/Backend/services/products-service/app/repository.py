from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session # para manejar las sesiones de base de datos

from .db import SessionLocal
from .models import Product
from .orm_models import ProductORM

# Repositorio con la lógica de acceso a la base de datos, para crear, leer, actualizar y eliminar productos. 
class ProductRepository:
    def __init__(self) -> None:
        self._session_factory = SessionLocal # crea nuevas sesiones de base de datos para cada operación

    def save(self, product: Product) -> Product:
        with self._session_factory() as session:
            session: Session
            existing = session.get(ProductORM, product.id) # verifica si el producto ya existe en la base de datos

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

    # Devuelve una lista de todos los productos en la base de datos (aunque no tengan stock).
    def find_all(self) -> List[Product]:

        # Se crea la consulta SQL mediante SQLAlchemy para seleccionar todos los productos de la tabla products
        statement = select(ProductORM)

        with self._session_factory() as session:
            session: Session
            orm_products = session.scalars(statement).all() # ejecuta la consulta y obtiene todos los productos como objetos ORM
        return [self._orm_to_product(p) for p in orm_products]

    # Devuelve un producto específico por su ID, o None si no se encuentra.
    def find_by_id(self, product_id: str) -> Product | None:
        # Se crea la consulta SQL mediante SQLAlchemy para seleccionar el producto con el ID especificado
        statement = select(ProductORM).where(ProductORM.id == product_id)

        with self._session_factory() as session:
            session: Session
            orm_product = session.scalars(statement).first() # ejecuta la consulta y obtiene el primer resultado (o None si no se encuentra)

        if not orm_product:
            return None
        return self._orm_to_product(orm_product)

    # Elimina un producto de la base de datos por su ID. Si el producto no existe, no hace nada.
    def delete(self, product_id: str) -> None:
        with self._session_factory() as session:
            session: Session
            existing = session.get(ProductORM, product_id) # verifica si el producto existe en la base de datos
            if not existing:
                return
            session.delete(existing)
            session.commit()

    # Convierte un objeto ORM de producto a un objeto de Product (clase de Python).
    @staticmethod
    def _orm_to_product(orm_product: ProductORM) -> Product:
        return Product(
            id=orm_product.id,
            name=orm_product.name,
            description=orm_product.description,
            stock=orm_product.stock,
            active=orm_product.active,
        )
