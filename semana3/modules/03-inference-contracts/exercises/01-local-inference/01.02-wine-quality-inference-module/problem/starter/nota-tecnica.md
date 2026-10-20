# Nota técnica

## Decisión 1: validar el artefacto

El cargador comprueba que el artefacto contiene las características esperadas, un estimador con `predict` y `predict_proba`, y una versión no vacía.

## Decisión 2: usar la versión del artefacto

El CLI toma `model_version` del artefacto y la incluye en cada predicción. Así, la salida indica qué versión del modelo se ha utilizado.
