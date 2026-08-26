from __future__ import annotations

import importlib.util
import threading
import unittest
from pathlib import Path

import requests

MODULE_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = MODULE_ROOT / "examples" / "pump-maintenance-api" / "server.py"
CLIENT_PATH = MODULE_ROOT / "examples" / "python-client" / "client.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se puede cargar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALID_PAYLOAD = {
    "machine_id": "pump-017",
    "measurements": {
        "temperature_c": 91.2,
        "vibration_mm_s": 8.4,
        "pressure_bar": 4.7,
        "runtime_hours": 12840,
    },
}


class TimeoutSession:
    def post(self, *args, **kwargs):
        raise requests.Timeout("tiempo agotado")


class ClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server_module = load_module("pump_api_server_for_client", SERVER_PATH)
        cls.client_module = load_module("prediction_client", CLIENT_PATH)
        cls.server = cls.server_module.build_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_request_prediction_returns_decoded_json(self) -> None:
        result = self.client_module.request_prediction(
            VALID_PAYLOAD, base_url=self.base_url, timeout=2
        )

        self.assertEqual(result["machine_id"], "pump-017")
        self.assertIn("risk_score", result["prediction"])

    def test_request_prediction_exposes_422_as_http_error(self) -> None:
        payload = {
            **VALID_PAYLOAD,
            "measurements": {**VALID_PAYLOAD["measurements"], "vibration_mm_s": "alta"},
        }

        with self.assertRaises(self.client_module.PredictionHTTPError) as context:
            self.client_module.request_prediction(
                payload, base_url=self.base_url, timeout=2
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(context.exception.detail["error"]["code"], "validation_error")

    def test_request_prediction_converts_timeout_to_transport_error(self) -> None:
        with self.assertRaises(self.client_module.PredictionTransportError):
            self.client_module.request_prediction(
                VALID_PAYLOAD,
                base_url="http://127.0.0.1:8000",
                timeout=0.1,
                session=TimeoutSession(),
            )


if __name__ == "__main__":
    unittest.main()
