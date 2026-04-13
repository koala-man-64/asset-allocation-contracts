from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import UTC, date, datetime

try:
    from packaging.version import InvalidVersion, Version
except ImportError:  # pragma: no cover - packaging is usually installed, but pip always vendors it.
    from pip._vendor.packaging.version import InvalidVersion, Version  # type: ignore[import-not-found]


NPM_SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)-dev\.(0|[1-9]\d*)$")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute the contracts release version for the active workflow run."
    )
    parser.add_argument(
        "--date",
        dest="release_date",
        help="UTC release date in YYYY-MM-DD format. Defaults to today's UTC date.",
    )
    parser.add_argument(
        "--run-number",
        default=os.environ.get("GITHUB_RUN_NUMBER"),
        help="GitHub Actions run number. Defaults to GITHUB_RUN_NUMBER.",
    )
    parser.add_argument(
        "--run-attempt",
        default=os.environ.get("GITHUB_RUN_ATTEMPT"),
        help="GitHub Actions run attempt. Defaults to GITHUB_RUN_ATTEMPT.",
    )
    return parser


def parse_release_date(raw_value: str | None) -> date:
    if raw_value is None:
        return datetime.now(UTC).date()

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid --date value {raw_value!r}; expected YYYY-MM-DD.") from exc


def parse_positive_int(raw_value: str | None, *, name: str) -> int:
    if raw_value is None or raw_value == "":
        raise ValueError(f"{name} is required.")
    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw_value!r}.") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than zero, got {parsed}.")
    return parsed


def validate_release_version(version: str) -> None:
    try:
        Version(version)
    except InvalidVersion as exc:
        raise ValueError(f"Release version {version!r} is not valid for Python packaging.") from exc

    if not NPM_SEMVER_PATTERN.fullmatch(version):
        raise ValueError(f"Release version {version!r} is not valid npm semver.")


def compute_release_version(release_date: date, run_number: int, run_attempt: int) -> str:
    version = (
        f"{release_date.year}.{release_date.month}.{release_date.day}"
        f"-dev.{run_number}{run_attempt:03d}"
    )
    validate_release_version(version)
    return version


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        release_date = parse_release_date(args.release_date)
        run_number = parse_positive_int(args.run_number, name="run-number")
        run_attempt = parse_positive_int(args.run_attempt, name="run-attempt")
        version = compute_release_version(release_date, run_number, run_attempt)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
