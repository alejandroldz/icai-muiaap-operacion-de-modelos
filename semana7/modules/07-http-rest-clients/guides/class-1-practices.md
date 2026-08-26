# Guion docente — Clase 1: HTTP, REST, JSON y clientes de inferencia

**Duración:** 120 minutos: 90 minutos de explicación y demo, y 30 minutos de
ejercicios intercalados.

## Propósito

Cambiar el modelo mental de “llamo a una función Python” por “envío un mensaje
a otro proceso mediante un contrato”. Al terminar, el alumnado puede leer,
construir y diagnosticar una interacción HTTP sin conocer la tecnología del
servidor.

La API preparada representa mantenimiento predictivo de bombas industriales.
El caso es local, independiente y determinista. En esta sesión no se enseña
FastAPI, OpenAPI avanzado ni autenticación; esos contenidos corresponden a S8,
S9 y S10.

## Resultados de aprendizaje

Cada estudiante puede:

1. explicar por qué HTTP es un protocolo y REST un estilo de diseño;
2. identificar URL, método, headers, body, status y respuesta;
3. elegir GET, POST, PUT, PATCH o DELETE y razonar seguridad e idempotencia;
4. distinguir `path`, `query`, `Content-Type` y `Accept`;
5. interpretar `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`,
   `429`, `500` y `503`;
6. traducir datos básicos entre JSON y Python;
7. invocar `POST /v1/predictions` con curl, Postman y `requests`;
8. manejar timeout, conexión y respuestas HTTP no exitosas.

## Preparación docente

- Confirmar **Python 3.12** y `uv` en el equipo docente.
- Desde la raíz `semana7/modules/07-http-rest-clients`, ejecutar en este orden:

  ```text
  uv sync
  uv run pytest -q
  uv run python examples/pump-maintenance-api/server.py
  ```

- En otra terminal, desde la misma raíz, comprobar el cliente:

  ```text
  uv run python examples/python-client/client.py examples/pump-maintenance-api/samples/prediction-valid.json
  ```

- En la raíz, `uv sync` puede crear un `uv.lock` local no versionado; ese lock
  no se entrega. La caché de `uv` debe prepararse antes si el aula no tiene
  red. Solo los subproyectos starter y solución incluyen locks reproducibles.
- Arrancar la [API preparada](../examples/pump-maintenance-api/README.md) y
  comprobar `GET /health`, un `200` y un `422`.
- Tener dos terminales abiertas y usar los payloads ya preparados.
- Importar la colección y el entorno de Postman sin depender de una cuenta.
- Entregar los [microejercicios](../exercises/01-http-json-microexercises/problem/README.md).
- Tener disponible el servidor local como primer fallback y la
  [transcripción de respaldo](../examples/transcripts/fallback-session.txt) como
  segundo fallback.
- No recorrer el código de `server.py`: en S7 el servidor es una caja negra.

## Guion minutado

| Minutos | Tipo | Acción docente y actividad | Evidencia |
|---:|---|---|---|
| 0–8 | Explicación, 8 | Contrastar llamada Python y llamada HTTP. Presentar propósito y límites. | Frontera cliente/servidor localizada. |
| 8–18 | Explicación, 10 | HTTP como protocolo; REST como estilo orientado a recursos. | Diferencia expresada en una frase. |
| 18–20 | Ejercicio, 2 | Clasificar llamada local, API HTTP de acciones y API de recursos. | Respuestas 1A–1C. |
| 20–31 | Explicación, 11 | Anatomía de URL, petición y respuesta; path frente a query. | Intercambio anotado. |
| 31–34 | Ejercicio, 3 | Marcar partes de una URL y de una respuesta. | Respuestas 2A–2C. |
| 34–45 | Explicación, 11 | Métodos, seguridad semántica, idempotencia y recursos. | Matriz de métodos. |
| 45–48 | Ejercicio, 3 | Elegir método y anticipar qué ocurre al repetirlo. | Respuestas 3A–3E. |
| 48–61 | Explicación, 13 | Diseño de `Prediction` y códigos 2xx, 4xx y 5xx. | Mapa situación → status. |
| 61–64 | Ejercicio, 3 | Resolver JSON roto, medida inválida y modelo no disponible. | `400`, `422`, `503`. |
| 64–73 | Explicación, 9 | `Content-Type`, `Accept` y JSON ↔ Python. | Tabla de tipos. |
| 73–75 | Ejercicio, 2 | Corregir `True`, `None` y una tupla que no son JSON. | JSON válido. |
| 75–86 | Demo, 11 | Ejecutar salud, predicción válida e inválida con curl. | Status, header y body leídos en orden. |
| 86–89 | Ejercicio, 3 | Repetir el POST con el payload inválido. | Código y campo rechazado. |
| 89–94 | Explicación, 5 | Presentar Postman y repartir roles. | Método, URL, headers y body listos. |
| 94–105 | Ejercicio, 11 | Completar el [ejercicio Postman](../examples/postman/README.md). | Tabla con `200`, `422` y request ID. |
| 105–114 | Demo, 9 | Cliente `requests`: `json=`, `timeout`, `raise_for_status()` y errores. | Flujo de éxito/fallo seguido. |
| 114–117 | Ejercicio, 3 | Localizar tres defensas y comparar 422 con puerto incorrecto. | `HTTPError` frente a conexión. |
| 117–120 | Cierre, 3 | Exit ticket, assignment y puente a clase 2/S8. | Una decisión de contrato justificada. |

**Comprobación:** explicación/demo = 90 minutos; ejercicios = 30 minutos.

## Núcleo conceptual

### HTTP no es REST

HTTP define mensajes. REST es un estilo que hace la interfaz más previsible al
usar recursos, representaciones y métodos con semántica conocida. Una llamada
puede usar HTTP sin estar orientada a recursos.

```text
POST /runModelNow       acción expresada en la URL
POST /v1/predictions    creación/obtención de una representación Prediction
```

REST no es una etiqueta que haya que “aprobar”; interesa justificar un diseño
coherente. Las peticiones deben contener lo necesario para entenderlas.

### URL, path y query

```text
http://127.0.0.1:8000/v1/predictions?machine_id=pump-017&limit=10
|__|   |_______| |__| |_____________| |____________________________|
scheme    host   port       path                    query
```

- El path identifica el recurso o colección.
- La query filtra, pagina o modifica la representación.
- El fragmento `#...` permanece en el cliente y no llega al servidor.
- No colocar secretos o datos sensibles en URLs: suelen aparecer en logs.

### Métodos

| Método | Intención | Seguro | Idempotente |
|---|---|---:|---:|
| GET | Leer | Sí | Sí |
| POST | Crear o iniciar una operación | No | Normalmente no |
| PUT | Reemplazar completamente | No | Sí |
| PATCH | Modificar parcialmente | No | No garantizado |
| DELETE | Eliminar | No | Sí |

“Seguro” significa que no pretende cambiar el estado, no que esté cifrado. En
local usamos HTTP; fuera del equipo la expectativa es HTTPS. Repetir DELETE
puede dar primero `204` y luego `404` sin perder su idempotencia: el estado
final sigue siendo “recurso ausente”. No todos los recursos necesitan todos
los métodos; una predicción suele ser inmutable.

### Recursos y contrato de predicción

```text
GET  /v1/predictions/{prediction_id}
POST /v1/predictions
GET  /v1/predictions?machine_id=pump-017&limit=10
```

La API del laboratorio devuelve `200` porque calcula y devuelve inmediatamente
una representación sin exponer persistencia. Si creara un recurso recuperable,
`201 Created` y `Location` serían una elección natural. `v1` versiona el
contrato HTTP; `model_version` versiona el modelo.

### Status concretos

| Status | Lectura práctica | Ejemplo |
|---:|---|---|
| 200 | Éxito con cuerpo | Predicción calculada |
| 201 | Recurso creado | Predicción persistida con `Location` |
| 204 | Éxito sin cuerpo | Borrado completado |
| 400 | Mensaje mal formado | JSON truncado |
| 401 | No hay credenciales válidas | Token ausente o inválido |
| 403 | Identidad conocida sin permiso | Rol insuficiente |
| 404 | Recurso/ruta inexistente | Path incorrecto |
| 409 | Conflicto con el estado actual | Identificador duplicado |
| 422 | JSON válido que incumple el contrato | Vibración es texto |
| 429 | Demasiadas peticiones | Revisar `Retry-After` |
| 500 | Fallo inesperado del servidor | Excepción no controlada |
| 503 | Servicio temporalmente no disponible | Modelo aún no listo |

Una etiqueta `maintenance_required` no es un error HTTP. El código habla de la
operación del servicio, no de si el resultado funcional es favorable.

### Headers y JSON

- `Content-Type` describe el cuerpo enviado o recibido.
- `Accept` describe el formato de respuesta deseado.
- JSON object/array/string/number/boolean/null corresponden normalmente a
  `dict`/`list`/`str`/`int|float`/`bool`/`None`.
- JSON escribe `true`, `false` y `null`, no `True`, `False` y `None`.
- Tuplas, sets, fechas, NumPy y `NaN` requieren conversión explícita.

## Preguntas que abren conversación

| Pregunta | Respuesta esperada |
|---|---|
| “¿Abrir localhost en el navegador ya es REST?” | Es HTTP; REST depende del diseño. |
| “¿Por qué las medidas no van en la URL?” | Son datos estructurados y podrían quedar en logs. |
| “¿Está prohibido `/predict`?” | No, pero `/predictions` expresa mejor el recurso. |
| “¿Qué puede pasar si repito el POST?” | Puede procesarse dos veces. |
| “¿Un segundo DELETE con 404 rompe la idempotencia?” | No; el estado final es el mismo. |
| “¿JSON roto y vibración textual son el mismo error?” | No: 400 frente a 422. |
| “¿401 y 403 significan lo mismo?” | No: credenciales inválidas frente a permiso insuficiente. |
| “¿Mantenimiento requerido es un error HTTP?” | No, es una predicción válida. |
| “¿Por qué timeout en localhost?” | Para limitar la espera y adquirir un hábito operable. |
| “¿`json=` analiza la respuesta?” | No; serializa la petición. `.json()` analiza la respuesta. |

## Mapa de 26 diapositivas

| # | Título | Clave |
|---:|---|---|
| 1 | De función a servicio | Gancho S6 → S7 |
| 2 | Resultado y límites | Qué sí y qué no |
| 3 | Caso de la bomba | Contexto autocontenido |
| 4 | HTTP en una frase | Protocolo de mensajes |
| 5 | Cliente y servidor | Flujo request/response |
| 6 | HTTP frente a REST | Protocolo/estilo |
| 7 | Anatomía de URL | Scheme, host, port, path, query |
| 8 | Path o query | Identidad/filtro |
| 9 | Anatomía del request | Método, headers, body |
| 10 | Anatomía del response | Status, headers, body |
| 11 | GET y POST | Lectura/creación-operación |
| 12 | PUT, PATCH, DELETE | Sustitución/cambio/borrado |
| 13 | Seguro no es cifrado | Semántica HTTP |
| 14 | Repetir una petición | Idempotencia |
| 15 | Diseñar recursos | Sustantivos y colecciones |
| 16 | `/v1/predictions` | Contrato del caso |
| 17 | Éxitos 200/201/204 | Cuerpo y `Location` |
| 18 | 400 frente a 422 | Sintaxis/contrato |
| 19 | 401/403/404 | Identidad, permiso, existencia |
| 20 | 409/429 | Conflicto y límite |
| 21 | 500/503 | Bug frente a indisponibilidad |
| 22 | Headers | `Content-Type` y `Accept` |
| 23 | JSON ↔ Python | Tipos y trampas |
| 24 | curl | Ver el intercambio |
| 25 | Postman | Ejercicio visual |
| 26 | `requests` y puente | Cliente robusto y S8 |

## Demos y contingencias

- Para curl, usar los comandos ya preparados y leer status → headers → body.
- Para Python, mostrar `json=`, `timeout`, `raise_for_status()` y tratamiento de
  error antes de enseñar la salida.
- Un timeout real es poco determinista: mostrar la transcripción o inyectar el
  caso en pruebas, no manipular la red del aula.
- Si el puerto 8000 está ocupado, arrancar en 8765 y cambiar una sola base URL.
- Si falla la API, ejecutar el mismo servidor desde otra copia local.
- Si falla Postman, trabajar por parejas; como fallback final, construir la
  petición y contrastarla con la salida de curl.
- Si falta `requests`, usar el entorno docente ya preparado; no depender de una
  instalación desde internet durante la sesión.

## Assignment

El [laboratorio 02](../exercises/02-api-client-lab/problem/README.md) es una
**ampliación posterior a la clase 1** o assignment; **no es la clase 2**.
Consiste en entregar una ficha del recurso `Prediction` y un cliente Python
pequeño:

- método, ruta, request y response;
- decisiones para `200`, `400`, `422`, `404` y `503`;
- llamada con `json=`, `timeout` y `raise_for_status()`;
- manejo separado de timeout, conexión y error HTTP;
- evidencia de una petición válida y una inválida con `request_id`.

No se entrega código de servidor.

## Puente a clase 2 y S8

La [clase 2](class-2-workshop.md) lleva estas decisiones al contrato HTTP del
proyecto Wine Quality y sustituye el gateway local por un cliente HTTP. En S8
se implementará ese contrato con FastAPI. Haber decidido antes recursos,
payloads y errores evita que la sintaxis del framework dicte el diseño.
