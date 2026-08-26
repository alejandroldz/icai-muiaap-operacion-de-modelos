from __future__ import annotations

import json
import unittest

import requests
from client import PredictionClientError, request_prediction

PAYLOAD = {
    "machine_id": "pump-017",
    "measurements": {
        "temperature_c": 91.2,
        "vibration_mm_s": 8.4,
        "pressure_bar": 4.7,
        "runtime_hours": 12840,
    },
}


class FakeResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body or {"prediction": {"label": "normal"}}
        self.text = json.dumps(self._body)

    def raise_for_status(self):
        if self.status_code >= 400:
            response = requests.Response()
            response.status_code = self.status_code
            response._content = b'{"error":{"code":"validation_error"}}'
            response.headers["Content-Type"] = "application/json"
            raise requests.HTTPError(response=response)

    def json(self):
        return self._body


class RecordingSession:
    def __init__(self, response=None, exception=None):
        self.response = response or FakeResponse()
        self.exception = exception
        self.call = None

    def post(self, url, **kwargs):
        self.call = (url, kwargs)
        if self.exception:
            raise self.exception
        return self.response


class ClientExerciseTest(unittest.TestCase):
    def test_sends_json_accept_and_timeout(self):
        session = RecordingSession()

        result = request_prediction(
            PAYLOAD,
            base_url="http://example.test",
            timeout=3,
            session=session,
        )

        url, kwargs = session.call
        self.assertEqual(url, "http://example.test/v1/predictions")
        self.assertEqual(kwargs["json"], PAYLOAD)
        self.assertEqual(kwargs["headers"], {"Accept": "application/json"})
        self.assertEqual(kwargs["timeout"], 3)
        self.assertEqual(result["prediction"]["label"], "normal")

    def test_converts_http_error_and_preserves_status(self):
        session = RecordingSession(response=FakeResponse(status_code=422))

        with self.assertRaises(PredictionClientError) as context:
            request_prediction(PAYLOAD, session=session)

        self.assertEqual(context.exception.status_code, 422)

    def test_converts_timeout(self):
        session = RecordingSession(exception=requests.Timeout("late"))

        with self.assertRaises(PredictionClientError):
            request_prediction(PAYLOAD, session=session)

    def test_converts_connection_error(self):
        session = RecordingSession(exception=requests.ConnectionError("offline"))

        with self.assertRaises(PredictionClientError) as context:
            request_prediction(PAYLOAD, session=session)

        self.assertIn("conectar", str(context.exception).lower())

    def test_rejects_success_json_that_is_not_an_object(self):
        session = RecordingSession(response=FakeResponse(body=[1]))

        with self.assertRaises(PredictionClientError) as context:
            request_prediction(PAYLOAD, session=session)

        self.assertIn("objeto", str(context.exception).lower())


if __name__ == "__main__":
    unittest.main()
