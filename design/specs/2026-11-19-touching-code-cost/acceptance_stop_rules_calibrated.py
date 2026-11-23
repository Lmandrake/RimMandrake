#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_CALIBRATE_JUDGE_STOP_RULES_WORDS_UNTIL_RUN.

Each judging brief that got a stopping level on 2026-11-19 (standing_rulings.md §Touching code has a cost; if you see
it, do it) is listed in a family of infrastructure/state/judge_calibration.json whose status, read by
refusal_contract.status() at the brief's current hash, is CALIBRATED. The art judge brief also carries its stop rule.

Expected on a correct result: PASS 6/6. On the base (2026-11-19, the filing commit) it reads FAIL with 0 or 1 of 7 (the retired Auditor's brief was the seventh until 2026-11-23).
Exit 0 all pass; 1 any check fails; 3 the registry or refusal_contract could not be read (no score is printed).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BRIEFS = [
    "src/RimMandrake/rimflow/roles/operations.md",
    "src/RimMandrake/Utils/findings_judge_prompt.md",
    "design/RimMandrake/scene_look_judge_brief.md",
    ".claude/agents/rm-judge.md",
    "design/RimMandrake/art_judge_brief.md",
]
ART_STOP = "## When the look is enough"


def main():
    try:
        sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "rimflow"))
        import refusal_contract as RC
        fams = RC.load_calibration()["families"]       # the registry and root refusal_contract itself reads
        with open(os.path.join(RC.calibration_root(), "design", "RimMandrake", "art_judge_brief.md"),
                  encoding="utf-8") as fh:
            art = fh.read()
    except Exception as e:  # noqa: BLE001 - could not look is its own answer, never a score
        print("UNMEASURED: %s: %s" % (type(e).__name__, e))
        return 3
    ok = 0
    for b in BRIEFS:
        hits = [f for f, row in fams.items() if b in (row.get("brief") or [])]
        st = {f: RC.status(f) for f in hits}
        good = any(s == "CALIBRATED" for s in st.values())
        ok += good
        print("%s  %s  %s" % ("ok  " if good else "FAIL", b, st or "in no family"))
    good = ART_STOP in art
    ok += good
    print("%s  art_judge_brief.md carries %r" % ("ok  " if good else "FAIL", ART_STOP))
    n = len(BRIEFS) + 1
    print("%s %d/%d" % ("PASS" if ok == n else "FAIL", ok, n))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
