# Clase 1 — HTTP, REST, JSON y clientes de inferencia

## Pregunta de la sesión

¿Qué cambia cuando `predict(features)` deja de ser una llamada local y pasa a
ser una conversación entre dos procesos?

## Resultado

Podrás leer una URL, construir una petición, interpretar la respuesta y
consumir la API de mantenimiento de bombas con tres clientes distintos. No
necesitas saber cómo está implementado el servidor.

## El intercambio

```text
cliente                     API local
   |  POST /v1/predictions     |
   |  headers + JSON ---------->|
   |                            | valida y calcula
   |<----------- 200 + JSON     |
```

Una petición tiene método, URL, headers y, a veces, body. Una respuesta tiene
status, headers y, a veces, body.

## API usada

```text
GET  http://127.0.0.1:8000/health
POST http://127.0.0.1:8000/v1/predictions
```

El body del POST es JSON:

```json
{
  "machine_id": "pump-017",
  "measurements": {
    "temperature_c": 91.2,
    "vibration_mm_s": 8.4,
    "pressure_bar": 4.7,
    "runtime_hours": 12840
  }
}
```

## Ruta de trabajo

1. Resolver los [microejercicios](../../exercises/01-http-json-microexercises/problem/README.md).
2. Observar el cable con [curl](../../examples/curl/README.md).
3. Construir una petición en [Postman](../../examples/postman/README.md).
4. Como ampliación posterior a la clase 1, completar el
   [cliente Python](../../exercises/02-api-client-lab/problem/README.md).

El punto 4 no es la clase 2. La continuidad del proyecto Wine Quality está en
la [sesión 02](../02-wine-http-gateway/README.md).

## Chuleta mínima

- GET lee; POST crea o inicia una operación.
- PUT reemplaza; PATCH modifica parcialmente; DELETE elimina.
- GET es seguro e idempotente. PUT y DELETE son idempotentes. POST no suele
  serlo; PATCH no lo garantiza.
- `Content-Type` describe el cuerpo; `Accept` solicita un formato de respuesta.
- `400`: JSON roto. `422`: JSON legible que incumple el contrato.
- `500`: fallo inesperado. `503`: indisponibilidad temporal.
- Un resultado de “alto riesgo” puede ser un `200`: la API funcionó.

## Antes de salir

Debes poder completar sin ayuda:

> Una petición contiene ___; una respuesta contiene ___; repetir un POST puede
> ___; un timeout se controla con ___.
