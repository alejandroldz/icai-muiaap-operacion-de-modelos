# Postman — ejercicio dedicado

Postman se usa como cliente visual; no se importa OpenAPI ni se añaden scripts
avanzados.

## Preparación local

1. Arrancar la API local.
2. Importar `pump-maintenance-s7.postman_collection.json`.
3. Importar y seleccionar `local-s7.postman_environment.json`.
4. Confirmar que `base_url` vale `http://127.0.0.1:8000`.

## Ejercicio, 11 minutos

En parejas, una persona maneja Postman y otra comprueba el contrato.

1. Abrir `Health`, enviarla y localizar status, header y body.
2. Abrir `Prediction - valid (200)` y revisar método, URL, headers y body antes
   de pulsar **Send**.
3. Registrar código, `Content-Type`, `X-Request-Id`, etiqueta y puntuación.
4. Abrir `Prediction - invalid (422)` y localizar el campo rechazado.
5. Explicar por qué la respuesta es `422` y no `400`.
6. Cambiar manualmente la URL a `/v1/prediction` y anticipar el `404`.

### Evidencia

| Caso | Método y path | Status | `request_id` | Qué corregiría |
|---|---|---:|---|---|
| Salud | | | | |
| Predicción válida | | | | |
| Contrato inválido | | | | |

Si Postman no funciona en un equipo, se trabaja por parejas. Como último
fallback, se construye la petición sin enviarla y se contrasta con las
respuestas obtenidas por curl.
