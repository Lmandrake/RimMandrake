#!/usr/bin/env python3
"""Source pins for the ExplosiveGrowth fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/ExplosiveGrowth_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by reverting the line by hand, 2026-10-16).

    python3 src/RimMandrake/ExplosiveGrowth/selftest_explosivegrowth_gpt_fixes.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def main():
    mc = read("RM_MapComponent_ExplosiveGrowth.cs")
    expose = method_body(mc, "public override void ExposeData()")
    check("sanity: map component ExposeData found", "Scribe_Collections.Look(ref ruptures" in expose)
    # EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS
    for f in ("nextPassTick", "lastPassTick"):
        check("EGROWTH_RELOAD_FIX_FREE_CHARGE_PASS: %s scribed with default -1" % f,
              re.search(r'Scribe_Values\.Look\(ref %s, "%s", -1\);' % (f, f), expose) is not None)
    if fails:
        print("FAIL: %d failed" % len(fails))
        return 1
    print("PASS: 0 failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
