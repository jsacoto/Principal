# Revisión de la versión adjunta `ups-digital-observatory-v3.zip`

Fecha de revisión: 2026-10-19.

## Objetivo

Comparar la versión adjunta con la versión vigente del Observatorio TD UPS sin perder los cambios posteriores ya incorporados: API `/api/v1`, OpenAPI/SwaggerHub, pronóstico por cronograma, manual de usuario, seguridad y Docker.

## Resultado sobre el modelo matemático

**No se detectó modificación de las ecuaciones institucionales.** La comparación del `engine.py` mostró únicamente comentarios y docstrings explicativos. Se mantienen exactamente:

- `C_d = sum(E_i * I_i,d) / sum(I_i,d)`;
- `M_d = 5 * C_d`;
- `IGMD = sum(v_d * M_d)`;
- normalización de KRs de crecimiento/reducción;
- `IOC` e `IOC(5)`;
- normalización de KPIs;
- `IKO` e `IKO(5)`;
- `IGTD = 0.50*IGMD + 0.30*IOC(5) + 0.20*IKO(5)` mediante pesos configurables que deben sumar 1;
- sensibilidad `Delta M_d / Delta E_i = 5 * I_i,d / sum(I_i,d)`.

Para impedir regresiones futuras se añadió `tests/test_model_regression.py`, que fija casos de referencia, límites de niveles de madurez y la combinación calibrada de capas.

## Backend

Los cambios útiles de la versión adjunta son principalmente de **legibilidad y documentación interna**:

- comentarios explícitos sobre la agregación de tracks `a/b` en el modelo de 16 iniciativas;
- explicación de la selección del máximo nivel de contribución para no duplicar peso;
- docstrings de fórmulas en el motor;
- notas sobre fallback de responsables y trazabilidad objetivo-dimensión.

No se adoptaron imports sin uso presentes en la versión adjunta. Tampoco se reemplazaron los routers actuales, porque la versión vigente ya incluye mejoras posteriores: `/api/v1`, catálogo de APIs, SwaggerHub y forecasting.

## Frontend

Los cambios detectados en los componentes React/Next.js de la versión adjunta son **formateo/refactor visual del código fuente**, sin cambios relevantes en DOM, clases Tailwind, comportamiento de componentes, navegación o experiencia del usuario. Por ello **no se sustituyeron** los componentes vigentes: hacerlo aumentaría el diff sin producir una mejora visible y podría complicar la evolución posterior.

La versión vigente conserva todas las mejoras funcionales posteriores del frontend, incluido el cliente centralizado `/backend/api/v1` y los tipos del módulo de pronóstico.

## Dataset

Las diferencias observadas en varios `portfolio_blob_0*.py` corresponden a variaciones de serialización/final de archivo y no justifican reemplazar la instantánea vigente. No se modificó la matriz ni los datos calculados por este motivo.

## Decisión de integración

Se integraron únicamente mejoras seguras y aditivas:

1. documentación inline del motor y trazabilidad;
2. comentarios de mantenimiento en seed/analytics;
3. suite de regresión matemática para proteger el modelo formal;
4. este informe de revisión.

Se preservaron íntegramente las capacidades incorporadas después de v3: autenticación/RBAC, evidencias, API v1, OpenAPI/SwaggerHub, pronóstico, manual de usuario y Docker.
