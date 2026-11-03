#!/usr/bin/env python3
"""Selftest of block_unbounded_robocopy.py: unbounded robocopy refused, bounded and mentions allowed.

    python3 .claude/hooks/selftest_block_unbounded_robocopy.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HERE, "block_unbounded_robocopy.py")
sys.path.insert(0, HERE)
import block_unbounded_robocopy as H  # noqa: E402

REFUSE = [
    "robocopy.exe E:\\ D:\\ClaudeWork\\usb /E",                                  # the 2026-11-02 shape
    "/mnt/c/Windows/System32/Robocopy.exe a b /E",
    "robocopy a b /E /R:2 /W:5",                                                # bounded retries, no deadline
    "timeout 600 robocopy a b /E",                                              # deadline, default retries
    "timeout 600 robocopy a b /E /R:1000000 /W:30",
    "timeout 600 robocopy a b /R:2 /W:120",
    "cd /tmp && cmd.exe /c robocopy a b /E",
    "powershell.exe -NoProfile -Command \"robocopy a b /MIR\"",
    "ls; FOO=1 robocopy.exe a b /R:2 /W:5",
]
ALLOW = [
    "timeout 600 robocopy.exe a b /E /R:2 /W:5",
    "timeout -k 10 1800 robocopy.exe E:\\ D:\\x /E /R:0 /W:0",
    "timeout 30m cmd.exe /c robocopy a b /R:3 /W:10",
    "grep -n robocopy infrastructure/state/lessons/*.md",
    "echo robocopy is dangerous",
    "git log --grep robocopy",
    "cat .claude/hooks/block_unbounded_robocopy.py",
    "ls -la",
    "",
]

FAILS = []
for c in REFUSE:
    if not H.problems(c):
        FAILS.append("should refuse: %r" % c)
for c in ALLOW:
    if H.problems(c):
        FAILS.append("should allow: %r -> %s" % (c, H.problems(c)))


def run(cmd, tool="Bash"):
    p = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": tool, "tool_input": {"command": cmd}}),
                       capture_output=True, text=True, timeout=30)
    return p.returncode, p.stderr


rc, err = run(REFUSE[0])
if rc != 2 or "/R:" not in err:
    FAILS.append("hook process: unbounded robocopy gave rc=%d" % rc)
rc, _ = run(ALLOW[0])
if rc != 0:
    FAILS.append("hook process: bounded robocopy gave rc=%d" % rc)
rc, _ = run(REFUSE[0], tool="Read")
if rc != 0:
    FAILS.append("hook process: non-Bash tool gave rc=%d" % rc)

# Wired: settings.json runs this hook on Bash.
cfg = json.load(open(os.path.join(HERE, "..", "settings.json"), encoding="utf-8"))
wired = any("block_unbounded_robocopy.py" in h.get("command", "")
            for m in cfg.get("hooks", {}).get("PreToolUse", []) if m.get("matcher") == "Bash"
            for h in m.get("hooks", []))
if not wired:
    FAILS.append("settings.json: block_unbounded_robocopy.py is not on the PreToolUse Bash matcher")

n = len(REFUSE) + len(ALLOW) + 4
for f in FAILS:
    print("FAIL " + f)
print("RESULT: %d/%d %s" % (n - len(FAILS), n, "PASS" if not FAILS else "FAIL"))
sys.exit(1 if FAILS else 0)
