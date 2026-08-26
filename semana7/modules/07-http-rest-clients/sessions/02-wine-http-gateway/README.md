# Sesión 02 — Del gateway local a un cliente HTTP

## Pregunta guía

¿Cómo puede la app Wine Quality consumir un endpoint sin acoplar su interfaz ni
su controlador a `requests`?

## Objetivos

Al terminar, el alumnado podrá:

- convertir un contrato HTTP en una implementación de `InferenceGateway`;
- enviar JSON con timeout explícito y una sesión HTTP inyectable;
- distinguir errores de entrada, disponibilidad, timeout y respuesta;
- validar el payload de salida antes de entregarlo al controlador;
- cambiar entre modo demo y modo HTTP mediante configuración.

## Punto de partida

La sesión continúa el proyecto iniciado en S1 y parte de la app robusta de S6.
Se mantienen `PredictionController`, presentación, estado y telemetría. La API
Wine Quality se entrega como caja negra y no se implementa con FastAPI en S7.

## Material

- [Contrato observable de la API](../../examples/wine-quality-api/README.md)
- [Guion docente de 120 minutos](../../guides/class-2-workshop.md)
- [Enunciado](../../exercises/03-wine-http-gateway/README.md)
- [Starter](../../exercises/03-wine-http-gateway/problem/starter/README.md)
- [Solución y réplica](../../solutions/03-wine-http-gateway/README.md)

## Flujo de trabajo

1. Observar `GET /health` y dos llamadas a `POST /v1/predictions`.
2. Escribir la tabla de traducción entre HTTP y errores del dominio.
3. Ejecutar los tests rojos del starter.
4. Implementar `HttpInferenceGateway` en incrementos pequeños.
5. Activar HTTP con `MODEL_API_URL` sin cambiar el controlador.
6. Verificar tests, estilo y ambos modos de la app.

## Criterio de salida

La suite de la solución queda en verde, Ruff no informa incidencias y la misma
pantalla predice tanto con `DemoGateway` como con `HttpInferenceGateway`.
