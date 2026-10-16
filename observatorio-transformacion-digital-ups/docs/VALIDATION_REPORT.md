# Validation report — Docker environment v1.1.0

Validation performed in the build workspace on 2026-10-16.

## Completed successfully

- Python compile check for the FastAPI application.
- Backend test suite: **8/8 passed**.
- Seed integrity: **29 initiatives**, **336 activity/phase rows**, **16 institutional groups**.
- API smoke run with SQLite fallback:
  - `GET /health/ready` → ready/database ok.
  - `GET /api/observatory/summary?scope=all` → returns IGTD and portfolio counts.
- YAML parsing of:
  - `docker-compose.yml`
  - `docker-compose.mac.yml`
  - `docker-compose.test.yml`
  - `docker-compose.server.yml`
- `bash -n` syntax validation for every shell script.
- TypeScript/TSX syntax transpilation: **16 source files parsed successfully**.

## Environment limitation

Docker Engine is not installed in the build workspace, so actual container startup could not be executed here. The Mac test environment is designed to close that gap with `./scripts/test-mac.sh`, which builds the API and Web images, runs the backend against ephemeral PostgreSQL, performs the Next.js typecheck/build, and finishes with a full-stack smoke test.

An attempted direct `npm install` in the build workspace timed out because external package access is restricted; dependency resolution is therefore intentionally delegated to Docker Desktop / Docker Engine in the target environment.
