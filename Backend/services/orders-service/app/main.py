from fastapi import FastAPI
from alembic import command
from alembic.config import Config
from pathlib import Path
import os

from .controller import router as orders_router

# Inicialización de la aplicación FastAPI y registro del enrutador de órdenes.
app = FastAPI(title="NovaLink Orders Service", version="1.0.0")
app.include_router(orders_router)


@app.on_event("startup")
def run_db_migrations() -> None:
    """
    Ejecuta las migraciones de Alembic al iniciar el servicio.
    """
    if os.getenv("RUN_DB_MIGRATIONS_ON_STARTUP", "false").lower() != "true":
        print("[orders-service] Startup migrations disabled (RUN_DB_MIGRATIONS_ON_STARTUP!=true).")
        return

    root_dir = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(root_dir / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(root_dir / "alembic"))
    try:
        command.upgrade(alembic_cfg, "head")
    except SystemExit as exc:
        # Alembic can raise SystemExit when invoked programmatically in some environments.
        # Migrations already logged as executed; avoid killing the API process.
        print(f"[orders-service] Alembic exited during startup with code={exc.code}; continuing.")

@app.get("/health")
def healthcheck():
    """
    Ruta de salud para verificar que el servicio de órdenes está funcionando correctamente. 
    Devuelve un mensaje de estado.
    """
    return {"status": "ok", "service": "orders-service"}
