# Matriz de entornos Docker

| Característica | Mac Dev | Test | Producción |
|---|---:|---:|---:|
| Archivo | `docker-compose.mac.yml` | `docker-compose.test.yml` | `docker-compose.server.yml` |
| Hot reload | Sí | No | No |
| PostgreSQL persistente | Sí | No (`tmpfs`) | Sí |
| Evidencias persistentes | Sí (`uploads_mac_data`) | No | Sí (`uploads_data`) |
| API expuesta al host | Sí | No | No |
| Web expuesta al host | Sí | No | No |
| Nginx | No | No | Sí |
| Autenticación/RBAC | Sí | Sí | Sí |
| API tests | Manual/host | Sí | No |
| Next typecheck/build | Durante imagen | Sí | Durante imagen |
| Smoke portal público | Manual | Sí | Healthchecks |
| Cookie Secure | No | No | Sí |
| Contraseña de ejemplo | Solo local | Efímera | Rechazada por script |

El mismo código y los mismos Dockerfiles se utilizan en desarrollo, validación y despliegue; cambian el target de imagen, persistencia y configuración de seguridad.
