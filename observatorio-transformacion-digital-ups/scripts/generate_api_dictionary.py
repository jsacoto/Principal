#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.main import app  # noqa: E402
from app.routers.catalog import DB_MAP, FRONTEND_MAP  # noqa: E402


def access(operation: dict) -> str:
    return "Autorizado" if operation.get("security") else "Público"


def main() -> None:
    schema = app.openapi()
    rows: list[tuple[str, str, str, str, str, str]] = []
    for path, item in sorted(schema.get("paths", {}).items()):
        if not path.startswith("/api/v1"):
            continue
        for method, op in item.items():
            m = method.upper()
            if m not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            tag = (op.get("tags") or ["other"])[0]
            db = ", ".join(f"`{x}`" for x in DB_MAP.get(tag, [])) or "-"
            frontend = FRONTEND_MAP.get((m, path)) or "-"
            rows.append((m, path, access(op), frontend, db, op.get("summary") or op.get("operationId") or ""))

    out = ROOT / "docs" / "API_DICTIONARY.md"
    lines = [
        "# Diccionario de APIs - Observatorio de Transformación Digital UPS",
        "",
        f"**Contrato:** OpenAPI {schema.get('openapi')} · **Versión API:** {schema['info']['version']} · **Prefijo canónico:** `/api/v1`",
        "",
        "La aplicación frontend consume exclusivamente el contrato versionado `/api/v1`. Las rutas históricas `/api/...` se mantienen de forma temporal para compatibilidad, pero no se publican en OpenAPI ni en SwaggerHub.",
        "",
        "## Puntos de documentación",
        "",
        "- Swagger UI: `/docs`",
        "- ReDoc: `/redoc`",
        "- Contrato OpenAPI JSON: `/openapi.json`",
        "- Catálogo ejecutable: `/api/v1/catalog`",
        "- Especificación versionada en repositorio: `openapi/openapi.json`",
        "- Catálogo SwaggerHub de la organización: https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c",
        "",
        "## Endpoints",
        "",
        "| Método | Endpoint | Acceso | Función frontend | Entidades principales | Propósito |",
        "|---|---|---|---|---|---|",
    ]
    for method, path, auth, frontend, db, summary in rows:
        summary = summary.replace("|", "\\|")
        lines.append(f"| `{method}` | `{path}` | {auth} | `{frontend}` | {db} | {summary} |")

    lines += [
        "",
        "## Convenciones",
        "",
        "- Las respuestas son JSON, excepto la descarga binaria de evidencias.",
        "- La autenticación usa la cookie HTTP-only `ups_td_session`; OpenAPI la declara como `UPSObservatorySession`.",
        "- Los endpoints de administración requieren rol `admin`.",
        "- Los endpoints de gestión verifican permisos por iniciativa antes de permitir modificaciones o descargas.",
        "- La API pública nunca expone contraseñas, hashes de sesión ni nombres internos de archivos almacenados.",
        "",
        "## Capas de consumo",
        "",
        "```text",
        "Next.js / apps/web/lib/api.ts",
        "             |",
        "             v",
        "       REST /api/v1",
        "             |",
        "             v",
        "FastAPI -> servicios analíticos / autorización -> SQLAlchemy -> PostgreSQL",
        "```",
        "",
        "El diccionario se regenera con `python scripts/generate_api_dictionary.py`. El contrato se regenera con `python scripts/export_openapi.py`.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"API dictionary generated: {out}")
    print(f"Endpoints: {len(rows)}")


if __name__ == "__main__":
    main()
