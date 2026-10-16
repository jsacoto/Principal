from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

ADMIN_EMAIL = "transformaciondigital@ups.edu.ec"
ADMIN_PASSWORD = "Test-UPS-Digital-2026!"


def login(client: TestClient, email: str, password: str):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["user"]


def test_admin_login_and_create_responsible_user():
    with TestClient(app) as client:
        admin = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
        assert admin["role"] == "admin"
        me = client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json()["user"]["email"] == ADMIN_EMAIL

        created = client.post("/api/admin/users", json={
            "name": "Responsable Prueba",
            "email": "responsable.prueba@ups.edu.ec",
            "password": "Responsable-2026!",
            "role": "responsible",
            "initiative_codes": ["1.a"],
        })
        assert created.status_code == 201, created.text
        body = created.json()
        assert body["initiative_codes"] == ["1.a"]


def test_responsible_permissions_progress_audit_and_upload():
    with TestClient(app) as client:
        user = login(client, "responsable.prueba@ups.edu.ec", "Responsable-2026!")
        assert user["role"] == "responsible"
        initiatives = client.get("/api/management/initiatives")
        assert initiatives.status_code == 200
        assert [x["code"] for x in initiatives.json()] == ["1.a"]

        forbidden = client.get("/api/management/initiatives/1.b")
        assert forbidden.status_code == 403

        detail = client.get("/api/management/initiatives/1.a")
        assert detail.status_code == 200
        activity = next(a for a in detail.json()["activities"] if a["activity_type"] == "activity")
        new_progress = min(100, (activity["progress"] or 0) + 1)
        updated = client.patch(f"/api/management/activities/{activity['id']}", json={
            "progress": new_progress,
            "state": "En desarrollo" if new_progress < 100 else "Completo",
            "priority": activity["priority"] or "Media",
            "start_date": activity["start_date"],
            "end_date": activity["end_date"],
            "observation": activity["observation"],
            "justification": "Actualización de prueba respaldada por evidencia documental.",
        })
        assert updated.status_code == 200, updated.text
        assert updated.json()["progress"] == new_progress

        upload = client.post(
            f"/api/management/activities/{activity['id']}/evidence",
            files={"file": ("evidencia-prueba.txt", b"evidencia de avance", "text/plain")},
            data={"description": "Documento de prueba para justificar el avance."},
        )
        assert upload.status_code == 201, upload.text
        evidence = upload.json()
        assert evidence["original_name"] == "evidencia-prueba.txt"
        download = client.get(f"/api/management/evidence/{evidence['id']}/download")
        assert download.status_code == 200
        assert download.content == b"evidencia de avance"

        audit = client.get("/api/management/initiatives/1.a/audit")
        assert audit.status_code == 200
        assert audit.json()["changes"]
        assert audit.json()["uploads"]


def test_admin_initiative_template_and_creation():
    with TestClient(app) as client:
        login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
        template = client.get("/api/admin/initiative-template")
        assert template.status_code == 200
        assert "Avance (%)" in template.json()["notion_template_fields"]
        assert len(template.json()["dimensions"]) == 5

        created = client.post("/api/admin/initiatives", json={
            "code": "TEST27",
            "objective_code": "O5",
            "scope": "Sostenibilidad",
            "description": "Iniciativa de prueba para validar la plantilla institucional del Observatorio.",
            "leader_name": "Responsable Prueba",
            "leader_email": "responsable.prueba@ups.edu.ec",
            "status": "Por Iniciar",
            "contributions": {"D1": 0, "D2": 0, "D3": 1, "D4": 0, "D5": 3},
            "activities": [{
                "external_id": "1",
                "title": "Levantar línea base ambiental y energética",
                "progress": 0,
                "state": "Por Iniciar",
                "priority": "Alta",
                "start_date": "2026-11-01",
                "end_date": "2026-12-15",
                "observation": "Actividad inicial de prueba.",
                "in_field": "LB-01",
                "responsible_name": "Responsable Prueba",
                "responsible_email": "responsable.prueba@ups.edu.ec",
            }],
        })
        assert created.status_code == 201, created.text
        assert created.json()["initiative"]["code"] == "TEST27"
        detail = client.get("/api/management/initiatives/TEST27")
        assert detail.status_code == 200
        assert detail.json()["contributions"]["D5"] == 3
