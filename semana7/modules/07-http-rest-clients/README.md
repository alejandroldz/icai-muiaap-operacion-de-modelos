# Módulo 07 — HTTP, REST, JSON y clientes

## Resultado de aprendizaje

Al terminar la semana, el alumnado puede leer un intercambio HTTP, justificar
un contrato REST, consumir una API y aislar ese consumo detrás de un gateway.
La API se entrega ejecutable: construir un backend con FastAPI corresponde a
S8.

## Recorrido de las dos clases

### Clase 1 — observar y consumir HTTP

El caso de bombas es autocontenido y sirve para practicar método, ruta, cuerpo,
cabeceras, códigos de estado y clientes.

1. [Sesión 01: HTTP, REST y JSON](sessions/01-http-rest-json/README.md)
2. [Guion docente de clase 1](guides/class-1-practices.md)
3. [Microejercicios](exercises/01-http-json-microexercises/problem/README.md)
4. [API de bombas](examples/pump-maintenance-api/README.md)
5. Clientes con [curl](examples/curl/README.md),
   [Postman](examples/postman/README.md) y
   [Python](examples/python-client/README.md)
6. [Laboratorio 02](exercises/02-api-client-lab/problem/README.md), ampliación
   posterior a la clase 1 y no la clase 2

### Clase 2 — continuar Wine Quality

La app construida hasta S6 mantiene su controlador y su interfaz. El único
cambio arquitectónico es sustituir el gateway local por un cliente HTTP.

1. [Sesión 02: del gateway local a HTTP](sessions/02-wine-http-gateway/README.md)
2. [Guion docente de 120 minutos](guides/class-2-workshop.md)
3. [Enunciado del ejercicio 03](exercises/03-wine-http-gateway/README.md)
4. [Starter](exercises/03-wine-http-gateway/problem/starter/README.md)
5. [API Wine Quality, caja negra](examples/wine-quality-api/README.md)
6. [Solución y réplica docente](solutions/03-wine-http-gateway/README.md)

## Requisitos y preparación reproducible

Se requieren **Python 3.12** y [`uv`](https://docs.astral.sh/uv/). Desde
`semana7/modules/07-http-rest-clients`:

```bash
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

En la raíz, `uv sync` puede crear un `uv.lock` local no versionado. Ese archivo
no forma parte del material reproducible. Solo los subproyectos `starter` y
`solution` incluyen locks versionados y se preparan con
`uv sync --locked --extra app`, como detallan sus README.

## Arranque rápido de clase 1

En una terminal:

```bash
uv run python examples/pump-maintenance-api/server.py
```

En otra terminal:

```bash
uv run python examples/python-client/client.py examples/pump-maintenance-api/samples/prediction-valid.json
```

## Arranque rápido de clase 2

La API Wine se ejecuta desde la raíz del módulo:

```bash
uv run python examples/wine-quality-api/server.py
```

El starter, sus pruebas y la app se ejecutan desde
`exercises/03-wine-http-gateway/problem/starter`. Las instrucciones completas
incluyen Bash y PowerShell.

## Límite didáctico

- En clase 1 se usa el dominio de bombas para aprender HTTP sin depender del
  proyecto acumulativo.
- En clase 2 se vuelve a Wine Quality y se implementa solo el lado cliente.
- En S8 se reemplazará la caja negra por un backend FastAPI compatible con el
  mismo contrato.
