#!/usr/bin/env python3
"""PreToolUse/Agent hook — refuse a helper named by a bare code (C6, A5, `Lane A2`).

Owner 2026-10-31: "We had explicitly asked that everyone use our naming scheme to avoid
trouble like that." A letter+digits code collides with legacy ledger ids. Item-style
names (RM_X, SUBJECT_INTENT_TWIST) pass; a legacy B-style id passes only with a title.

    python3 .claude/hooks/selftest_block_agent_coded_name.py
"""
import json
import re
import sys

CODE = re.compile(r"\b[A-Za-z]\d{1,3}\b")
LANE = re.compile(r"\blanes?\s+[A-Za-z]\d*\b", re.I)
# a legacy id followed by a dash/colon/period and words: "B12 - cold storage chain"
TITLED = re.compile(r"\b[A-Za-z]\d{1,3}\b\s*[-:\u2013\u2014.]\s*[A-Za-z]{3,}")

REASON = (
    "Blocked: this `Agent` description is, or contains, a bare code ({hit}).\n\n"
    "Codes like C6, A5 or `Lane A2` collide with legacy ledger ids (owner, 2026-10-31: "
    "everyone uses the naming scheme). Use the item ID (SUBJECT_INTENT_TWIST) or plain "
    "words (bug fixes, cold storage chain, review wave, content).\n"
    "Grammar: design/RimMandrake/ticket_naming_2026-10-10.md"
)


def coded(description):
    """The offending text, or ''."""
    text = str(description or "")
    m = LANE.search(text)
    if m:
        return m.group(0)
    for m in CODE.finditer(text):
        if not TITLED.match(text, m.start()):
            return m.group(0)
    return ""


def main():
    try:
        tool_input = json.load(sys.stdin).get("tool_input", {}) or {}
        hit = coded(tool_input.get("description")) if isinstance(tool_input, dict) else ""
    except Exception:
        return 0  # fail open
    if not hit:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": REASON.format(hit=hit)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
