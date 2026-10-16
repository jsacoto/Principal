import os
from pathlib import Path

DB = Path(__file__).parent / "test_observatory.db"
if DB.exists():
    DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{DB}"

from fastapi.testclient import TestClient
from app.main import app


def test_health_and_seeded_portfolio():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        ready = client.get("/health/ready")
        assert ready.status_code == 200
        assert ready.json()["database"] == "ok"
        initiatives = client.get("/api/initiatives").json()
        assert len(initiatives) == 29
        ref = client.get("/api/initiatives?scope=reference16").json()
        assert len(ref) == 16


def test_executive_summary_and_model():
    with TestClient(app) as client:
        summary = client.get("/api/observatory/summary").json()
        assert 0 <= summary["igtd"] <= 5
        assert len(summary["dimensions"]) == 5
        assert len(summary["objectives"]) == 5
        assert summary["reference_maturity"] == {"D1":4.0,"D2":3.0,"D3":2.5,"D4":3.5,"D5":2.0}
        assert summary["portfolio_count"] == 29
        assert summary["activity_count"] > 200
        model16 = client.get("/api/observatory/summary?scope=institutional16").json()
        assert model16["portfolio_count"] == 16
        assert model16["activity_count"] < summary["activity_count"]
        assert len(model16["dimensions"]) == 5


def test_initiative_detail_and_what_if():
    with TestClient(app) as client:
        initiative = client.get("/api/initiatives/1.a").json()
        assert initiative["code"] == "1.a"
        assert len(initiative["activities"]) >= 8
        simulation = client.post("/api/observatory/what-if", json={"initiative_code":"1.a","progress_percent":100}).json()
        assert simulation["simulated_progress_percent"] == 100
        assert "dimension_deltas" in simulation
        grouped = client.post("/api/observatory/what-if?scope=institutional16", json={"initiative_code":"1.a","progress_percent":100}).json()
        assert grouped["simulated_progress_percent"] == 100
        verified = client.patch("/api/initiatives/1.a/verification", json={"progress_percent":91.5,"verified_by":"Comité TD","note":"Validación de prueba con evidencia."})
        assert verified.status_code == 200
        body = verified.json()
        assert body["verified_progress"] == 91.5
        assert body["progress_verified_by"] == "Comité TD"


def test_data_quality_flags_known_issues():
    with TestClient(app) as client:
        quality = client.get("/api/observatory/data-quality").json()
        types = {x["type"] for x in quality["issues"]}
        assert "invalid_date_range" in types
        assert "initiative_progress_mismatch" in types
        assert "test_row" in types
