import os
from datetime import date, timedelta
from pathlib import Path

DB = Path(__file__).parent / "test_contract.db"
if DB.exists():
    DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"
os.environ["INITIAL_ADMIN_EMAIL"] = "transformaciondigital@ups.edu.ec"
os.environ["INITIAL_ADMIN_PASSWORD"] = "Test-UPS-Digital-2026!"
os.environ["UPLOAD_DIR"] = str(Path(__file__).parent / "uploads-contract")

from fastapi.testclient import TestClient
from app.main import app


def test_v1_is_canonical_and_legacy_hidden_from_openapi():
    with TestClient(app) as client:
        assert client.get("/api/v1/observatory/summary?scope=all").status_code == 200
        assert client.get("/api/observatory/summary?scope=all").status_code == 200
        schema = client.get("/openapi.json").json()
        paths = schema["paths"]
        assert "/api/v1/observatory/summary" in paths
        assert "/api/observatory/summary" not in paths
        assert schema["info"]["version"] == "1.0.0"
        assert schema["info"]["x-platform-version"] == "3.1.0"


def test_api_catalog_links_frontend_and_database_entities():
    with TestClient(app) as client:
        payload = client.get("/api/v1/catalog").json()
        assert payload["api_version"] == "v1"
        assert payload["endpoint_count"] >= 25
        summary = next(x for x in payload["endpoints"] if x["path"] == "/api/v1/observatory/summary" and x["method"] == "GET")
        assert summary["frontend_function"] == "getSummary"
        assert "initiatives" in summary["database_entities"]


def test_openapi_declares_cookie_auth_for_protected_routes():
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        scheme = schema["components"]["securitySchemes"]["UPSObservatorySession"]
        assert scheme["type"] == "apiKey"
        assert scheme["in"] == "cookie"
        protected = schema["paths"]["/api/v1/management/initiatives"]["get"]
        assert protected["security"] == [{"UPSObservatorySession": []}]


def test_schedule_forecast_returns_non_regressive_scenario():
    with TestClient(app) as client:
        target = (date.today() + timedelta(days=365)).isoformat()
        response = client.get(f"/api/v1/forecast/schedule?target_date={target}&scope=all")
        assert response.status_code == 200
        body = response.json()
        assert body["model"] == "schedule-compliance-baseline-v1"
        assert body["projected"]["igmd"] >= body["current"]["igmd"] - 1e-6
        assert body["schedule_coverage"]["total_activities"] > 0
        assert len(body["initiatives"]) == 29
