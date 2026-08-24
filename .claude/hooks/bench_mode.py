#!/usr/bin/env python3
"""BENCH mode delivery — UserPromptSubmit.

🔴 WHY THIS EXISTS. Doctrine written to POLICY.md reaches a seat only when it WAKES,
and seats run for hours. BENCH is the one rule that must arrive the instant the owner
speaks, in a window that has been awake since morning — and no agent may message
another, so nothing else can carry it. This hook is the delivery route: he says he is
here, and the rulebook lands in that window's context on that turn.

It reads the BENCH page out of `infrastructure/agents/POLICY.md` rather than carrying a
copy, so the two can never drift. Filed 2026-08-23 under TRIM_VALIDATION_LAYERS_1.

⚠️ Prints nothing on an ordinary prompt — every turn pays this, so it stays cheap.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "infrastructure" / "agents" / "POLICY.md"

# He does not type a command. These are the ways he actually says it.
# ⚠️ Widened 2026-08-23 after a real miss: he wrote "I want to go into Bench now" and
# the pattern only knew "go to bench", so the rulebook never landed and the window ran
# a BENCH turn on BELT rules. A false positive here costs one extra print of a page he
# asked for; a false negative costs the whole mode. Lean permissive.
ARRIVE = re.compile(
    r"\b(i'?m here|i am here|on the bench|in the bench|bench mode|"
    r"(go|going|get|getting|switch|switching|move|moving|drop|put me|jump)\s+"
    r"(in)?to\s+(the\s+)?bench|"
    r"bench\s+(now|please)|(into|onto)\s+bench|"
    r"run with (this|it)|let'?s knock (this|it) out|work with me)\b", re.I)
DEPART = re.compile(
    r"\b(stepping away|step away|back to normal|you'?re on your own|"
    r"i'?m off|heading out|going afk|afk now|leaving now|off the bench)\b", re.I)


def bench_page() -> str:
    """The BENCH section of POLICY.md, verbatim. Empty string if it is gone."""
    try:
        text = POLICY.read_text(encoding="utf-8")
    except OSError:
        return ""
    start = text.find("## 🔴 BENCH")
    if start < 0:
        return ""
    nxt = text.find("\n## ", start + 1)
    return text[start:nxt if nxt > 0 else len(text)].strip()


def main() -> int:
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
    except Exception:
        return 0
    if DEPART.search(prompt):
        print("🔻 OFF THE BENCH — he is leaving. Before you rejoin the BELT: anything you "
              "started together and did not finish becomes a normal item (`rimflow file`), "
              "named in ONE line. Then work the queue as usual. Do not hold for an answer.")
        return 0
    if ARRIVE.search(prompt):
        page = bench_page()
        if page:
            print("🪑 HE IS AT THE BENCH. This rulebook is in force for this window, NOW — "
                  "it replaces the process in POLICY.md until he leaves.\n\n" + page)
        else:
            print("🪑 HE IS AT THE BENCH, but the BENCH page is missing from "
                  "infrastructure/agents/POLICY.md — say so in one line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
