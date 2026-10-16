#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
./scripts/check-mac.sh

cleanup() {
  docker compose -f docker-compose.test.yml down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

echo "[1/3] Backend tests against ephemeral PostgreSQL"
docker compose -f docker-compose.test.yml build api-tests
docker compose -f docker-compose.test.yml run --rm api-tests

echo "[2/3] Frontend TypeScript + production build"
docker compose -f docker-compose.test.yml build web-tests
docker compose -f docker-compose.test.yml run --rm web-tests

echo "[3/3] Full-stack smoke test"
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from smoke postgres-test api-smoke web-smoke smoke

echo "Todos los tests Docker/Mac finalizaron correctamente."
