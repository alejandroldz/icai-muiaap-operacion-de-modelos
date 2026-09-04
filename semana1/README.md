# Semana 1 — Fundamentos de MLOps con MLflow

Esta semana introduce el paso de un notebook experimental a una operación
observable con MLflow y Databricks Free Edition.

El material completo está en
[`modules/01-mlflow-databricks-foundations/`](modules/01-mlflow-databricks-foundations/).
Incluye dos clases, dos prácticas de notebook, una ficha de proyecto, una guía
docente y los datasets didácticos de `data/raw/`.

## Clase 1 — Del prototipo a la operación y puesta a punto

Contenido conceptual y de diseño: diferencia entre prototipo y producción,
unidades de evidencia de MLflow, riesgos iniciales y lectura crítica de un
notebook heredado.

El assignment de esta clase es preparar el entorno para la clase 2: instalar
`uv` con Python 3.12, Git y, en Windows, Git Bash; configurar la
identidad Git; confirmar una cuenta GitHub y el acceso al repositorio; y crear
una cuenta de Databricks Free Edition. El acceso se comprueba abriendo
`semana1/` como Git Folder, conectando *compute* serverless y leyendo el dataset
de la práctica. También se prepara un editor con soporte para notebooks, `curl`
y Postman para la práctica de HTTP, y se registra de forma no bloqueante el
estado de Docker y Compose para el bloque posterior. La ficha de proyecto no
forma parte de este assignment.

[Material de la clase 1](modules/01-mlflow-databricks-foundations/sessions/01-prototipo-a-operacion/README.md)

## Clase 2 — Tracking, trazas y evaluación

Construcción práctica del ciclo de MLflow: runs comparables, métricas,
artefactos, gate, Registry, alias `Champion`, API local y observabilidad.
También se trabaja AgentOps/LLMOps con trazas y evaluación determinista.

[Material de la clase 2](modules/01-mlflow-databricks-foundations/sessions/02-mlflow-free-edition/README.md)

## Prácticas y entregables

- [Assignment de puesta a punto](../assignments/semana01_clase01_assignment.pdf): `uv`, Python 3.12, Git, GitHub, Git Bash en Windows, editor, `curl`, Postman, Databricks Free Edition y revisión anticipada de Docker.
- [Práctica de ciclo de vida de ML](modules/01-mlflow-databricks-foundations/exercises/01_tracking_mlops/README.md): runs, gate, Registry y API local.
- [Práctica de AgentOps y LLMOps](modules/01-mlflow-databricks-foundations/exercises/02_agent_llmops/README.md): trazas, evaluación y fallos controlados.
- [Assignment técnico de la clase 2](../assignments/semana01_clase02_assignment.pdf): evidencia trazable de MLflow, AgentOps y API local.

## Entorno

Las prácticas están diseñadas para abrirse como Git Folder en Databricks Free
Edition. El notebook de ciclo de vida usa el dataset relativo a esta semana:

```text
semana1/data/raw/WineQT.csv
```

No se necesitan credenciales, endpoints de pago ni datos reales de pacientes.
El resultado es exclusivamente didáctico y no debe utilizarse para diagnóstico
ni para tomar decisiones sobre pacientes.

## Cómo comprobar la semana

La semana 1 no tiene una suite `pytest` local: sus prácticas son notebooks
pensados para Databricks Free Edition. Desde la raíz de esta semana se pueden
validar la estructura, el dataset y el formato JSON de todas las libretas:

```bash
cd semana1
test -f data/raw/WineQT.csv
find modules -name '*.ipynb' -print0 | xargs -0 -n1 jq empty
```

Para comprobar el comportamiento didáctico, abre la carpeta `semana1/` como
Git Folder en Databricks y ejecuta las versiones `_solucion.ipynb`. Después
ejecuta las versiones sin resolver para que el alumnado complete sus `TODO`.
