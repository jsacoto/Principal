# Despliegue Docker en servidor

## Requisitos

- Linux x86_64 o ARM64.
- Docker Engine + Docker Compose v2.
- DNS y TLS institucional mediante reverse proxy, balanceador o gateway.

## Configuración

```bash
cp .env.server.example .env
```

Cambie al menos:

```env
POSTGRES_PASSWORD=<secreto-fuerte-bd>
INITIAL_ADMIN_PASSWORD=<secreto-fuerte-admin>
INITIAL_ADMIN_EMAIL=transformaciondigital@ups.edu.ec
PUBLIC_ORIGIN=https://observatorio.ups.edu.ec
SESSION_COOKIE_SECURE=true
APP_PORT=80
MAX_UPLOAD_MB=20
```

No guarde `.env` en Git.

## Arranque

```bash
./scripts/start-server.sh
```

El script rechaza los placeholders de contraseña y el dominio de ejemplo.

## Topología

```text
Internet / TLS institucional
           │
           ▼
       Nginx :80
       ├── /          → Next.js :3000
       ├── /api/*     → FastAPI :8000
       ├── /backend/* → Next.js rewrite → FastAPI
       ├── /docs      → FastAPI Swagger
       └── /healthz   → Nginx health
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
           PostgreSQL :5432     /data/uploads
            red privada        volumen persistente
```

PostgreSQL, FastAPI y Next.js no publican puertos al host en el manifiesto de producción.

## Persistencia

- Base de datos: volumen `postgres_data`.
- Evidencias subidas: volumen `uploads_data`.

Ambos deben incluirse en la política institucional de backup.

## Backup mínimo

PostgreSQL:

```bash
docker compose -f docker-compose.server.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

Evidencias: respalde el volumen `uploads_data` con la estrategia de backup de Docker/host empleada por la institución.

## Seguridad recomendada

- TLS público obligatorio.
- `SESSION_COOKIE_SECURE=true`.
- Contraseñas únicas y secret manager institucional.
- Restricción de acceso a `/docs` si el observatorio se publica en Internet.
- Antivirus/antimalware para archivos antes de una explotación institucional masiva.
- Política de retención y auditoría.
- SSO/OIDC institucional como evolución del módulo local de autenticación.
