import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Configuración de url de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://products_user:products_pass@products-db:5432/products_db",
)

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Declaracion de la base para los modelos
class Base(DeclarativeBase):
    pass

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)