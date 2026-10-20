"""TODO: carga del .joblib e inferencia sobre características preparadas."""
import joblib
from pathlib import Path
from model_inference.preprocess import preprocess_wine_request, FEATURE_NAMES
# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.
DEFAULT_MODEL_PATH =  Path(__file__).resolve().parents[2] / "models" / "wine_quality_classifier.joblib"


def load_wine_quality_model(path=DEFAULT_MODEL_PATH):
    model = joblib.load(path)
    if not isinstance(model, dict):
        raise ValueError("El artefacto debe contener un estimador y metadatos.")
    if model.get("feature_names") != list(FEATURE_NAMES):
        raise ValueError("Los feature_names del artefacto no coinciden con el contrato.")
    estimator = model.get("estimator")
    if not hasattr(estimator, "predict") or not hasattr(estimator, "predict_proba"):
        raise ValueError("El artefacto no contiene un clasificador compatible.")
    model_version = model.get("model_version")
    if not isinstance(model_version, str) or not model_version:
        raise ValueError("El artefacto no declara una versión de modelo válida.")
    estimator = model.get("estimator")
    return estimator, model_version



def infer_wine_quality(model, row):
    row_preprocess = preprocess_wine_request(row)
    prediction = model.predict([row_preprocess.as_vector()])
    proba = model.predict_proba([row_preprocess.as_vector()])
    return prediction, max(proba[0])
    
