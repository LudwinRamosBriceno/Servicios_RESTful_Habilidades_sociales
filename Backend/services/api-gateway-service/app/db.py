"""Configuración de la base de datos para el API Gateway."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Configuracion central de acceso a base de datos para el gateway.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://gateway_user:gateway_pass@gateway-db:5432/gateway_db",
)

# Motor SQLAlchemy compartido; pool_pre_ping evita conexiones muertas.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    """Base declarativa para modelos ORM del gateway."""

    pass


# Fabrica de sesiones para operaciones en la base de datos.
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, class_=Session
)
