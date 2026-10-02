#!/usr/bin/env python3
"""Worktrees are OFF in this project — owner ruling 2026-10-02 (decision taken by question card).

Why: worktree agents duplicated full 4 GB checkouts by the hundred, and reported work as
"committed" while it sat on side branches or as uncommitted edits that never reached main.
Every writing helper now edits in its window's own clone (/home/mandrake/rm/<seat>) and that
window commits explicit paths. Read-only helpers never needed a checkout.

Three entry points, one message:
    PreToolUse/Agent   refuse `isolation: "worktree"`
    PreToolUse/Bash    refuse `git worktree add`
    WorktreeCreate     `--worktree-create`: exit 1 (covers `claude --worktree` and any spawn
                       that slips past the Agent check)

    python3 .claude/hooks/selftest_block_worktrees.py
"""
import json
import re
import sys

REASON = (
    "Blocked: worktrees are OFF in this project (owner ruling 2026-10-02).\n\n"
    "Worktree agents duplicated whole checkouts and left work stranded on side branches.\n"
    "Spawn the helper WITHOUT `isolation`; it edits in this window's clone, and this\n"
    "window commits the paths it changed (`./publish -m \"...\" <paths>`). Run writing\n"
    "helpers one at a time when their paths could overlap. Read-only helpers are fine as is.\n"
    "Doc: design/RimMandrake/GIT_WORKFLOW.md"
)

WORKTREE_ADD = re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+worktree\s+add\b")


def deny():
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": REASON}}))


def main(argv):
    if "--worktree-create" in argv:
        try:
            sys.stdin.read()
        except Exception:
            pass
        print(REASON, file=sys.stderr)
        return 1
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0  # fail open on unreadable input
    tool = ev.get("tool_name", "")
    ti = ev.get("tool_input", {}) or {}
    if tool == "Agent" and str(ti.get("isolation") or "").strip().lower() == "worktree":
        deny()
    elif tool == "Bash" and WORKTREE_ADD.search(str(ti.get("command") or "")):
        deny()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
