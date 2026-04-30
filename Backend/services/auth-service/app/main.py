from fastapi import FastAPI

from .controller import router as auth_router

app = FastAPI(title="NovaLink Auth Service", version="1.0.0")
app.include_router(auth_router)


@app.get("/health")
def healthcheck():
    """
    Ruta de salud para verificar que el servicio de autenticación está funcionando correctamente.
    """
    return {"status": "ok", "service": "auth-service"}

# Prueba Github Actions