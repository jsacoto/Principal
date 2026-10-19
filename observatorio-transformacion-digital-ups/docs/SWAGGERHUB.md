# Publicación del contrato API en SwaggerHub Catalog

El Observatorio exporta un contrato OpenAPI desde el código FastAPI y lo sincroniza con SwaggerHub mediante GitHub Actions.

## Catálogo institucional suministrado

https://catalog.swaggerhub.com/?orgId=84d99bc4-2aaa-4509-ad59-92a56e878e5c

El `orgId` de la URL del catálogo es un identificador del catálogo, mientras que la CLI/Registry API de SwaggerHub requiere el **Owner ID / slug** utilizado en las rutas de APIs de SwaggerHub. Por ese motivo el repositorio no debe adivinar ese valor.

## Configuración única en GitHub

En `Settings -> Secrets and variables -> Actions` configure:

### Secret

- `SWAGGERHUB_API_KEY`: clave personal de SwaggerHub. No debe guardarse en archivos `.env`, código fuente ni commits.

### Variables

- `SWAGGERHUB_OWNER`: Owner ID / slug de la organización en SwaggerHub.
- `SWAGGERHUB_API_NAME`: opcional; valor sugerido `ups-digital-transformation-observatory`.
- `SWAGGERHUB_API_VERSION`: opcional; por defecto `1.0.0`.
- `SWAGGERHUB_VISIBILITY`: `private` o `public`; por defecto `private`.

## Flujo automático

`.github/workflows/swaggerhub-openapi.yml` ejecuta:

1. pruebas backend;
2. exportación de `openapi/openapi.json`;
3. generación de `docs/API_DICTIONARY.md`;
4. instalación de SwaggerHub CLI;
5. creación o actualización del contrato;
6. publicación y selección de la versión por defecto.

Si no existen `SWAGGERHUB_API_KEY` o `SWAGGERHUB_OWNER`, la validación y la generación del contrato continúan, pero la etapa de publicación se omite de forma segura.

## Ejecución local

```bash
python scripts/export_openapi.py
python scripts/generate_api_dictionary.py
```

Para publicación manual, después de instalar `swaggerhub-cli`:

```bash
export SWAGGERHUB_API_KEY='...'
swaggerhub api:create OWNER/ups-digital-transformation-observatory/1.0.0 \
  --file openapi/openapi.json \
  --visibility private
```

Si la versión ya existe use `swaggerhub api:update` en lugar de `api:create`.
