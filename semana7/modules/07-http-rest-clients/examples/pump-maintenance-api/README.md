# API local preparada — mantenimiento de bombas

Esta carpeta es una **caja negra docente**. En S7 se ejecuta y se observa su
contrato; no se estudia ni se modifica su implementación. El servidor usa la
biblioteca estándar, pero se ejecuta dentro del entorno preparado con `uv`.

## Arranque

Después de ejecutar `uv sync`, desde la raíz del módulo:

```text
uv run python examples/pump-maintenance-api/server.py
```

Debe aparecer:

```text
API S7 disponible en http://127.0.0.1:8000
```

Detener con `Ctrl+C`. Si el puerto está ocupado:

```text
uv run python examples/pump-maintenance-api/server.py --port 8765
```

## Contrato observable

- `GET /health`: `200`, estado del servicio y versión del modelo.
- `POST /v1/predictions`: `200` con predicción o `422` con errores de campo.
- JSON mal formado: `400`.
- Ruta desconocida: `404`.

La salida contiene `X-Request-Id` y el mismo `request_id` en el JSON. No se
devuelven trazas, rutas locales ni detalles internos.

## Datos

- `samples/prediction-valid.json`: solicitud válida de riesgo alto.
- `samples/prediction-invalid.json`: JSON válido con un tipo incorrecto.
- `samples/prediction-malformed.txt`: JSON truncado para observar un `400`.

La puntuación es determinista y sirve únicamente para enseñar el contrato de
una inferencia. No representa una garantía de fallo mecánico.
