#!/usr/bin/env python3
"""Selftest for block_worktrees.py."""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).with_name("block_worktrees.py")


def run(payload, *args):
    p = subprocess.run([sys.executable, str(HOOK), *args], input=json.dumps(payload),
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


CASES = [
    ({"tool_name": "Agent", "tool_input": {"isolation": "worktree", "model": "sonnet"}}, True),
    ({"tool_name": "Agent", "tool_input": {"model": "sonnet"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "git worktree add ../x origin/main"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": "cd /home/mandrake/rm/bench && git -C . worktree add /home/x"}}, True),
    ({"tool_name": "Bash", "tool_input": {"command": "git worktree list"}}, False),
    ({"tool_name": "Bash", "tool_input": {"command": "git worktree remove /home/x"}}, False),
]

fails = 0
for payload, want_deny in CASES:
    rc, out, _ = run(payload)
    denied = '"deny"' in out
    ok = rc == 0 and denied == want_deny
    fails += not ok
    print(("PASS" if ok else "FAIL"), json.dumps(payload["tool_input"])[:80])
rc, out, err = run({"name": "agent-x", "cwd": "/home/mandrake/rm/bench"}, "--worktree-create")
ok = rc == 1 and "OFF" in err and out == ""
fails += not ok
print(("PASS" if ok else "FAIL"), "WorktreeCreate refuses")
print(f"{len(CASES) + 1 - fails}/{len(CASES) + 1} passed")
sys.exit(1 if fails else 0)
