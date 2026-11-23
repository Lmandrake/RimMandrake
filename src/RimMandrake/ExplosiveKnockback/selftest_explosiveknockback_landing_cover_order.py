#!/usr/bin/env python3
"""A thrown pawn breaks the pit cover it lands on AFTER every other landing hook has run (visit 4, 2026-11-23).

Live on the parent build, sc_pit_fall's solo lane read descents=2 in 3 of 3 runs: our RespawnPawn postfix broke the cover
(FlowWorks drops the pawn: fall one), then FlowWorks' own landing postfix saw the now-open pit under the same pawn and
dropped it again (fall two, hurt twice). So the break is its own postfix at Priority.Last, in no other postfix.
    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_landing_cover_order.py [--file PATH]
Exit 0 only when every row holds. The planted rows show each can fail.
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source", "RM_PawnFlyerPatches.cs")


def strip(s):
    return re.sub(r"//[^\n]*", "", s)


def check(text):
    t = strip(text)
    out = []
    calls = [m.start() for m in re.finditer(r"(?<!void )\bBreakCoverUnderLanding\(", t)]
    out.append(("one caller", len(calls) == 1))
    posts = []
    for m in re.finditer(r"((?:\[[^\]\n]*\]\s*)*)public static void Postfix\([^)]*\)\s*\{", t):
        depth, i = 1, m.end()
        while depth and i < len(t):
            depth += {"{": 1, "}": -1}.get(t[i], 0)
            i += 1
        posts.append((m.group(1), m.start(), i))
    mine = [p for p in posts if any(p[1] <= c < p[2] for c in calls)]
    out.append(("the caller is a Postfix", len(mine) == 1))
    out.append(("that Postfix is Priority.Last", bool(mine) and "HarmonyPriority(Priority.Last)" in mine[0][0]))
    body = t[mine[0][1]:mine[0][2]] if mine else ""
    out.append(("that Postfix does nothing else (the landing's resume keeps its own order)",
                bool(mine) and "Resume(" not in body and "Landed(" not in body))
    return out


def main():
    path = sys.argv[sys.argv.index("--file") + 1] if "--file" in sys.argv else SRC
    text = open(path, encoding="utf-8-sig").read()
    rows = check(text)
    plants = [("priority dropped", text.replace("[HarmonyPriority(Priority.Last)]", "")),
              ("also called by the landing postfix", text.replace("            Landed(__state?.pawn);",
                                                                  "            Landed(__state?.pawn);\n            BreakCoverUnderLanding(__state?.pawn);"))]
    for name, bad in plants:
        rows.append(("planted: %s is seen" % name, bad != text and not all(ok for _, ok in check(bad))))
    for name, ok in rows:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    bad = sum(not ok for _, ok in rows)
    print("landing cover order: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
