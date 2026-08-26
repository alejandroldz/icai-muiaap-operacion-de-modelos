# Starter — Wine Quality mediante HTTP

## Objetivo

La app de S6 ya separa Streamlit, controlador y gateway. En esta práctica
implementarás `HttpInferenceGateway` y seleccionarás ese adaptador con
`MODEL_API_URL`. No se modifica el servidor ni se introduce FastAPI: eso
corresponde a S8.

## Dónde ejecutar cada comando

Se usan dos carpetas:

- **raíz del módulo:** `semana7/modules/07-http-rest-clients`;
- **raíz del starter:**
  `exercises/03-wine-http-gateway/problem/starter` dentro del módulo.

## 1. Preparar el entorno

Desde la raíz del starter:

```bash
uv sync --locked --extra app
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

`uv sync` usa el entorno declarado en este starter. Antes de implementar, la
suite completa debe mostrar exactamente **17 green / 17 red**: los tests
heredados de S6 protegen lo existente y los nuevos tests describen el trabajo
pendiente de S7.

## 2. Leer el rojo por grupos

Comprueba primero que el comportamiento previo continúa verde:

```bash
uv run pytest -q tests/test_controller.py tests/test_gateway.py tests/test_presentation.py tests/test_session.py
```

Después trabaja los tests del cliente HTTP:

```bash
uv run pytest -q tests/test_http_gateway.py
```

Por último integra la selección por configuración:

```bash
uv run pytest -q tests/test_app_gateway_selection.py
```

Repite el test más pequeño que falle, implementa un solo comportamiento y
vuelve a ejecutarlo antes de continuar.

## 3. Orden recomendado de implementación

1. Constructor: validar `base_url` y `timeout`; aceptar una sesión inyectada.
2. Camino feliz: enviar `{"features": ...}` a `/v1/predictions`.
3. Respuesta: aceptar 2xx, guardar el ID remoto en `last_request_id` para
   diagnóstico y validar `prediction`. El controlador mantiene su ID local.
4. Errores: mapear 422, 503, timeout, conexión, otros status y JSON inválido.
5. Integración: priorizar `MODEL_API_URL` en `build_gateway`.

El controlador no debe conocer `requests` ni la URL del servicio.

## 4. Probar la app en dos terminales

### Terminal 1 — API desde la raíz del módulo

```bash
uv run python examples/wine-quality-api/server.py
```

### Terminal 2 — app desde la raíz del starter

En Bash:

```bash
MODEL_API_URL=http://127.0.0.1:8000 uv run streamlit run app.py
```

En PowerShell:

```powershell
$env:MODEL_API_URL = "http://127.0.0.1:8000"
uv run streamlit run app.py
```

Sin `MODEL_API_URL`, la app debe conservar `DemoGateway`:

```bash
uv run streamlit run app.py
```

## 5. Definición de terminado

- `uv run pytest -q` termina completamente en verde.
- `uv run ruff check .` y `uv run ruff format --check .` no informan cambios.
- La app funciona sin variable en modo demo.
- La app funciona con la variable en modo HTTP.
- Los errores no muestran el cuerpo remoto ni detalles internos.
- Puedes explicar por qué solo cambian el adaptador y la configuración.
