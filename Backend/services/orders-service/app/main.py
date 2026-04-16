from fastapi import FastAPI

from .controller import router as orders_router

app = FastAPI(title="NovaLink Orders Service", version="1.0.0")
app.include_router(orders_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": "orders-service"}
