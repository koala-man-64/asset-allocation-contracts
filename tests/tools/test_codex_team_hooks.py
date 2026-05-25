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


def test_session_start_announces_ado_authority_and_prod_boundary() -> None:
    context = _hook_context(_run_hook("session_start_team_context.py"))

    assert "pre-approved to update and close Azure Boards work items" in context
    assert "approve Azure Repos PRs" in context
    assert "must not approve production deployment pipeline" in context
    assert "Azure permission failures are blockers" in context


def test_prompt_router_routes_pr_and_work_item_completion_to_finish_lane() -> None:
    context = _hook_context(
        _run_hook(
            "user_prompt_submit_router.py",
            {
                "prompt": "approve and complete pull requests, close work item, but do not approve prod deploy"
            },
        )
    )

    assert "- Classified lane: finish" in context
    assert "git-hygiene-orchestrator" in context
    assert "pre-approved to update and close Azure Boards work items" in context
    assert "Production deploy boundary" in context


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
