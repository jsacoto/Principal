# Autorización, trazabilidad y evidencias

## Roles

### Administrador

Puede ver y modificar toda la cartera, crear usuarios, asignar iniciativas y registrar nuevas iniciativas.

### Responsable

Solo puede acceder a las iniciativas vinculadas en `user_initiative_permissions` con `can_edit=true`.

## Sesión

1. El usuario envía correo y contraseña a `/api/auth/login`.
2. La contraseña se verifica con PBKDF2-HMAC-SHA256.
3. Se genera un token aleatorio de alta entropía.
4. PostgreSQL guarda únicamente el SHA-256 del token.
5. El navegador recibe el token en cookie HTTP-only `ups_td_session`.
6. Cada operación de gestión resuelve la sesión y comprueba el permiso sobre la iniciativa.

## Trazabilidad de avances

`activity_progress_logs` conserva:

- actividad;
- avance anterior y nuevo;
- estado anterior y nuevo;
- justificación;
- usuario responsable;
- fecha y hora.

La API exige una justificación de al menos tres caracteres para cada actualización de actividad.

## Evidencias

Los archivos cargados desde la plataforma se guardan en `/data/uploads` dentro del contenedor y en un volumen Docker persistente. El nombre original se conserva solo como metadato; el archivo físico utiliza UUID para evitar colisiones y rutas manipuladas.

La descarga exige una sesión válida y permiso sobre la iniciativa propietaria de la actividad.

## Límites

La versión actual implementa control de acceso local. Para despliegue institucional se recomienda integrar posteriormente SSO de la UPS (OIDC/SAML), antivirus de archivos, almacenamiento de objetos institucional y políticas corporativas de retención.
