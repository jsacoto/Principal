# Arquitectura

## Capas

### Presentación
Next.js App Router, React, TypeScript, Tailwind CSS, Recharts y Framer Motion. La UI usa superficies translúcidas, tipografía tabular para métricas, contraste adaptativo y navegación compacta.

### API y dominio
FastAPI + Pydantic v2. Los endpoints separan:

- `/api/observatory/*`: índices, brechas, simulación y calidad del dato.
- `/api/initiatives/*`: portafolio y trazabilidad actividad-responsable-evidencia.
- `/api/model/*`: dimensiones, objetivos, KRs y KPIs.

### Persistencia
PostgreSQL en Docker/servidor. SQLAlchemy 2 modela dimensiones, objetivos, iniciativas, actividades, responsables, evidencias, contribuciones I(i,d), KRs, KPIs, trazabilidad e historial de índices.

## Flujo analítico

1. Se toma Eᵢ desde `verified_progress` cuando existe; de lo contrario, `reported_progress`.
2. Se aplica la matriz `InitiativeDimension` para C_d y M_d.
3. Los KRs se normalizan y agregan por objetivo para IOC.
4. Los KPIs se normalizan para IKO.
5. IGTD combina IGMD, IOC(5) e IKO(5) con λ=(0.50, 0.30, 0.20).
6. El módulo de brechas prioriza contribuciones 2/3 sobre dimensiones M_d<3 y KRs<0.60.
7. What-If reemplaza temporalmente un Eᵢ y recalcula sin escribir en DB.
8. La verificación manual de avance persiste `verified_progress`, responsable, fecha y nota; ese Eᵢ prevalece sobre el avance reportado.
9. `TraceabilityRecord` mantiene aristas genéricas entre iniciativa, actividad, dimensión, objetivo, KR, KPI y evidencia. Los enlaces KPI→evidencia solo deben crearse cuando exista una definición institucional explícita; el seed no los inventa.

## Dos alcances del portafolio

- `institutional16`: portafolio conceptual de **16 iniciativas numeradas 1–16**. Los tracks 1.a/1.b, 3.a/3.b y 8.a/8.b se agregan por número institucional mediante media simple del avance disponible y máximo nivel de contribución por dimensión, evitando duplicar el denominador de la matriz I(i,d).
- `all`: portafolio operativo ampliado de **29 páginas de iniciativa** de Notion, hasta la Iniciativa 26.
- `reference16`: alias de compatibilidad para el cálculo agregado de 16 iniciativas.

La UI principal alterna `all` e `institutional16`. El Data Explorer conserva las 29 páginas operativas para trazabilidad completa.
