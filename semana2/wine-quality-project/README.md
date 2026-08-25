# Wine Quality — Semana 2

Proyecto reproducible para entrenar y comprobar un modelo básico de clasificación sobre el conjunto de datos Wine Quality.

## Estructura

```text
wine-quality-project/
├── data/
│   └── raw/
│       └── WineQT.csv
├── src/
│   └── wine_quality/
│       ├── __init__.py
│       └── train.py
├── tests/
│   └── test_train.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Preparación

Desde `semana2/wine-quality-project`:

```bash
uv sync --locked
```

Este comando crea el entorno virtual `.venv` e instala exactamente las versiones registradas en `uv.lock`.

## Ejecutar el entrenamiento

```bash
uv run --frozen python -m wine_quality.train
```

El programa debe mostrar:

- 1143 filas;
- 11 variables de entrada;
- 6 clases;
- una métrica F1 macro aproximada de `0.3402`.

## Ejecutar los tests

```bash
uv run --frozen pytest -q
```

Resultado esperado:

```text
1 passed
```

## Revisar la calidad del código

```bash
uv run --frozen ruff check .
```

Resultado esperado:

```text
All checks passed!
```

## Reproducibilidad

- `pyproject.toml` declara las dependencias del proyecto.
- `uv.lock` fija sus versiones exactas.
- `.venv` se genera localmente y no se versiona.
- El dataset original se conserva en `data/raw/`.
- El entrenamiento se ejecuta como un módulo Python.
- Los tests comprueban tanto los datos como la repetibilidad del entrenamiento.