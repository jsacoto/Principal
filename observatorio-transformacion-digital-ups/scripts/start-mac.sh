#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
./scripts/check-mac.sh
[ -f .env ] || cp .env.mac.example .env

docker compose -f docker-compose.mac.yml --env-file .env up --build -d

echo "Esperando servicios..."
for _ in $(seq 1 60); do
  if curl -fsS "http://localhost:${API_PORT:-8000}/health/ready" >/dev/null 2>&1 && \
     curl -fsS "http://localhost:${WEB_PORT:-3000}" >/dev/null 2>&1; then
    echo "Observatorio listo."
    echo "Web:     http://localhost:${WEB_PORT:-3000}"
    echo "API:     http://localhost:${API_PORT:-8000}"
    echo "Swagger: http://localhost:${API_PORT:-8000}/docs"
    echo "Acceso local inicial: transformaciondigital@ups.edu.ec"
    echo "Use la contraseña INITIAL_ADMIN_PASSWORD definida en .env."
    exit 0
  fi
  sleep 2
done

echo "ERROR: el stack no alcanzó estado saludable."
docker compose -f docker-compose.mac.yml --env-file .env ps
docker compose -f docker-compose.mac.yml --env-file .env logs --tail=120
exit 1
