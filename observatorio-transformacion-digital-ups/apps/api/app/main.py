from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers.admin import router as admin_router
from .routers.auth import router as auth_router
from .routers.initiatives import router as initiatives_router
from .routers.management import router as management_router
from .routers.model import router as model_router
from .routers.observatory import router as observatory_router
from .seed import seed_database
from .services.auth_seed import seed_initial_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
        seed_initial_admin(db)
    yield


settings = get_settings()
app = FastAPI(
    title="UPS Digital Maturity Observatory API",
    description="Public observatory plus authenticated governance workspace for UPS Digital Transformation.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ups-digital-observatory-api", "version": "2.0.0"}


@app.get("/health/ready")
def readiness():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok", "service": "ups-digital-observatory-api", "version": "2.0.0"}


app.include_router(observatory_router)
app.include_router(model_router)
app.include_router(initiatives_router)
app.include_router(auth_router)
app.include_router(management_router)
app.include_router(admin_router)
