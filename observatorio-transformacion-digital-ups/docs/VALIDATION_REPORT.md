# Validation report — Portal público + gestión autorizada v2.0

Validación realizada en el workspace de construcción el 2026-10-16.

## Backend

- Python compile check: OK.
- Suite: **11/11 tests passed**.
- Seed: **29 iniciativas**, **336 filas de actividad/fase**, **16 grupos institucionales**.
- Motor IGMD/IOC/IKO/IGTD: cubierto por tests previos.
- Login administrativo: cubierto.
- Alta de usuario responsable: cubierto.
- Permisos por iniciativa: cubiertos.
- Bloqueo de iniciativa no autorizada: cubierto (HTTP 403).
- Actualización de actividad con justificación: cubierta.
- Auditoría de cambio: cubierta.
- Carga de archivo de evidencia: cubierta.
- Descarga autorizada de evidencia: cubierta.
- Plantilla de nueva iniciativa: cubierta.
- Creación de nueva iniciativa alineada O1–O5 / D1–D5: cubierta.

## Frontend

- Parse/transpilación sintáctica de **28 archivos TypeScript/TSX**: OK con TypeScript 5.8 disponible en el workspace.
- Se añadieron las rutas públicas `/`, `/model`, `/dimensions`, `/contact`, `/login` y las rutas autorizadas `/gestion`, `/gestion/nueva`, `/gestion/usuarios`.

## Docker/Compose

Se valida sintaxis YAML de:

- `docker-compose.yml`
- `docker-compose.mac.yml`
- `docker-compose.test.yml`
- `docker-compose.server.yml`

Los manifiestos incorporan volumen persistente de evidencias y variables de autenticación.

## Limitación del workspace

Docker Engine no está instalado en este entorno de construcción; por ello no es posible arrancar físicamente los contenedores aquí. El cierre de validación en la Mac se realiza con:

```bash
./scripts/test-mac.sh
```

Ese flujo construye imágenes reales, ejecuta PostgreSQL efímero, los tests backend, `next build` y el smoke test de páginas públicas.
