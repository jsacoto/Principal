# Observatorio de Transformación Digital UPS

Plataforma full-stack para gobernanza, trazabilidad y medición continua de la Transformación Digital de la Universidad Politécnica Salesiana (UPS).

La solución implementa la cadena metodológica:

**Iniciativa (Eᵢ) → Dimensión (D1–D5) → Objetivo (O1–O5) → KR → KPI → Evidencias → IGMD / IOC / IKO / IGTD**

## Arquitectura

```text
                         ┌───────────────────────────────┐
                         │ Observatorio TD UPS / Next.js │
                         └──────────────┬────────────────┘
                                        │
                                  /backend + /api
                                        │
                         ┌──────────────▼────────────────┐
                         │       FastAPI / Python         │
                         │ Motor IGMD · IOC · IKO · IGTD │
                         └──────────────┬────────────────┘
                                        │
                         ┌──────────────▼────────────────┐
                         │        PostgreSQL 16           │
                         └───────────────────────────────┘

Producción: Internet → Nginx → Next.js → FastAPI → PostgreSQL
```

## Datos incorporados

- **29 páginas de iniciativa** de la cartera Notion.
- **336 registros** entre fases, actividades y subactividades.
- **16 grupos institucionales** para preservar el modelo matemático original de cartera.
- Líderes, responsables, avance, estado, prioridad, fechas, observaciones y referencias de evidencia.
- KRs/KPIs de demostración marcados como `demo_seed`.
- Matriz I(i,d) inicial marcada como `provisional_mapping` hasta validación institucional.

## Tres entornos Docker

### Mac / desarrollo

```bash
cp .env.mac.example .env
./scripts/start-mac.sh
```

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### Pruebas Docker en Mac

```bash
./scripts/test-mac.sh
```

Ejecuta backend contra PostgreSQL efímero, TypeScript + build de Next.js y un smoke test full-stack.

### Producción / servidor

```bash
cp .env.server.example .env
./scripts/start-server.sh
```

El stack de producción expone únicamente Nginx; API, Web y PostgreSQL permanecen en la red Docker privada.

## Manifiestos

| Archivo | Uso |
|---|---|
| `docker-compose.mac.yml` | Desarrollo/hot reload en Docker Desktop para Mac |
| `docker-compose.test.yml` | Tests reproducibles + smoke test |
| `docker-compose.server.yml` | Producción con Nginx |
| `docker-compose.yml` | Stack local production-like |

## Validación

La versión publicada incluye:

- **8/8 tests backend** aprobados.
- **29 iniciativas**, **336 actividades/fases**, **16 grupos institucionales**.
- Verificación YAML de los cuatro manifiestos Compose.
- Verificación sintáctica de scripts shell.
- Smoke local del API y endpoint `/health/ready`.
- Verificación sintáctica TypeScript/TSX de 16 archivos.

Consulte `docs/VALIDATION_REPORT.md` y `docs/MAC_TEST_ENVIRONMENT.md`.

## Modelo UPS

- D1 Oferta Académica y Aprendizaje Digital
- D2 Experiencia Universitaria y Procesos
- D3 Sostenibilidad Económica y Analítica de Datos
- D4 Investigación, Vinculación e Innovación
- D5 Sostenibilidad Ambiental – Universidad Cero Emisiones

- O1 / OB1 Flexibilizar la oferta académica
- O2 / OB2 Mejorar experiencia del estudiante y colaborador
- O3 / OB3 Asegurar sostenibilidad económica con datos y modelos predictivos
- O4 / OB4 Articular docencia, investigación y vinculación
- O5 Universidad Cero Emisiones
