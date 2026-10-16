from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers.initiatives import router as initiatives_router
from .routers.model import router as model_router
from .routers.observatory import router as observatory_router
from .seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


settings = get_settings()
app = FastAPI(
    title="UPS Digital Maturity Observatory API",
    description="Three-layer digital transformation governance engine for the Universidad Politécnica Salesiana.",
    version="1.1.0",
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
    return {"status": "ok", "service": "ups-digital-observatory-api", "version": "1.1.0"}


@app.get("/health/ready")
def readiness():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok", "service": "ups-digital-observatory-api"}


app.include_router(observatory_router)
app.include_router(initiatives_router)
app.include_router(model_router)
