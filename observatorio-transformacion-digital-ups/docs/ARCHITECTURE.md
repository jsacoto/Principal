# Arquitectura v2.0

## 1. Portal público

Next.js App Router expone cinco áreas públicas:

- `/` — dashboard ejecutivo IGTD y D1–D5;
- `/model` — modelo de tres capas, objetivos y fórmulas;
- `/dimensions` — descripción de D1–D5;
- `/contact` — contacto institucional;
- `/login` — acceso autorizado.

La página principal consume únicamente endpoints analíticos de lectura.

## 2. Espacio autorizado

Rutas de interfaz:

- `/gestion` — cartera asignada, actualización de actividades, justificaciones y evidencias;
- `/gestion/nueva` — alta de nuevas iniciativas (administrador);
- `/gestion/usuarios` — usuarios y permisos (administrador).

FastAPI implementa sesiones persistidas en PostgreSQL. El navegador recibe una cookie HTTP-only; la base de datos guarda únicamente el hash SHA-256 del token de sesión.

### Roles

- `admin`: toda la cartera y administración.
- `responsible`: solo iniciativas vinculadas en `user_initiative_permissions`.

## 3. Trazabilidad de cambios

Una edición autorizada de actividad produce:

```text
Usuario autenticado
      │
      ▼
Permiso de iniciativa
      │
      ▼
PATCH actividad + justificación
      │
      ├── activity_progress_logs
      ├── recálculo de avance de iniciativa
      └── actualización de IGMD/IGTD en la siguiente lectura
```

La carga de evidencia genera `evidence_uploads` y una arista `TraceabilityRecord` actividad→evidencia.

## 4. Evidencias

Los archivos se guardan en `/data/uploads` con nombre físico UUID y metadatos en PostgreSQL. Docker monta esa ruta en:

- `uploads_mac_data` en Mac;
- `uploads_data` en local production-like y servidor.

La descarga exige sesión válida y permiso sobre la iniciativa.

## 5. Motor analítico

1. Se toma `verified_progress` cuando existe; en otro caso `reported_progress`.
2. La matriz `InitiativeDimension` produce cobertura `C_d` y madurez `M_d`.
3. KRs → IOC.
4. KPIs → IKO.
5. `IGTD = 0.50·IGMD + 0.30·IOC(5) + 0.20·IKO(5)` por defecto.
6. What-If recalcula sin persistir.
7. La vista `institutional16` mantiene las 16 iniciativas conceptuales históricas; las iniciativas nuevas entran al portafolio operativo `all`.

## 6. Persistencia

SQLAlchemy 2 / PostgreSQL 16 modela:

- dimensiones, objetivos, iniciativas, líderes, actividades y responsables;
- evidencias Notion y evidencias subidas a la plataforma;
- contribuciones I(i,d), KRs, KPIs, trazabilidad e historial de índices;
- usuarios, permisos, sesiones y auditoría de avances.

## 7. Despliegue

```text
Internet / TLS institucional
          │
          ▼
      Nginx gateway
       ┌────┴────┐
       ▼         ▼
    Next.js    FastAPI
                 │
        ┌────────┴────────┐
        ▼                 ▼
   PostgreSQL       uploads_data
```

Nginx es el único servicio publicado en producción.
