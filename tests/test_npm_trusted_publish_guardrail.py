from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_guardrail_module():
    script_path = repo_root() / "scripts" / "check_npm_trusted_publish.py"
    spec = importlib.util.spec_from_file_location("check_npm_trusted_publish", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MockResponse:
    def __init__(self, *, status: int, payload: object):
        self.status = status
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_guardrail_fails_without_github_oidc_env(monkeypatch, capsys) -> None:
    module = load_guardrail_module()
    monkeypatch.delenv("ACTIONS_ID_TOKEN_REQUEST_URL", raising=False)
    monkeypatch.delenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)

    exit_code = module.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "must run in GitHub Actions with id-token: write enabled" in captured.err


def test_guardrail_passes_with_successful_oidc_exchange(monkeypatch, capsys, tmp_path: Path) -> None:
    module = load_guardrail_module()
    summary_path = tmp_path / "summary.md"
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "https://token.actions.githubusercontent.com?id=123")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "github-request-token")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_path))

    def fake_urlopen(request, timeout=15):
        if request.full_url.startswith("https://token.actions.githubusercontent.com"):
            assert "audience=npm%3Aregistry.npmjs.org" in request.full_url
            assert request.headers["Authorization"] == "Bearer github-request-token"
            return MockResponse(status=200, payload={"value": "github-oidc-token"})
        if request.full_url.startswith("https://registry.npmjs.org/-/npm/v1/oidc/token/exchange/package/"):
            assert request.headers["Authorization"] == "Bearer github-oidc-token"
            return MockResponse(status=201, payload={"token_type": "oidc", "token": "npm-exchange-token"})
        raise AssertionError(f"Unexpected URL requested: {request.full_url}")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    exit_code = module.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "npm trusted publishing preflight passed for @asset-allocation/contracts" in captured.out
    assert "npm trusted publishing preflight" in summary_path.read_text(encoding="utf-8")


def test_guardrail_surfaces_npm_exchange_errors(monkeypatch, capsys) -> None:
    module = load_guardrail_module()
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_URL", "https://token.actions.githubusercontent.com?id=123")
    monkeypatch.setenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "github-request-token")
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)

    def fake_urlopen(request, timeout=15):
        if request.full_url.startswith("https://token.actions.githubusercontent.com"):
            return MockResponse(status=200, payload={"value": "github-oidc-token"})
        if request.full_url.startswith("https://registry.npmjs.org/-/npm/v1/oidc/token/exchange/package/"):
            raise module.HTTPError(
                request.full_url,
                404,
                "Not Found",
                hdrs=None,
                fp=io.BytesIO(b'{"error":"package or trusted publisher not found"}'),
            )
        raise AssertionError(f"Unexpected URL requested: {request.full_url}")

    monkeypatch.setattr(module, "urlopen", fake_urlopen)

    exit_code = module.main([])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "HTTP 404" in captured.err
    assert "workflow filename 'release.yml'" in captured.err


def test_release_workflow_and_package_metadata_contract() -> None:
    package_json = json.loads((repo_root() / "ts" / "package.json").read_text(encoding="utf-8"))
    release_workflow = (repo_root() / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert package_json["name"] == "@asset-allocation/contracts"
    assert package_json["repository"]["url"] == "git+https://github.com/koala-man-64/asset-allocation-contracts.git"
    assert "id-token: write" in release_workflow
    assert "Verify npm trusted publisher" in release_workflow
    assert "python scripts/check_npm_trusted_publish.py" in release_workflow
