# Entorno de pruebas en Mac

## Requisitos

- macOS 13+ recomendado.
- Docker Desktop con Docker Compose v2.
- 8 GB RAM mínimo; 12–16 GB recomendados.
- `curl`.

Las imágenes elegidas son multi-arquitectura y no fijan `linux/amd64`, por lo que funcionan en Mac Intel y Apple Silicon.

## Arranque de desarrollo

```bash
cp .env.mac.example .env
./scripts/start-mac.sh
```

Servicios:

- Portal: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Cuenta local inicial:

```text
transformaciondigital@ups.edu.ec
```

La contraseña se obtiene de `INITIAL_ADMIN_PASSWORD` en `.env`.

## Persistencia local

- PostgreSQL: `postgres_mac_data`.
- Evidencias: `uploads_mac_data`.

`./scripts/reset-mac.sh` elimina el entorno local y sus volúmenes, por lo que también borra las evidencias cargadas solo en esa instancia de prueba.

## Pruebas reproducibles

```bash
./scripts/test-mac.sh
```

### Etapa A — API

Construye el target `test` de FastAPI y ejecuta `pytest` contra PostgreSQL 16 efímero. La suite v2.0 cubre 11 pruebas, incluyendo autenticación, permisos, auditoría, archivos y nueva iniciativa.

### Etapa B — Frontend

Construye el target `test` de Next.js. Durante la imagen se ejecutan:

```bash
npm run typecheck
npm run build
```

### Etapa C — Smoke test

Arranca imágenes equivalentes a producción y comprueba:

- `/health/ready`;
- `/api/observatory/summary?scope=all`;
- `/`;
- `/model`;
- `/dimensions`;
- `/contact`.

## Prueba manual recomendada

1. Abra `http://localhost:3000` y confirme el dashboard público.
2. Revise Modelo TD, Dimensiones y Contacto.
3. Ingrese por Acceso autorizado.
4. Cree un usuario responsable desde Gestión → Usuarios.
5. Asigne una iniciativa.
6. Inicie sesión con esa cuenta.
7. Modifique una actividad con justificación.
8. Cargue un archivo `.pdf` o `.txt`.
9. Revise el Historial de la iniciativa.
