from fastapi import FastAPI

from .controller import router as user_router

app = FastAPI(title="NovaLink Users Service", version="1.0.0")
app.include_router(user_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok", "service": "users-service"}
