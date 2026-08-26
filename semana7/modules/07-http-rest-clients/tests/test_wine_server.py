from __future__ import annotations

import http.client
import importlib.util
import io
import json
import threading
import unittest
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

MODULE_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = MODULE_ROOT / "examples" / "wine-quality-api" / "server.py"
SAMPLES_PATH = SERVER_PATH.parent / "samples"

EXPECTED_FEATURE_RANGES = {
    "fixed_acidity": (0.0, 20.0),
    "volatile_acidity": (0.0, 2.0),
    "citric_acid": (0.0, 2.0),
    "residual_sugar": (0.0, 20.0),
    "chlorides": (0.0, 1.0),
    "free_sulfur_dioxide": (0.0, 100.0),
    "total_sulfur_dioxide": (0.0, 300.0),
    "density": (0.98, 1.01),
    "ph": (2.5, 4.5),
    "sulphates": (0.0, 3.0),
    "alcohol": (5.0, 20.0),
}

VALID_FEATURES = {
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


def load_server_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "wine_quality_api_server", SERVER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se puede cargar {SERVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextmanager
def running_server(
    module: ModuleType,
    *,
    mode: str = "ready",
    delay_seconds: float = 0.0,
) -> Iterator[tuple[object, str]]:
    server = module.build_server(
        "127.0.0.1",
        0,
        mode=mode,
        delay_seconds=delay_seconds,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    try:
        yield server, f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request_json(
    base_url: str,
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
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = Request(f"{base_url}{path}", data=data, headers=headers, method=method)
    try:
        response = urlopen(request, timeout=2)
    except HTTPError as error:
        response = error

    try:
        body = json.loads(response.read().decode("utf-8"))
        response_headers = dict(response.headers.items())
        status = response.status
    finally:
        response.close()

    assert response_headers["X-Request-Id"] == body["request_id"]
    return status, response_headers, body


class ServerArtifactTest(unittest.TestCase):
    def test_wine_server_exists(self) -> None:
        self.assertTrue(
            SERVER_PATH.is_file(),
            f"Falta implementar la API docente en {SERVER_PATH}",
        )


@unittest.skipUnless(SERVER_PATH.is_file(), "La API Wine se implementa tras el RED")
class WineQualityServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_server_module()
        cls.server_context = running_server(cls.module)
        cls.server, cls.base_url = cls.server_context.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server_context.__exit__(None, None, None)

    def test_contract_exposes_the_exact_eleven_feature_ranges(self) -> None:
        self.assertEqual(self.module.FEATURE_RANGES, EXPECTED_FEATURE_RANGES)

    def test_health_returns_model_readiness(self) -> None:
        status, headers, body = request_json(self.base_url, "/health")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["model_status"], "ready")
        self.assertEqual(body["model_version"], "wine-quality-demo-v1")

    def test_valid_prediction_returns_existing_contract(self) -> None:
        status, _, body = request_json(
            self.base_url,
            "/v1/predictions",
            method="POST",
            payload={"features": VALID_FEATURES},
        )

        self.assertEqual(status, 200)
        self.assertEqual(
            body["prediction"],
            {
                "quality_band": "needs_review",
                "confidence": 0.71,
                "model_version": "wine-quality-demo-v1",
                "preprocessing_version": "wine-red-features-v1",
            },
        )

    def test_calculation_uses_the_documented_thresholds_and_confidence_cap(
        self,
    ) -> None:
        acceptable = {
            **VALID_FEATURES,
            "alcohol": 12.0,
            "volatile_acidity": 0.5,
            "sulphates": 0.6,
        }
        excellent = {**acceptable, "alcohol": 14.5}
        high_score = {
            **VALID_FEATURES,
            "alcohol": 20.0,
            "volatile_acidity": 0.0,
            "sulphates": 3.0,
        }

        self.assertEqual(
            self.module.calculate_prediction(acceptable)["quality_band"],
            "acceptable",
        )
        self.assertEqual(
            self.module.calculate_prediction(acceptable)["confidence"],
            0.6,
        )
        self.assertEqual(
            self.module.calculate_prediction(excellent)["quality_band"],
            "excellent",
        )
        self.assertEqual(
            self.module.calculate_prediction(high_score)["confidence"],
            0.95,
        )

    def test_invalid_features_return_422(self) -> None:
        invalid = {**VALID_FEATURES, "alcohol": "mucho"}
        status, _, body = request_json(
            self.base_url,
            "/v1/predictions",
            method="POST",
            payload={"features": invalid},
        )

        self.assertEqual(status, 422)
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertIn(
            "features.alcohol",
            [error["field"] for error in body["error"]["fields"]],
        )

    def test_missing_unknown_and_out_of_range_features_return_422(self) -> None:
        invalid = {
            **VALID_FEATURES,
            "alcohol": 20.1,
            "unexpected_feature": 1.0,
        }
        del invalid["ph"]

        status, _, body = request_json(
            self.base_url,
            "/v1/predictions",
            method="POST",
            payload={"features": invalid},
        )

        self.assertEqual(status, 422)
        fields = [error["field"] for error in body["error"]["fields"]]
        self.assertIn("features.ph", fields)
        self.assertIn("features.alcohol", fields)
        self.assertIn("features.unexpected_feature", fields)

    def test_malformed_json_returns_400(self) -> None:
        status, _, body = request_json(
            self.base_url,
            "/v1/predictions",
            method="POST",
            raw_body=b'{"features": {"alcohol": 9.4}',
        )

        self.assertEqual(status, 400)
        self.assertEqual(body["error"]["code"], "invalid_json")

    def test_unknown_route_returns_404(self) -> None:
        status, _, body = request_json(self.base_url, "/v1/unknown")

        self.assertEqual(status, 404)
        self.assertEqual(body["error"]["code"], "not_found")

    def test_unavailable_mode_returns_503(self) -> None:
        with running_server(self.module, mode="unavailable") as (_, base_url):
            status, _, body = request_json(
                base_url,
                "/v1/predictions",
                method="POST",
                payload={"features": VALID_FEATURES},
            )

        self.assertEqual(status, 503)
        self.assertEqual(body["error"]["code"], "model_unavailable")

    def test_post_errors_preserve_persistent_connection_framing(self) -> None:
        scenarios = (
            ("ready", "/v1/unknown", 404, "/health", 200),
            ("unavailable", "/v1/predictions", 503, "/v1/unknown", 404),
        )
        request_body = json.dumps({"features": VALID_FEATURES})

        for mode, first_path, first_status, second_path, second_status in scenarios:
            with self.subTest(mode=mode, status=first_status):
                with running_server(self.module, mode=mode) as (server, _):
                    host, port = server.server_address
                    connection = http.client.HTTPConnection(host, port, timeout=2)
                    connection.connect()
                    original_socket = connection.sock
                    try:
                        connection.request(
                            "POST",
                            first_path,
                            body=request_body,
                            headers={"Content-Type": "application/json"},
                        )
                        first_response = connection.getresponse()
                        first_response.read()

                        self.assertEqual(first_response.status, first_status)
                        self.assertFalse(first_response.will_close)
                        self.assertIs(connection.sock, original_socket)

                        connection.request("GET", second_path)
                        second_response = connection.getresponse()
                        second_response.read()

                        self.assertEqual(second_response.status, second_status)
                        self.assertIs(connection.sock, original_socket)
                    finally:
                        connection.close()

    def test_extreme_integer_returns_422_without_stopping_server(self) -> None:
        regular_body = json.dumps({"features": VALID_FEATURES})
        extreme_body = regular_body.replace(
            '"alcohol": 9.4',
            '"alcohol": ' + "9" * 5_000,
        ).encode("utf-8")

        status, _, body = request_json(
            self.base_url,
            "/v1/predictions",
            method="POST",
            raw_body=extreme_body,
        )
        health_status, _, _ = request_json(self.base_url, "/health")

        self.assertEqual(status, 422)
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertIn(
            "features.alcohol",
            [error["field"] for error in body["error"]["fields"]],
        )
        self.assertEqual(health_status, 200)

    def test_disconnected_client_during_delayed_response_is_absorbed(self) -> None:
        request_body = json.dumps({"features": VALID_FEATURES}).encode("utf-8")

        class DisconnectedWriter:
            def __init__(self, error_type: type[OSError]) -> None:
                self.error_type = error_type

            def write(self, _: bytes) -> None:
                raise self.error_type("client disconnected")

        for error_type in (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError,
        ):
            with self.subTest(error_type=error_type.__name__):
                handler = object.__new__(self.module.WineQualityHandler)
                handler.path = "/v1/predictions"
                handler.headers = {"Content-Length": str(len(request_body))}
                handler.rfile = io.BytesIO(request_body)
                handler.wfile = DisconnectedWriter(error_type)
                handler.server = SimpleNamespace(mode="ready", delay_seconds=0.01)
                handler.close_connection = False
                handler.send_response = lambda _: None
                handler.send_header = lambda *_: None
                handler.end_headers = lambda: None

                with patch.object(self.module.time, "sleep") as sleep:
                    handler.do_POST()

                sleep.assert_called_once_with(0.01)
                self.assertTrue(handler.close_connection)

    def test_oversized_body_returns_413_and_closes_connection(self) -> None:
        oversized_payload = {
            "features": VALID_FEATURES,
            "padding": "x" * self.module.MAX_REQUEST_BODY_BYTES,
        }
        body = json.dumps(oversized_payload).encode("utf-8")
        host, port = self.server.server_address
        connection = http.client.HTTPConnection(host, port, timeout=2)
        try:
            connection.request(
                "POST",
                "/v1/predictions",
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            response_body = json.loads(response.read().decode("utf-8"))

            self.assertEqual(response.status, 413)
            self.assertEqual(response_body["error"]["code"], "payload_too_large")
            self.assertEqual(
                response.getheader("X-Request-Id"), response_body["request_id"]
            )
            self.assertEqual(response.getheader("Connection"), "close")
            self.assertTrue(response.will_close)
        finally:
            connection.close()

    def test_sample_payloads_are_executable_contract_examples(self) -> None:
        valid = json.loads((SAMPLES_PATH / "prediction-valid.json").read_text())
        invalid = json.loads((SAMPLES_PATH / "prediction-invalid.json").read_text())

        self.assertEqual(set(valid), {"features"})
        self.assertEqual(set(valid["features"]), set(EXPECTED_FEATURE_RANGES))
        self.assertIsInstance(invalid["features"]["alcohol"], str)
        self.assertEqual(
            request_json(
                self.base_url,
                "/v1/predictions",
                method="POST",
                payload=valid,
            )[0],
            200,
        )
        self.assertEqual(
            request_json(
                self.base_url,
                "/v1/predictions",
                method="POST",
                payload=invalid,
            )[0],
            422,
        )


if __name__ == "__main__":
    unittest.main()
