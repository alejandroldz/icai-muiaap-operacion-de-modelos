from __future__ import annotations

import importlib.util
import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MODULE_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = MODULE_ROOT / "examples" / "pump-maintenance-api" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("pump_api_server", SERVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se puede cargar {SERVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalAPITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_server_module()
        cls.server = cls.module.build_server("127.0.0.1", 0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request_json(
        self,
        path: str,
        *,
        method: str = "GET",
        payload: object | None = None,
        raw_body: bytes | None = None,
    ) -> tuple[int, dict[str, str], dict[str, object]]:
        data = raw_body
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )
        try:
            response = urlopen(request, timeout=2)
        except HTTPError as exc:
            response = exc
        body = json.loads(response.read().decode("utf-8"))
        return response.status, dict(response.headers.items()), body

    def test_health_returns_json_and_model_status(self) -> None:
        status, headers, body = self.request_json("/health")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["model_status"], "ready")

    def test_valid_prediction_returns_200_and_traceable_result(self) -> None:
        payload = {
            "machine_id": "pump-017",
            "measurements": {
                "temperature_c": 91.2,
                "vibration_mm_s": 8.4,
                "pressure_bar": 4.7,
                "runtime_hours": 12840,
            },
        }

        status, headers, body = self.request_json(
            "/v1/predictions", method="POST", payload=payload
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["machine_id"], "pump-017")
        self.assertEqual(body["prediction"]["label"], "maintenance_required")
        self.assertGreaterEqual(body["prediction"]["risk_score"], 0.5)
        self.assertEqual(body["model_version"], "pump-risk-1.0.0")
        self.assertEqual(headers["X-Request-Id"], body["request_id"])

    def test_valid_json_with_invalid_measurement_returns_422(self) -> None:
        payload = {
            "machine_id": "pump-017",
            "measurements": {
                "temperature_c": 91.2,
                "vibration_mm_s": "alta",
                "pressure_bar": 4.7,
                "runtime_hours": 12840,
            },
        }

        status, _, body = self.request_json(
            "/v1/predictions", method="POST", payload=payload
        )

        self.assertEqual(status, 422)
        self.assertEqual(body["error"]["code"], "validation_error")
        fields = [item["field"] for item in body["error"]["fields"]]
        self.assertIn("measurements.vibration_mm_s", fields)

    def test_malformed_json_returns_400(self) -> None:
        status, _, body = self.request_json(
            "/v1/predictions",
            method="POST",
            raw_body=b'{"machine_id": "pump-017",',
        )

        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_json")


if __name__ == "__main__":
    unittest.main()
