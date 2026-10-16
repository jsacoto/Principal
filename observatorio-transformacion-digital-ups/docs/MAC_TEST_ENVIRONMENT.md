# Entorno de pruebas en Mac

## Requisitos

- macOS 13 o superior recomendado.
- Docker Desktop 4.x o superior con Docker Compose v2.
- 8 GB de RAM como mínimo; 12–16 GB recomendados para compilación fluida de Next.js.
- `curl`, incluido por defecto en macOS.

No se fija `platform: linux/amd64`; todas las imágenes seleccionadas son multi-arquitectura y pueden ejecutarse de forma nativa en Mac Intel y Apple Silicon.

## Comprobación

```bash
./scripts/check-mac.sh
```

## Desarrollo

```bash
cp .env.mac.example .env
./scripts/start-mac.sh
```

El entorno monta el código fuente dentro de los contenedores para hot reload. Los módulos Node y la caché `.next` se guardan en volúmenes Docker separados para evitar problemas entre el sistema de archivos macOS y Linux.

## Pruebas reproducibles

```bash
./scripts/test-mac.sh
```

### Etapa A — API

Construye el target `test` de FastAPI y ejecuta `pytest` contra PostgreSQL 16 efímero.

### Etapa B — Frontend

Construye el target `test` de Next.js. Durante el build se ejecutan:

```bash
npm run typecheck
npm run build
```

### Etapa C — Smoke test

Arranca imágenes equivalentes a producción y verifica:

- `/health/ready` de FastAPI;
- `/api/observatory/summary?scope=all`;
- respuesta HTTP del frontend.

## Reiniciar datos locales

```bash
./scripts/reset-mac.sh
```

Este comando elimina el volumen local de PostgreSQL del entorno Mac; no toca datos externos ni Notion.
