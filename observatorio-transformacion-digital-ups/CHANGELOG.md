# Changelog

## 1.1.0 — Docker environments

- Añadido entorno Mac con hot reload (`docker-compose.mac.yml`).
- Añadido entorno de pruebas reproducibles (`docker-compose.test.yml`).
- Endurecido despliegue de servidor con Nginx, healthchecks, red privada y rotación de logs.
- Dockerfiles multi-stage para API y Web.
- Contenedores de aplicación no root.
- Endpoint `/health/ready` con comprobación real de base de datos.
- Scripts `check-mac`, `test-mac`, `reset-mac` y Makefile.
- Documentación separada para Mac, testing y servidor.
