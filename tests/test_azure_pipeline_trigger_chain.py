from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PIPELINE_TRIGGER = (
    "      trigger:\n        branches:\n          include:\n            - main"
)


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def pipeline_resource_block(text: str, alias: str) -> str:
    marker = f"    - pipeline: {alias}\n"
    start = text.index(marker)
    next_resource = text.find("\n    - pipeline:", start + len(marker))
    next_section = text.find("\npool:", start + len(marker))
    candidates = [idx for idx in (next_resource, next_section) if idx != -1]
    end = min(candidates) if candidates else len(text)
    return text[start:end]


def test_release_is_triggered_by_contracts_ci_only() -> None:
    release = read("azure-pipelines/release.yml")

    assert "\ntrigger: none\npr: none\n" in release
    assert release.count(MAIN_PIPELINE_TRIGGER) == 1
    assert "source: asset-allocation-contracts-ci" in pipeline_resource_block(
        release, "contractsCi"
    )
    assert MAIN_PIPELINE_TRIGGER in pipeline_resource_block(release, "contractsCi")


def test_contracts_has_no_deploy_pipeline() -> None:
    assert not (REPO_ROOT / "azure-pipelines" / "deploy-prod.yml").exists()
