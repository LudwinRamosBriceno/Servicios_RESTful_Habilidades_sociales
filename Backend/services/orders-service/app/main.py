from fastapi import FastAPI
from alembic import command
from alembic.config import Config
from pathlib import Path

from .controller import router as orders_router

# Inicialización de la aplicación FastAPI y registro del enrutador de órdenes.
app = FastAPI(title="NovaLink Orders Service", version="1.0.0")
app.include_router(orders_router)


@app.on_event("startup")
def run_db_migrations() -> None:
    """
    Ejecuta las migraciones de Alembic al iniciar el servicio.
    """
    root_dir = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    command.upgrade(alembic_cfg, "head")

@app.get("/health")
def healthcheck():
    """
    Ruta de salud para verificar que el servicio de órdenes está funcionando correctamente. 
    Devuelve un mensaje de estado.
    """
    return {"status": "ok", "service": "orders-service"}
