# Solución — laboratorio de clientes

Corresponde a la ampliación posterior a la clase 1; no es material de clase 2.

La solución ejecutable está en [client.py](client.py). La versión ampliada con
CLI y detalle del error devuelto por la API está en el
[ejemplo docente](../../examples/python-client/client.py).

## Decisiones clave

- `json=payload` evita serializar manualmente y configura el tipo de contenido.
- `Accept: application/json` declara el formato esperado.
- `timeout` impide una espera sin límite.
- `raise_for_status()` hace imposible confundir un `422` con un resultado.
- timeout, conexión y status HTTP requieren mensajes y acciones diferentes.
- se analiza JSON después de comprobar el status de éxito.

Un POST no se reintenta de manera ciega: el servidor podría haber procesado la
operación aunque el cliente no recibiera la respuesta. Las claves de
idempotencia se introducen más adelante.
