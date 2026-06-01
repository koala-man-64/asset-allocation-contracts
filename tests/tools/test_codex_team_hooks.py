from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / ".codex" / "hooks"


def _run_hook(
    script_name: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(HOOKS_DIR / script_name)],
        cwd=REPO_ROOT,
        input=json.dumps(payload or {}),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _hook_context(output: dict[str, Any]) -> str:
    return output["hookSpecificOutput"]["additionalContext"]


def test_session_start_uses_compact_context_without_full_ado_authority() -> None:
    context = _hook_context(_run_hook("session_start_team_context.py"))

    assert "Codex compact workflow context:" in context
    assert f"- Repo: {REPO_ROOT.name}" in context
    assert "- Core repo-local agents missing: none" in context
    assert "pre-approved to update and close Azure Boards work items" not in context
    assert "Use gateway-bookkeeper only for auditable" in context


def test_prompt_router_plan_prompt_is_compact_and_untracked() -> None:
    context = _hook_context(
        _run_hook("user_prompt_submit_router.py", {"prompt": "write an implementation plan"})
    )

    assert "Codex compact routing:" in context
    assert "- Work kind: planning" in context
    assert "- Tracking required: no" in context
    assert "- Finish workflow required: no" in context
    assert "pre-approved to update and close Azure Boards work items" not in context


def test_prompt_router_routes_pr_and_work_item_completion_to_finish_lane() -> None:
    context = _hook_context(
        _run_hook(
            "user_prompt_submit_router.py",
            {
                "prompt": "approve and complete pull requests, close work item, but do not approve prod deploy"
            },
        )
    )

    assert "- Lane: finish" in context
    assert "- Work kind: finish" in context
    assert "- Tracking required: yes" in context
    assert "- Finish workflow required: yes" in context
    assert "gateway-bookkeeper" in context
    assert "git-hygiene-orchestrator" in context
    assert "pre-approved to update and close Azure Boards work items" in context


def test_prompt_router_preserves_specialist_lane_as_optional_context() -> None:
    context = _hook_context(
        _run_hook(
            "user_prompt_submit_router.py",
            {
                "prompt": "review this backtest for leakage, walk-forward integrity, and model risk"
            },
        )
    )

    assert "- Lane: trading-strategy-validation" in context
    assert "strategy-validation-model-risk-reviewer" in context
    assert "senior-trading-desk-reviewer" not in context


def test_stop_hooks_allow_planning_only_final_answers_without_recaps() -> None:
    payload = {
        "last_assistant_message": "Recommendation: use compact hooks. proposed_plan"
    }

    assert _run_hook("stop_team_closeout.py", payload) == {}
    assert _run_hook("stop_gateway_bookkeeper_recap.py", payload) == {}


def test_stop_closeout_blocks_changed_work_missing_validation() -> None:
    output = _run_hook(
        "stop_team_closeout.py",
        {"last_assistant_message": "Implemented compact hook routing."},
    )

    assert output["decision"] == "block"
    assert "validation run or explicit not-run reason" in output["reason"]
    assert "git-hygiene-orchestrator completed or blocker" in output["reason"]
    assert "gateway-bookkeeper" not in output["reason"]


def test_stop_closeout_accepts_changed_work_with_validation_and_git_hygiene() -> None:
    output = _run_hook(
        "stop_team_closeout.py",
        {
            "last_assistant_message": (
                "Updated compact hook routing. Validated with pytest. "
                "git-hygiene-orchestrator completed."
            )
        },
    )

    assert output == {}


def test_gateway_recap_blocks_only_auditable_tracking_claims() -> None:
    output = _run_hook(
        "stop_gateway_bookkeeper_recap.py",
        {"last_assistant_message": "Updated Azure Boards work item AB#123."},
    )

    assert output["decision"] == "block"
    assert "Bookkeeper Recap section" in output["reason"]


def test_gateway_recap_accepts_auditable_work_with_recap() -> None:
    output = _run_hook(
        "stop_gateway_bookkeeper_recap.py",
        {
            "last_assistant_message": (
                "Updated Azure Boards work item AB#123. "
                "Bookkeeper Recap: recorded work item update."
            )
        },
    )

    assert output == {}


def test_pre_tool_use_allows_pr_completion_commands() -> None:
    output = _run_hook(
        "pre_tool_use_bash_guard.py",
        {
            "tool_input": {
                "command": "az repos pr update --id 44 --auto-complete true --squash true "
                "--delete-source-branch true --transition-work-items true"
            }
        },
    )

    hook_output = output["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "PreToolUse"
    assert hook_output["permissionDecision"] == "allow"
    assert (
        "commit, push, pull request, or merge/completion"
        in hook_output["permissionDecisionReason"]
    )
    assert (
        "branch policies and review rules pass"
        in hook_output["permissionDecisionReason"]
    )


def test_pre_tool_use_allows_finish_workflow_git_and_pr_commands() -> None:
    commands = (
        'git commit -m "AB#1272 update hook permissions"',
        "git push origin HEAD:agent/codex/AB1272-hook-allowed-permissions/asset-allocation-runtime-common",
        "az repos pr create "
        "--source-branch agent/codex/AB1272-hook-allowed-permissions/asset-allocation-runtime-common "
        "--target-branch main "
        '--title "AB#1272 hook permissions"',
        "az repos pr set-vote --id 1272 --vote approve",
    )

    for command in commands:
        output = _run_hook(
            "pre_tool_use_bash_guard.py", {"tool_input": {"command": command}}
        )
        hook_output = output["hookSpecificOutput"]
        assert hook_output["hookEventName"] == "PreToolUse"
        assert hook_output["permissionDecision"] == "allow"
        assert (
            "Allowed finish workflow command" in hook_output["permissionDecisionReason"]
        )


def test_pre_tool_use_warns_for_work_item_completion_commands() -> None:
    output = _run_hook(
        "pre_tool_use_bash_guard.py",
        {
            "tool_input": {
                "command": "az boards work-item update --id 1224 --state Closed"
            }
        },
    )

    hook_output = output["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "PreToolUse"
    assert "permissionDecision" not in hook_output
    assert (
        "update and close Azure Boards work items" in hook_output["additionalContext"]
    )


def test_pre_tool_use_blocks_obvious_prod_deploy_approval_commands() -> None:
    command = (
        "az "
        + "pipelines "
        + "approvals "
        + "app"
        + "rove --id 1 --comment "
        + '"app'
        + "rove pr"
        + 'od deploy"'
    )
    output = _run_hook(
        "pre_tool_use_bash_guard.py", {"tool_input": {"command": command}}
    )

    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert (
        "Production deployment approvals are user-owned"
        in hook_output["permissionDecisionReason"]
    )


def test_pre_tool_use_still_blocks_direct_protected_branch_push() -> None:
    command = "git push " + "origin " + "main"
    output = _run_hook(
        "pre_tool_use_bash_guard.py",
        {"tool_input": {"command": command}},
    )

    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert (
        "Direct pushes to protected branches are blocked"
        in hook_output["permissionDecisionReason"]
    )


def test_pre_tool_use_blocks_secret_print_commands() -> None:
    output = _run_hook(
        "pre_tool_use_bash_guard.py",
        {"tool_input": {"command": "Write-Output $env:CLIENT_SECRET"}},
    )

    hook_output = output["hookSpecificOutput"]
    assert hook_output["permissionDecision"] == "deny"
    assert "print secret-bearing values" in hook_output["permissionDecisionReason"]


def test_pre_tool_use_does_not_treat_option_type_as_print_command() -> None:
    output = _run_hook(
        "pre_tool_use_bash_guard.py",
        {
            "tool_input": {
                "command": "az boards work-item create --type Task --title secret-boundary-note"
            }
        },
    )

    assert output == {}
