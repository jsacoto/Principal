# Matriz de entornos Docker

| Característica | Mac Dev | Test | Producción |
|---|---:|---:|---:|
| Archivo | `docker-compose.mac.yml` | `docker-compose.test.yml` | `docker-compose.server.yml` |
| Hot reload | Sí | No | No |
| PostgreSQL persistente | Sí | No (`tmpfs`) | Sí |
| API expuesta al host | Sí | No | No |
| Web expuesta al host | Sí | No | No |
| Nginx | No | No | Sí |
| API tests | Manual/host | Sí | No |
| Next typecheck/build | Durante imagen | Sí | Durante imagen |
| Full-stack smoke | Manual | Sí | Healthchecks |
| Contraseña local simple | Permitida | Efímera | Prohibida por script |

El objetivo es que el mismo código y los mismos Dockerfiles se utilicen durante desarrollo, validación y despliegue; solo cambia el target de imagen y la configuración de orquestación.
