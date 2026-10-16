# Procedencia y calidad de datos

## Fuente

Cartera Notion: `Cartera - Iniciativas de Transformación Digital`.
Instantánea de trabajo: 2026-10-16.

## Cobertura incluida

- 29 páginas operativas de iniciativa en Notion.
- Vista analítica adicional de 16 iniciativas conceptuales (1–16), agregando los tracks a/b cuando existen.
- 336 registros de fase/actividad.
- Objetivo OB/O normalizado, ámbito, descripción y avance reportado.
- Líderes de iniciativa.
- Responsables de actividad como IDs Notion cuando estaban presentes.
- Progreso de actividad cuando Notion lo registra numéricamente.
- Estado, prioridad, fechas, observaciones y contador de evidencias.

## No se persisten URLs firmadas de evidencia

Los adjuntos de Notion devuelven URLs firmadas con expiración corta. Guardarlas en el seed produciría enlaces rotos. Se conserva `evidence_count` y una referencia lógica; una futura sincronización con integración Notion debe obtener una URL nueva bajo demanda.

## Controles automáticos

El endpoint `/api/observatory/data-quality` detecta, entre otros:

- fechas de fin anteriores al inicio;
- actividades 100% que siguen como "En desarrollo";
- filas de prueba como "Hola";
- la discrepancia de la Iniciativa 24: título 0% frente a actividades marcadas como completas.

## Matriz de contribución

El brief menciona una matriz institucional I(i,d) de niveles 0..3, pero no suministra los valores oficiales. Para que el motor sea ejecutable se incluyó una matriz **provisional y explícitamente no validada**. Debe sustituirse por la matriz aprobada por la UPS cuando esté disponible.

## Datos creados en la plataforma

Las iniciativas creadas desde `/gestion/nueva` no se presentan como datos procedentes de Notion. Se identifican con `data_origin=platform_created`. Sus contribuciones D1–D5 se registran con `source=platform_template` y `validated=true`, porque son declaradas explícitamente por un administrador al crear la iniciativa.

Los archivos subidos desde Gestión se almacenan como `EvidenceUpload`; no sustituyen ni reescriben las evidencias históricas de Notion.
