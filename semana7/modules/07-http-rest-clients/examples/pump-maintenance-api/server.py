"""API local de caja negra para el laboratorio de clientes HTTP de S7.

El alumnado solo necesita ejecutar este archivo. La implementación usa la
biblioteca estándar para no adelantar FastAPI ni requerir acceso a internet.
"""

from __future__ import annotations

import argparse
import json
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

MODEL_VERSION = "pump-risk-1.0.0"
MEASUREMENT_RANGES = {
    "temperature_c": (-20.0, 150.0),
    "vibration_mm_s": (0.0, 50.0),
    "pressure_bar": (0.0, 30.0),
    "runtime_hours": (0.0, 200_000.0),
}


def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"


def validate_prediction_payload(payload: Any) -> list[dict[str, str]]:
    """Devuelve errores de contrato sin lanzar excepciones internas."""
    if not isinstance(payload, dict):
        return [{"field": "body", "message": "must be a JSON object"}]

    errors: list[dict[str, str]] = []
    machine_id = payload.get("machine_id")
    if not isinstance(machine_id, str) or not machine_id.strip():
        errors.append({"field": "machine_id", "message": "must be a non-empty string"})

    measurements = payload.get("measurements")
    if not isinstance(measurements, dict):
        errors.append({"field": "measurements", "message": "must be a JSON object"})
        return errors

    for name, (minimum, maximum) in MEASUREMENT_RANGES.items():
        field = f"measurements.{name}"
        if name not in measurements:
            errors.append({"field": field, "message": "field is required"})
            continue
        value = measurements[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append({"field": field, "message": "must be a number"})
            continue
        if not minimum <= float(value) <= maximum:
            errors.append(
                {
                    "field": field,
                    "message": f"must be between {minimum:g} and {maximum:g}",
                }
            )

    return errors


def calculate_prediction(payload: dict[str, Any]) -> dict[str, Any]:
    """Calcula una salida determinista para practicar el contrato HTTP."""
    values = payload["measurements"]
    risk_score = 0.05
    if values["temperature_c"] >= 80:
        risk_score += 0.30
    if values["vibration_mm_s"] >= 6:
        risk_score += 0.35
    if not 2 <= values["pressure_bar"] <= 8:
        risk_score += 0.15
    if values["runtime_hours"] >= 10_000:
        risk_score += 0.15
    risk_score = round(min(risk_score, 0.99), 2)
    label = "maintenance_required" if risk_score >= 0.5 else "normal"
    return {"label": label, "risk_score": risk_score}


class PumpMaintenanceHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "S7LocalAPI/1.0"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        *,
        request_id: str,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Request-Id", request_id)
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self, request_id: str) -> None:
        self._send_json(
            HTTPStatus.NOT_FOUND,
            {
                "error": {
                    "code": "not_found",
                    "message": "The requested resource does not exist",
                },
                "request_id": request_id,
            },
            request_id=request_id,
        )

    def do_GET(self) -> None:  # noqa: N802 - nombre requerido por http.server
        request_id = new_request_id()
        if urlsplit(self.path).path != "/health":
            self._not_found(request_id)
            return
        self._send_json(
            HTTPStatus.OK,
            {
                "status": "ok",
                "service": "pump-maintenance-prediction",
                "model_status": "ready",
                "model_version": MODEL_VERSION,
                "request_id": request_id,
            },
            request_id=request_id,
        )

    def do_POST(self) -> None:  # noqa: N802 - nombre requerido por http.server
        request_id = new_request_id()
        if urlsplit(self.path).path != "/v1/predictions":
            self._not_found(request_id)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "error": {
                        "code": "invalid_json",
                        "message": "The request body is not valid JSON",
                    },
                    "request_id": request_id,
                },
                request_id=request_id,
            )
            return

        errors = validate_prediction_payload(payload)
        if errors:
            self._send_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {
                    "error": {
                        "code": "validation_error",
                        "message": "JSON is valid but violates the input contract",
                        "fields": errors,
                    },
                    "request_id": request_id,
                },
                request_id=request_id,
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "machine_id": payload["machine_id"],
                "prediction": calculate_prediction(payload),
                "model_version": MODEL_VERSION,
                "request_id": request_id,
            },
            request_id=request_id,
        )


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), PumpMaintenanceHandler)
    server.daemon_threads = True
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="API local preparada para S7")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    server = build_server(args.host, args.port)
    print(f"API S7 disponible en http://{args.host}:{args.port}")
    print("Detener con Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI detenida")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
