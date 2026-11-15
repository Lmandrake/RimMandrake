#!/usr/bin/env python3
# selftest-timeout: 30
"""Another mod's dropped live cord is not an overhead line: the overhead-lines master switch must not silence it.

Bars shock_reach_setting ("under Only downed lines the fallen wire and the dropped deck cord bite"; the delegated detail
"Only downed lines keeps FlowWorks' dropped bridge-deck cords biting") and settings_switch_cleanly ("flips each feature
switch ... and sees just that feature change"). Found by the blind challenge of 2026-11-15
(RIMMANDRAKE_UNGATE_GSS_DROPPED_CORDS_FROM_OVERHEAD_MASTER): RM_FallenWireShock.RebuildContacts returned before
ExternalContacts when AerialSettings.enabled was off, and CheckPawns returned on the same switch, so with overhead lines off a
collapsed FlowWorks bridge deck's live cord neither bit nor lit fuel.

RM_FallenWireShock is Verse-bound, so this reads its source. Checks:
  C1 RebuildContacts reaches ExternalContacts with the master off (no early return on !AerialSettings.enabled);
  C2 our own aerial strands are still gated on the master inside RebuildContacts;
  C3 CheckPawns has no early return on !AerialSettings.enabled;
  C4 CheckPawns still skips a downed-span contact while the master is off (stale contacts after a flip).
Mutants: the old gate put back in RebuildContacts, and in CheckPawns, must each go red; the shipped text must read green.
Exit 0 green, 1 red, 2 instrument broke (a mutant that did not apply or did not go red).
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "Source" / "Aerial" / "RM_FallenWireShock.cs"


def body(text, name):
    """The brace-matched body of the first method called name."""
    m = re.search(r"public static void " + name + r"\s*\(", text)
    if not m:
        return None
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        depth += {"{": 1, "}": -1}.get(text[j], 0)
        if depth == 0:
            return text[i:j + 1]
    return None


def strip_comments(t):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", t, flags=re.S)


EARLY = re.compile(r"if\s*\([^;{]*!\s*AerialSettings\.enabled[^;{]*\)\s*return\s*;")


def checks(text):
    """name -> (ok, why) over one copy of the source."""
    t = strip_comments(text)
    rb, cp = body(t, "RebuildContacts"), body(t, "CheckPawns")
    if rb is None or cp is None:
        return None
    ext = rb.find("ExternalContacts(")
    before = rb[:ext] if ext >= 0 else rb
    return {
        "C1_rebuild_reaches_external_with_master_off": (ext >= 0 and not EARLY.search(before), "an early return on the master before ExternalContacts"),
        "C2_own_spans_still_gated": (bool(re.search(r"if\s*\(\s*AerialSettings\.enabled\s*\)", before)), "the aerial strand loop is not under the master"),
        "C3_checkpawns_no_master_return": (not EARLY.search(cp), "CheckPawns returns on the master"),
        "C4_checkpawns_skips_stale_span": (bool(re.search(r"LineKind\.DownedSpan\s*&&\s*!\s*AerialSettings\.enabled", cp)), "a downed-span contact is not skipped with the master off"),
    }


def main():
    text = SRC.read_text(encoding="utf-8")
    got = checks(text)
    if got is None:
        print("UNMEASURED: RebuildContacts or CheckPawns not found in", SRC)
        return 2
    ok = True
    for name, (good, why) in got.items():
        print(("PASS  " if good else "FAIL  ") + name + ("" if good else "  [%s]" % why))
        ok &= good
    # mutants: the old gates put back must read red (so this test can fail)
    mutants = {
        "M1_old_rebuild_gate": (r"(public static void RebuildContacts\([^{]*\{)", r"\1\n            if (!AerialSettings.enabled) return;"),
        "M2_old_checkpawns_gate": (r"(public static void CheckPawns\([^{]*\{)", r"\1\n            if (contacts.Count == 0 || !AerialSettings.enabled) return;"),
    }
    for name, (pat, rep) in mutants.items():
        mt, n = re.subn(pat, rep, text, count=1)
        res = checks(mt) if n == 1 else None
        if res is None:
            print("UNMEASURED  %s did not apply" % name)
            return 2
        red = not all(g for g, _ in res.values())
        print(("PASS  " if red else "FAIL  ") + name + " reads red")
        ok &= red
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
