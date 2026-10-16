#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker Engine/Compose no está instalado."
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.server.example .env
  echo "Se creó .env desde .env.server.example. Edite POSTGRES_PASSWORD, INITIAL_ADMIN_PASSWORD y PUBLIC_ORIGIN antes de continuar."
  exit 1
fi

if grep -q 'CHANGE_THIS_WITH_A_LONG_RANDOM_SECRET' .env; then
  echo "ERROR: cambie POSTGRES_PASSWORD en .env."
  exit 1
fi

if grep -q 'CHANGE_THIS_ADMIN_PASSWORD_TOO' .env; then
  echo "ERROR: cambie INITIAL_ADMIN_PASSWORD en .env."
  exit 1
fi

if grep -q 'observatorio.example.edu.ec' .env; then
  echo "ERROR: cambie PUBLIC_ORIGIN en .env."
  exit 1
fi

if ! grep -q '^SESSION_COOKIE_SECURE=true' .env; then
  echo "ADVERTENCIA: en producción se recomienda SESSION_COOKIE_SECURE=true detrás de HTTPS."
fi

docker compose -f docker-compose.server.yml --env-file .env up --build -d

echo "Stack de producción iniciado en puerto ${APP_PORT:-80}."
echo "Compruebe: curl -fsS http://127.0.0.1:${APP_PORT:-80}/healthz"
echo "Los archivos de evidencia se conservan en el volumen Docker uploads_data."
