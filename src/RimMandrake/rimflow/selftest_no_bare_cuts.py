#!/usr/bin/env python3
"""selftest_no_bare_cuts.py -- no new silent cut of stored text (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS).

Owner, 2026-11-12, when 687 of 813 stored judge refusals ended at character 600: "WHY would anything cut off text at
600 characters?! please get rid of these arbitrary cuts!" Every such cut in rimflow was removed or routed through
`fulltext.fit` (a real bound: whole text to a side file, pointer + full length in the field) or `fulltext.clip`
(a display line that says it is cut and where the rest is). Census:
D:\\ClaudeWork\\rimmandrake\\refusal_contract\\truncation_census.md

This lint fails on a bare literal slice of 3+ digits (`x[:600]`, `x[-1500:]`) or a NOTE_MAX/SUMMARY_MAX slice in the
scanned files (rimflow and every Utils tool). A slice that is not a text cut (a list, a dedup key, a filename, a search window) carries
`# cut-ok: <why>` on its line. Selftests are not scanned (they build long strings on purpose).

OWED: designer_stage.py, coverage_judge.py, refusal_contract.py and evidence_gate.py were being rebuilt by another
helper (refusal-contract T1-T3) and are not scanned yet; their sites are listed in the census. Two-digit slices
(`[:80]`) are not caught: most are ids, slugs and hashes, and a pass over them is owed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(os.path.dirname(HERE), "Utils")

CUT = re.compile(r"\[\s*:\s*(\d{3,}|NOTE_MAX|SUMMARY_MAX)\b[^\]]*\]|\[\s*-\s*(\d{3,})\s*:\s*\]")
SKIP = {"fulltext.py", "designer_stage.py", "coverage_judge.py", "refusal_contract.py", "evidence_gate.py"}
# Utils: every tool, fixed in the same pass (its evidence, verdicts, refusals, notes and reports are stored whole too).
SCAN_UTILS = True


def scan_text(text, name):
    """-> ["name:line: source"] for every bare cut in `text`."""
    bad = []
    for n, line in enumerate(text.splitlines(), 1):
        code = "" if "cut-ok:" in line else re.sub(r"(^|\s)#(\s.*)?$", "", line)   # drop a trailing comment
        if not code:
            continue
        for m in CUT.finditer(code):
            if "fulltext." in code[max(0, m.start() - 200):m.start()]:
                continue
            bad.append("%s:%d: %s" % (name, n, line.strip()[:160]))   # cut-ok: a lint report line
            break
    return bad


def targets():
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".py") and not f.startswith("selftest_") and f not in SKIP:
            yield os.path.join(HERE, f)
    if SCAN_UTILS:
        for f in sorted(os.listdir(UTILS)):
            if f.endswith(".py") and not f.startswith(("selftest_", "test_")):
                yield os.path.join(UTILS, f)


def main():
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        print("%s  %s%s" % ("PASS" if cond else "FAIL", name, ("  " + str(detail)) if detail and not cond else ""))
        fails += 0 if cond else 1

    # the instrument can see: a planted cut is caught, a marked or routed one is not
    planted = 'rec["detail"] = why[:600]\nrec["why"] = text[-1500:]\nnote = s[:NOTE_MAX]\n'
    check("planted bare cuts are caught (3 of 3)", len(scan_text(planted, "planted")) == 3, scan_text(planted, "planted"))
    fine = ('keys = sorted(names)[:200]  # cut-ok: a list\n'
            'rec["detail"] = fulltext.fit(why, 600)\n'
            'h = sha[:12]\n'
            '# an old comment said [:600]\n')
    check("cut-ok, fulltext.fit, short slices and comments pass", scan_text(fine, "fine") == [], scan_text(fine, "fine"))

    bad = []
    n = 0
    for p in targets():
        n += 1
        with open(p, encoding="utf-8") as f:
            bad += scan_text(f.read(), os.path.relpath(p, os.path.dirname(HERE)))
    check("scanned files are many (instrument sees the tree)", n >= 250, n)
    check("no bare cut of stored text (%d files)" % n, not bad, "\n  " + "\n  ".join(bad))
    print("%d fail(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
