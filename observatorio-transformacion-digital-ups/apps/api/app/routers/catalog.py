from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/catalog", tags=["api-catalog"])

FRONTEND_MAP = {
    ("GET", "/api/v1/observatory/summary"): "getSummary",
    ("GET", "/api/v1/observatory/gaps"): "getGaps",
    ("POST", "/api/v1/observatory/what-if"): "runWhatIf",
    ("GET", "/api/v1/observatory/data-quality"): "getQuality",
    ("GET", "/api/v1/model/dimensions"): "getDimensions",
    ("GET", "/api/v1/model/objectives"): "getObjectives",
    ("GET", "/api/v1/model/key-results"): "getKeyResults",
    ("GET", "/api/v1/model/kpis"): "getKpis",
    ("GET", "/api/v1/model/traceability"): "getTraceability",
    ("GET", "/api/v1/initiatives"): "getInitiatives",
    ("GET", "/api/v1/initiatives/{code}"): "getInitiative",
    ("PATCH", "/api/v1/initiatives/{code}/verification"): "verifyInitiative",
    ("POST", "/api/v1/auth/login"): "login",
    ("GET", "/api/v1/auth/me"): "getMe",
    ("POST", "/api/v1/auth/logout"): "logout",
    ("POST", "/api/v1/auth/change-password"): "changePassword",
    ("GET", "/api/v1/management/initiatives"): "getManagedInitiatives",
    ("GET", "/api/v1/management/initiatives/{code}"): "getManagedInitiative",
    ("PATCH", "/api/v1/management/activities/{activity_id}"): "updateManagedActivity",
    ("POST", "/api/v1/management/activities/{activity_id}/evidence"): "uploadActivityEvidence",
    ("GET", "/api/v1/management/initiatives/{code}/audit"): "getInitiativeAudit",
    ("GET", "/api/v1/admin/users"): "getAdminUsers",
    ("POST", "/api/v1/admin/users"): "createAdminUser",
    ("PATCH", "/api/v1/admin/users/{user_id}"): "updateAdminUser",
    ("GET", "/api/v1/admin/initiative-template"): "getInitiativeTemplate",
    ("POST", "/api/v1/admin/initiatives"): "createInitiative",
    ("GET", "/api/v1/forecast/schedule"): "getScheduleForecast",
    ("GET", "/api/v1/catalog"): "getApiCatalog",
}

DB_MAP = {
    "observatory": ["initiatives", "initiative_dimensions", "key_results", "kpis", "activities"],
    "model": ["dimensions", "objectives", "key_results", "kpis", "traceability_records"],
    "initiatives": ["initiatives", "initiative_leaders", "activities", "activity_assignees", "initiative_dimensions"],
    "authentication": ["users", "auth_sessions", "user_initiative_permissions"],
    "management": ["initiatives", "activities", "activity_progress_logs", "evidence_uploads", "traceability_records"],
    "administration": ["users", "user_initiative_permissions", "initiatives", "activities", "initiative_dimensions"],
    "forecasting": ["initiatives", "activities", "initiative_dimensions", "key_results", "kpis"],
    "api-catalog": [],
}


@router.get("", summary="Diccionario ejecutable de APIs")
def api_catalog(request: Request):
    schema = request.app.openapi()
    endpoints = []
    for path, path_item in sorted(schema.get("paths", {}).items()):
        if not path.startswith("/api/v1"):
            continue
        for method, operation in path_item.items():
            if method.upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            tags = operation.get("tags", [])
            tag = tags[0] if tags else "other"
            endpoints.append({
                "method": method.upper(),
                "path": path,
                "summary": operation.get("summary") or operation.get("operationId", ""),
                "tags": tags,
                "authentication": "session-cookie" if operation.get("security") else "public",
                "frontend_function": FRONTEND_MAP.get((method.upper(), path)),
                "database_entities": DB_MAP.get(tag, []),
                "operation_id": operation.get("operationId"),
            })
    return {
        "name": "UPS Digital Transformation Observatory API",
        "api_version": "v1",
        "contract_version": schema.get("info", {}).get("version"),
        "openapi": "/openapi.json",
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "swaggerhub_catalog": "https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c",
        "endpoint_count": len(endpoints),
        "endpoints": endpoints,
    }
