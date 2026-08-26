# API local Wine Quality — contrato observable

Esta API se entrega como **caja negra** para la clase 2. El alumnado puede
arrancarla, enviar peticiones y observar respuestas, pero no debe abrir ni
modificar `server.py`. Su implementación con FastAPI se estudiará en S8.

## Arranque

Desde `semana7/modules/07-http-rest-clients`:

```bash
uv run python examples/wine-quality-api/server.py
```

Opciones docentes:

```bash
uv run python examples/wine-quality-api/server.py --port 8765
uv run python examples/wine-quality-api/server.py --mode unavailable
uv run python examples/wine-quality-api/server.py --delay-seconds 6
```

Por defecto escucha únicamente en `127.0.0.1:8000`. `Ctrl+C` detiene el
proceso.

## Endpoints

```text
GET  /health
POST /v1/predictions
```

Todas las respuestas JSON incluyen `request_id` y la cabecera
`X-Request-Id`. Ambos valores son iguales y permiten correlacionar lo que ve el
cliente con una petición concreta.

## Salud — `GET /health`

Respuesta disponible, status `200`:

```json
{
  "status": "ok",
  "service": "wine-quality-prediction",
  "model_status": "ready",
  "model_version": "wine-quality-demo-v1",
  "request_id": "req_..."
}
```

En modo `--mode unavailable`, devuelve `503` con un objeto `error`.

## Predicción — `POST /v1/predictions`

Enviar `Content-Type: application/json` y un objeto `features` con exactamente
los 11 campos numéricos:

```json
{
  "features": {
    "fixed_acidity": 7.4,
    "volatile_acidity": 0.7,
    "citric_acid": 0.0,
    "residual_sugar": 1.9,
    "chlorides": 0.076,
    "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0,
    "density": 0.9978,
    "ph": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4
  }
}
```

### Rangos aceptados

Los límites son inclusivos.

| Campo | Mínimo | Máximo |
|---|---:|---:|
| `fixed_acidity` | 0 | 20 |
| `volatile_acidity` | 0 | 2 |
| `citric_acid` | 0 | 2 |
| `residual_sugar` | 0 | 20 |
| `chlorides` | 0 | 1 |
| `free_sulfur_dioxide` | 0 | 100 |
| `total_sulfur_dioxide` | 0 | 300 |
| `density` | 0.98 | 1.01 |
| `ph` | 2.5 | 4.5 |
| `sulphates` | 0 | 3 |
| `alcohol` | 5 | 20 |

No se aceptan booleanos, valores no finitos, campos ausentes ni campos extra.

### Respuesta válida

Status `200`:

```json
{
  "prediction": {
    "quality_band": "needs_review",
    "confidence": 0.69,
    "model_version": "wine-quality-demo-v1",
    "preprocessing_version": "wine-red-features-v1"
  },
  "request_id": "req_..."
}
```

`quality_band` puede ser `needs_review`, `acceptable` o `excellent`; la
confianza está entre 0 y 1. La predicción es determinista y sirve para practicar
el contrato, no como modelo de negocio real.

## Errores y códigos de estado

| Status | Situación observable | Decisión esperada del cliente |
|---:|---|---|
| `200` | Salud o predicción válida | Validar el JSON antes de usarlo. |
| `400` | Cuerpo que no es JSON válido o longitud incorrecta | Error de petición. |
| `404` | Ruta desconocida | Error HTTP del backend. |
| `413` | Cuerpo superior a 64 KiB | Error HTTP del backend. |
| `422` | JSON válido que incumple campos, tipos o rangos | `InputContractError`. |
| `503` | API iniciada con `--mode unavailable` | `ArtifactUnavailableError`. |

El error tiene esta forma general:

```json
{
  "error": {
    "code": "validation_error",
    "message": "JSON is valid but violates the input contract",
    "fields": [
      {"field": "features.alcohol", "message": "must be a number"}
    ]
  },
  "request_id": "req_..."
}
```

El gateway no debe copiar el body remoto en mensajes de usuario. Debe traducir
el status a los errores estables del proyecto y guardar el ID remoto solo en
`last_request_id` para diagnóstico. `PredictionController` conserva su propio
identificador local de S6; no recibe ni muestra el ID remoto.

## Muestras

- [`samples/prediction-valid.json`](samples/prediction-valid.json): devuelve
  `200`.
- [`samples/prediction-invalid.json`](samples/prediction-invalid.json): usa un
  texto en `alcohol` y devuelve `422`.
