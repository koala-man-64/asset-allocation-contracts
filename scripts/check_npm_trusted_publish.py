from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


DEFAULT_PACKAGE_NAME = "@asset-allocation/contracts"
OIDC_AUDIENCE = "npm:registry.npmjs.org"
TRUSTED_PUBLISHER_HINT = (
    "Verify the npm trusted publisher configuration for "
    "owner/user 'koala-man-64', repository 'asset-allocation-contracts', "
    "workflow filename 'release.yml', and blank environment unless one is intentionally used."
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify npm trusted publishing from the active GitHub Actions OIDC context."
    )
    parser.add_argument(
        "--package",
        default=os.environ.get("NPM_PACKAGE_NAME", DEFAULT_PACKAGE_NAME),
        help=f"npm package name to verify (default: {DEFAULT_PACKAGE_NAME})",
    )
    return parser


def write_step_summary(message: str) -> None:
    step_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not step_summary_path:
        return

    Path(step_summary_path).write_text(message, encoding="utf-8", errors="strict")


def with_audience_parameter(url: str, audience: str) -> str:
    parsed = urlparse(url)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("audience", audience))
    return urlunparse(parsed._replace(query=urlencode(query)))


def fetch_github_oidc_token(audience: str) -> str:
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    if not request_url or not request_token:
        raise RuntimeError(
            "This guardrail must run in GitHub Actions with id-token: write enabled. "
            "Missing ACTIONS_ID_TOKEN_REQUEST_URL or ACTIONS_ID_TOKEN_REQUEST_TOKEN."
        )

    token_request = Request(
        with_audience_parameter(request_url, audience),
        headers={
            "Authorization": f"Bearer {request_token}",
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(token_request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub OIDC token request failed with HTTP {exc.code}: {error_body}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub OIDC token request failed: {exc.reason}") from exc

    oidc_token = payload.get("value")
    if not oidc_token:
        raise RuntimeError("GitHub OIDC token response did not include a token value.")

    return oidc_token


def exchange_npm_oidc_token(package_name: str, oidc_token: str) -> dict[str, Any]:
    exchange_request = Request(
        "https://registry.npmjs.org/-/npm/v1/oidc/token/exchange/package/"
        f"{quote(package_name, safe='')}",
        headers={
            "Authorization": f"Bearer {oidc_token}",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(exchange_request, timeout=15) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            if response.status != 201:
                raise RuntimeError(
                    f"npm trusted publishing preflight failed for {package_name}: "
                    f"HTTP {response.status} {response_body}"
                )
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"npm trusted publishing preflight failed for {package_name}: "
            f"HTTP {exc.code} {error_body}. {TRUSTED_PUBLISHER_HINT}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"npm trusted publishing preflight failed for {package_name}: "
            f"{exc.reason}. {TRUSTED_PUBLISHER_HINT}"
        ) from exc

    try:
        return json.loads(response_body) if response_body else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"npm trusted publishing preflight returned invalid JSON for {package_name}: "
            f"{response_body}"
        ) from exc


def run_preflight(package_name: str) -> str:
    oidc_token = fetch_github_oidc_token(OIDC_AUDIENCE)
    exchange_payload = exchange_npm_oidc_token(package_name, oidc_token)
    token_type = exchange_payload.get("token_type", "unknown")
    return (
        f"npm trusted publishing preflight passed for {package_name} "
        f"(token_type={token_type})."
    )


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)

    try:
        success_message = run_preflight(args.package)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(success_message)
    write_step_summary(
        "## npm trusted publishing preflight\n\n"
        f"- Package: `{args.package}`\n"
        f"- Status: `{success_message}`\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
