import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Configuracion central de acceso a base de datos para users-service.
# Usa variable de entorno y fallback para entorno local/docker.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://users_user:users_pass@users-db:5432/users_db",
)

# Motor SQLAlchemy compartido; pool_pre_ping evita usar conexiones muertas.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    # Base declarativa para todos los modelos ORM del servicio.
    pass


# Fabrica de sesiones: cada uso debe controlar commit/rollback de forma explicita.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)