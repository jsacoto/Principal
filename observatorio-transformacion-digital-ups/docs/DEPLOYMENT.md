# Despliegue Docker en servidor

## Requisitos

- Linux x86_64 o ARM64.
- Docker Engine + Compose v2.
- DNS y TLS administrados por la institución, reverse proxy o balanceador.

## Configuración

```bash
cp .env.server.example .env
```

Defina al menos:

```env
POSTGRES_PASSWORD=<secreto-fuerte>
PUBLIC_ORIGIN=https://observatorio.ups.edu.ec
APP_PORT=80
```

No guarde `.env` en Git.

## Arranque

```bash
./scripts/start-server.sh
```

## Topología

```text
Internet/TLS terminator
        │
        ▼
      Nginx :80
      ├── /        → Next.js :3000
      ├── /api/*   → FastAPI :8000
      ├── /docs    → FastAPI Swagger
      └── /healthz → Nginx health
                       │
                       ▼
                 PostgreSQL :5432
                (red privada Docker)
```

PostgreSQL, FastAPI y Next.js no publican puertos al host en el manifiesto de producción.

## Operación

```bash
docker compose -f docker-compose.server.yml ps
docker compose -f docker-compose.server.yml logs -f --tail=200
docker compose -f docker-compose.server.yml pull
docker compose -f docker-compose.server.yml up --build -d
```

## Backup mínimo de PostgreSQL

Ejemplo manual:

```bash
docker compose -f docker-compose.server.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

La política institucional debe definir retención, cifrado, ubicación y pruebas de restauración.
