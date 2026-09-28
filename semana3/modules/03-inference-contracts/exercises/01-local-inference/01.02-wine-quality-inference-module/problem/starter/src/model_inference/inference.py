"""TODO: carga del .joblib e inferencia sobre características preparadas."""
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from model_inference.preprocess import preprocess_wine_request
# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.
DEFAULT_MODEL_PATH =  Path(__file__).resolve().parents[2] / "models" / "wine_quality_classifier.joblib"


def load_wine_quality_model(path=DEFAULT_MODEL_PATH):
    model = joblib.load(path)
    rfc: RandomForestClassifier = model["estimator"]
    return rfc


def infer_wine_quality(model: RandomForestClassifier, row: np.ndarray):
    row_preprocess = preprocess_wine_request(row=row)
    prediction = model.predict(row_preprocess) 
    proba = model.predict_proba(row_preprocess)
    return prediction, max(proba[0])
    
