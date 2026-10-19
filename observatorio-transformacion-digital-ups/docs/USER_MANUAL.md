# Manual de Usuario - Observatorio de Transformación Digital UPS

**Versión de la plataforma:** 3.1  
**Coordinación responsable:** Transformación Digital UPS  
**Contacto:** transformaciondigital@ups.edu.ec

## 1. Propósito

El Observatorio de Transformación Digital permite consultar el estado de madurez digital de la Universidad Politécnica Salesiana y gestionar, con autorización, el avance de las iniciativas que alimentan dicho cálculo.

La plataforma separa dos espacios:

- **Portal público**: consulta del dashboard, modelo, dimensiones y contacto.
- **Gestión autorizada**: actualización de actividades, justificaciones, evidencias, auditoría, usuarios y nuevas iniciativas.

## 2. Página principal y dashboard

Al ingresar a la plataforma se presenta el dashboard ejecutivo. Sus principales elementos son:

- **IGTD**: Índice Global Ajustado de Transformación Digital, escala 0-5.
- **IGMD**: madurez estructural derivada de las iniciativas y su contribución a D1-D5.
- **IOC**: cumplimiento estratégico de objetivos/KRs.
- **IKO**: desempeño operativo de KPIs.
- **Radar D1-D5**: comparación de madurez por dimensión.
- **Heatmap O1-O5 x D1-D5**: intensidad estratégica entre objetivos y dimensiones.
- **Alertas de calidad**: inconsistencias detectadas en datos de iniciativas o actividades.

La vista permite alternar entre el portafolio operativo actual y el modelo agregado de 16 iniciativas conceptuales.

## 3. Pestaña Modelo TD

La pestaña **Modelo TD** explica el marco institucional de tres capas:

1. Madurez estructural.
2. Cumplimiento estratégico mediante OKRs/KRs.
3. Desempeño operativo mediante KPIs.

La cadena de trazabilidad es:

`Iniciativa -> Dimensión -> Objetivo -> KR -> KPI -> Evidencia -> IGMD/IOC/IKO/IGTD`

Esta sección es de consulta y no modifica información.

## 4. Pestaña Dimensiones

La pestaña **Dimensiones** presenta la definición y alcance de:

- D1. Oferta Académica y Aprendizaje Digital.
- D2. Experiencia Universitaria y Procesos.
- D3. Sostenibilidad Económica y Analítica de Datos.
- D4. Investigación, Vinculación e Innovación.
- D5. Sostenibilidad Ambiental - Universidad Cero Emisiones.

Cada dimensión contiene una explicación funcional y criterios de observación.

## 5. Pestaña Contacto

La pestaña **Contacto** dirige las consultas institucionales a:

**transformaciondigital@ups.edu.ec**

## 6. Acceso autorizado

Seleccione **Acceso autorizado** e ingrese correo y contraseña.

La plataforma maneja dos perfiles:

### Responsable

Puede:

- consultar sus iniciativas asignadas;
- actualizar avance, estado, prioridad, fechas y observaciones de actividades;
- justificar cada cambio;
- cargar evidencias;
- consultar auditoría de sus iniciativas.

No puede administrar usuarios ni modificar iniciativas no asignadas.

### Administrador

Además de las funciones anteriores puede:

- consultar toda la cartera;
- crear usuarios;
- asignar iniciativas a responsables;
- activar o desactivar cuentas;
- crear nuevas iniciativas;
- definir contribuciones D1-D5.

## 7. Gestión de iniciativas

Una vez autenticado, ingrese a **Gestión**.

La lista muestra únicamente las iniciativas permitidas para el usuario. Seleccione una iniciativa para revisar sus actividades y evidencias.

En el detalle se visualizan:

- código y objetivo;
- descripción;
- avance reportado y verificado;
- contribuciones a D1-D5;
- actividades;
- responsables;
- fechas;
- estado y prioridad;
- evidencias cargadas.

## 8. Actualización de una actividad

Seleccione la actividad correspondiente y modifique únicamente los campos necesarios:

- Avance (%).
- Estado.
- Prioridad.
- Fecha inicio.
- Fecha fin.
- Observación.

La **justificación es obligatoria**. Debe explicar de forma breve y verificable por qué se modifica el avance o el estado.

Al guardar:

1. la actividad se actualiza;
2. se registra el usuario y la fecha;
3. se conserva el valor anterior y nuevo;
4. se recalcula el avance de la iniciativa;
5. el motor analítico podrá reflejar el cambio en la siguiente consulta.

## 9. Carga de evidencias

En una actividad puede adjuntarse una evidencia. La plataforma admite, según la configuración por defecto:

- PDF;
- Word;
- Excel;
- PowerPoint;
- PNG/JPG/WEBP;
- CSV/TXT;
- ZIP.

El tamaño máximo por defecto es 20 MB y puede ser ajustado por el administrador del servidor.

Al cargar un archivo agregue una descripción que indique qué demuestra la evidencia.

Los archivos quedan asociados a la actividad, al usuario que los subió y a la fecha de carga.

## 10. Auditoría

La vista de auditoría permite revisar:

- cambios de avance;
- cambios de estado;
- justificaciones;
- usuario responsable;
- fecha y hora;
- evidencias cargadas.

Esta información no debe eliminarse como parte de la operación normal, ya que constituye trazabilidad institucional.

## 11. Administración de usuarios

Disponible únicamente para administradores.

Para crear un usuario registre:

- nombre;
- correo;
- contraseña inicial;
- rol;
- iniciativas autorizadas.

Para responsables, asigne explícitamente las iniciativas que podrán editar.

Se recomienda que la contraseña inicial sea cambiada en el primer acceso y que las cuentas que ya no requieran acceso sean desactivadas.

## 12. Creación de nuevas iniciativas

Desde **Gestión -> Nueva iniciativa**, el administrador completa:

- código;
- objetivo O1-O5;
- ámbito;
- descripción;
- líder y correo;
- estado;
- contribuciones D1-D5 en escala 0-3;
- actividades iniciales.

Para cada actividad pueden registrarse:

- Id;
- actividad para la implementación;
- fechas inicio/fin;
- avance;
- responsable;
- estado;
- prioridad;
- campo In;
- observación.

La nueva iniciativa queda integrada al modelo y sus contribuciones pasan al motor de madurez.

## 13. Pronóstico por cronograma

La versión 3.1 incorpora una línea base de proyección que responde a la pregunta:

**¿Qué madurez alcanzaría la UPS si se cumplen los cronogramas registrados?**

Es un escenario determinista, no un modelo de IA. Utiliza las fechas fin de las actividades y proyecta su avance hacia 100% en la fecha comprometida.

El resultado puede recalcular IGMD e IGTD para una fecha objetivo y mostrar las variaciones por dimensión.

## 14. Documentación de APIs

Para equipos técnicos:

- Swagger UI: `/docs`.
- ReDoc: `/redoc`.
- OpenAPI JSON: `/openapi.json`.
- Diccionario de APIs: `/api/v1/catalog`.

El frontend consume exclusivamente el prefijo versionado `/api/v1`.

## 15. Buenas prácticas de uso

- Actualice el avance únicamente cuando exista evidencia o una justificación clara.
- No utilice 100% si la actividad todavía requiere entregables pendientes.
- Mantenga fechas de inicio y fin consistentes.
- Use observaciones para documentar reprogramaciones o dependencias.
- Adjunte evidencias con nombres descriptivos.
- No comparta credenciales.
- Cierre sesión en equipos compartidos.
- Reporte inconsistencias a transformaciondigital@ups.edu.ec.

## 16. Solución de problemas

### No puedo iniciar sesión

Verifique correo y contraseña. Si la cuenta está desactivada o la contraseña fue olvidada, contacte a la Coordinación.

### No veo una iniciativa

El responsable solo visualiza iniciativas asignadas. Solicite al administrador revisar sus permisos.

### No puedo guardar una actividad

Verifique que:

- la justificación tenga contenido;
- el avance esté entre 0 y 100;
- el estado y prioridad sean válidos;
- la fecha fin no sea anterior a la fecha inicio.

### No puedo subir un archivo

Revise extensión y tamaño. Si el problema continúa, contacte a la Coordinación.

### El índice no cambia inmediatamente como esperaba

El índice depende de la contribución de la iniciativa a cada dimensión, el avance analítico utilizado y los componentes estratégicos/operativos del modelo. Un cambio de una sola actividad puede tener impacto reducido o nulo sobre determinadas dimensiones.

## 17. Contacto y soporte

**Coordinación de Transformación Digital UPS**  
Correo: **transformaciondigital@ups.edu.ec**
