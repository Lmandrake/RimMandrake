#!/usr/bin/env python3
"""PermissionRequest hook: answer every Bash permission prompt with "allow".

Owner, 2026-10-12: an "allow bash" prompt raised by an unattended live-pass subagent sat
for 2.3 hours until he could look. Bash is already allowed wholesale in user settings; the
prompts that still appear come from built-in command checks, and nobody is there to answer
them. The project's PreToolUse hooks still block what must never run — they refuse, they
never ask — so allowing here removes only the wait.

Each auto-allowed command is appended to ~/.claude/auto_allowed_bash.log for audit.
"""
import json
import sys
import time
from pathlib import Path

LOG = Path.home() / ".claude" / "auto_allowed_bash.log"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    cmd = (payload.get("tool_input") or {}).get("command", "")
    try:
        with LOG.open("a") as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{payload.get('cwd', '')}\t{cmd[:500]!r}\n")
    except OSError:
        pass
    json.dump({"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                      "decision": {"behavior": "allow"}}}, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
