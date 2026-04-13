from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROJECT_SECTION_HEADER = re.compile(r"^\[project\]\s*$")
SECTION_HEADER = re.compile(r"^\[[^\]]+\]\s*$")
PROJECT_VERSION_LINE = re.compile(r'^(?P<indent>\s*)version\s*=\s*"[^"]+"(?P<suffix>\s*(?:#.*)?)$')


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stage a release version into python/pyproject.toml and ts/package.json."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing python/pyproject.toml and ts/package.json (default: current directory).",
    )
    parser.add_argument("--version", required=True, help="Release version to stage into both manifests.")
    return parser


def update_pyproject_version(pyproject_text: str, version: str) -> str:
    updated_lines: list[str] = []
    in_project_section = False
    replacements = 0

    for line in pyproject_text.splitlines():
        stripped = line.strip()
        if PROJECT_SECTION_HEADER.fullmatch(stripped):
            in_project_section = True
        elif SECTION_HEADER.fullmatch(stripped):
            in_project_section = False

        if in_project_section:
            match = PROJECT_VERSION_LINE.match(line)
            if match is not None:
                line = f'{match.group("indent")}version = "{version}"{match.group("suffix")}'
                replacements += 1

        updated_lines.append(line)

    if replacements != 1:
        raise ValueError(
            "Expected exactly one [project] version entry in python/pyproject.toml, "
            f"found {replacements}."
        )

    return "\n".join(updated_lines) + "\n"


def update_package_json_version(package_json_text: str, version: str) -> str:
    try:
        package_json = json.loads(package_json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse ts/package.json: {exc}") from exc

    package_json["version"] = version
    return json.dumps(package_json, indent=2) + "\n"


def stage_release_version(repo_root: Path, version: str) -> None:
    pyproject_path = repo_root / "python" / "pyproject.toml"
    package_json_path = repo_root / "ts" / "package.json"

    if not pyproject_path.is_file():
        raise ValueError(f"Missing Python manifest: {pyproject_path}")
    if not package_json_path.is_file():
        raise ValueError(f"Missing TypeScript manifest: {package_json_path}")

    pyproject_path.write_text(
        update_pyproject_version(pyproject_path.read_text(encoding="utf-8"), version),
        encoding="utf-8",
    )
    package_json_path.write_text(
        update_package_json_version(package_json_path.read_text(encoding="utf-8"), version),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    try:
        stage_release_version(repo_root, args.version)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Staged release version {args.version} in {repo_root}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
