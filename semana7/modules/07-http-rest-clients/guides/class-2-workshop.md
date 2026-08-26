# Guion docente — clase 2: del gateway local a HTTP

## Propósito

En 120 minutos, cada pareja conecta la aplicación Wine Quality de S6 a una API
local mediante `HttpInferenceGateway`. El servidor se trata como **caja negra**:
la práctica trabaja contrato, cliente y errores. FastAPI queda reservado para
S8.

## Preparación

### Antes de la clase

- Verificar Python 3.12 y `uv` en los equipos.
- Desde la raíz del módulo, ejecutar `uv sync` y `uv run pytest -q`.
- En esa raíz, `uv sync` puede crear un `uv.lock` local no versionado. Solo los
  locks incluidos en starter y solución son material reproducible.
- Comprobar que `uv run python examples/wine-quality-api/server.py` deja
  disponible `http://127.0.0.1:8000/health`.
- Preparar una copia limpia del
  [starter](../exercises/03-wine-http-gateway/problem/starter/README.md) por
  pareja y conservar la
  [solución](../solutions/03-wine-http-gateway/README.md) solo para contraste.
- Si el puerto 8000 está ocupado, usar `--port 8765` y cambiar únicamente
  `MODEL_API_URL`.

### Organización

Trabajar por parejas. Una persona conduce el teclado y otra contrasta el
contrato y los tests; intercambian papeles en el minuto 62. El objetivo no es
leer `server.py`, sino deducir y respetar su interfaz observable.

## Secuencia exacta — 120 minutos

| Minutos | Actividad | Evidencia observable |
|---|---|---|
| **0–10** | Recuperar la arquitectura S6: `Streamlit → Controller → Gateway`. Presentar el cambio de frontera y la regla “solo cambia el adaptador”. | Diagrama con `HttpInferenceGateway` y API caja negra. |
| **10–25** | Arrancar la API, consultar `GET /health` y enviar los JSON válido e inválido a `POST /v1/predictions`. | Tres intercambios con status, body y `request_id`. |
| **25–45** | Traducir el contrato HTTP a decisiones de cliente: payload, timeout, 2xx, 422, 503, 5xx, JSON inválido y fallo de conexión. | Tabla status/excepción completada por cada pareja. |
| **45–62** | Ejecutar el starter en rojo. Implementar constructor, URL normalizada y petición inyectable siguiendo `test_http_gateway.py`. | Primeros tests del gateway pasan sin usar red real. |
| **62–82** | Implementar camino feliz: `POST`, cabeceras, timeout, lectura de `request_id` y validación de `PredictionPayload`. | Tests de contrato feliz en verde. |
| **82–100** | Implementar el mapeo de errores y proteger mensajes frente a cuerpos o detalles internos del servidor. | Tests 422, 503, timeout, conexión, 5xx y respuesta inválida en verde. |
| **100–112** | Integrar `MODEL_API_URL` en `app.py`; comprobar modo demo sin variable y modo HTTP con la API. | La misma interfaz funciona con ambos gateways. |
| **112–120** | Ejecutar suite y Ruff, reunir evidencias y realizar el debrief. | Capturas, salida de pruebas y decisión técnica explicada. |

## Pistas graduadas

Entregar una pista solo cuando la pareja haya explicado qué observa.

### Nivel 1 — localizar la responsabilidad

- ¿Qué protocolo espera `PredictionController`?
- ¿Qué archivo puede cambiar sin tocar presentación, estado ni telemetría?
- ¿Qué diferencia hay entre un error 422 y no poder abrir una conexión?

### Nivel 2 — orientar la traducción

- Construir siempre `{"features": dict(values)}`.
- Usar una sesión inyectada y pasar `timeout` en cada `POST`.
- Resolver primero el status; después interpretar el JSON de éxito.
- Guardar el `request_id` remoto en `last_request_id` solo para diagnóstico. El
  controlador conserva el identificador local que ya generaba en S6.

### Nivel 3 — desbloqueo concreto

- `422` se traduce a `InputContractError`.
- `503` y la conexión rechazada se traducen a
  `ArtifactUnavailableError`.
- `requests.Timeout` se traduce a `InferenceTimeoutError`.
- Otros status no exitosos, JSON inválido o respuesta incompatible se traducen
  a `BackendInferenceError`.

## Evidencias

Cada pareja entrega:

1. `src/model_ui/http_gateway.py` y el cableado mínimo de `app.py`.
2. Salida completa de `uv run pytest -q` y de ambos comandos Ruff.
3. Evidencia de la app en modo demo y en modo HTTP.
4. Un intercambio válido y otro 422 con status, JSON y `request_id`.
5. Una explicación breve de por qué el controlador no necesitó cambios.

No se entrega ni modifica código del servidor.

## Contingencias

- Sin Streamlit: terminar el gateway con tests y usar los JSON de ejemplo como
  evidencia del contrato.
- Puerto ocupado: iniciar la API con `--port 8765`.
- Entorno sin red: preparar previamente la caché docente. Los subproyectos de
  starter y solución sí incluyen sus locks propios.
- Pareja bloqueada en varios errores: asignar primero un único caso 422 y
  generalizar después.

## Debrief

Cerrar con estas preguntas:

- ¿Qué parte de la aplicación depende ahora de HTTP?
- ¿Por qué un 422 no debe mostrarse igual que un 503?
- ¿Qué aporta validar la respuesta aunque el servidor devuelva 200?
- ¿Qué contrato deberá conservar el backend FastAPI de S8 para no romper la
  app?
