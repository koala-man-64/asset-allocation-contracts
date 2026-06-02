from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_hook(script_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(repo_root() / ".codex" / "hooks" / script_name)],
        input=json.dumps(payload),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    if not result.stdout.strip():
        return {}
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, dict)
    return parsed


def test_user_prompt_finish_route_keeps_jobs_quality_gates_optional() -> None:
    output = run_hook(
        "user_prompt_submit_router.py",
        {"prompt": "finish it and open the pull request"},
    )

    context = output["hookSpecificOutput"]["additionalContext"]

    assert "- Lane: finish" in context
    assert "- Tracking required: yes" in context
    assert "- Finish workflow required: yes" in context
    assert "gateway-bookkeeper" in context
    assert "git-hygiene-orchestrator" in context
    assert "code-drift-sentinel" in context
    assert "software-testing-validation-architect" in context
    assert "qa-release-gate-agent" in context


def test_stop_closeout_blocks_changed_work_missing_quality_gate_summary() -> None:
    output = run_hook(
        "stop_team_closeout.py",
        {
            "last_assistant_message": (
                "Updated repo hooks. Validated with py_compile. "
                "git-hygiene-orchestrator completed."
            )
        },
    )

    assert output["decision"] == "block"
    assert "code-drift-sentinel completed, not applicable, or blocker" in output["reason"]
    assert "software-testing-validation-architect completed, not applicable, or blocker" in output["reason"]
    assert "gateway-bookkeeper" not in output["reason"]


def test_stop_closeout_accepts_changed_work_with_quality_gate_summary() -> None:
    output = run_hook(
        "stop_team_closeout.py",
        {
            "last_assistant_message": (
                "Updated repo hooks. Validated with py_compile. "
                "code-drift-sentinel completed. software-testing-validation-architect completed. "
                "git-hygiene-orchestrator completed."
            )
        },
    )

    assert output == {}


def test_session_start_uses_compact_context_without_ado_authority() -> None:
    output = run_hook("session_start_team_context.py", {})

    context = output["hookSpecificOutput"]["additionalContext"]

    assert "Codex compact workflow context" in context
    assert "Core repo-local agents missing: none" in context
    assert "pre-approved to update and close Azure Boards work items" not in context
