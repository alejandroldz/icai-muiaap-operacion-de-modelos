# Semana 5: dos prácticas Churn → Wine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar S5 para que la clase 1 enseñe y practique Streamlit con una miniapp Churn guiada y la clase 2 transfiera ese patrón a un frontal Wine que exige el bundle real de S4.

**Architecture:** La práctica 5.1 proporciona una función pura `predict()` y deja al alumno tres responsabilidades observables: recoger valores dentro de `st.form`, llamar una vez al predictor tras el submit y presentar resultado/error. La práctica 5.2 es autocontenida, proporciona el esquema Wine completo, elimina todo modo demo y obliga a que la UI atraviese `PackagedBundleGateway` configurado mediante `MODEL_UI_BUNDLE`. Presentación, guías y assignments describen exactamente esos dos recorridos.

**Tech Stack:** Python 3.11+, Streamlit 1.40+, pytest, Ruff, Pydantic, uv, ReportLab/pypdf para assignments y `@oai/artifact-tool` para PowerPoint.

---

## Mapa de archivos

### Práctica 5.1 Churn

- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/README.md`: enunciado de 60 minutos.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/app.py`: starter con tres tareas del alumno.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/pyproject.toml`: entorno autocontenido sin Gradio.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/README.md`: comandos y checklist.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/src/churn_demo/{__init__.py,model.py}`: contrato completo proporcionado.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/tests/{fake_streamlit.py,test_app.py,test_model.py}`.
- Crear `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/app.py` resuelto.
- Crear `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/{README.md,pyproject.toml,uv.lock}`.
- Crear `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/src/churn_demo/{__init__.py,model.py}`.
- Crear `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/tests/{fake_streamlit.py,test_app.py,test_model.py}`.
- Crear `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/explainer/readme.md`.
- Retirar de la ruta activa `examples/churn-demo/`, `exercises/01-ui-form-contract/`, `exercises/class-1-microexercises.md` y `solutions/class-1-microexercises-reference.md` después de migrar su contenido útil.

### Práctica 5.2 Wine

- Modificar ambos árboles `exercises/02-first-streamlit/problem/starter/` y `solutions/02-first-streamlit/`.
- `src/model_ui/ui_schema.py` pasa a estar completo en starter y solución; no procede de 5.1.
- `src/model_ui/gateway.py` conserva `InferenceGateway`, `PackagedBundleGateway` y la validación; elimina `DemoGateway` y `UnavailableGateway`.
- `app.py` exige `MODEL_UI_BUNDLE`; ningún recorrido produce una predicción simulada.
- Actualizar `tests/test_app.py`, `tests/test_gateway.py`, README y explainer.

### Narrativa y entregables

- Modificar `README.md` únicamente donde enlaza los materiales de S5.
- Modificar `semana5/README.md` y `semana5/modules/05-streamlit-basic-model-ui/README.md`.
- Modificar `semana5/assets/05-wine-quality/README.md` si describe un modo demo o el handoff anterior.
- Modificar `guides/class-1-practices.md`, `guides/class-2-workshop.md` y los README de ambas sesiones.
- Revisar `sessions/01-streamlit-basics/notebooks/01-streamlit-basics-guiada.ipynb` para que apunte al nuevo starter/solución.
- Modificar `tools/test_generate_assignment_pdfs.py` y `tools/generate_assignment_pdfs.py`.
- Regenerar `assignments/semana05_clase01_assignment.pdf` y `assignments/semana05_clase02_assignment.pdf`.
- Crear `Operacion de Modelos/S05/Teoria/Guia docente - Semana 05 - Clase 1 - Churn 60-60.docx` como copia coherente; no sobrescribir las guías existentes.
- Crear una nueva copia `Operacion de Modelos/S05/Teoria/MUIAAp_S5_Interfaces_Churn_Wine.pptx`; no sobrescribir el original ni las copias anteriores.

---

### Task 1: Crear el contrato y las pruebas de la práctica 5.1 Churn

**Files:**
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/pyproject.toml`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/src/churn_demo/__init__.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/src/churn_demo/model.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/tests/test_model.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/tests/fake_streamlit.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/tests/test_app.py`

- [ ] **Step 1: Crear el subproyecto sin Gradio**

Usar este `pyproject.toml` tanto en starter como en solución:

```toml
[project]
name = "week5-churn-streamlit"
version = "0.1.0"
description = "Practica guiada S5: interfaz Streamlit sobre una funcion Churn."
requires-python = ">=3.11"
dependencies = ["streamlit>=1.40,<2.0"]

[dependency-groups]
dev = ["pytest>=8.0,<9.0", "ruff>=0.8,<1.0"]

[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/churn_demo"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

- [ ] **Step 2: Migrar la función pura y sus tests sin cambiar su contrato**

Copiar el contenido actual de:

```text
examples/churn-demo/src/churn_demo/model.py
examples/churn-demo/tests/test_model.py
```

a los destinos del starter. No reescribir la función: copiar `model.py`
byte por byte para mantener exactamente su firma, validación y cálculo.

La copia se realizará también en la solución para que problema y solución
compartan el mismo núcleo por hash.

- [ ] **Step 3: Escribir primero el doble de Streamlit**

`tests/fake_streamlit.py` debe registrar formulario, widgets, submit y salida:

```python
class FakeStreamlit:
    def __init__(self, *, submitted: bool = False) -> None:
        self.submitted = submitted
        self.active_form: str | None = None
        self.forms: list[str] = []
        self.widgets: list[tuple[str, str, dict[str, object]]] = []
        self.submit_calls: list[tuple[str, str]] = []
        self.events: list[tuple[object, ...]] = []

    def form(self, key: str):
        self.forms.append(key)
        return FormContext(self, key)

    def slider(self, label: str, min_value, max_value, value, *, key: str):
        form_key = self.require_form("slider")
        self.widgets.append(("slider", label, {
            "min_value": min_value, "max_value": max_value,
            "value": value, "key": key, "form_key": form_key,
        }))
        return value

    def number_input(self, label: str, **kwargs):
        form_key = self.require_form("number_input")
        self.widgets.append(("number_input", label, {**kwargs, "form_key": form_key}))
        return kwargs["value"]

    def checkbox(self, label: str, *, value: bool, key: str):
        form_key = self.require_form("checkbox")
        self.widgets.append(("checkbox", label, {
            "value": value, "key": key, "form_key": form_key,
        }))
        return value

    def form_submit_button(self, label: str) -> bool:
        form_key = self.require_form("form_submit_button")
        self.submit_calls.append((label, form_key))
        return self.submitted

    def info(self, value: object) -> None:
        self.events.append(("info", value))

    def error(self, value: object) -> None:
        self.events.append(("error", value))

    def success(self, value: object) -> None:
        self.events.append(("success", value))

    def metric(self, label: str, value: object) -> None:
        self.events.append(("metric", label, value))

    def write(self, value: object) -> None:
        self.events.append(("write", value))
```

Completar el mismo archivo con el contexto y las comprobaciones siguientes;
`require_form` y `output_text` son métodos de `FakeStreamlit`:

```python
class FormContext:
    def __init__(self, owner: "FakeStreamlit", key: str) -> None:
        self.owner = owner
        self.key = key

    def __enter__(self):
        if self.owner.active_form is not None:
            raise AssertionError("Solo puede haber un formulario activo")
        self.owner.active_form = self.key
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.owner.active_form = None


def require_form(self, component: str) -> str:
    if self.active_form is None:
        raise AssertionError(f"{component} debe estar dentro de st.form")
    return self.active_form


def output_text(self) -> str:
    return repr(self.events)
```

- [ ] **Step 4: Escribir las pruebas rojas del frontal**

`tests/test_app.py` debe contener exactamente estas siete conductas:

```python
from pathlib import Path

import pytest

import app
from fake_streamlit import FakeStreamlit

SAMPLE = {
    "tenure_months": 2,
    "monthly_spend_eur": 95.0,
    "support_calls": 4,
    "has_annual_contract": False,
}

PREDICTION = {
    "will_churn": True,
    "label": "Baja probable",
    "risk_score": 0.95,
    "explanation": "Regla docente; umbral 0,50.",
}


class RecordingPredictor:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def __call__(self, **values):
        self.calls.append(dict(values))
        return PREDICTION


def test_collect_profile_uses_one_form_four_widgets_and_one_submit():
    st = FakeStreamlit(submitted=False)
    submitted, values = app.collect_profile(st)

    assert submitted is False
    assert st.forms == ["churn_form"]
    assert [item[2]["key"] for item in st.widgets] == [
        "tenure_months",
        "monthly_spend_eur",
        "support_calls",
        "has_annual_contract",
    ]
    assert st.submit_calls == [("Calcular riesgo", "churn_form")]
    assert set(values) == {
        "tenure_months", "monthly_spend_eur",
        "support_calls", "has_annual_contract",
    }


def test_editing_without_submit_makes_zero_calls(monkeypatch):
    st = FakeStreamlit(submitted=False)
    predictor = RecordingPredictor()
    monkeypatch.setattr(app, "collect_profile", lambda _st: (False, SAMPLE))

    app.run_app(st, predictor)

    assert predictor.calls == []


def test_submit_makes_one_call_and_renders(monkeypatch):
    st = FakeStreamlit(submitted=True)
    predictor = RecordingPredictor()
    monkeypatch.setattr(app, "collect_profile", lambda _st: (True, SAMPLE))

    app.run_app(st, predictor)

    assert predictor.calls == [SAMPLE]
    assert "Baja probable" in st.output_text()
    assert "0.95" in st.output_text()


def test_predict_error_is_human_and_hides_raw_detail(monkeypatch):
    st = FakeStreamlit(submitted=True)
    monkeypatch.setattr(app, "collect_profile", lambda _st: (True, SAMPLE))

    def failing_predictor(**_values):
        raise ValueError(r"Traceback C:\secret\customer.csv")

    app.run_app(st, failing_predictor)

    output = st.output_text()
    assert "No se pudo calcular" in output
    assert "Traceback" not in output
    assert "customer.csv" not in output


def test_render_prediction_shows_label_score_and_explanation():
    st = FakeStreamlit()
    app.render_prediction(st, PREDICTION)
    output = st.output_text()
    assert "Baja probable" in output
    assert "0.95" in output
    assert "umbral 0,50" in output


def test_fake_rejects_widgets_outside_form():
    st = FakeStreamlit()
    with pytest.raises(AssertionError, match="dentro de st.form"):
        st.slider("Antigüedad", 0, 120, 12, key="tenure_months")


def test_app_does_not_use_gradio_state_or_cache():
    source = Path(app.__file__).read_text(encoding="utf-8")
    for forbidden in ("gradio", "session_state", "cache_data", "cache_resource"):
        assert forbidden not in source
```

- [ ] **Step 5: Ejecutar las pruebas y comprobar el rojo esperado**

Run:

```powershell
cd semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter
uv sync
uv run python -m pytest -q
```

Expected: los seis tests de `model.py` pasan; los tests de interfaz fallan porque
`app.py` todavía no existe o no define `collect_profile`, `render_prediction` y
`run_app`.

- [ ] **Step 6: Commit del contrato y las pruebas**

```powershell
git add semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit
git commit -m "test: define guided churn UI practice"
```

---

### Task 2: Construir el starter y la solución de la práctica 5.1

**Files:**
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/app.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/app.py`
- Create: `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/{pyproject.toml,README.md}`
- Create: `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/src/churn_demo/{__init__.py,model.py}`
- Create: `semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/tests/{fake_streamlit.py,test_app.py,test_model.py}`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/{README.md,explainer/readme.md}`
- Create: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/README.md`

- [ ] **Step 1: Crear el starter con tres huecos observables**

El starter define las firmas y el cableado, pero deja las funciones del alumno
con fallos explícitos:

```python
from collections.abc import Callable
from typing import Any

from churn_demo.model import ChurnPrediction, predict

Predictor = Callable[..., ChurnPrediction]


def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:
    """Renderiza cuatro widgets dentro de un único formulario."""
    raise NotImplementedError("STUDENT TASK: construye el formulario Churn")


def render_prediction(st: Any, result: ChurnPrediction) -> None:
    """Muestra etiqueta, score orientativo y explicación."""
    raise NotImplementedError("STUDENT TASK: presenta la predicción")


def run_app(st: Any, predictor: Predictor) -> None:
    """Conecta submit, llamada al predictor y actualización visible."""
    raise NotImplementedError("STUDENT TASK: conecta el submit con predict()")


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Churn sintético · S5", page_icon="📉")
    st.title("¿Qué cliente podría darse de baja?")
    st.caption("Caso docente sintético; el score no es una probabilidad calibrada.")
    run_app(st, predict)
```

Los tres huecos corresponden exactamente al trabajo del alumno: formulario,
llamada condicionada por el botón y actualización visible.

- [ ] **Step 2: Implementar la solución mínima**

```python
def collect_profile(st: Any) -> tuple[bool, dict[str, object]]:
    with st.form("churn_form"):
        values = {
            "tenure_months": st.slider(
                "Antigüedad (meses)", 0, 120, 12, key="tenure_months"
            ),
            "monthly_spend_eur": st.number_input(
                "Gasto mensual (€)", min_value=0.0, max_value=300.0,
                value=60.0, step=1.0, key="monthly_spend_eur"
            ),
            "support_calls": st.slider(
                "Llamadas a soporte", 0, 20, 1, key="support_calls"
            ),
            "has_annual_contract": st.checkbox(
                "Tiene contrato anual", value=False,
                key="has_annual_contract"
            ),
        }
        submitted = st.form_submit_button("Calcular riesgo")
    return submitted, values


def render_prediction(st: Any, result: ChurnPrediction) -> None:
    st.success(result["label"])
    st.metric("Score orientativo", f'{result["risk_score"]:.2f}')
    st.write(result["explanation"])


def run_app(st: Any, predictor: Predictor) -> None:
    submitted, values = collect_profile(st)
    if not submitted:
        st.info("Ajusta el perfil y pulsa «Calcular riesgo».")
        return
    try:
        result = predictor(**values)
    except ValueError:
        st.error("No se pudo calcular el riesgo con esos valores.")
        return
    render_prediction(st, result)
```

- [ ] **Step 3: Ejecutar la solución y comprobar verde**

```powershell
cd semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit
uv sync
uv run python -m pytest -q
uv run ruff check app.py src tests
uv run ruff format --check app.py src tests
```

Expected: todos los tests pasan y Ruff informa `All checks passed!`.

- [ ] **Step 4: Confirmar el rojo pedagógico del starter**

```powershell
cd semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter
uv run python -m pytest -q
```

Expected: `5 failed, 8 passed`. Fallan únicamente las comprobaciones de
formulario, 0/1 llamadas, presentación y error que corresponden a los tres
huecos del alumno; el contrato del modelo y el fake permanecen verdes.

- [ ] **Step 5: Escribir el enunciado, la explicación y el checklist**

El README principal debe usar exactamente esta secuencia:

```text
0–10 contrato y predicciones
10–25 formulario
25–35 submit y llamada
35–45 resultado y error
45–55 tests
55–60 QA y puente a Wine
```

El checklist manual contiene cuatro filas: arranque, edición sin envío, submit
válido y resultado actualizado. El explainer explica por qué `app.py` no puede
contener la regla de churn y por qué no se usan `session_state` ni caché.

- [ ] **Step 6: Verificar hashes del núcleo proporcionado**

```powershell
Get-FileHash semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit/problem/starter/src/churn_demo/model.py
Get-FileHash semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit/src/churn_demo/model.py
```

Expected: los dos SHA-256 son idénticos.

- [ ] **Step 7: Commit de la práctica 5.1**

```powershell
git add semana5/modules/05-streamlit-basic-model-ui/exercises/01-churn-streamlit semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit
git commit -m "feat: add guided churn Streamlit practice"
```

---

### Task 3: Convertir la práctica 5.2 en Wine bundle-only

**Files:**
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/app.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/src/model_ui/gateway.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/src/model_ui/ui_schema.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/tests/test_app.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/tests/test_gateway.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/app.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/src/model_ui/gateway.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/src/model_ui/ui_schema.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/tests/test_app.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/tests/test_gateway.py`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/{README.md,explainer/readme.md}`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/README.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit/README.md`

- [ ] **Step 1: Escribir las pruebas que prohíben el modo demo**

Reemplazar las pruebas de `DemoGateway` por estas invariantes:

```python
def test_build_gateway_without_configuration_raises(monkeypatch):
    monkeypatch.delenv("MODEL_UI_BUNDLE", raising=False)
    with pytest.raises(ArtifactUnavailableError, match="MODEL_UI_BUNDLE"):
        app.build_gateway()


def test_build_gateway_uses_the_configured_bundle(monkeypatch, tmp_path):
    bundle = tmp_path / "wine-bundle"
    bundle.mkdir()
    sentinel = RecordingGateway()
    monkeypatch.setenv("MODEL_UI_BUNDLE", str(bundle))
    monkeypatch.setattr(
        app.PackagedBundleGateway,
        "from_bundle_path",
        lambda path: sentinel if path == bundle else None,
    )
    assert app.build_gateway() is sentinel


def test_runtime_gateway_module_has_no_demo_gateway():
    import model_ui.gateway as gateway_module
    assert not hasattr(gateway_module, "DemoGateway")
    assert not hasattr(gateway_module, "UnavailableGateway")


def test_configured_app_hides_bundle_error_details():
    st = FakeStreamlit()

    def failing_factory():
        raise ArtifactUnavailableError(r"Traceback C:\secret\wine.joblib")

    app.run_configured_app(st, failing_factory)

    output = st.output_text()
    assert "MODEL_UI_BUNDLE" in output
    assert "Traceback" not in output
    assert "wine.joblib" not in output
```

`tests/test_gateway.py` debe comprobar además la integración con el formato
real de S4 mediante un bundle temporal, no mediante un gateway simulado:

```python
import json
from pathlib import Path

import joblib

from model_ui.gateway import FEATURE_NAMES, PackagedBundleGateway

SAMPLE = {
    "fixed_acidity": 7.4,
    "volatile_acidity": 0.7,
    "citric_acid": 0.0,
    "residual_sugar": 1.9,
    "chlorides": 0.076,
    "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0,
    "density": 0.9978,
    "ph": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4,
}


class FixedEstimator:
    def predict(self, features: list[list[float]]) -> list[str]:
        return ["acceptable" for _ in features]

    def predict_proba(self, features: list[list[float]]) -> list[list[float]]:
        return [[0.1, 0.8, 0.1] for _ in features]


def write_test_bundle(bundle_path: Path) -> None:
    bundle_path.mkdir()
    manifest = {
        "schema_version": "wine-quality-bundle-v1",
        "model_version": "wine-test-v1",
        "preprocessing_version": "wine-red-features-v1",
        "feature_names": list(FEATURE_NAMES),
        "output_labels": ["needs_review", "acceptable", "excellent"],
        "estimator_type": "FixedEstimator",
    }
    (bundle_path / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    joblib.dump({"estimator": FixedEstimator()}, bundle_path / "model.joblib")


def test_packaged_bundle_gateway_runs_the_s4_bundle(tmp_path):
    bundle_path = tmp_path / "wine-bundle"
    write_test_bundle(bundle_path)

    prediction = PackagedBundleGateway.from_bundle_path(bundle_path).predict(SAMPLE)

    assert prediction.quality_band == "acceptable"
    assert prediction.confidence == 0.8
    assert prediction.model_version == "wine-test-v1"
    assert prediction.preprocessing_version == "wine-red-features-v1"
```

Mantener las pruebas de cero/una llamada y de bundle ausente. Cambiar las
versiones del `PREDICTION` de test a nombres neutrales como `wine-model-v1` y
`wine-preprocessing-v1`.

- [ ] **Step 2: Ejecutar las pruebas y verificar el rojo**

Run en starter y solución:

```powershell
uv run python -m pytest -q
```

Expected: falla la ausencia de configuración porque `build_gateway()` todavía
devuelve `DemoGateway`, y falla la comprobación que exige eliminar esa clase.

- [ ] **Step 3: Eliminar `DemoGateway` del runtime**

En `app.py` dejar la selección así:

```python
def build_gateway() -> InferenceGateway:
    """Carga obligatoriamente el bundle de S4 configurado."""
    bundle_value = os.getenv("MODEL_UI_BUNDLE")
    if not bundle_value:
        raise ArtifactUnavailableError("MODEL_UI_BUNDLE no está configurado.")
    try:
        return PackagedBundleGateway.from_bundle_path(Path(bundle_value))
    except Exception as error:  # noqa: BLE001
        raise ArtifactUnavailableError("No se pudo cargar el bundle de S4.") from error


def render_bundle_error(st: Any) -> None:
    st.error("No se pudo cargar el bundle de S4.")
    st.info("Configura MODEL_UI_BUNDLE y vuelve a ejecutar la aplicación.")


def run_configured_app(st: Any, gateway_factory=build_gateway) -> None:
    try:
        gateway = gateway_factory()
    except ArtifactUnavailableError:
        render_bundle_error(st)
        return
    run_app(st, gateway)
```

`main()` configura título/caption y termina llamando a
`run_configured_app(st)`, nunca a `build_gateway()` fuera de esa frontera de
error.

En `gateway.py` eliminar completamente `DemoGateway` y `UnavailableGateway`.
Los fallos de configuración/carga se traducen en `app.py`; los dobles solo
existen dentro de `tests/`.

- [ ] **Step 4: Hacer que el esquema Wine del starter esté completo**

Copiar al starter el `FIELD_SPECS` actualmente resuelto en
`solutions/02-first-streamlit/src/model_ui/ui_schema.py`. El archivo debe
contener once nombres únicos y tipos no opcionales:

```python
@dataclass(frozen=True, slots=True)
class FieldSpec:
    name: str
    label: str
    min_value: float
    max_value: float
    default: float
    step: float
```

Eliminar cualquier texto que indique que procede de 5.1. El test de esquema
debe estar verde desde el primer checkout de la práctica 5.2.

- [ ] **Step 5: Conservar dos tareas del alumno en el starter**

`collect_values()` y `render_prediction()` mantienen sus
`NotImplementedError`. `run_app()` se entrega resuelto con cero llamadas antes
de submit y una después. `run_configured_app()` traduce de forma segura el
bundle ausente sin mostrar la causa ni la ruta.

- [ ] **Step 6: Verificar solución y starter**

```powershell
cd semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit
uv run python -m pytest -q
uv run ruff check app.py src tests
uv run ruff format --check app.py src tests

cd ../../../exercises/02-first-streamlit/problem/starter
uv run python -m pytest -q
```

Expected: solución completamente verde; starter falla solo en las dos tareas
del alumno (`collect_values` y `render_prediction`). Ningún resultado de test
contiene `DemoGateway`.

- [ ] **Step 7: Reescribir instrucciones y evidencia**

Los README deben exigir:

```powershell
$env:MODEL_UI_BUNDLE = 'RUTA_AL_BUNDLE_DE_S4'
uv run --with 'streamlit>=1.40,<2.0' streamlit run app.py
```

La matriz QA contiene exactamente: arranque con bundle, edición sin envío,
submit válido y bundle ausente. Aclarar que dobles del gateway solo existen en
tests y que una ejecución sin bundle nunca es una entrega válida.

- [ ] **Step 8: Commit de la práctica 5.2**

```powershell
git add semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit
git commit -m "refactor: require the S4 bundle in the Wine UI"
```

---

### Task 4: Unificar guías, sesiones y navegación de S5

**Files:**
- Modify: `README.md` (solo navegación de S5)
- Modify: `semana5/README.md`
- Modify: `semana5/assets/05-wine-quality/README.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/README.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/guides/class-1-practices.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/guides/class-2-workshop.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/sessions/01-streamlit-basics/README.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/sessions/01-streamlit-basics/notebooks/01-streamlit-basics-guiada.ipynb`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/sessions/02-first-model-ui/README.md`
- Modify: `semana5/modules/05-streamlit-basic-model-ui/examples/basic-app/README.md`
- Delete after migration: `semana5/modules/05-streamlit-basic-model-ui/examples/churn-demo/`
- Delete after migration: `semana5/modules/05-streamlit-basic-model-ui/exercises/01-ui-form-contract/`
- Delete after migration: `semana5/modules/05-streamlit-basic-model-ui/exercises/class-1-microexercises.md`
- Delete after migration: `semana5/modules/05-streamlit-basic-model-ui/solutions/class-1-microexercises-reference.md`

- [ ] **Step 1: Escribir un chequeo rojo de coherencia textual**

Ejecutar antes de editar:

```powershell
rg -n "80 min|40 min|01-ui-form-contract|ui_schema.py.*5\.1|DemoGateway|modo demo|examples/churn-demo" semana5
```

Expected: aparecen referencias activas que contradicen el diseño aprobado.

- [ ] **Step 2: Reescribir la clase 1 como 60+60**

El guion docente debe contener exactamente:

```text
0–10 propósito y caso Churn
10–20 contrato predict() y salida
20–35 rerun, widgets y formulario
35–50 demo guiada Streamlit
50–60 preparación del starter
60–70 contrato y predicciones del alumno
70–85 formulario
85–95 submit y llamada
95–105 resultado y error
105–115 tests
115–120 QA y puente Churn → Wine
```

La práctica activa enlazada es únicamente `exercises/01-churn-streamlit/`.

- [ ] **Step 3: Reescribir la clase 2 como transferencia conceptual**

Explicar que 5.1 no entrega un archivo reutilizable. La transferencia conserva
`st.form`, submit, 0/1 llamadas, frontera de inferencia y presentación; Wine
añade once campos, `InferenceGateway` y el bundle de S4.

- [ ] **Step 4: Actualizar notebook y enlaces**

El notebook guiado puede conservar sus predicciones Churn, pero todos sus paths
deben apuntar a `solutions/01-churn-streamlit` para la demo docente. No debe
importar Gradio.

- [ ] **Step 5: Retirar los materiales anteriores de rutas activas**

Antes de borrar, resolver las rutas absolutas y verificar que todas están bajo:

```text
semana5/modules/05-streamlit-basic-model-ui/
```

Eliminar únicamente los cuatro destinos exactos listados en esta tarea. No usar
globs ni borrar el módulo completo.

- [ ] **Step 6: Verificar enlaces y ausencia de residuos**

```powershell
rg -n "01-ui-form-contract|ui_schema.py.*5\.1|DemoGateway|examples/churn-demo" semana5
```

Expected: cero referencias activas. Ejecutar además el comprobador de enlaces
Markdown sobre todos los README y guías modificados; expected: cero rutas
inexistentes.

- [ ] **Step 7: Commit de documentación**

```powershell
git add -- README.md semana5/README.md semana5/assets/05-wine-quality/README.md semana5/modules/05-streamlit-basic-model-ui/README.md semana5/modules/05-streamlit-basic-model-ui/guides/class-1-practices.md semana5/modules/05-streamlit-basic-model-ui/guides/class-2-workshop.md semana5/modules/05-streamlit-basic-model-ui/sessions/01-streamlit-basics semana5/modules/05-streamlit-basic-model-ui/sessions/02-first-model-ui semana5/modules/05-streamlit-basic-model-ui/examples/basic-app/README.md semana5/modules/05-streamlit-basic-model-ui/examples/churn-demo semana5/modules/05-streamlit-basic-model-ui/exercises/01-ui-form-contract semana5/modules/05-streamlit-basic-model-ui/exercises/class-1-microexercises.md semana5/modules/05-streamlit-basic-model-ui/solutions/class-1-microexercises-reference.md
git commit -m "docs: align week 5 around churn then Wine"
```

---

### Task 5: Actualizar la guía docente en una copia nueva

**Files:**
- Read only: `Operacion de Modelos/S05/Teoria/Guia docente - Semana 05 - Clase 1 - actualizada.docx`
- Create: `Operacion de Modelos/S05/Teoria/Guia docente - Semana 05 - Clase 1 - Churn 60-60.docx`

- [ ] **Step 1: Cargar la skill de documentos e inspeccionar la guía completa**

Leer `documents/SKILL.md`, extraer el texto y renderizar todas las páginas de la
guía fuente. Registrar cualquier referencia a 27 diapositivas, práctica Wine de
40 minutos, `ui_schema.py`, bitácora separada o `DemoGateway`.

- [ ] **Step 2: Crear una copia con el guion 60+60 aprobado**

La nueva guía debe contener:

```text
0–60   teoría y demostración Churn
60–120 práctica 5.1 miniapp Churn
cierre puente conceptual Churn → Wine
clase 2 práctica Wine con bundle S4 obligatorio
```

Actualizar el número y títulos de diapositivas para coincidir con la nueva
presentación. Integrar las antiguas preguntas de microejercicios como pausas de
la práctica, nunca como una tercera entrega.

- [ ] **Step 3: Renderizar y verificar el DOCX**

Usar `render_docx.py` para generar PNG de todas las páginas y un PDF temporal.
Inspeccionar cada página: sin texto cortado, tablas partidas de forma ilegible,
encabezados huérfanos ni referencias a materiales retirados.

- [ ] **Step 4: Verificar la copia y preservar las fuentes**

Confirmar que los dos DOCX originales conservan hash y fecha. La nueva guía es
un archivo adicional y no se añade a Git porque vive fuera de la raíz del
repositorio.

---

### Task 6: Regenerar los assignments 5.1 y 5.2

**Files:**
- Modify: `tools/test_generate_assignment_pdfs.py`
- Modify: `tools/generate_assignment_pdfs.py`
- Modify: `assignments/semana05_clase01_assignment.pdf`
- Modify: `assignments/semana05_clase02_assignment.pdf`

- [ ] **Step 1: Cambiar primero los tests del contenido**

Las definiciones S5 deben exigir:

```python
def test_week_five_definitions_and_rubrics() -> None:
    first, second = week_five_assignments()
    assert first.title == "Del formulario a la inferencia: miniapp Churn"
    assert first.duration == "60 min"
    assert second.title == "Del bundle S4 al frontal Wine"
    assert second.duration == "120 min"
    assert all(sum(int(p) for _, p in item.rubric) == 10 for item in (first, second))


def test_week_five_class_one_builds_a_churn_frontend() -> None:
    content = assignment_text(week_five_assignments()[0])
    for required in (
        "predict()", "st.form", "st.form_submit_button", "cero llamadas",
        "una llamada", "label", "risk_score", "explanation", "app.py",
        "tests", "01-churn-streamlit",
    ):
        assert required in content
    for forbidden in ("ui_schema.py", "FIELD_SPECS", "MODEL_UI_BUNDLE"):
        assert forbidden not in content


def test_week_five_class_two_requires_the_s4_bundle() -> None:
    content = assignment_text(week_five_assignments()[1])
    for required in (
        "bundle de S4", "MODEL_UI_BUNDLE", "st.form", "gateway.predict(values)",
        "cero llamadas", "una llamada", "quality_band", "confidence",
        "model_version", "preprocessing_version", "bundle ausente",
    ):
        assert required in content
    assert "DemoGateway" not in content
    assert "modo demo" not in content.lower()
```

- [ ] **Step 2: Ejecutar y confirmar que los tests fallan con los assignments anteriores**

```powershell
uv run python -m pytest tools/test_generate_assignment_pdfs.py -q
```

Expected: fallan las aserciones de título, duración y alcance de S5.

- [ ] **Step 3: Reescribir las dos definiciones S5**

Assignment 5.1 debe reflejar la secuencia de 60 minutos, tres responsabilidades
del alumno, checklist de cuatro casos y rúbrica 2+2+2+2+2.

Assignment 5.2 debe declarar el bundle S4 como prerrequisito, proporcionar el
esquema Wine completo, prohibir el modo demo y exigir las cuatro salidas. Sus
comandos deben aparecer en líneas PowerShell independientes, sin `&&`.

- [ ] **Step 4: Ejecutar toda la suite del generador**

```powershell
uv run python -m pytest tools/test_generate_assignment_pdfs.py -q
uv run ruff check tools/generate_assignment_pdfs.py tools/test_generate_assignment_pdfs.py
```

Expected: todos los tests pasan y Ruff no reporta errores.

- [ ] **Step 5: Regenerar únicamente la semana 5**

```powershell
uv run python tools/generate_assignment_pdfs.py --week 5
```

Expected: se actualizan solo los dos PDF `semana05_clase0{1,2}_assignment.pdf`.

- [ ] **Step 6: Validar los PDF**

Con pypdf comprobar dos páginas A4 por archivo, nueve secciones, títulos nuevos
y ausencia de `DemoGateway`. Renderizar las cuatro páginas con Poppler y
revisarlas individualmente a tamaño completo: ningún corte, solape o línea de
comando partida de forma ambigua.

- [ ] **Step 7: Commit de assignments**

```powershell
git add tools/generate_assignment_pdfs.py tools/test_generate_assignment_pdfs.py assignments/semana05_clase01_assignment.pdf assignments/semana05_clase02_assignment.pdf
git commit -m "docs: regenerate week 5 assignments"
```

---

### Task 7: Crear la nueva copia de la presentación S5

**Files:**
- Create: `tmp/s5_churn_wine/revise_s5_deck.mjs`
- Create: `Operacion de Modelos/S05/Teoria/MUIAAp_S5_Interfaces_Churn_Wine.pptx`
- Read only: `C:/Users/jaandr7/Desktop/Personal/ICAI/Operacion de Modelos/Presentaciones Nuevas2/MUIAAp_S5_Interfaces.pptx`

- [ ] **Step 1: Cargar las instrucciones de presentaciones y preparar el workspace**

Leer completamente `presentations/SKILL.md`, `style_guidelines.md`,
`references/template-following.md`, `artifact_tool_docs/API_QUICK_START.md` y
`artifact_tool_docs/API_DOCS.md`. Inicializar `tmp/s5_churn_wine` con el script
de workspace de `@oai/artifact-tool`.

- [ ] **Step 2: Registrar el original y crear una copia de trabajo**

Calcular SHA-256, tamaño y fecha del original. Importarlo con
`@oai/artifact-tool`; no usar `python-pptx`. Mantener sin cambios las
diapositivas 1–12 y editar únicamente 13–34.

- [ ] **Step 3: Implementar este mapa narrativo visible**

```text
13  Caso guía: churn sintético — propósito, 4 entradas y 3 salidas visibles
14  2. Cómo piensa Streamlit
15  Rerun de arriba abajo aplicado al perfil Churn
16  st.form + st.form_submit_button
17  UI → predict() → resultado; la regla no vive en la UI
18  Widget → tipo → argumento para los cuatro campos
19  Invariante: 0 llamadas al editar; 1 al enviar
20  Resultado actualizado y error humano
21  Alcance: S5 sí / S6 después
22  3. Práctica 5.1 — miniapp Churn
23  Misión, starter y entregable
24  Paso 1: leer predict() y predecir dos perfiles
25  Paso 2: construir el formulario
26  Paso 3: conectar submit y llamada
27  Paso 4: presentar resultado y error
28  Tests y QA de cuatro casos
29  Entrega y rúbrica de la práctica 5.1
30  Puente Churn → Wine: se conserva / cambia
31  4. Práctica 5.2 — frontal Wine sobre bundle S4
32  11 campos → form → gateway → PredictionPayload; sin DemoGateway
33  Evidencias, bundle ausente y rúbrica 5.2
34  Cierre y avance S6
```

El término `Churn` debe aparecer antes de la explicación de rerun. El término
`Wine` aparece en el puente y en la práctica 5.2, no como entrega de clase 1.
Las diapositivas 15–20 llevarán una etiqueta visible y consistente
`Caso guía · Churn sintético`; no se confiará esta distinción únicamente a las
notas del presentador.

- [ ] **Step 4: Añadir notas y fuentes**

Todas las diapositivas 13–34 deben contener un bloque `[Sources]` con rutas
locales válidas a la práctica, solución, guía o contrato S4 utilizado. Las
notas de la 30 deben decir de forma explícita que se transfieren conceptos, no
campos ni código de Churn.

- [ ] **Step 5: Exportar y ejecutar QA programática**

Exportar a:

```text
C:/Users/jaandr7/Desktop/Personal/ICAI/Operacion de Modelos-NEW/Operacion de Modelos/S05/Teoria/MUIAAp_S5_Interfaces_Churn_Wine.pptx
```

Renderizar las 34 diapositivas, ejecutar `slides_test.py` y el validador de
fidelidad de plantilla. Expected: 0 desbordamientos, 0 placeholders vacíos y 0
incidencias de fidelidad.

- [ ] **Step 6: Inspeccionar visualmente cada diapositiva**

Revisar cada PNG individual a tamaño completo y después el montaje. Confirmar
especialmente 13, 15–20, 22–33: títulos en una línea, código legible, ningún
texto sobre el pie o la marca de agua y transición Churn/Wine inequívoca.

- [ ] **Step 7: Verificar que el original sigue intacto**

Recalcular su SHA-256 y fecha; deben coincidir con el registro de Step 2.

---

### Task 8: Verificación integrada y cierre

**Files:**
- Verify all S5 files changed in Tasks 1–7.

- [ ] **Step 1: Ejecutar las suites finales en paralelo**

```powershell
uv run --directory semana5/modules/05-streamlit-basic-model-ui/solutions/01-churn-streamlit python -m pytest -q
uv run --directory semana5/modules/05-streamlit-basic-model-ui/solutions/02-first-streamlit python -m pytest -q
uv run python -m pytest tools/test_generate_assignment_pdfs.py -q
```

Expected: las dos soluciones y el generador están completamente verdes.

- [ ] **Step 2: Verificar los starters**

Ejecutar sus suites por separado. Expected:

- 5.1: `8 passed, 5 failed`; fallan únicamente formulario, 0/1 llamadas,
  presentación y error por los tres huecos intencionados del alumno.
- 5.2: pasan esquema, gateway, 0/1 llamadas y seguridad; fallan solo
  `collect_values` y `render_prediction`.

- [ ] **Step 3: Ejecutar estilo y compilación**

```powershell
uv run ruff check app.py src tests
uv run ruff format --check app.py src tests
uv run python -m compileall -q app.py src tests
```

Ejecutar en los cuatro árboles starter/solution. Expected: todo verde.

- [ ] **Step 4: Buscar contradicciones residuales**

```powershell
rg -n "01-ui-form-contract|ui_schema.py.*5\.1|DemoGateway|modo demo|80 min|40 min" semana5 tools/generate_assignment_pdfs.py
```

Expected: cero coincidencias activas. Las menciones de Gradio solo pueden
describir una alternativa no evaluable; `session_state`, caché, FSM y
telemetría solo pueden aparecer como fuera de alcance o avance de S6.

- [ ] **Step 5: Repetir QA de enlaces y artefactos**

Confirmar cero enlaces Markdown rotos, dos assignments de dos páginas A4 y una
presentación de 34 diapositivas sin overflow. Verificar hashes idénticos de los
dos `model.py` Churn y que el original PPTX conserva su hash inicial.

- [ ] **Step 6: Revisión independiente**

Solicitar una revisión de coherencia que lea presentación, assignments,
prácticas y guías como si fuera un alumno. No cerrar si encuentra una tercera
práctica, un modo Wine simulado, un handoff `ui_schema.py` desde 5.1 o una
instrucción incompatible con PowerShell.

- [ ] **Step 7: Comprobar el estado final sin incorporar cambios ajenos**

```powershell
git status --short
git diff --cached --name-only
```

El PowerPoint se entrega fuera de la raíz Git y no se intenta añadir al índice.
Antes de cada commit de las tareas anteriores, comprobar la lista staged y
retirar del índice cualquier cambio ajeno a S5.
