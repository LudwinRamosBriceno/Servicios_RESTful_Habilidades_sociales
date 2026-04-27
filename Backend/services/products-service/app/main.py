from fastapi import FastAPI

from .controller import router as product_router

app = FastAPI(title="NovaLink Products Service", version="1.0.0")
app.include_router(product_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": "products-service"}
