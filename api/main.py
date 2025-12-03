from fastapi import FastAPI
from api.auth.routes import router as auth_router

app = FastAPI(
    title="BizFiz Cloud",
    description="MVP Cloud + Storage backend",
    version="0.1"
)

app.include_router(auth_router, prefix="/auth")
