# Ejercicio 03 — De gateway local a cliente HTTP

## Reto

Evoluciona la aplicación Wine Quality de S6 para consumir una API de
predicción. La interfaz y `PredictionController` ya dependen del protocolo
`InferenceGateway`; implementa el nuevo adaptador sin introducir HTTP en las
demás capas.

## Trabajo del alumnado

Parte del [starter](problem/starter/README.md) y completa únicamente los TODO de
S7:

1. construir `HttpInferenceGateway` con URL, timeout y sesión inyectable;
2. enviar `POST /v1/predictions` con el contrato acordado;
3. validar la respuesta y conservar el ID remoto en `last_request_id` solo para
   diagnóstico;
4. traducir status y fallos de transporte a errores del dominio;
5. seleccionar el gateway HTTP cuando exista `MODEL_API_URL`;
6. mantener el modo demo cuando la variable no esté definida.

No abras ni modifiques `examples/wine-quality-api/server.py`: durante esta
semana es una caja negra. Tampoco implementes un backend; FastAPI se introduce
en S8.

## Restricciones de diseño

- No modificar `controller.py`, `presentation.py`, `session.py` ni
  `telemetry.py`.
- No hacer llamadas reales de red desde los tests unitarios.
- No incluir cuerpos remotos, trazas ni payloads en mensajes al usuario.
- Mantener un timeout explícito y una única configuración de URL base.

## Entrega

- Código del gateway y cableado de la app.
- Tests en verde y comprobaciones Ruff.
- Evidencia de modo demo y modo HTTP.
- Evidencia de una petición válida y una inválida con `request_id`.
- Explicación breve de la traducción 422, 503, timeout y conexión.

La [solución de referencia](../../solutions/03-wine-http-gateway/README.md)
incluye la réplica docente y se consulta después de la entrega.
