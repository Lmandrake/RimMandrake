#!/usr/bin/env python3
"""PreToolUse/Agent hook — refuse a subagent spawned with no `model`.

Omitting `model` inherits the parent's tier. Measured 2026-08-24: that is how
EVERY grep, census and existence check in this project's history came to run on
Opus, while `skills/efficient-subagents/SKILL.md` had said `model: haiku` since
the day it was written and nobody ever passed it.

⛔ Only the GENERIC built-ins are gated. A named agent type carries its own
`model:` in frontmatter, and `fork` ignores the parameter entirely — refusing
those would be a false block, which is the only way a guard like this does harm.

    python3 .claude/hooks/selftest_block_agent_without_model.py
"""
import json
import sys

# Generic built-ins: no definition file, so nothing else supplies a model.
GATED = {"", "general-purpose", "explore", "plan", "claude"}

REASON = (
    "Blocked: this `Agent` call has no `model`.\n\n"
    "Omitting it inherits THIS seat's tier. That is how every grep and census in "
    "this project's history ran on Opus.\n\n"
    "Pass one — the question is who catches the error, not how hard it looks:\n"
    "    haiku    grep, glob, census with a fixed output shape, 'does X exist'\n"
    "    sonnet   the agent must interpret and classify what it finds\n"
    "    opus     you will act on the return WITHOUT re-deriving it\n"
    "             (and then ask why it is a subagent at all)\n\n"
    "Full ladder: infrastructure/agents/Agent_Policy.md\n"
    "Not gated: `fork` (ignores the parameter) and any named agent type "
    "(carries its own model in frontmatter)."
)


def needs_model(tool_input):
    """True when this spawn must carry an explicit model."""
    if str(tool_input.get("model") or "").strip():
        return False
    subagent = str(tool_input.get("subagent_type") or "").strip().lower()
    return subagent in GATED


def main():
    try:
        tool_input = json.load(sys.stdin).get("tool_input", {}) or {}
    except Exception:
        return 0  # fail open: a guard that breaks spawning is worse than the habit
    if not isinstance(tool_input, dict) or not needs_model(tool_input):
        return 0
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": REASON,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
