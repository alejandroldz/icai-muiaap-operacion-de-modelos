from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

import app
from model_ui.gateway import DemoGateway
from model_ui.http_gateway import HttpInferenceGateway


def test_build_gateway_prefers_http_url() -> None:
    gateway = app.build_gateway("missing-bundle.joblib", "http://127.0.0.1:8000")

    assert isinstance(gateway, HttpInferenceGateway)


def test_build_gateway_keeps_demo_without_configuration() -> None:
    assert isinstance(app.build_gateway(None, None), DemoGateway)


def test_build_gateway_treats_blank_http_url_as_absent() -> None:
    assert isinstance(app.build_gateway(None, "   "), DemoGateway)


def test_build_gateway_uses_bundle_when_http_url_is_blank(monkeypatch: Any) -> None:
    sentinel = object()
    received_paths: list[Path] = []

    def fake_from_bundle_path(bundle_path: Path) -> object:
        received_paths.append(bundle_path)
        return sentinel

    monkeypatch.setattr(
        app.PackagedBundleGateway,
        "from_bundle_path",
        staticmethod(fake_from_bundle_path),
    )

    gateway = app.build_gateway("bundle.joblib", "   ")

    assert gateway is sentinel
    assert received_paths == [Path("bundle.joblib")]


def test_cached_gateway_forwards_both_configuration_values(monkeypatch: Any) -> None:
    sentinel = object()
    calls: list[tuple[str | None, str | None]] = []

    class PassthroughStreamlit:
        @staticmethod
        def cache_resource(**_kwargs: Any) -> Any:
            return lambda function: function

    def fake_build_gateway(
        bundle_value: str | None,
        api_url: str | None,
    ) -> object:
        calls.append((bundle_value, api_url))
        return sentinel

    monkeypatch.setattr(app, "build_gateway", fake_build_gateway)

    result = app.get_cached_gateway(
        PassthroughStreamlit(), "bundle.joblib", "http://api.test"
    )

    assert result is sentinel
    assert calls == [("bundle.joblib", "http://api.test")]


def test_main_reads_model_api_url(monkeypatch: Any) -> None:
    captured: list[tuple[str | None, str | None]] = []

    class StopAfterGateway(Exception):
        pass

    class FakeStreamlit:
        session_state: dict[str, Any] = {}

        @staticmethod
        def set_page_config(**_kwargs: Any) -> None:
            pass

        @staticmethod
        def title(_value: str) -> None:
            pass

        @staticmethod
        def caption(_value: str) -> None:
            pass

    def stop_with_configuration(
        _st: Any,
        bundle_value: str | None,
        api_url: str | None,
    ) -> None:
        captured.append((bundle_value, api_url))
        raise StopAfterGateway

    monkeypatch.setitem(sys.modules, "streamlit", FakeStreamlit())
    monkeypatch.setattr(app, "get_cached_gateway", stop_with_configuration)
    monkeypatch.setenv("MODEL_UI_BUNDLE", "bundle.joblib")
    monkeypatch.setenv("MODEL_API_URL", "http://api.test")

    with pytest.raises(StopAfterGateway):
        app.main()

    assert captured == [("bundle.joblib", "http://api.test")]
