# Solución y réplica docente — Wine Quality mediante HTTP

Esta solución añade `HttpInferenceGateway` y mantiene sin cambios el contrato
que consume `PredictionController`. `MODEL_API_URL` selecciona HTTP;
`DemoGateway` continúa siendo el modo por defecto.

## 1. Preparación limpia

Sitúate primero en `semana7/modules/07-http-rest-clients` y sincroniza el
entorno que ejecuta la API:

```bash
uv sync
```

Después entra en la solución y prepara la app:

```bash
cd solutions/03-wine-http-gateway
uv sync --locked --extra app
```

En la raíz, `uv sync` puede crear un `uv.lock` local no versionado. Solo el lock
incluido en este subproyecto forma parte del material reproducible. Si el
equipo docente va a trabajar sin red, debe precargar antes la caché de `uv`.

## 2. Pruebas y estilo

Desde la raíz de la solución:

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

La suite no abre conexiones reales: inyecta una sesión falsa para comprobar
el request, la respuesta y cada traducción de error.

## 3. Levantar la API

### Terminal 1 — raíz del módulo

```bash
uv run python examples/wine-quality-api/server.py
```

Debe anunciar `http://127.0.0.1:8000`. Se detiene con `Ctrl+C`.

## 4. Verificar el contrato a mano

Ejecuta estas llamadas desde la raíz del módulo, con la API activa.

### Salud — `GET /health`

Bash:

```bash
curl -i http://127.0.0.1:8000/health
```

PowerShell:

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

Resultado esperado: `200`, `model_status` igual a `ready` y el mismo
`request_id` en el JSON y en `X-Request-Id`.

### Predicción válida

Bash:

```bash
curl -i -X POST http://127.0.0.1:8000/v1/predictions -H "Content-Type: application/json" --data-binary @examples/wine-quality-api/samples/prediction-valid.json
```

PowerShell:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/v1/predictions -H "Content-Type: application/json" --data-binary "@examples/wine-quality-api/samples/prediction-valid.json"
```

Resultado esperado: `200` y un objeto `prediction` válido.

### Predicción inválida

Bash:

```bash
curl -i -X POST http://127.0.0.1:8000/v1/predictions -H "Content-Type: application/json" --data-binary @examples/wine-quality-api/samples/prediction-invalid.json
```

PowerShell:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/v1/predictions -H "Content-Type: application/json" --data-binary "@examples/wine-quality-api/samples/prediction-invalid.json"
```

Resultado esperado: `422`, `validation_error` y detalle del campo `alcohol`.

## 5. Simular indisponibilidad y otro puerto

Detén la API y reiníciala en modo no disponible:

```bash
uv run python examples/wine-quality-api/server.py --mode unavailable
```

Tanto salud como predicción deben devolver `503`; la app lo traduce a
`ArtifactUnavailableError`.

Para descartar un conflicto con el puerto 8000:

```bash
uv run python examples/wine-quality-api/server.py --port 8765
```

En ese caso usa `http://127.0.0.1:8765` como URL base.

## 6. Comprobar la app en modo demo

### Terminal 2 — raíz de la solución

En Bash:

```bash
unset MODEL_API_URL
uv run streamlit run app.py
```

En PowerShell:

```powershell
Remove-Item Env:MODEL_API_URL -ErrorAction SilentlyContinue
uv run streamlit run app.py
```

La app debe construir `DemoGateway` y predecir sin la API.

## 7. Comprobar la app en modo HTTP

Mantén la API de la Terminal 1 activa en modo `ready`. En la Terminal 2, desde
la solución, ejecuta:

Bash:

```bash
MODEL_API_URL=http://127.0.0.1:8000 uv run streamlit run app.py
```

PowerShell:

```powershell
$env:MODEL_API_URL = "http://127.0.0.1:8000"
uv run streamlit run app.py
```

La app debe construir `HttpInferenceGateway`, enviar el formulario al endpoint
y presentar la predicción sin exponer detalles del transporte.

## Checklist visual

- El formulario conserva los 11 campos y sus límites.
- Se observa el estado de carga antes del resultado.
- La predicción muestra categoría, confianza y versiones.
- Un 422 presenta un mensaje de entrada corregible.
- Un 503 o la API detenida presenta una recuperación de disponibilidad.
- La pantalla conserva el identificador local generado por el controlador de
  S6. El ID remoto queda solo en `HttpInferenceGateway.last_request_id` para
  diagnóstico y no se propaga a la pantalla.
- Limpiar y reintentar no duplica resultados ni telemetría.

## Cierre

Detén Streamlit y la API con `Ctrl+C`. FastAPI no es necesario para esta
réplica: en S8 se implementará un backend que conserve el contrato observado.
