#!/usr/bin/env python3
"""PreToolUse/Agent hook — refuse a spawn that would run on an unbounded context.

Measured 2026-10-23 (Transient/token_burn_20261023/, token_census.py): 2.18B tokens in
one morning, 89% in helpers. Generic helpers run on the 1M window, so they never compact;
every call re-sends the whole conversation (contexts reached 966k). The rm-* definitions in
.claude/agents/ compact at 150k and carry the context-discipline rules.

Refused: general-purpose, claude, an omitted type, and fork (inherits this seat's whole
context). Allowed: rm-*, the read-only built-ins and any other named definition.
Override is the harness environment only (RM_ALLOW_UNBOUNDED_AGENT=1), which an agent's
prompt cannot set. A session that STARTED before the rm-* definitions existed cannot see them
(definitions load at startup), so it is let through until its next restart.

    python3 .claude/hooks/selftest_block_unbounded_agent.py
"""
import json
import os
import sys

REFUSED = {"", "general-purpose", "claude", "fork"}

REASON = (
    "Blocked: `{t}` runs on an unbounded context (1M window, never compacts; a fork also "
    "inherits this whole seat's conversation). Measured 2026-10-23: such helpers re-read "
    "300k-966k tokens on every call.\n\n"
    "Use a bounded definition (.claude/agents/, auto-compact at 150k, one item each):\n"
    "    rm-fixer    sonnet  well-defined fix a selftest/validator/compiler proves\n"
    "    rm-builder  opus    design or complex code (C#/Harmony, new systems)\n"
    "    rm-bridge   opus    live game driver, script-driven\n"
    "    rm-judge    opus    taste/art judging of work it did not make\n"
    "    rm-search   haiku   bounded search the parent re-checks\n"
    "    Explore / web-fetch for read-only lookups.\n"
    "Why and how: skills/efficient-subagents/SKILL.md §Context burn."
)


def refused_type(tool_input):
    t = str(tool_input.get("subagent_type") or "").strip().lower()
    return t if t in REFUSED else None


DEFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "rm-fixer.md")


def session_predates_defs(transcript_path):
    """True when the session's transcript is older than the rm-* definitions."""
    try:
        return _first_stamp(transcript_path) < os.path.getmtime(DEFS)
    except Exception:
        return False


def _first_stamp(path):
    import datetime
    with open(path, errors="ignore") as f:
        for line in f:
            ts = json.loads(line).get("timestamp")
            if ts:
                return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    return float("inf")


def main():
    if os.environ.get("RM_ALLOW_UNBOUNDED_AGENT") == "1":
        return 0
    try:
        data = json.load(sys.stdin)
        tool_input = data.get("tool_input", {}) or {}
    except Exception:
        return 0
    if session_predates_defs(str(data.get("transcript_path") or "")):
        return 0
    if not isinstance(tool_input, dict):
        return 0
    t = refused_type(tool_input)
    if t is None:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": REASON.format(t=t or "(no subagent_type)"),
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
