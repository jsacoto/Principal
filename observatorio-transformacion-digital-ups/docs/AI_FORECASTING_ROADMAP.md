# Hoja de ruta de IA para pronóstico de madurez digital

## Recomendación

Sí es viable incorporar IA, pero **no se recomienda utilizar un LLM como motor numérico principal de pronóstico**. La arquitectura más sólida para el Observatorio es híbrida:

1. **Motor matemático institucional**: conserva C_d, M_d, IGMD, IOC, IKO e IGTD como reglas deterministas y auditables.
2. **Modelo de pronóstico**: estima el avance futuro E_i(t) y/o la probabilidad de cumplimiento de actividades e iniciativas.
3. **LLM + RAG**: interpreta evidencias, justificaciones y observaciones; explica los resultados; responde preguntas en lenguaje natural; nunca sustituye las fórmulas institucionales.

## Fase 0 implementada: escenario de cumplimiento del cronograma

Endpoint:

`GET /api/v1/forecast/schedule?target_date=YYYY-MM-DD&scope=all`

Este escenario no es IA. Proyecta cada actividad con fecha fin para que alcance 100% en su fecha comprometida y recalcula IGMD e IGTD. Las actividades sin fecha fin mantienen su avance actual.

Es útil como **línea base contrafactual**: “¿qué nivel de madurez alcanzaríamos si se cumplen los cronogramas registrados?”.

## Fase 1 recomendada: pronóstico probabilístico

Con historial suficiente, cada actividad puede estimar:

- probabilidad de terminar antes de la fecha objetivo;
- avance esperado por fecha;
- P10/P50/P90 del avance;
- riesgo de retraso;
- probabilidad de que una iniciativa alcance hitos de 60%, 80% y 100%.

Esos resultados alimentan el motor existente:

`E_i(t) -> C_d(t) -> M_d(t) -> IGMD(t) -> IGTD(t)`

El resultado debe mostrar intervalos, no una única cifra:

- IGTD esperado;
- rango P10-P90;
- dimensiones con mayor incertidumbre;
- iniciativas que explican el riesgo.

## Fase 2: modelos recomendados

### Con pocos datos históricos

Preferir:

- Monte Carlo sobre duraciones y retrasos;
- modelos bayesianos jerárquicos;
- supervivencia / hazard models para probabilidad de terminación;
- reglas de riesgo basadas en desvío de cronograma.

Son más interpretables y adecuados cuando todavía existen pocas iniciativas.

### Con un historial mediano

Cuando existan cientos o miles de observaciones temporales de actividades:

- Gradient Boosting (XGBoost/LightGBM/CatBoost);
- modelos de series temporales probabilísticas;
- Temporal Fusion Transformer si el volumen y la frecuencia temporal justifican su complejidad.

Variables sugeridas:

- avance semanal/mensual;
- días desde último cambio;
- retrasos acumulados;
- duración planificada vs. real;
- número de reprogramaciones;
- prioridad;
- responsable;
- dependencias;
- cantidad/calidad de evidencias;
- contribución I(i,d);
- objetivo O1-O5;
- dimensión D1-D5;
- estado de KRs/KPIs relacionados.

## Fase 3: LLM/RAG institucional

El LLM aporta mayor valor en tareas semánticas:

- resumir evidencias adjuntas;
- extraer hitos, fechas, responsables y riesgos de documentos;
- clasificar justificaciones de retraso;
- generar un resumen ejecutivo de por qué cambia IGTD;
- contestar “¿qué iniciativas explican la caída de D3?”;
- comparar escenarios;
- generar recomendaciones basadas en reglas y datos recuperados del Observatorio.

El LLM debe usar RAG sobre datos autorizados y respetar los permisos por iniciativa.

## Arquitectura propuesta

```text
PostgreSQL + Evidencias
        |
        +--> Feature/History Store
        |          |
        |          +--> Forecast Engine (Monte Carlo / ML)
        |                         |
        |                         v
        |                    E_i(t) probabilístico
        |                         |
        +-------------------------+
                                  v
                    Motor institucional IGMD/IOC/IKO/IGTD
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
            Dashboard de pronóstico       LLM + RAG
            P10 / P50 / P90              explicación y consulta
```

## Datos que deben empezar a almacenarse ahora

Para que una futura IA sea defendible, registrar desde ya:

- snapshot de avance de cada actividad en cada actualización;
- fecha/hora del cambio;
- usuario responsable;
- fecha planificada inicial y fecha reprogramada;
- fecha real de terminación;
- justificación textual;
- evidencias asociadas;
- dependencias entre actividades;
- historial de contribuciones D1-D5;
- historial de KRs/KPIs;
- versiones históricas de IGMD/IOC/IKO/IGTD.

La tabla `activity_progress_logs` ya constituye un primer historial, pero debe ampliarse con eventos de cronograma y snapshots periódicos.

## Gobierno y explicabilidad

- Ningún modelo debe modificar avances automáticamente.
- Las predicciones deben registrar versión del modelo, fecha, variables y horizonte.
- El dashboard debe distinguir “dato observado”, “escenario determinista” y “predicción IA”.
- Las predicciones deben incluir incertidumbre y principales factores explicativos.
- Las evidencias utilizadas por un LLM deben respetar RBAC y trazabilidad.
- Para información institucional sensible, considerar modelos privados/on-premise o proveedores con acuerdos institucionales apropiados.

## API futura sugerida

- `POST /api/v1/ai/forecast` -> pronóstico probabilístico IGMD/IGTD.
- `GET /api/v1/ai/forecast/{run_id}` -> resultados, P10/P50/P90 y variables.
- `POST /api/v1/ai/explain` -> explicación de un cambio o escenario.
- `POST /api/v1/ai/evidence/analyze` -> extracción estructurada desde evidencias.
- `POST /api/v1/ai/query` -> consulta RAG sobre el Observatorio respetando permisos.

La implementación debe iniciarse cuando se disponga de una base temporal suficientemente completa para entrenar o calibrar el modelo de riesgo.
