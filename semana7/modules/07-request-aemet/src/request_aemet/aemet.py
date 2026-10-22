import requests
from dotenv import load_dotenv
import os

def get_aemet_data(url: str, params: dict = None):
    load_dotenv()
    API_KEY = os.getenv("AEMET_KEY")
    headers = {
        "api_key": API_KEY
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response

def get_aemet_inventario_estaciones():
    params = {"idema": 3195}
    endpoint = "p"
    url = f"https://opendata.aemet.es{endpoint}"
    response = get_aemet_data(url, params=params)
if __name__ == "__main__":

