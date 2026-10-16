#!/usr/bin/env bash
set -euo pipefail

fail=0
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Aviso: este script fue diseñado para macOS; sistema detectado: $(uname -s)."
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker CLI no está disponible. Instale Docker Desktop para Mac."
  fail=1
elif ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker Desktop está instalado pero el daemon no está ejecutándose."
  fail=1
else
  echo "Docker: $(docker --version)"
  echo "Arquitectura: $(uname -m)"
  docker compose version
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl no está disponible."
  fail=1
fi

exit "$fail"
