# Cliente Python de referencia

`client.py` muestra el patrón mínimo para consumir una API de inferencia:

- `json=payload` serializa el diccionario y añade el tipo de contenido;
- `Accept: application/json` expresa el formato esperado;
- `timeout` evita una espera sin límite;
- `raise_for_status()` separa éxito de respuestas 4xx/5xx;
- las excepciones distinguen transporte, HTTP y contrato de respuesta.

Después de `uv sync`, con la API arrancada y desde la raíz del módulo:

```text
uv run python examples/python-client/client.py examples/pump-maintenance-api/samples/prediction-valid.json
```

Para observar el error de validación:

```text
uv run python examples/python-client/client.py examples/pump-maintenance-api/samples/prediction-invalid.json
```

Para provocar un fallo de conexión de forma segura:

```text
uv run python examples/python-client/client.py examples/pump-maintenance-api/samples/prediction-valid.json --base-url http://127.0.0.1:8999
```

No se reintenta automáticamente un POST: podría duplicar una operación si el
servidor hubiera procesado la petición pero se perdiera la respuesta.
