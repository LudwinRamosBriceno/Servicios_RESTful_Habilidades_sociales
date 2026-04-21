from fastapi import FastAPI

from .controller import router as user_router

# Aplicacion principal del microservicio de usuarios.
app = FastAPI(title="NovaLink Users Service", version="1.0.0")
# Registra endpoints funcionales bajo el prefijo definido en el controller.
app.include_router(user_router)


@app.get("/health")
def healthcheck():
    """Endpoint para verificar disponibilidad del servicio."""
    # Utilizado por monitoreo/orquestadores para comprobar que el servicio responde.
    return {"status": "ok", "service": "users-service"}
