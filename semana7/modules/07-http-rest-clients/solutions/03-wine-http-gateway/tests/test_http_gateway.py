from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, current_thread
from typing import Any

import pytest
import requests

from model_ui.contracts import PredictionPayload
from model_ui.errors import (
    ArtifactUnavailableError,
    BackendInferenceError,
    InferenceTimeoutError,
    InputContractError,
)
from model_ui.gateway import FEATURE_NAMES
from model_ui.http_gateway import HttpInferenceGateway

VALID_FEATURES = {name: float(index) for index, name in enumerate(FEATURE_NAMES)}
SUCCESS_BODY = {
    "prediction": {
        "quality_band": "acceptable",
        "confidence": 0.81,
        "model_version": "wine-api-v1",
        "preprocessing_version": "wine-red-features-v1",
    },
    "request_id": "req_test",
}


class FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        body: Any = None,
        json_exception: ValueError | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status
        self._body = {} if body is None else body
        self._json_exception = json_exception
        self.headers = {} if headers is None else headers
        self.json_calls = 0

    def json(self) -> Any:
        self.json_calls += 1
        if self._json_exception is not None:
            raise self._json_exception
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


class RecordingSession:
    def __init__(
        self,
        response: FakeResponse | None = None,
        *,
        exception: requests.RequestException | None = None,
    ) -> None:
        self._response = response
        self._exception = exception
        self.call: tuple[str, dict[str, Any]] | None = None

    def post(self, url: str, **kwargs: Any) -> FakeResponse:
        self.call = (url, kwargs)
        if self._exception is not None:
            raise self._exception
        assert self._response is not None
        return self._response


def test_sends_expected_http_request() -> None:
    session = RecordingSession(FakeResponse(body=SUCCESS_BODY))
    gateway = HttpInferenceGateway("http://example.test/", timeout=3, session=session)

    result = gateway.predict(VALID_FEATURES)

    assert session.call == (
        "http://example.test/v1/predictions",
        {
            "json": {"features": VALID_FEATURES},
            "headers": {"Accept": "application/json"},
            "timeout": 3.0,
        },
    )
    assert result == PredictionPayload.model_validate(SUCCESS_BODY["prediction"])
    assert gateway.last_request_id == "req_test"


def test_accepts_other_2xx_status_and_reads_request_id_header() -> None:
    body = {"prediction": SUCCESS_BODY["prediction"]}
    response = FakeResponse(
        status=201,
        body=body,
        headers={"X-Request-Id": "req_header"},
    )
    gateway = HttpInferenceGateway(
        "http://example.test", session=RecordingSession(response)
    )

    result = gateway.predict(VALID_FEATURES)

    assert result.model_version == "wine-api-v1"
    assert gateway.last_request_id == "req_header"


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (422, InputContractError),
        (503, ArtifactUnavailableError),
        (500, BackendInferenceError),
    ],
)
def test_maps_http_statuses_without_exposing_response_body(
    status: int,
    expected: type[Exception],
) -> None:
    response = FakeResponse(
        status=status,
        body={"detail": "secret-upstream-detail"},
        headers={"X-Request-Id": "req_problem"},
    )
    gateway = HttpInferenceGateway(
        "http://example.test", session=RecordingSession(response)
    )

    with pytest.raises(expected) as captured:
        gateway.predict(VALID_FEATURES)

    assert "secret-upstream-detail" not in str(captured.value)
    assert gateway.last_request_id == "req_problem"
    assert response.json_calls == 0


@pytest.mark.parametrize(
    ("status", "expected", "invalid_body"),
    [
        (422, InputContractError, "empty body"),
        (503, ArtifactUnavailableError, "<html>unavailable</html>"),
    ],
)
def test_maps_known_error_status_before_parsing_body(
    status: int,
    expected: type[Exception],
    invalid_body: str,
) -> None:
    response = FakeResponse(
        status=status,
        json_exception=ValueError(invalid_body),
    )
    gateway = HttpInferenceGateway(
        "http://example.test", session=RecordingSession(response)
    )

    with pytest.raises(expected) as captured:
        gateway.predict(VALID_FEATURES)

    assert invalid_body not in str(captured.value)
    assert response.json_calls == 0


def test_rejects_redirect_before_parsing_compatible_payload() -> None:
    response = FakeResponse(status=302, body=SUCCESS_BODY)
    gateway = HttpInferenceGateway(
        "http://example.test", session=RecordingSession(response)
    )

    with pytest.raises(BackendInferenceError, match="HTTP 302"):
        gateway.predict(VALID_FEATURES)

    assert response.json_calls == 0


def test_maps_timeout() -> None:
    gateway = HttpInferenceGateway(
        "http://example.test",
        session=RecordingSession(exception=requests.Timeout("secret-timeout")),
    )

    with pytest.raises(InferenceTimeoutError) as captured:
        gateway.predict(VALID_FEATURES)

    assert "secret-timeout" not in str(captured.value)


def test_clears_request_id_before_a_failed_request() -> None:
    class SuccessThenTimeoutSession:
        def __init__(self) -> None:
            self.calls = 0

        def post(self, _url: str, **_kwargs: Any) -> FakeResponse:
            self.calls += 1
            if self.calls == 1:
                return FakeResponse(body=SUCCESS_BODY)
            raise requests.Timeout("secret-timeout")

    gateway = HttpInferenceGateway(
        "http://example.test", session=SuccessThenTimeoutSession()
    )
    gateway.predict(VALID_FEATURES)
    assert gateway.last_request_id == "req_test"

    with pytest.raises(InferenceTimeoutError):
        gateway.predict(VALID_FEATURES)

    assert gateway.last_request_id is None


def test_request_id_is_isolated_between_threads() -> None:
    response_barrier = Barrier(2)
    read_barrier = Barrier(2)

    class ThreadAwareSession:
        @staticmethod
        def post(_url: str, **_kwargs: Any) -> FakeResponse:
            request_id = current_thread().name
            response_barrier.wait(timeout=2)
            return FakeResponse(body={**SUCCESS_BODY, "request_id": request_id})

    gateway = HttpInferenceGateway("http://example.test", session=ThreadAwareSession())

    def predict_and_read_request_id() -> tuple[str, str | None]:
        expected = current_thread().name
        gateway.predict(VALID_FEATURES)
        read_barrier.wait(timeout=2)
        return expected, gateway.last_request_id

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(lambda _index: predict_and_read_request_id(), range(2))
        )

    assert all(expected == actual for expected, actual in results)
    assert gateway.last_request_id is None


def test_maps_connection_failure() -> None:
    gateway = HttpInferenceGateway(
        "http://example.test",
        session=RecordingSession(exception=requests.ConnectionError("secret-host")),
    )

    with pytest.raises(ArtifactUnavailableError) as captured:
        gateway.predict(VALID_FEATURES)

    assert "secret-host" not in str(captured.value)


def test_maps_other_request_failure() -> None:
    gateway = HttpInferenceGateway(
        "http://example.test",
        session=RecordingSession(exception=requests.RequestException("secret-http")),
    )

    with pytest.raises(BackendInferenceError) as captured:
        gateway.predict(VALID_FEATURES)

    assert "secret-http" not in str(captured.value)


@pytest.mark.parametrize(
    "response",
    [
        FakeResponse(json_exception=ValueError("not JSON")),
        FakeResponse(body=[]),
        FakeResponse(body={"prediction": {"quality_band": "unknown"}}),
    ],
    ids=["invalid-json", "json-not-object", "invalid-prediction"],
)
def test_rejects_non_json_or_incompatible_prediction(response: FakeResponse) -> None:
    gateway = HttpInferenceGateway(
        "http://example.test", session=RecordingSession(response)
    )

    with pytest.raises(BackendInferenceError):
        gateway.predict(VALID_FEATURES)


@pytest.mark.parametrize("base_url", ["", "   "])
def test_rejects_empty_base_url(base_url: str) -> None:
    with pytest.raises(ValueError, match="base_url"):
        HttpInferenceGateway(base_url)


@pytest.mark.parametrize("timeout", [0, -0.1])
def test_rejects_non_positive_timeout(timeout: float) -> None:
    with pytest.raises(ValueError, match="timeout"):
        HttpInferenceGateway("http://example.test", timeout=timeout)
