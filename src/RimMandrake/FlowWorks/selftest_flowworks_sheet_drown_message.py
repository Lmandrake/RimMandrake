#!/usr/bin/env python3
"""OVERFLOW_DROWNING_FIX_NO_WARNING (offline, no game): a pawn drowning in spilled sheet water on undug soil gets the
"X is drowning." message whether deep swimming is on or off.

RM_Swim.Tick skips a pawn on undug, non-water terrain with no exhaustion ("the common case: dry ground"), and its water
read (RM_SwimWater.WaterMetresAt) never sees the sheet, so it cannot send the message there. The sheet branch of
RM_PitFillEffects.Tick added the drowning but sent the message only when swimming was OFF: with the shipped default (on)
the pawn drowned silently. The branch now sends it unconditionally (DrownMessage throttles per pawn, so no double).

Each check fails on the pre-fix code; the planted regression (the old guard put back) must fail (can-fail).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def sheet_branch(fe):
    """The undug-cell (sheet water) branch of RM_PitFillEffects.Tick, up to its `continue;`."""
    i = fe.find("int sdl = Sheet.RM_MapComponent_Sheet.StandingDlAt(map, c);")
    if i < 0:
        return ""
    j = fe.find("continue;", i)
    return fe[i:j] if j > 0 else ""


def verdict(fe, sw):
    """Return the list of failed clause names for this pair of sources."""
    bad = []
    br = sheet_branch(fe)
    code = "\n".join(l.split("//")[0] for l in br.splitlines())   # comments do not count
    if "HealthUtility.AdjustSeverity(p, drowning, sadd);" not in code:
        bad.append("sheet branch adds drowning")
    if "Swimming.RM_Swim.DrownMessage(p);" not in code:
        bad.append("sheet branch sends the message")
    if re.search(r"RM_SwimWater\.On", code):
        bad.append("no swimming guard on the sheet message")
    if "if (exh == null && !dug && (t == null || !t.IsWater))" not in sw:
        bad.append("premise: RM_Swim.Tick skips undug dry soil (if it stops, revisit)")
    if "Sheet" in "".join(l.split("//")[0] for l in body(sw, "static float WaterMetresAt").splitlines()):
        bad.append("premise: the swim water read ignores the sheet (if it stops, revisit)")
    return bad


def body(src, sig):
    i = src.find(sig)
    if i < 0:
        return ""
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    return ""


def main():
    fe = read("RM_PitFillEffects.cs")
    sw = read(os.path.join("Swimming", "RM_Swim.cs"))
    bad = verdict(fe, sw)
    for name in ("sheet branch adds drowning", "sheet branch sends the message", "no swimming guard on the sheet message",
                 "premise: RM_Swim.Tick skips undug dry soil (if it stops, revisit)",
                 "premise: the swim water read ignores the sheet (if it stops, revisit)"):
        check(name, name not in bad)
    # can-fail: put the pre-fix guard back into the sheet branch; the check must notice
    planted = fe.replace("Swimming.RM_Swim.DrownMessage(p);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t\tcontinue;",
                         "if (!Swimming.RM_SwimWater.On) { Swimming.RM_Swim.DrownMessage(p); }\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t\tcontinue;", 1)
    check("can-fail: planted swimming-off guard is caught", planted != fe and "no swimming guard on the sheet message" in verdict(planted, sw))
    if FAILS:
        print("FAIL %d: %s" % (len(FAILS), ", ".join(FAILS)))
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
