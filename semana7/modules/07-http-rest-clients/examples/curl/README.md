# Ejemplos curl

Ejecutar la API en una terminal y estos comandos desde la raíz del módulo en
otra. Usar los ficheros evita que las comillas de JSON oculten el concepto HTTP.

## PowerShell

En Windows se usa `curl.exe` para evitar el alias histórico `curl` de Windows
PowerShell.

```powershell
$baseUrl = "http://127.0.0.1:8000"
curl.exe -i "$baseUrl/health"
```

```powershell
curl.exe -i -X POST "$baseUrl/v1/predictions" `
  -H "Accept: application/json" `
  -H "Content-Type: application/json" `
  --data-binary "@examples/pump-maintenance-api/samples/prediction-valid.json"
```

```powershell
curl.exe -i -X POST "$baseUrl/v1/predictions" `
  -H "Accept: application/json" `
  -H "Content-Type: application/json" `
  --data-binary "@examples/pump-maintenance-api/samples/prediction-invalid.json"
```

## Bash

```bash
BASE_URL="http://127.0.0.1:8000"
curl -i "$BASE_URL/health"
```

```bash
curl -i -X POST "$BASE_URL/v1/predictions" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @examples/pump-maintenance-api/samples/prediction-valid.json
```

```bash
curl -i -X POST "$BASE_URL/v1/predictions" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  --data-binary @examples/pump-maintenance-api/samples/prediction-invalid.json
```

## Qué observar

1. La línea de estado antes del cuerpo.
2. `Content-Type` y `X-Request-Id` en la respuesta.
3. La diferencia entre `200`, `400` y `422`.
4. El resultado funcional no determina el código HTTP: una predicción de
   mantenimiento requerido sigue siendo una respuesta correcta.
