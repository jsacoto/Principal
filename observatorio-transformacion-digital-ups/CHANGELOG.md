# Changelog

## 2.0.0 — Portal público + gestión autorizada

- Nueva navegación pública: Inicio, Modelo TD, Dimensiones, Contacto y Acceso autorizado.
- Página principal con dashboard IGTD y madurez D1–D5.
- Página explicativa del modelo de tres capas y objetivos O1–O5.
- Página detallada de D1–D5.
- Contacto institucional `transformaciondigital@ups.edu.ec`.
- Autenticación local segura con sesiones HTTP-only, PBKDF2 y tokens almacenados como hash.
- Roles `admin` y `responsible` con permisos por iniciativa.
- Edición autorizada de actividades con justificación obligatoria.
- Historial auditable de cambios de avance/estado.
- Carga/descarga autorizada de archivos de evidencia.
- Volúmenes Docker persistentes para evidencias.
- Gestión administrativa de usuarios y permisos.
- Formulario de nuevas iniciativas basado en la plantilla Notion UPS y alineado a O1–O5 / D1–D5.
- Protección del endpoint histórico de verificación de avance.
- Suite backend ampliada a 11 tests.

## 1.1.0 — Docker environments

- Añadido entorno Mac con hot reload (`docker-compose.mac.yml`).
- Añadido entorno de pruebas reproducibles (`docker-compose.test.yml`).
- Endurecido despliegue de servidor con Nginx, healthchecks, red privada y rotación de logs.
- Dockerfiles multi-stage para API y Web.
- Contenedores de aplicación no root.
- Endpoint `/health/ready` con comprobación real de base de datos.
- Scripts `check-mac`, `test-mac`, `reset-mac` y Makefile.
- Documentación separada para Mac, testing y servidor.
