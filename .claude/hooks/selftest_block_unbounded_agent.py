#!/usr/bin/env python3
"""Selftest for block_unbounded_agent.py."""
import json, os, subprocess, sys
HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block_unbounded_agent.py")
CASES = [("general-purpose", True), ("claude", True), ("", True), ("fork", True),
         ("rm-fixer", False), ("rm-bridge", False), ("Explore", False), ("web-fetch", False)]
fails = 0
for t, deny in CASES:
    inp = {"tool_input": {"prompt": "x", "model": "sonnet"}}
    if t: inp["tool_input"]["subagent_type"] = t
    env = dict(os.environ); env.pop("RM_ALLOW_UNBOUNDED_AGENT", None)
    out = subprocess.run([sys.executable, HOOK], input=json.dumps(inp), capture_output=True, text=True, env=env).stdout
    got = '"deny"' in out
    if got != deny:
        fails += 1; print(f"FAIL {t!r}: deny={got}, want {deny}")
env = dict(os.environ, RM_ALLOW_UNBOUNDED_AGENT="1")
if '"deny"' in subprocess.run([sys.executable, HOOK], input='{"tool_input":{"subagent_type":"claude"}}', capture_output=True, text=True, env=env).stdout:
    fails += 1; print("FAIL override")
# a session that started before the definitions existed is let through
import tempfile
old = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False); old.write('{"timestamp":"2020-01-01T00:00:00Z"}\n'); old.close()
new = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False); new.write('{"timestamp":"2099-01-01T00:00:00Z"}\n'); new.close()
env = dict(os.environ); env.pop("RM_ALLOW_UNBOUNDED_AGENT", None)
for path, deny in ((old.name, False), (new.name, True)):
    out = subprocess.run([sys.executable, HOOK], input=json.dumps({"transcript_path": path, "tool_input": {"subagent_type": "claude"}}), capture_output=True, text=True, env=env).stdout
    if ('"deny"' in out) != deny:
        fails += 1; print(f"FAIL predates path={path} deny={not deny}")
print("PASS" if not fails else f"{fails} FAIL"); sys.exit(1 if fails else 0)
