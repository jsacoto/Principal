# Cliente de APIs del frontend

El frontend Next.js no accede directamente a PostgreSQL. Toda lectura o modificación atraviesa FastAPI.

## Punto de entrada

`apps/web/lib/api.ts`

Constante canónica:

```ts
const API = '/backend/api/v1';
```

En desarrollo Next.js reescribe `/backend/*` hacia FastAPI. En producción Nginx y Next.js mantienen el mismo contrato desde el navegador.

## Funciones principales

- `getSummary()` -> dashboard IGTD/IGMD/IOC/IKO.
- `getInitiatives()` / `getInitiative()` -> portafolio.
- `getDimensions()` / `getObjectives()` / `getKeyResults()` / `getKpis()` -> modelo.
- `runWhatIf()` -> simulador.
- `getScheduleForecast()` -> proyección por cronograma.
- `login()` / `logout()` / `getMe()` -> autenticación.
- `getManagedInitiatives()` / `updateManagedActivity()` -> gestión autorizada.
- `uploadActivityEvidence()` -> evidencias.
- `getInitiativeAudit()` -> historial y auditoría.
- `getAdminUsers()` / `createAdminUser()` / `updateAdminUser()` -> administración.
- `getInitiativeTemplate()` / `createInitiative()` -> nuevas iniciativas.
- `getApiCatalog()` -> diccionario de endpoints.

## Regla arquitectónica

No se deben introducir consultas SQL ni credenciales PostgreSQL en `apps/web`. Si una pantalla necesita información nueva:

1. se crea/expande un servicio en FastAPI;
2. se expone mediante `/api/v1`;
3. se documenta en OpenAPI;
4. se añade una función tipada a `apps/web/lib/api.ts`;
5. se actualiza el diccionario y pruebas del contrato.
