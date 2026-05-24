import re
from pathlib import Path

from hook_utils import (
    additional_context,
    deny_pre_tool,
    dirty_summary,
    emit_json,
    extract_command,
    normalized_command,
    path_is_inside,
    read_hook_input,
    repo_root,
    upstream_gone,
)


SECRET_WORDS = (
    "pat",
    "token",
    "secret",
    "password",
    "client_secret",
    "connectionstring",
    "connection_string",
    "private_key",
    "oauth",
)


def contains_destructive_git(command: str) -> str | None:
    checks = (
        (r"\bgit\s+reset\s+--hard\b", "git reset --hard is blocked. Preserve the current worktree and inspect diffs instead."),
        (r"\bgit\s+clean\b[^\n;|&]*(?:-[a-z]*f[a-z]*d|-[a-z]*d[a-z]*f)", "git clean with force/delete flags is blocked. Review untracked files and remove only explicit task-owned paths."),
        (r"\bgit\s+checkout\s+--\b", "git checkout -- is blocked because it can discard work. Inspect the file diff and request explicit approval before reverting."),
        (r"\bgit\s+restore\s+\.\b", "git restore . is blocked because it can discard broad worktree changes. Restore only explicit task-owned paths after approval."),
        (r"\bgit\s+branch\s+-D\b", "git branch -D is blocked. Use git branch -d only after proving the branch is merged and not checked out in any worktree."),
        (r"\bgit\s+push\b[^\n;|&]*(?:--force(?!-with-lease)|\s-f(?:\s|$))", "git push --force is blocked. Use the repo-approved sync path and avoid rewriting shared history."),
    )
    for pattern, reason in checks:
        if re.search(pattern, command):
            return reason
    if re.search(r"\bgit\s+push\s+(?:origin\s+)?(?:main|master|trunk|develop|staging|production)\b", command):
        return "Direct pushes to protected branches are blocked. Use a task branch and PR policy path."
    if re.search(r"\bgit\s+push\s+origin\s+head:(?:main|master|trunk|develop|staging|production)\b", command):
        return "Direct pushes to protected branches are blocked. Use a task branch and PR policy path."
    return None


def contains_secret_print(command: str) -> str | None:
    if not any(word in command for word in SECRET_WORDS):
        return None
    if re.search(r"\b(echo|write-output|write-host|printenv|env|set|cat|type|get-content)\b", command):
        return "Command appears to print secret-bearing values. Do not echo tokens, PATs, OAuth codes, connection strings, or private keys."
    return None


def contains_external_recursive_delete_or_move(command: str, root: Path) -> str | None:
    patterns = (
        r"\brm\s+-[a-z]*r[a-z]*f?\s+([^\s;&|]+)",
        r"\bremove-item\b[^\n;|&]*\s-recurse\b[^\n;|&]*\s+([^\s;&|]+)",
        r"\brmdir\s+/s\b[^\n;|&]*\s+([^\s;&|]+)",
        r"\bmove-item\b\s+([^\s;&|]+)",
        r"\bmv\s+([^\s;&|]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, command)
        if match and not path_is_inside(match.group(1), root):
            return "Recursive delete or move outside the repository root is blocked. Restrict filesystem changes to explicit task-owned paths inside the workspace."
    return None


def risky_context(command: str, root: Path) -> str | None:
    risky = (
        "git commit" in command
        or re.search(r"\bgit\s+push\b", command)
        or "az boards work-item update" in command
        or "az repos pr create" in command
    )
    if not risky:
        return None

    notes = []
    status = dirty_summary(root)
    if status.startswith("dirty"):
        notes.append(f"working tree is {status}")
    if upstream_gone(root):
        notes.append("current branch upstream is gone")
    if not notes:
        return None
    return "Caution before running this command: " + "; ".join(notes) + ". Confirm task-owned scope, validation, and git-hygiene expectations before proceeding."


def main() -> int:
    payload = read_hook_input()
    command = normalized_command(extract_command(payload))
    if not command:
        return 0

    root = repo_root()
    for check in (contains_destructive_git, contains_secret_print):
        reason = check(command)
        if reason:
            return emit_json(deny_pre_tool(reason))

    reason = contains_external_recursive_delete_or_move(command, root)
    if reason:
        return emit_json(deny_pre_tool(reason))

    context = risky_context(command, root)
    if context:
        return emit_json(additional_context("PreToolUse", context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
