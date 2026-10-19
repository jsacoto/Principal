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
from .routers.catalog import router as catalog_router
from .routers.forecast import router as forecast_router
from .routers.initiatives import router as initiatives_router
from .routers.management import router as management_router
from .routers.model import router as model_router
from .routers.observatory import router as observatory_router
from .seed import seed_database
from .services.auth_seed import seed_initial_admin

PLATFORM_VERSION = "3.1.0"
API_CONTRACT_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
LEGACY_API_PREFIX = "/api"

OPENAPI_TAGS = [
    {"name": "observatory", "description": "Índices IGMD/IOC/IKO/IGTD, brechas, simulaciones y calidad del dato."},
    {"name": "model", "description": "Dimensiones D1-D5, objetivos O1-O5, KRs, KPIs y trazabilidad."},
    {"name": "initiatives", "description": "Consulta pública del portafolio y verificación autorizada de avance."},
    {"name": "authentication", "description": "Inicio/cierre de sesión y gestión de contraseña."},
    {"name": "management", "description": "Actualización autorizada de actividades, evidencias y auditoría."},
    {"name": "administration", "description": "Usuarios, permisos y creación de iniciativas basada en plantilla institucional."},
    {"name": "forecasting", "description": "Escenarios de proyección de madurez basados en cronogramas."},
    {"name": "api-catalog", "description": "Diccionario ejecutable de APIs y relación con el cliente frontend."},
]


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
    title="UPS Digital Transformation Observatory API",
    description=(
        "API REST del Observatorio de Transformación Digital de la Universidad Politécnica Salesiana. "
        "Expone el modelo D1-D5/O1-O5, el motor IGMD-IOC-IKO-IGTD, el portafolio de iniciativas, "
        "la gestión autorizada de avances/evidencias y escenarios de proyección. La ruta canónica es /api/v1; "
        "las rutas /api sin versión se mantienen temporalmente por compatibilidad y no se publican en OpenAPI."
    ),
    version=API_CONTRACT_VERSION,
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
    contact={"name": "Coordinación de Transformación Digital UPS", "email": "transformaciondigital@ups.edu.ec"},
    servers=[{"url": "/", "description": "Mismo host del Observatorio"}],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["api-catalog"], summary="Comprobar disponibilidad de la API")
def health():
    return {
        "status": "ok",
        "service": "ups-digital-observatory-api",
        "platform_version": PLATFORM_VERSION,
        "api_version": "v1",
        "contract_version": API_CONTRACT_VERSION,
    }


@app.get("/health/ready", tags=["api-catalog"], summary="Comprobar disponibilidad de API y base de datos")
def readiness():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "ok",
        "service": "ups-digital-observatory-api",
        "platform_version": PLATFORM_VERSION,
        "api_version": "v1",
        "contract_version": API_CONTRACT_VERSION,
    }


API_ROUTERS = [
    observatory_router,
    model_router,
    initiatives_router,
    auth_router,
    management_router,
    admin_router,
    forecast_router,
    catalog_router,
]

for router in API_ROUTERS:
    app.include_router(router, prefix=API_PREFIX)

# Compatibilidad con la versión 3.0. Estas rutas siguen funcionando para clientes antiguos,
# pero quedan fuera del contrato OpenAPI/SwaggerHub para evitar duplicación.
for router in API_ROUTERS:
    app.include_router(router, prefix=LEGACY_API_PREFIX, include_in_schema=False)


original_openapi = app.openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = original_openapi()
    schema["info"]["x-platform-version"] = PLATFORM_VERSION
    schema["info"]["x-contact-email"] = "transformaciondigital@ups.edu.ec"
    schema["info"]["x-swaggerhub-catalog"] = "https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c"
    schema["x-api-lifecycle"] = "active"
    schema["x-api-version-prefix"] = API_PREFIX
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
