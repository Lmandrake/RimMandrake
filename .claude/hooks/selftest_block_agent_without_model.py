#!/usr/bin/env python3
"""Selftest for block_agent_without_model.py. Run it after any edit to that file.

The cases that matter are the FALSE BLOCKS — `fork` and named agent types. A
guard that refuses a legitimate spawn costs more than the habit it prevents.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "hook", os.path.join(HERE, "block_agent_without_model.py"))
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

CASES = [
    # (name, tool_input, expect_block)
    ("bare general-purpose", {"subagent_type": "general-purpose"}, True),
    ("no subagent_type at all", {"prompt": "go"}, True),
    ("Explore, no model", {"subagent_type": "Explore"}, True),
    ("Plan, no model", {"subagent_type": "Plan"}, True),
    ("empty-string model", {"subagent_type": "general-purpose", "model": ""}, True),
    ("whitespace model", {"subagent_type": "general-purpose", "model": "  "}, True),
    ("sonnet given, general-purpose", {"subagent_type": "general-purpose", "model": "sonnet"}, False),
    ("sonnet given", {"subagent_type": "Explore", "model": "sonnet"}, False),
    ("opus given", {"model": "opus"}, False),
    # false-block guards
    ("fork ignores model", {"subagent_type": "fork"}, False),
    ("named plugin agent", {"subagent_type": "feature-dev:code-reviewer"}, False),
    ("named agent, mixed case", {"subagent_type": "Code-Simplifier"}, False),
    ("case-insensitive gate", {"subagent_type": "GENERAL-PURPOSE"}, True),
]

fails = []
for name, ti, expect in CASES:
    got = hook.needs_model(ti)
    if got != expect:
        fails.append("%s: expected block=%s, got %s" % (name, expect, got))

BAN_CASES = [
    ("alias", {"model": "haiku"}, True),
    ("mixed case with spaces", {"model": " Haiku "}, True),
    ("full id", {"model": "us.anthropic.claude-haiku-5-5"}, True),
    ("on a named agent", {"subagent_type": "rm-search", "model": "haiku"}, True),
    ("on fork", {"subagent_type": "fork", "model": "haiku"}, True),
    ("sonnet", {"model": "sonnet"}, False),
    ("opus", {"model": "opus"}, False),
    ("no model", {"subagent_type": "general-purpose"}, False),
    ("named agent, no pin here", {"subagent_type": "feature-dev:code-reviewer"}, False),
]
for name, ti, expect in BAN_CASES:
    if hook.banned(ti) != expect:
        fails.append("ban %s: expected %s" % (name, expect))

with tempfile.TemporaryDirectory() as root:
    agents = os.path.join(root, ".claude", "agents")
    os.makedirs(agents)
    with open(os.path.join(agents, "pinned.md"), "w") as out:
        out.write("---\nname: pinned\nmodel: haiku\n---\n")
    with open(os.path.join(agents, "fine.md"), "w") as out:
        out.write("---\nname: fine\nmodel: sonnet\n---\nmodel: haiku in the body\n")
    os.environ["CLAUDE_PROJECT_DIR"] = root
    if not hook.banned({"subagent_type": "pinned"}):
        fails.append("definition pin not refused")
    if hook.banned({"subagent_type": "pinned", "model": "sonnet"}):
        fails.append("explicit sonnet over a pin refused")
    if hook.banned({"subagent_type": "fine"}):
        fails.append("body text read as a pin")

# The whole contract: a real deny on stdout, with the ban's reason.
run = subprocess.run([sys.executable, os.path.join(HERE, "block_agent_without_model.py")],
                     input=json.dumps({"tool_input": {"model": "haiku"}}),
                     capture_output=True, text=True)
out = json.loads(run.stdout)["hookSpecificOutput"]
if out["permissionDecision"] != "deny" or "banned" not in out["permissionDecisionReason"]:
    fails.append("stdin ban: no deny")

# fail-open on garbage stdin is exercised by main() returning 0, not needs_model
total = len(CASES) + len(BAN_CASES) + 4
print("%d/%d" % (total - len(fails), total))
for f in fails:
    print("  FAIL " + f)
sys.exit(1 if fails else 0)
