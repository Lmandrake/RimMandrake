#!/usr/bin/env python3
"""Guard: the art judge applies ONE outline rule, and it is "no outlines".

Owner card 2026-10-04 (ART_VERSION_WRANGLING_1) retired the 2026-09-14
"clean black outline" clause; common.HOUSE_ART_REGISTER says "no outlines".
ART_JUDGE_FIX_KEYLINE_BRIEF_DISAGREEMENT found the judge brief (B1, B2) still
asking for an outline/keyline and art_checks.outline_coherence flagging the
keyline-free regens the art_eval compare had correctly picked (Ullai,
Emberscythe, 2026-10-23). This test fails if either half comes back.

    python3 src/RimMandrake/Utils/selftest_art_judge_no_keyline.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BRIEF = REPO / "design/RimMandrake/art_judge_brief.md"
TEX = REPO / "src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands"
REGENS = ("Ullai", "Emberscythe")   # keyline-free art_eval picks, 2026-10-23

# A clause that ASKS for a line. Negations ("no outlines", "not a keyline") are fine.
DEMAND = re.compile(
    r"\b(?:with|carr(?:y|ies)|needs?|requires?|must(?:\s+have)?|should(?:\s+have)?|wants?|draws?"
    r"|asks?\s+for|clean|bold|thick|dark|black)[\s,]+(?:a\s+|an\s+)?(?:\d+\s*px\s+)?"
    r"(?:clean[\s,]+)?(?:bold[\s,]+)?(?:dark[\s,]+)?(?:black\s+)?(?:outlines?|keylines?)\b"
    r"|\boutlined\s+in\b", re.I)
# A demand preceded, within the same clause, by one of these is a prohibition.
NEGATION = re.compile(r"\b(?:no|not|never|without|nor)\b[^.;:]{0,30}$", re.I)


def demands(body: str) -> list:
    return [m.group(0) for m in DEMAND.finditer(body)
            if not NEGATION.search(body[max(0, m.start() - 40):m.start()])]


def _style_rules(text: str) -> dict:
    """{'A1': '...', 'B1a': '...', ...}: every numbered rule bullet in the brief."""
    rules, cur = {}, None
    for line in text.splitlines():
        h = re.match(r"- ([A-Z]\d+[a-z]?)\. ", line)
        if h:
            cur = h.group(1)
            rules[cur] = line
        elif cur and line.startswith("  "):
            rules[cur] += " " + line.strip()
        else:
            cur = None
    return rules


def main() -> int:
    fails = []
    rules = _style_rules(BRIEF.read_text(encoding="utf-8"))
    if "B1" not in rules or "B2" not in rules:
        fails.append("could not parse B1/B2 out of %s; the parser is blind, not passing" % BRIEF)
    for rid, body in rules.items():
        for hit in demands(body):
            fails.append("%s asks for an outline/keyline: %r" % (rid, hit))
    if not any("no outlines" in b.lower() and "2026-10-04" in b for b in rules.values()):
        fails.append("no style rule states 'No outlines' citing the 2026-10-04 card")

    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE / "artpipe"))
    import art_checks  # noqa: E402
    if hasattr(art_checks, "outline_coherence"):
        fails.append("art_checks.outline_coherence exists again: it enforces the retired keyline rule")
    import artpiped  # noqa: E402
    if any("outline" in c or "keyline" in c for c in artpiped.FACTS_SINGLE_FILE_CHECKS):
        fails.append("artpiped.FACTS_SINGLE_FILE_CHECKS names an outline check: %r"
                     % (artpiped.FACTS_SINGLE_FILE_CHECKS,))

    files = [p for c in REGENS for p in sorted((TEX / c).glob(c + "_*.png"))]
    if len(files) < len(REGENS):
        fails.append("found %d regen facings under %s; the instrument cannot see them" % (len(files), TEX))
    else:
        found = art_checks.run([str(p) for p in files])
        bad = [f for f in found if re.search("outline|keyline", f.check + " " + f.detail, re.I)]
        if bad:
            fails.append("keyline findings on keyline-free regens: %s"
                         % ", ".join("%s:%s" % (f.subject, f.check) for f in bad))
        print("checked %d facings of %s: %d findings, 0 may be about outlines"
              % (len(files), "/".join(REGENS), len(found)))

    for f in fails:
        print("FAIL  " + f)
    if fails:
        return 1
    print("PASS  judge brief and art_checks agree: no outlines (owner card 2026-10-04)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
