"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.

import argparse
from pathlib import Path
import pandas as pd
from model_inference.contracts import WineQualityPrediction
from model_inference.inference import  DEFAULT_MODEL_PATH, infer_wine_quality, load_wine_quality_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    predicts = predict_file(args.input, args.model)
    df_predicts = pd.DataFrame(predicts)
    df_predicts.to_csv(args.output, index=False)


def predict_file(path: str, model_path: str = str(DEFAULT_MODEL_PATH)) -> list:
    file_path = Path(path)
    data = pd.read_csv(file_path)
    model = load_wine_quality_model(model_path)
    results = []
    for index, row in data.iterrows():
        predict, probabilities = infer_wine_quality(model=model, row=row)
        result = {
            "sample_id": row["sample_id"],
            "quality_band": predict[0],
            "confidence": probabilities,
            "model_version": "wine-quality-rf-v1",
            "preprocessing_version": "wine-red-features-v1",
        }
        WineQualityPrediction.model_validate(result)
        results.append(result)
        
  
    return results

if __name__ == "__main__":
    main()


