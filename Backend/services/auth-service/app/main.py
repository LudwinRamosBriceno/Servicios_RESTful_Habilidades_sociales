"""Punto de entrada para el servicio de autenticación."""

from fastapi import FastAPI

from .controller import router as auth_router

app = FastAPI(title="NovaLink Auth Service", version="1.0.0")
app.include_router(auth_router)


@app.get("/health")
def healthcheck():
    """Ruta de salud para verificar el estado del servicio."""
    return {"status": "ok", "service": "auth-service"}
