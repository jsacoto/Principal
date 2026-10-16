#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
read -r -p "Esto eliminará la base PostgreSQL local del Observatorio. ¿Continuar? [y/N] " answer
case "$answer" in
  y|Y|yes|YES)
    docker compose -f docker-compose.mac.yml down -v --remove-orphans
    echo "Entorno local reiniciado. Ejecute ./scripts/start-mac.sh para recrearlo."
    ;;
  *) echo "Cancelado." ;;
esac
