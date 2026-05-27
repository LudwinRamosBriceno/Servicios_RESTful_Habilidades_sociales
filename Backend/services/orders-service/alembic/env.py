"""Entorno de migración de Alembic para el servicio de órdenes."""

from __future__ import with_statement

import os
from logging.config import fileConfig

import app.orm_models  # noqa: F401
from alembic import context
from app.db import Base
from sqlalchemy import engine_from_config, pool

# Este es el entorno de migración de Alembic.
# Configura el contexto de migración y ejecuta las migraciones según sea necesario.
config = context.config

# Si se proporciona una URL de base de datos a través de la variable de entorno DATABASE_URL,
# se actualiza la configuración de Alembic para usar esa URL en lugar de la predeterminada
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Configuración del registro de logging de Alembic utilizando el archivo de configuración especificado.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Se obtiene el objeto de metadatos de SQLAlchemy a partir de la clase base de los modelos ORM,
# que se utiliza para generar las migraciones basadas en los cambios en los modelos.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta las migraciones en modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta las migraciones en modo en linea."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Se determina el modo de ejecución (offline o en línea) y se ejecutan las migraciones en consecuencia.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
