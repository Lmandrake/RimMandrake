#!/usr/bin/env python3
"""FLOWWORKS_CLIMBERS_REWIRE_NAMES_THAT_LEFT: every one of OUR defNames (RM_, RSW_, RUT_) that
Patches/Canals/FlowWorks_LadderClimbers.xml names is a ThingDef defined somewhere under src/.

Why: a patch that matches nothing logs nothing (CLAUDE.md). When a creature moves tier (RSW_X -> RM_X) the old name
in the climber list silently stops matching, and that creature never gets its ladder traits. Third-party names
(GR_, VGE_, ...) are not checked here: their defs are not in this repo.

Exit 0: every name of ours matches a def. Exit 1: names that match nothing, each with the twin that does exist.
Exit 2: could not look (the patch or src/ is missing, or no defName was read).
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PATCH = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "Patches", "Canals", "FlowWorks_LadderClimbers.xml")
OURS = re.compile(r"^(RM|RSW|RUT)_")


def defined_names(src_root):
    names = set()
    for root, dirs, files in os.walk(src_root):
        dirs[:] = [d for d in dirs if d not in ("obj", "bin", ".git", "art_source")]
        for f in files:
            if f.endswith(".xml"):
                with open(os.path.join(root, f), encoding="utf-8", errors="ignore") as fh:
                    names.update(re.findall(r"<defName>\s*([^<\s]+)\s*</defName>", fh.read()))
    return names


def main():
    if not os.path.isfile(PATCH):
        print("COULD NOT LOOK: %s is missing" % PATCH)
        return 2
    with open(PATCH, encoding="utf-8") as fh:
        named = sorted(set(re.findall(r'defName="([^"]+)"', fh.read())))
    ours = [n for n in named if OURS.match(n)]
    have = defined_names(os.path.join(ROOT, "src"))
    if not ours or len(have) < 100:
        print("COULD NOT LOOK: %d names of ours in the patch, %d defs read under src/" % (len(ours), len(have)))
        return 2
    bad = []
    for n in ours:
        if n not in have:
            base = OURS.sub("", n)
            twins = [p + "_" + base for p in ("RM", "RSW", "RUT") if p + "_" + base in have]
            bad.append("%s matches no def (twin: %s)" % (n, ", ".join(twins) or "none"))
    if bad:
        print("FAIL: %d of %d names of ours match no def" % (len(bad), len(ours)))
        for b in bad:
            print("  " + b)
        return 1
    print("PASS: %d of %d names of ours match a def" % (len(ours), len(ours)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
