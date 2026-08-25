#!/usr/bin/env python3
"""Selftest for block_agent_without_model.py. Run it after any edit to that file.

The cases that matter are the FALSE BLOCKS — `fork` and named agent types. A
guard that refuses a legitimate spawn costs more than the habit it prevents.
"""
import importlib.util
import os
import sys

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
    ("haiku given", {"subagent_type": "general-purpose", "model": "haiku"}, False),
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

# fail-open on garbage stdin is exercised by main() returning 0, not needs_model
print("%d/%d" % (len(CASES) - len(fails), len(CASES)))
for f in fails:
    print("  FAIL " + f)
sys.exit(1 if fails else 0)
