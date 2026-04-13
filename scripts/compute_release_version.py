from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path


STABLE_SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve the committed contracts release version from the repo manifests."
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root containing python/pyproject.toml and ts/package.json.",
    )
    return parser


def validate_release_version(version: str) -> None:
    if not STABLE_SEMVER_PATTERN.fullmatch(version):
        raise ValueError(
            f"Release version {version!r} is not a stable semver value. Use x.y.z."
        )


def read_python_version(repo_root: Path) -> str:
    pyproject_path = repo_root / "python" / "pyproject.toml"
    if not pyproject_path.exists():
        raise ValueError(f"Python manifest not found: {pyproject_path}")

    with pyproject_path.open("rb") as handle:
        payload = tomllib.load(handle)

    version = payload.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Could not read [project].version from {pyproject_path}")
    return version


def read_typescript_version(repo_root: Path) -> str:
    package_json_path = repo_root / "ts" / "package.json"
    if not package_json_path.exists():
        raise ValueError(f"TypeScript manifest not found: {package_json_path}")

    payload = json.loads(package_json_path.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"Could not read version from {package_json_path}")
    return version


def resolve_release_version(repo_root: Path) -> str:
    python_version = read_python_version(repo_root)
    typescript_version = read_typescript_version(repo_root)

    if python_version != typescript_version:
        raise ValueError(
            "Python and TypeScript package versions must match before release. "
            f"python={python_version!r}, ts={typescript_version!r}"
        )

    validate_release_version(python_version)
    return python_version


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        version = resolve_release_version(args.repo_root.resolve())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
