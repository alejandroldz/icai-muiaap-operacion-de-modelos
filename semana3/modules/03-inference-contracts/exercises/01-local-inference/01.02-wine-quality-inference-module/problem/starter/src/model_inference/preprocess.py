"""TODO: transformación de una muestra validada en el vector del modelo."""

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
import numpy as np
import pandas as pd
from model_inference.contracts import WineQualityRequest
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.
class WineFeatures():
    
    def as_vector(self, row: pd.Series):
        return np.array([
            row.fixed_acidity,
            row.volatile_acidity,
            row.citric_acid,
            row.residual_sugar,
            row.chlorides,
            row.free_sulfur_dioxide,
            row.total_sulfur_dioxide,
            row.density,
            row.ph,
            row.sulphates,
            row.alcohol
        ])
        



def preprocess_wine_request(row) -> np.ndarray:
    wf = WineFeatures()
    WineQualityRequest.model_validate(row[list(FEATURE_NAMES)].to_dict())
    array = wf.as_vector(row=row)
    
    return array.reshape(1, -1)
    
    
    
if __name__ == '__main__':
    csv_path = "../../assets/inference_samples.csv"
    df = pd.read_csv(csv_path)
    
    for index, row in df.iterrows():
        preprocess_wine_request(row)