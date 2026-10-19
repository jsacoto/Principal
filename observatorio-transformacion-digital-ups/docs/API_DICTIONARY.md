# Diccionario de APIs - Observatorio de Transformación Digital UPS

**Contrato:** OpenAPI 3.1.0 · **Versión API:** 1.0.0 · **Prefijo canónico:** `/api/v1`

La aplicación frontend consume exclusivamente el contrato versionado `/api/v1`. Las rutas históricas `/api/...` se mantienen de forma temporal para compatibilidad, pero no se publican en OpenAPI ni en SwaggerHub.

## Puntos de documentación

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- Contrato OpenAPI JSON: `/openapi.json`
- Catálogo ejecutable: `/api/v1/catalog`
- Especificación versionada en repositorio: `openapi/openapi.json`
- Catálogo SwaggerHub de la organización: https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c

## Endpoints

| Método | Endpoint | Acceso | Función frontend | Entidades principales | Propósito |
|---|---|---|---|---|---|
| `GET` | `/api/v1/admin/initiative-template` | Autorizado | `getInitiativeTemplate` | `users`, `user_initiative_permissions`, `initiatives`, `activities`, `initiative_dimensions` | Initiative Template |
| `POST` | `/api/v1/admin/initiatives` | Autorizado | `createInitiative` | `users`, `user_initiative_permissions`, `initiatives`, `activities`, `initiative_dimensions` | Create Initiative |
| `GET` | `/api/v1/admin/users` | Autorizado | `getAdminUsers` | `users`, `user_initiative_permissions`, `initiatives`, `activities`, `initiative_dimensions` | List Users |
| `POST` | `/api/v1/admin/users` | Autorizado | `createAdminUser` | `users`, `user_initiative_permissions`, `initiatives`, `activities`, `initiative_dimensions` | Create User |
| `PATCH` | `/api/v1/admin/users/{user_id}` | Autorizado | `updateAdminUser` | `users`, `user_initiative_permissions`, `initiatives`, `activities`, `initiative_dimensions` | Update User |
| `POST` | `/api/v1/auth/change-password` | Autorizado | `changePassword` | `users`, `auth_sessions`, `user_initiative_permissions` | Change Password |
| `POST` | `/api/v1/auth/login` | Público | `login` | `users`, `auth_sessions`, `user_initiative_permissions` | Login |
| `POST` | `/api/v1/auth/logout` | Autorizado | `logout` | `users`, `auth_sessions`, `user_initiative_permissions` | Logout |
| `GET` | `/api/v1/auth/me` | Autorizado | `getMe` | `users`, `auth_sessions`, `user_initiative_permissions` | Me |
| `GET` | `/api/v1/catalog` | Público | `getApiCatalog` | - | Diccionario ejecutable de APIs |
| `GET` | `/api/v1/forecast/schedule` | Público | `getScheduleForecast` | `initiatives`, `activities`, `initiative_dimensions`, `key_results`, `kpis` | Proyectar la madurez bajo cumplimiento del cronograma |
| `GET` | `/api/v1/initiatives` | Público | `getInitiatives` | `initiatives`, `initiative_leaders`, `activities`, `activity_assignees`, `initiative_dimensions` | List Initiatives |
| `GET` | `/api/v1/initiatives/{code}` | Público | `getInitiative` | `initiatives`, `initiative_leaders`, `activities`, `activity_assignees`, `initiative_dimensions` | Get Initiative |
| `PATCH` | `/api/v1/initiatives/{code}/verification` | Autorizado | `verifyInitiative` | `initiatives`, `initiative_leaders`, `activities`, `activity_assignees`, `initiative_dimensions` | Verify Initiative Progress |
| `PATCH` | `/api/v1/management/activities/{activity_id}` | Autorizado | `updateManagedActivity` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Update Activity |
| `POST` | `/api/v1/management/activities/{activity_id}/evidence` | Autorizado | `uploadActivityEvidence` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Upload Evidence |
| `GET` | `/api/v1/management/evidence/{evidence_id}/download` | Autorizado | `-` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Download Evidence |
| `GET` | `/api/v1/management/initiatives` | Autorizado | `getManagedInitiatives` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Management Initiatives |
| `GET` | `/api/v1/management/initiatives/{code}` | Autorizado | `getManagedInitiative` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Management Initiative |
| `GET` | `/api/v1/management/initiatives/{code}/audit` | Autorizado | `getInitiativeAudit` | `initiatives`, `activities`, `activity_progress_logs`, `evidence_uploads`, `traceability_records` | Initiative Audit |
| `GET` | `/api/v1/model/dimensions` | Público | `getDimensions` | `dimensions`, `objectives`, `key_results`, `kpis`, `traceability_records` | Dimensions |
| `GET` | `/api/v1/model/key-results` | Público | `getKeyResults` | `dimensions`, `objectives`, `key_results`, `kpis`, `traceability_records` | Key Results |
| `GET` | `/api/v1/model/kpis` | Público | `getKpis` | `dimensions`, `objectives`, `key_results`, `kpis`, `traceability_records` | Kpis |
| `GET` | `/api/v1/model/objectives` | Público | `getObjectives` | `dimensions`, `objectives`, `key_results`, `kpis`, `traceability_records` | Objectives |
| `GET` | `/api/v1/model/traceability` | Público | `getTraceability` | `dimensions`, `objectives`, `key_results`, `kpis`, `traceability_records` | Traceability |
| `GET` | `/api/v1/observatory/data-quality` | Público | `getQuality` | `initiatives`, `initiative_dimensions`, `key_results`, `kpis`, `activities` | Get Data Quality |
| `GET` | `/api/v1/observatory/gaps` | Público | `getGaps` | `initiatives`, `initiative_dimensions`, `key_results`, `kpis`, `activities` | Get Gaps |
| `GET` | `/api/v1/observatory/summary` | Público | `getSummary` | `initiatives`, `initiative_dimensions`, `key_results`, `kpis`, `activities` | Get Summary |
| `POST` | `/api/v1/observatory/what-if` | Público | `runWhatIf` | `initiatives`, `initiative_dimensions`, `key_results`, `kpis`, `activities` | Simulate |

## Convenciones

- Las respuestas son JSON, excepto la descarga binaria de evidencias.
- La autenticación usa la cookie HTTP-only `ups_td_session`; OpenAPI la declara como `UPSObservatorySession`.
- Los endpoints de administración requieren rol `admin`.
- Los endpoints de gestión verifican permisos por iniciativa antes de permitir modificaciones o descargas.
- La API pública nunca expone contraseñas, hashes de sesión ni nombres internos de archivos almacenados.

## Capas de consumo

```text
Next.js / apps/web/lib/api.ts
             |
             v
       REST /api/v1
             |
             v
FastAPI -> servicios analíticos / autorización -> SQLAlchemy -> PostgreSQL
```

El diccionario se regenera con `python scripts/generate_api_dictionary.py`. El contrato se regenera con `python scripts/export_openapi.py`.
