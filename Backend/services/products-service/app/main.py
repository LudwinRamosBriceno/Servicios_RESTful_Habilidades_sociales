from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .controller import router as product_router

app = FastAPI(title="NovaLink Products Service", version="1.0.0")
app.include_router(product_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": "products-service"}
