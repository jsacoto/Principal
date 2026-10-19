SHELL := /bin/bash

.PHONY: help mac-up mac-down mac-logs mac-test local-up local-down server-up server-down verify reset-mac api-contract

help:
	@echo "UPS Digital Maturity Observatory"
	@echo "  make mac-up      Entorno de desarrollo para Docker Desktop en Mac"
	@echo "  make mac-down    Detener entorno Mac"
	@echo "  make mac-logs    Seguir logs del entorno Mac"
	@echo "  make mac-test    Ejecutar pruebas Docker (API + web + smoke)"
	@echo "  make local-up    Stack local production-like"
	@echo "  make server-up   Stack de producción detrás de Nginx"
	@echo "  make verify      Pruebas rápidas sin Docker (backend + manifiestos)"
	@echo "  make api-contract Regenerar OpenAPI y diccionario de APIs"
	@echo "  make reset-mac   Eliminar volúmenes locales Mac"

mac-up:
	./scripts/start-mac.sh

mac-down:
	./scripts/stop.sh mac

mac-logs:
	docker compose -f docker-compose.mac.yml logs -f --tail=150

mac-test:
	./scripts/test-mac.sh

local-up:
	docker compose up --build -d

local-down:
	docker compose down

server-up:
	./scripts/start-server.sh

server-down:
	./scripts/stop.sh server

verify:
	./scripts/verify-local.sh

reset-mac:
	./scripts/reset-mac.sh

api-contract:
	python scripts/export_openapi.py
	python scripts/generate_api_dictionary.py
