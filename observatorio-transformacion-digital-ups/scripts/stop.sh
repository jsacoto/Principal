#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
MODE="${1:-mac}"
case "$MODE" in
  mac) docker compose -f docker-compose.mac.yml down ;;
  local) docker compose down ;;
  server) docker compose -f docker-compose.server.yml down ;;
  test) docker compose -f docker-compose.test.yml down -v --remove-orphans ;;
  *) echo "Uso: $0 [mac|local|server|test]"; exit 2 ;;
esac
