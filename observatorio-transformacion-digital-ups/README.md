# Observatorio de Transformación Digital UPS

Plataforma full-stack para **medición pública, gobernanza y trazabilidad autorizada** de la Transformación Digital de la Universidad Politécnica Salesiana (UPS).

La versión 3.1 mantiene la separación entre portal público y gestión autorizada, y añade un **contrato API versionado**, publicación automatizable en SwaggerHub y una línea base de pronóstico por cronograma:

1. **Portal público del Observatorio**: dashboard del Índice de Transformación Digital, modelo institucional, descripción de las dimensiones y contacto.
2. **Espacio de gestión autorizado**: responsables de iniciativas, actualización de actividades, justificaciones, evidencias, auditoría, usuarios y creación de nuevas iniciativas.

La cadena metodológica central es:

**Iniciativa (Eᵢ) → Dimensión (D1–D5) → Objetivo (O1–O5) → KR → KPI → Evidencias → IGMD / IOC / IKO / IGTD**

## Navegación pública

| Página | Contenido |
|---|---|
| **Inicio** | Dashboard ejecutivo con IGTD, IGMD, IOC, IKO, radar D1–D5, heatmap O1–O5 y alertas de calidad. |
| **Modelo TD** | Explicación del modelo de tres capas, objetivos, fórmulas y principio de trazabilidad. |
| **Dimensiones** | Descripción detallada de D1–D5, ámbitos observados y preguntas de gobernanza. |
| **Contacto** | Coordinación de Transformación Digital: `transformaciondigital@ups.edu.ec`. |
| **Acceso autorizado** | Inicio de sesión para responsables y administradores. |

## Gestión autorizada

La autenticación usa sesiones con token aleatorio almacenado **solo como hash** en PostgreSQL y cookie HTTP-only. El sistema incluye dos roles:

- **Administrador**: acceso a toda la cartera, creación de usuarios, asignación de permisos y creación de nuevas iniciativas.
- **Responsable**: puede gestionar únicamente las iniciativas que le hayan sido asignadas.

Los responsables pueden:

- modificar avance de actividades;
- actualizar estado, prioridad, fechas y observación;
- registrar una **justificación obligatoria** del cambio;
- adjuntar archivos de evidencia;
- descargar evidencias de sus iniciativas;
- consultar el historial de modificaciones.

Cada cambio de actividad conserva usuario, fecha, avance anterior/nuevo, estado anterior/nuevo y justificación en `activity_progress_logs`.

## Plantilla para nuevas iniciativas

La plantilla fue reconstruida a partir de la estructura observada en la cartera Notion UPS, incluyendo los campos de **Actividades principales**:

- Id;
- Actividades para la Implementación;
- Fecha Inicio;
- Fecha Fin;
- Avance (%);
- Responsable;
- Evidencias;
- Estado;
- In;
- Prioridad;
- Observación general.

La plataforma añade los elementos necesarios para el modelo del Observatorio:

- Objetivo O1–O5;
- ámbito;
- líder y correo;
- descripción;
- contribución `I(i,d)` a D1–D5 en escala 0–3.

Los archivos de evidencia de una iniciativa nueva se cargan desde **Gestión** una vez creada.

## Datos iniciales

La instantánea inicial incorpora:

- **29 páginas de iniciativa** de la cartera Notion;
- **336 registros** de fases, actividades y subactividades;
- **16 grupos institucionales** para preservar el modelo matemático original;
- líderes, responsables cuando Notion los expone, avance, estado, prioridad, fechas, observaciones y referencias de evidencia;
- KRs/KPIs de demostración marcados `demo_seed`;
- matriz histórica I(i,d) inicial marcada como provisional hasta validación institucional.

Las iniciativas creadas desde la nueva plantilla guardan sus contribuciones D1–D5 como `platform_template` y `validated=true`, ya que son definidas explícitamente por un administrador al registrarlas.

## Modelo UPS

### Dimensiones

- **D1** Oferta Académica y Aprendizaje Digital
- **D2** Experiencia Universitaria y Procesos
- **D3** Sostenibilidad Económica y Analítica de Datos
- **D4** Investigación, Vinculación e Innovación
- **D5** Sostenibilidad Ambiental – Universidad Cero Emisiones

### Objetivos

- **O1 / OB1** Flexibilizar la oferta académica
- **O2 / OB2** Mejorar experiencia del estudiante y colaborador
- **O3 / OB3** Asegurar sostenibilidad económica con datos y modelos predictivos
- **O4 / OB4** Articular docencia, investigación y vinculación
- **O5** Universidad Cero Emisiones

## Arquitectura

```text
                    PORTAL PUBLICO / GESTION AUTORIZADA
                               Next.js
                                  │
                            /backend/*
                                  │
                              FastAPI
               ┌──────────────────┼──────────────────┐
               │                  │                  │
        Motor analítico       Autorización      Evidencias
     IGMD/IOC/IKO/IGTD       RBAC + sesiones   /data/uploads
               │                  │                  │
               └──────────────────┴──────────────────┘
                                  │
                            PostgreSQL 16

Producción: Internet/TLS → Nginx → Next.js/FastAPI → PostgreSQL + volumen evidencias
```

## Desarrollo local en Mac

Requiere Docker Desktop.

```bash
cp .env.mac.example .env
./scripts/start-mac.sh
```

Servicios:

- Portal: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

La cuenta administrativa inicial local usa:

```text
transformaciondigital@ups.edu.ec
```

La contraseña se toma de `INITIAL_ADMIN_PASSWORD` en `.env`. El valor de `.env.mac.example` es **solo para pruebas locales** y no debe reutilizarse en producción.

Comandos:

```bash
make mac-up
make mac-logs
make mac-down
make reset-mac
```

Los archivos subidos desde la Mac se conservan en el volumen `uploads_mac_data`.

## Pruebas Docker en Mac

```bash
./scripts/test-mac.sh
```

Ejecuta:

1. tests FastAPI/engine/autenticación/permisos/evidencias contra PostgreSQL efímero;
2. TypeScript + `next build`;
3. smoke test del portal público.

## Producción / servidor

```bash
cp .env.server.example .env
```

Cambie obligatoriamente:

```env
POSTGRES_PASSWORD=una-clave-larga-y-segura
INITIAL_ADMIN_PASSWORD=otra-clave-larga-y-segura
PUBLIC_ORIGIN=https://observatorio.ups.edu.ec
SESSION_COOKIE_SECURE=true
```

Luego:

```bash
./scripts/start-server.sh
```

Producción expone únicamente **Nginx**. PostgreSQL, API y Web permanecen en la red Docker privada. Las evidencias se almacenan en el volumen persistente `uploads_data`.

## Manifiestos Docker

| Archivo | Uso |
|---|---|
| `docker-compose.mac.yml` | Desarrollo/hot reload en Docker Desktop para Mac |
| `docker-compose.test.yml` | Pruebas reproducibles y smoke test |
| `docker-compose.server.yml` | Producción con Nginx, PostgreSQL y volumen de evidencias |
| `docker-compose.yml` | Stack local production-like |

## API REST versionada

El contrato canónico es **`/api/v1`**. Las rutas antiguas `/api/...` se conservan temporalmente para compatibilidad, pero quedan fuera de OpenAPI/SwaggerHub. El frontend consume exclusivamente `/backend/api/v1`.

Puntos de documentación:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Diccionario ejecutable: `GET /api/v1/catalog`
- Contrato versionado en Git: `openapi/openapi.json`
- Diccionario humano: `docs/API_DICTIONARY.md`

Grupos principales:

```text
/api/v1/observatory/*   índices, brechas, what-if y calidad
/api/v1/model/*         D1-D5, O1-O5, KRs, KPIs y trazabilidad
/api/v1/initiatives/*   portafolio público y verificación
/api/v1/auth/*          autenticación
/api/v1/management/*    gestión autorizada, auditoría y evidencias
/api/v1/admin/*         usuarios, permisos y nuevas iniciativas
/api/v1/forecast/*      escenarios de proyección
/api/v1/catalog         diccionario de APIs
```

El endpoint de verificación sigue protegido por autenticación y permiso por iniciativa.


## SwaggerHub Catalog

El repositorio incluye `.github/workflows/swaggerhub-openapi.yml` para sincronizar el contrato con el catálogo suministrado:

`https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c`

La publicación requiere configurar en GitHub Actions el secret `SWAGGERHUB_API_KEY` y la variable `SWAGGERHUB_OWNER`. El workflow genera el contrato desde FastAPI, ejecuta tests y crea/actualiza la versión en SwaggerHub. Consulte `docs/SWAGGERHUB.md`.

## Pronóstico de madurez

La versión 3.1 añade una línea base determinista:

`GET /api/v1/forecast/schedule?target_date=YYYY-MM-DD&scope=all`

Responde a la pregunta: **“¿qué madurez alcanzaría la UPS si se cumplen los cronogramas registrados?”**. No se presenta como IA: sirve como referencia auditable antes de incorporar modelos probabilísticos. La propuesta de evolución hacia IA/LLM está en `docs/AI_FORECASTING_ROADMAP.md`.

## Validación

La versión 3.1 ejecuta **15/15 tests backend** y cubre, además del motor matemático:

- login administrativo;
- creación de responsable;
- asignación de permisos por iniciativa;
- bloqueo de acceso a iniciativas no autorizadas;
- actualización justificada de actividad;
- registro de auditoría;
- carga y descarga autorizada de evidencia;
- plantilla y creación de nueva iniciativa;
- contrato canónico `/api/v1` y compatibilidad legacy;
- seguridad de cookie declarada en OpenAPI;
- diccionario ejecutable de APIs;
- escenario de proyección de madurez por cronograma.

Consulte `docs/VALIDATION_REPORT.md`.

## Seguridad operativa

- API y Web corren como usuarios no root;
- `no-new-privileges` en producción;
- sesiones con tokens aleatorios almacenados como SHA-256 en DB;
- contraseñas con PBKDF2-HMAC-SHA256 (310.000 iteraciones + salt aleatorio);
- cookies HTTP-only, `SameSite=Lax` y `Secure=true` en producción;
- permisos por iniciativa;
- evidencias con nombre interno UUID y lista blanca de extensiones;
- límite de tamaño de archivo configurable (`MAX_UPLOAD_MB`, 20 MB por defecto);
- PostgreSQL no expuesto en producción;
- `.env` excluido de Git.

Para producción institucional se recomienda además TLS administrado por la UPS, secret manager, backups cifrados, política de retención, antivirus/antimalware para archivos y SSO institucional en una siguiente fase.

## Repositorio

`https://github.com/jsacoto/Principal/tree/main/observatorio-transformacion-digital-ups`


## Manual de usuario

**Manual de usuario:** [Manual_Usuario_Observatorio_Transformacion_Digital_UPS_v3.1.docx](./docs/Manual_Usuario_Observatorio_Transformacion_Digital_UPS_v3.1.docx)
