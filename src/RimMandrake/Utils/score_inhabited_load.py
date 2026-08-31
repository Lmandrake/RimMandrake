#!/usr/bin/env python3
"""
score_inhabited_load.py — grade a Player.log against EXPECTED_FAILURES §4.

VERSION 1.0  (2026-08-20)   Project: D:/Luke/dev/Rimworld/src/RimMandrake/Utils/
Dependency-free: Python 3.8+ stdlib only. Keep it that way.

WHAT THIS IS FOR
----------------
`infrastructure/state/EXPECTED_FAILURES_next_load.md` §4 names nine strings that
decide `Inhabited`'s first load — two that MUST be present and seven that must be
absent. They were written before the log existed, which is the whole point:

  🔴 A SIGNATURE INVENTED AFTER READING THE LOG IS NOT EVIDENCE, IT IS A STORY
  THAT FITS.

So they are encoded here rather than re-read by eye, and this tool cannot invent a
tenth one after the fact.

⚠️ ABSENCE OF AN ERROR IS NOT PROOF OF SUCCESS. A mod that never loaded produces
exactly as few errors as one that loaded perfectly. That is why P1 exists and why
this tool FAILS on a missing expected-present string just as hard as on a found
expected-absent one.

⚠️ THIS DOES NOT REPLACE `harvest_log.py`. That one carries every standing check
for the whole stack with measured baselines; run it too. This one answers one
block, so §4's Results table can be filled from output rather than from memory.

USAGE
-----
    python3 src/RimMandrake/Utils/score_inhabited_load.py
    python3 src/RimMandrake/Utils/score_inhabited_load.py --show F4
    python3 src/RimMandrake/Utils/score_inhabited_load.py --log <path>
    python3 src/RimMandrake/Utils/score_inhabited_load.py --markdown   # paste into §4

Exit 0 = every row passed. Exit 1 = at least one row failed or is unproven.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

sys.path.insert(0, HERE)
from game_paths import PLAYER_LOG   # noqa: E402

_LOGS = [PLAYER_LOG]

# Counted on the archived pre-load log named in §4. 25 is the number to beat --
# NOT zero; those 25 predate Inhabited entirely.
#
# ⚠️ It was first written as 33, which was TWO DIFFERENT ERRORS ADDED TOGETHER:
# 25 "Could not resolve cross-reference" (the DEF LOADER, against the live mod set)
# plus 8 "Could not load reference to" (SCRIBE -- the SAVE holds a name no def
# provides, and no mod change fixes it). Summing them would have scored a real
# regression as a pass. Only the first belongs to F7.
CROSSREF_BASELINE = 25

# id, must_be_present, label, regex, note
CHECKS = [
    ("P1", True, "the mod says it is in",
     r"\[Inhabited\] ready: (\d+) patches, (\d+) characters, (\d+) places, (\d+) casts",
     "READ THE COUNTS. 269 characters is the pass. 0 places / 0 casts is CORRECT -- "
     "no place or cast def instance exists yet, that content is blocked on DECIDE."),

    ("P2", True, "the def dump re-took",
     r"\[RimDefDump\]",
     "Enabling Inhabited took the list 577 -> 578, which lapsed the 'dump is "
     "definitive' ruling. The re-take is mandatory, not a bonus. Check the manifest "
     "reports 578, then DELETE dump_request.txt or every future load pays ~27s again."),

    ("F1", False, "assembly did not load",
     r"(?i)(ReflectionTypeLoadException|Could not load assembly).{0,200}Inhabited"
     r"|Inhabited.{0,200}(ReflectionTypeLoadException|Could not load assembly)",
     "CHECK THIS FIRST. If the DLL never loaded, every other row below is meaningless."),

    ("F2", False, "the DutyDef tripwire fired",
     r"Could not find Verse\.DutyDef named Inhabited_Resident|DefOfHelper.{0,200}Inhabited",
     "Duties_Inhabited.xml did not load. InhabitedDefOf names that duty precisely so "
     "a def file that fails to parse is LOUD instead of producing a silently duty-less mod."),

    ("F3", False, "a def names a class the assembly does not expose",
     r"Could not find type named Inhabited\.\w+",
     "F1 in disguise, or a namespace typo in a Defs file."),

    ("F4", False, "a CharacterDef failed its own ConfigErrors",
     r"Config error in Inhabited_\S+",
     "THE MOST LIKELY SINGLE FAILURE IN THIS BLOCK: all 807 traits were resolved "
     "against a 577-mod dump and the live set is 578. The defName in the message "
     "names the person. Fix by re-running cast_to_xml.py against the NEW dump."),

    ("F5", False, "a Harmony target moved",
     r"mandrake\.inhabited.{0,300}(Exception|HarmonyException|patch)"
     r"|(Exception|HarmonyException).{0,300}mandrake\.inhabited",
     "SHOULD BE IMPOSSIBLE -- both targets are bound to a delegate of the same "
     "signature at compile time, so a moved target fails the BUILD. If this fires, "
     "that proof was wrong and it is the more interesting finding."),

    ("F6", False, "a generated roster file is malformed",
     r"CastRoster_\w*.{0,200}(XML error|Exception|could not|failed)"
     r"|(XML error|Exception loading).{0,200}CastRoster_",
     "All eleven parse under Python. This would mean RimWorld's parser disagrees."),
]


def die(msg):
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(2)


def find_log(explicit):
    if explicit:
        if not os.path.isfile(explicit):
            die("no log at " + explicit)
        return explicit
    for p in _LOGS:
        if os.path.isfile(p):
            return p
    die("no Player.log found; tried:\n  " + "\n  ".join(_LOGS))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="path to Player.log")
    ap.add_argument("--show", help="print the matching lines for one row id, e.g. F4")
    ap.add_argument("--markdown", action="store_true",
                    help="emit the Results table rows to paste into EXPECTED_FAILURES §4")
    args = ap.parse_args()

    path = find_log(args.log)
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()

    print("log: %s  (%d lines)" % (path, len(lines)))

    # Provenance. A log that does not mention the mod at all is far more likely to
    # be the PREVIOUS session's than a catastrophic failure, and reporting the
    # second when it is the first wastes a load round.
    if not any("mandrake.rm.inhabited" in ln or "[Inhabited]" in ln
               or "Inhabited" in ln for ln in lines[:4000]):
        print("⚠️  no mention of Inhabited in the first 4000 lines -- is this the "
              "log from THIS launch? Player.log is rotated, not appended.")

    results = {}
    failures = 0

    for cid, must_present, label, pattern, note in CHECKS:
        rx = re.compile(pattern)
        hits = [(i + 1, ln) for i, ln in enumerate(lines) if rx.search(ln)]
        results[cid] = hits

        if args.show and args.show.upper() == cid:
            print("\n--- %s: %s ---" % (cid, label))
            for n, ln in hits[:60]:
                print("  %6d  %s" % (n, ln.strip()[:200]))
            if not hits:
                print("  (no matching lines)")
            return 0

        if must_present:
            ok = bool(hits)
            mark = " ok " if ok else "FAIL"
            detail = ("line %d" % hits[0][0]) if ok else "NOT FOUND -- expected present"
        else:
            ok = not hits
            mark = " ok " if ok else "FAIL"
            detail = "clean" if ok else ("%d hit(s), first at line %d" % (len(hits), hits[0][0]))

        if not ok:
            failures += 1
        print(" [%s] %-3s %-46s %s" % (mark, cid, label, detail))
        if not ok:
            print("        %s" % note)
        if cid == "P1" and hits:
            m = re.search(CHECKS[0][3], hits[0][1])
            if m:
                pa, ch, pl, ca = (int(x) for x in m.groups())
                verdict = "PASS" if ch == 269 else "SHORT BY %d" % (269 - ch)
                print("        counts: %d patches, %d characters (%s), %d places, %d casts"
                      % (pa, ch, verdict, pl, ca))
                if ch != 269:
                    failures += 1
                    print("        🔴 269 is the pass. A lower count means def files "
                          "failed to parse, and the number says how many.")

    # F7 is a baseline comparison, not a presence test.
    n_crossref = sum(1 for ln in lines if "Could not resolve cross-reference" in ln)
    trait_hits = [(i + 1, ln) for i, ln in enumerate(lines)
                  if "Could not resolve cross-reference" in ln and "TraitDef" in ln]
    if args.show and args.show.upper() == "F7":
        for n, ln in trait_hits[:60]:
            print("  %6d  %s" % (n, ln.strip()[:200]))
        return 0
    f7_ok = not trait_hits and n_crossref <= CROSSREF_BASELINE
    if not f7_ok:
        failures += 1
    print(" [%s] F7  %-46s %d cross-ref lines (baseline %d), %d naming a TraitDef"
          % (" ok " if f7_ok else "FAIL", "cross-references", n_crossref,
             CROSSREF_BASELINE, len(trait_hits)))
    if n_crossref < CROSSREF_BASELINE:
        print("        BETTER than baseline -- that is a docs update, not a pass to ignore.")

    if args.markdown:
        print("\n--- paste into EXPECTED_FAILURES §4 Results ---")
        for cid, must_present, label, _p, _n in CHECKS:
            hits = results[cid]
            if must_present:
                out = ("present, line %d" % hits[0][0]) if hits else "**MISSING**"
            else:
                out = "clean" if not hits else "**%d hit(s), line %d**" % (len(hits), hits[0][0])
            print("| %s | %s | |" % (cid, out))
        print("| F7 | %d cross-ref, %d TraitDef | baseline %d |"
              % (n_crossref, len(trait_hits), CROSSREF_BASELINE))

    print("\n%s" % ("ALL ROWS PASSED" if failures == 0
                    else "%d ROW(S) FAILED OR UNPROVEN" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
