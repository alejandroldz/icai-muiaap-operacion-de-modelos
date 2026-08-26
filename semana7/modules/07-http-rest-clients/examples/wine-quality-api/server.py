"""API Wine Quality suministrada como caja negra para la práctica de S7.

Usa únicamente la biblioteca estándar: en S7 se consume y observa HTTP; la
implementación de un backend con FastAPI se reserva para la semana siguiente.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import uuid
from decimal import Decimal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

MODEL_VERSION = "wine-quality-demo-v1"
PREPROCESSING_VERSION = "wine-red-features-v1"
MAX_REQUEST_BODY_BYTES = 64 * 1024
MAX_REJECTED_BODY_DRAIN_BYTES = 4 * MAX_REQUEST_BODY_BYTES
FEATURE_RANGES = {
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


def new_request_id() -> str:
    """Crea un identificador opaco para correlacionar petición y respuesta."""

    return f"req_{uuid.uuid4().hex[:12]}"


def validate_prediction_payload(
    payload: Any,
) -> tuple[dict[str, float] | None, list[dict[str, str]]]:
    """Valida el objeto HTTP y devuelve features normalizadas o errores."""

    if not isinstance(payload, dict):
        return None, [{"field": "body", "message": "must be a JSON object"}]

    features = payload.get("features")
    if not isinstance(features, dict):
        return None, [{"field": "features", "message": "must be a JSON object"}]

    errors: list[dict[str, str]] = []
    normalized: dict[str, float] = {}

    for name, (minimum, maximum) in FEATURE_RANGES.items():
        field = f"features.{name}"
        if name not in features:
            errors.append({"field": field, "message": "field is required"})
            continue

        value = features[name]
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            errors.append({"field": field, "message": "must be a number"})
            continue

        try:
            numeric_value = float(value)
        except (OverflowError, ValueError):
            errors.append({"field": field, "message": "must be a finite number"})
            continue
        if not math.isfinite(numeric_value):
            errors.append({"field": field, "message": "must be a finite number"})
            continue
        if not minimum <= numeric_value <= maximum:
            errors.append(
                {
                    "field": field,
                    "message": f"must be between {minimum:g} and {maximum:g}",
                }
            )
            continue
        normalized[name] = numeric_value

    for name in sorted(set(features).difference(FEATURE_RANGES)):
        errors.append(
            {
                "field": f"features.{name}",
                "message": "field is not allowed",
            }
        )

    return (None, errors) if errors else (normalized, [])


def calculate_prediction(features: dict[str, float]) -> dict[str, object]:
    """Calcula una predicción determinista para observar el contrato HTTP."""

    score = (
        5.5
        + 0.25 * (features["alcohol"] - 10.0)
        - 1.2 * (features["volatile_acidity"] - 0.5)
        + 0.4 * (features["sulphates"] - 0.6)
    )
    if score < 5.5:
        quality_band = "needs_review"
    elif score < 6.5:
        quality_band = "acceptable"
    else:
        quality_band = "excellent"

    confidence = round(min(0.95, 0.60 + abs(score - 6.0) * 0.12), 2)
    return {
        "quality_band": quality_band,
        "confidence": confidence,
        "model_version": MODEL_VERSION,
        "preprocessing_version": PREPROCESSING_VERSION,
    }


class WineQualityHTTPServer(ThreadingHTTPServer):
    """Servidor HTTP con estado docente configurable por la CLI."""

    mode: str
    delay_seconds: float


class WineQualityHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "S7WineQualityAPI/1.0"

    def log_message(self, format: str, *args: object) -> None:
        """Evita mezclar logs del servidor con los pasos de la práctica."""

        return

    @property
    def api_server(self) -> WineQualityHTTPServer:
        return self.server  # type: ignore[return-value]

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        *,
        request_id: str,
        close_connection: bool = False,
    ) -> None:
        response_payload = {**payload, "request_id": request_id}
        body = json.dumps(response_payload, ensure_ascii=False).encode("utf-8")
        if close_connection:
            self.close_connection = True
        try:
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Request-Id", request_id)
            if close_connection:
                self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True

    def _send_error(
        self,
        status: HTTPStatus,
        *,
        code: str,
        message: str,
        request_id: str,
        fields: list[dict[str, str]] | None = None,
        close_connection: bool = False,
    ) -> None:
        error: dict[str, Any] = {"code": code, "message": message}
        if fields is not None:
            error["fields"] = fields
        self._send_json(
            status,
            {"error": error},
            request_id=request_id,
            close_connection=close_connection,
        )

    def _not_found(
        self,
        request_id: str,
        *,
        close_connection: bool = False,
    ) -> None:
        self._send_error(
            HTTPStatus.NOT_FOUND,
            code="not_found",
            message="The requested resource does not exist",
            request_id=request_id,
            close_connection=close_connection,
        )

    def _model_unavailable(
        self,
        request_id: str,
        *,
        close_connection: bool = False,
    ) -> None:
        self._send_error(
            HTTPStatus.SERVICE_UNAVAILABLE,
            code="model_unavailable",
            message="The prediction model is not ready",
            request_id=request_id,
            close_connection=close_connection,
        )

    def _content_length(self) -> int | None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except (TypeError, ValueError):
            return None
        return content_length if content_length >= 0 else None

    def _discard_request_body(
        self,
        *,
        content_length: int | None = None,
        maximum_bytes: int = MAX_REQUEST_BODY_BYTES,
    ) -> bool:
        """Consume un body acotado para poder reutilizar la conexión HTTP."""

        length = self._content_length() if content_length is None else content_length
        if length is None or length > maximum_bytes:
            return False
        try:
            return len(self.rfile.read(length)) == length
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            return False

    def do_GET(self) -> None:  # noqa: N802 - nombre requerido por http.server
        request_id = new_request_id()
        if urlsplit(self.path).path != "/health":
            self._not_found(request_id)
            return

        if self.api_server.mode == "unavailable":
            self._model_unavailable(request_id)
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "status": "ok",
                "service": "wine-quality-prediction",
                "model_status": "ready",
                "model_version": MODEL_VERSION,
            },
            request_id=request_id,
        )

    def do_POST(self) -> None:  # noqa: N802 - nombre requerido por http.server
        request_id = new_request_id()
        if urlsplit(self.path).path != "/v1/predictions":
            body_consumed = self._discard_request_body()
            self._not_found(request_id, close_connection=not body_consumed)
            return

        if self.api_server.mode == "unavailable":
            body_consumed = self._discard_request_body()
            self._model_unavailable(request_id, close_connection=not body_consumed)
            return

        content_length = self._content_length()
        if content_length is None:
            self._send_error(
                HTTPStatus.BAD_REQUEST,
                code="invalid_content_length",
                message="Content-Length must be a non-negative integer",
                request_id=request_id,
                close_connection=True,
            )
            return
        if content_length > MAX_REQUEST_BODY_BYTES:
            self._discard_request_body(
                content_length=content_length,
                maximum_bytes=MAX_REJECTED_BODY_DRAIN_BYTES,
            )
            self._send_error(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                code="payload_too_large",
                message=(
                    "The request body exceeds the maximum size of "
                    f"{MAX_REQUEST_BODY_BYTES} bytes"
                ),
                request_id=request_id,
                close_connection=True,
            )
            return

        try:
            raw_body = self.rfile.read(content_length)
            payload = json.loads(
                raw_body.decode("utf-8"),
                parse_int=Decimal,
                parse_float=Decimal,
            )
        except (UnicodeDecodeError, ValueError):
            self._send_error(
                HTTPStatus.BAD_REQUEST,
                code="invalid_json",
                message="The request body is not valid JSON",
                request_id=request_id,
            )
            return

        features, errors = validate_prediction_payload(payload)
        if errors or features is None:
            self._send_error(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                code="validation_error",
                message="JSON is valid but violates the input contract",
                fields=errors,
                request_id=request_id,
            )
            return

        if self.api_server.delay_seconds > 0:
            time.sleep(self.api_server.delay_seconds)

        self._send_json(
            HTTPStatus.OK,
            {"prediction": calculate_prediction(features)},
            request_id=request_id,
        )


def build_server(
    host: str,
    port: int,
    mode: str = "ready",
    delay_seconds: float = 0.0,
) -> WineQualityHTTPServer:
    """Construye el servidor sin iniciarlo, lo que permite usar puerto 0."""

    if mode not in {"ready", "unavailable"}:
        raise ValueError("mode must be 'ready' or 'unavailable'")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be non-negative")

    server = WineQualityHTTPServer((host, port), WineQualityHandler)
    server.daemon_threads = True
    server.mode = mode
    server.delay_seconds = delay_seconds
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="API Wine Quality local de S7")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument(
        "--mode",
        choices=("ready", "unavailable"),
        default="ready",
    )
    parser.add_argument("--delay-seconds", default=0.0, type=float)
    args = parser.parse_args()

    server = build_server(
        args.host,
        args.port,
        mode=args.mode,
        delay_seconds=args.delay_seconds,
    )
    host, port = server.server_address
    print(f"API Wine S7 disponible en http://{host}:{port}")
    print("Detener con Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI detenida")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
