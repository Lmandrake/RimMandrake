#!/usr/bin/env python3
"""PreToolUse/Bash hook — BLOCKS a commit whose design doc contradicts canon.yml.

WHY THIS ONE BLOCKS WHEN ITS SIBLINGS ONLY WARN
===============================================
A 2026-08-20 audit of the 119-document design tier found 21 numbers asserted at two or
more different values, in files that all read as current. Water was 25%, 22–28%, 8.6%,
8.1% and 6.9%. Factions were 14, 13, 12 and 11. None of it was carelessness — every
document was written by someone who had measured something — and it took ten agents a
full pass to reconcile.

⚠️ The cost is asymmetric, which is what earns the block. A contradiction costs seconds
to fix at commit time and a day to find later, because by then it has been quoted
forward into three more documents by people with no reason to doubt it. `Lake` was cut
in one file and load-bearing in five; the terminator was +14 in one and −37 in another,
and both were right about different things that nobody had said out loud.

⛔ IT BLOCKS ONLY ON A HARD CONTRADICTION. `check_canon.py` classifies undated mod
counts as ADVISORY and never fails on them: every one of the twenty was true the day it
was written, and the defect is the missing date, not the number.

THE ESCAPE HATCH IS PART OF THE DESIGN
======================================
A doc that genuinely must state a value canon disagrees with says so:

    <!-- canon-ok: quoting the dead worldgen_sea_spec on purpose -->

on the line or the line above. ⚠️ A block with no escape is a block that gets disabled,
and a disabled hook protects nothing. Requiring a REASON is the point — it converts a
silent contradiction into a sentence someone wrote deliberately.

Fail-open, stdlib only in the hook itself. ⚠️ `check_canon.py` imports PyYAML; if it is
missing the checker exits 2 and this hook ALLOWS, because UNMEASURED is not the same as
FAILED and refusing to commit over a missing dependency helps nobody.

    python3 .claude/hooks/selftest_block_canon_contradiction.py
"""
import json
import os
import re
import subprocess
import sys


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (ev.get("tool_input") or {}).get("command") or ""
    if "git" not in cmd or "commit" not in cmd:
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    paths = [p for p in re.findall(r"[\w./-]+\.md", cmd) if p.startswith("design/")]
    if not paths:
        return 0
    exists = [p for p in paths if os.path.exists(os.path.join(root, p))]
    if not exists:
        return 0

    tool = os.path.join(root, "src", "RimMandrake", "Utils", "check_canon.py")
    if not os.path.exists(tool):
        return 0
    try:
        r = subprocess.run([sys.executable, tool, *exists], capture_output=True,
                           text=True, cwd=root, timeout=60)
    except Exception:
        return 0                                   # fail open
    if r.returncode != 1:
        # 0 = clean. 2 = could not measure (no PyYAML). Neither is a contradiction.
        return 0

    body = "\n".join(l for l in r.stdout.splitlines()
                     if l.strip() and not l.startswith("advisory"))
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Blocked: a design doc in this commit contradicts "
            "infrastructure/state/canon.yml.\n\n%s\n\n"
            "Canon holds ONE traceable value per contested number, each with the "
            "measurement or ruling behind it. A contradiction costs seconds to fix now "
            "and a day to find later, because by then it has been quoted forward into "
            "other documents by people with no reason to doubt it.\n\n"
            "Three ways out, in order of how often each is right:\n"
            "  1. The doc is wrong  -> fix the number. Strike the old one through with "
            "a date rather than deleting it; never lose the history of a number.\n"
            "  2. The doc is QUOTING a dead value on purpose -> mark the line:\n"
            "         <!-- canon-ok: why this line states it -->\n"
            "  3. CANON is wrong -> fix canon.yml, with a `src:` for the new value, "
            "and record the loser under `superseded:`.\n\n"
            "    python3 src/RimMandrake/Utils/check_canon.py --list"
            "\n\n\u26a0\ufe0f  NOTHING IN THAT COMMAND RAN \u2014 including anything BEFORE the "
            "part that was\nrefused. A PreToolUse hook fires before the shell, so a compound "
            "command is refused\nwhole. If you chained a file write to a commit, the write did "
            "not happen either." % body[:2500])}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
