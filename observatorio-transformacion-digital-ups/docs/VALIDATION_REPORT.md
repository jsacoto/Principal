# Validation report - API Governance, SwaggerHub & Forecast Baseline v3.1

Validacion realizada en el workspace de construccion el 2026-10-19.

## Backend y contrato API

- Python compile check: **OK**.
- Suite backend: **15/15 tests passed**.
- Seed: **29 iniciativas**, **336 filas de actividad/fase**, **16 grupos institucionales**.
- Motor IGMD/IOC/IKO/IGTD: cubierto por pruebas automatizadas.
- Contrato REST canonico: **`/api/v1`**.
- Compatibilidad temporal `/api/...`: activa, pero excluida del contrato OpenAPI.
- OpenAPI: **3.1.0**, API contractual **1.0.0**.
- Contrato exportado: `openapi/openapi.json`.
- Diccionario generado: `docs/API_DICTIONARY.md`.
- Catalogo ejecutable: `GET /api/v1/catalog`.
- Seguridad OpenAPI: cookie HTTP-only `ups_td_session` declarada como `UPSObservatorySession`.
- Operaciones documentadas del contrato de negocio: **29 operaciones API** distribuidas en **28 rutas `/api/v1`**. El OpenAPI contiene 30 rutas totales al incluir health/documentacion tecnica.

## Autenticacion, permisos y evidencias

Las pruebas cubren:

- login administrativo;
- alta de usuario responsable;
- permisos por iniciativa;
- bloqueo de iniciativa no autorizada (HTTP 403);
- actualizacion de actividad con justificacion obligatoria;
- auditoria de cambio;
- carga y descarga autorizada de evidencia;
- plantilla de nueva iniciativa;
- creacion de iniciativa alineada O1-O5 / D1-D5;
- cambio de contrasena y renovacion de fecha de actualizacion.

## Pronostico por cronograma

- Endpoint: `GET /api/v1/forecast/schedule`.
- El escenario es **determinista**, no un modelo de IA.
- Proyecta el avance de actividades fechadas hacia 100% en su fecha fin y recalcula IGMD, IGTD y deltas D1-D5.
- Se valida que el escenario de cumplimiento no degrade artificialmente el indice respecto del estado base para el conjunto de prueba.
- Se documenta una hoja de ruta para evolucionar hacia pronosticos probabilisticos e IA en `docs/AI_FORECASTING_ROADMAP.md`.

## Frontend

- Cliente API centralizado en `apps/web/lib/api.ts`.
- El frontend consume exclusivamente **`/backend/api/v1`**; no accede directamente a PostgreSQL.
- Se incorporaron clientes para catalogo de APIs y pronostico por cronograma.
- Parseo sintactico TypeScript/TSX: **30/30 archivos OK** con TypeScript 5.8.3 disponible en el workspace.
- `npm run typecheck`/`next build` no se ejecutaron fuera de Docker porque `node_modules` no esta materializado en el workspace; el target Docker de pruebas realiza esa validacion en la Mac/servidor.
- Las rutas publicas y autorizadas de v3 se mantienen.

## SwaggerHub y CI/CD

- Workflow preparado: `.github/workflows/swaggerhub-openapi.yml`.
- Para el repositorio monolitico `jsacoto/Principal`, se publica ademas una copia ejecutable en la raiz: `.github/workflows/ups-observatory-swaggerhub.yml`.
- El workflow ejecuta tests, regenera OpenAPI/diccionario y conserva ambos como artefacto.
- La sincronizacion con SwaggerHub se activa solo cuando existen:
  - secret `SWAGGERHUB_API_KEY`;
  - variable `SWAGGERHUB_OWNER`.
- Puede configurarse opcionalmente nombre, version y visibilidad mediante variables de GitHub Actions.
- El `orgId` del enlace de Catalog no se usa como sustituto del Owner slug requerido por SwaggerHub CLI.

## Docker/Compose

Se valida sintaxis YAML de:

- `docker-compose.yml`;
- `docker-compose.mac.yml`;
- `docker-compose.test.yml`;
- `docker-compose.server.yml`.

El smoke test Docker referencia los endpoints canonicos `/api/v1`.

## Manual de usuario

- Manual Word: `Manual_Usuario_Observatorio_Transformacion_Digital_UPS_v3.1.docx`.
- Extension: **9 paginas**.
- Se realizo render completo a PNG y revision visual de las **9/9 paginas**.
- Resultado: sin recortes, solapamientos, tablas fuera de margen ni numeracion de procedimientos inconsistente.

## Limitacion del workspace

Docker Engine no esta instalado en este entorno de construccion; por ello no se arrancaron fisicamente los contenedores aqui. El cierre de validacion en la Mac se realiza con:

```bash
./scripts/test-mac.sh
```

Ese flujo construye imagenes reales, ejecuta PostgreSQL efimero, tests backend, `next build` y smoke test full-stack.

La publicacion real en SwaggerHub tampoco se ejecuta desde este workspace porque no dispone de credenciales SwaggerHub del usuario. Una vez configurados `SWAGGERHUB_API_KEY` y `SWAGGERHUB_OWNER` en GitHub Actions, el workflow realiza create/update, publish y set-default del contrato.
