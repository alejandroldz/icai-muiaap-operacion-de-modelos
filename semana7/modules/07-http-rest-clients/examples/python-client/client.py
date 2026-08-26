"""Cliente de referencia para la API local de mantenimiento predictivo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


class PredictionClientError(RuntimeError):
    """Error base que la aplicación consumidora puede mostrar o registrar."""


class PredictionTransportError(PredictionClientError):
    """No se pudo completar el intercambio HTTP."""


class PredictionHTTPError(PredictionClientError):
    """La API respondió con un código 4xx o 5xx."""

    def __init__(self, status_code: int, detail: object, request_id: str | None):
        self.status_code = status_code
        self.detail = detail
        self.request_id = request_id
        super().__init__(f"API returned HTTP {status_code}: {detail}")


class PredictionProtocolError(PredictionClientError):
    """La respuesta de éxito no respeta el contrato JSON esperado."""


def response_detail(response: requests.Response) -> object:
    try:
        return response.json()
    except ValueError:
        return response.text[:200]


def request_prediction(
    payload: dict[str, Any],
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 5.0,
    session: Any | None = None,
) -> dict[str, Any]:
    """Envía una predicción y traduce fallos técnicos a errores controlados."""
    http_client = session if session is not None else requests
    try:
        response = http_client.post(
            f"{base_url.rstrip('/')}/v1/predictions",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise PredictionTransportError(
            "La API tardó demasiado en responder; inténtalo de nuevo más tarde."
        ) from exc
    except requests.ConnectionError as exc:
        raise PredictionTransportError(
            "No se pudo conectar; comprueba la URL y que la API esté arrancada."
        ) from exc
    except requests.HTTPError as exc:
        error_response = exc.response
        if error_response is None:
            raise PredictionHTTPError(0, str(exc), None) from exc
        raise PredictionHTTPError(
            error_response.status_code,
            response_detail(error_response),
            error_response.headers.get("X-Request-Id"),
        ) from exc
    except requests.RequestException as exc:
        raise PredictionTransportError(f"Fallo del cliente HTTP: {exc}") from exc

    try:
        result = response.json()
    except ValueError as exc:
        raise PredictionProtocolError(
            "La API respondió con éxito, pero el cuerpo no contiene JSON válido."
        ) from exc
    if not isinstance(result, dict):
        raise PredictionProtocolError("La respuesta JSON debe ser un objeto.")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Cliente HTTP de predicciones S7")
    parser.add_argument("payload", type=Path)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", default=5.0, type=float)
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
        result = request_prediction(
            payload, base_url=args.base_url, timeout=args.timeout
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"No se pudo leer el payload: {exc}")
        return 2
    except PredictionClientError as exc:
        print(f"La predicción no se completó: {exc}")
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
