import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Configuración de la base de datos utilizando SQLAlchemy ORM. 
# Se define la URL de conexión a la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@orders-db:5432/orders_db",
)

# Creación del motor de base de datos con la URL configurada y 
# habilitando el pool_pre_ping para verificar la conexión antes de usarla.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    """
    Clase base para los modelos ORM de SQLAlchemy. 
    Todos los modelos ORM deben heredar de esta clase para que SQLAlchemy pueda mapearlos 
    a las tablas correspondientes en la base de datos.
    """
    pass

# Creación de la fábrica de sesiones para interactuar con la base de datos.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
