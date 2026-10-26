#!/usr/bin/env python3
"""Offline selftest: with the Star Wars tier loaded no Fever Wood def still says "sekkulaath" to the player
(FEVERWOOD_DIANOGA_GIANT_MAP_1, DIANOGA_FIX_YOUNGCASK_LABEL_LEFTOVER).
    python3 src/RimStarWars/SWBestiary/selftest_dianoga_reskin_coverage.py [--patch PATH ...]

1. Every label / labelPlural / description / labelNoun / jobString / reportString node in
   src/RimMandrake/FeverWood/Defs whose text contains "sekkulaath" must be the xpath target
   `[defName="X"]/<tag>` of an op in a src/RimStarWars/**/Patches file (or a --patch copy).
   RM_SekkulaathYoungCask was added after the reskin and kept "sekkulaath young-cask".
   Top-level fields only; the 2026-10-26 live dump scan of every player-facing string found no nested leftover.
2. The instrument can see: >= 5 such nodes found, the tank and juvenile labels among them.
--patch replaces the default patch set (e.g. `git show <old>:...DianogaGiant.xml` plus the tank swap -> red).
"""
import argparse
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FW_DEFS = os.path.join(REPO, "src", "RimMandrake", "FeverWood", "Defs")
SW_PATCHES = glob.glob(os.path.join(REPO, "src", "RimStarWars", "**", "Patches", "**", "*.xml"), recursive=True)
TAGS = ("label", "labelPlural", "description", "labelNoun", "jobString", "reportString")
PROBE = (("RM_SekkulaathTank", "label"), ("RM_Sekkulaath_Juvenile", "label"))
TARGET_RE = re.compile(r'\[defName="([^"]+)"\]/(\w+)\s*<')


def leftovers():
    out = set()
    for p in glob.glob(os.path.join(FW_DEFS, "**", "*.xml"), recursive=True):
        try:
            root = ET.parse(p).getroot()
        except ET.ParseError:
            continue
        for el in root:
            dn = el.findtext("defName")
            if not dn:
                continue
            for tag in TAGS:
                t = el.findtext(tag)
                if t and "sekkulaath" in t.lower():
                    out.add((dn, tag))
    return out


def targeted(paths):
    out = set()
    for p in paths:
        raw = open(p, encoding="utf-8", errors="replace").read()
        out.update(TARGET_RE.findall(raw.replace("</xpath>", "<")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append")
    a = ap.parse_args(argv)
    fails = []
    need = leftovers()
    have = targeted(a.patch or SW_PATCHES)
    if len(need) < 5:
        fails.append("instrument blind: only %d sekkulaath-bearing nodes in %s" % (len(need), FW_DEFS))
    if not all(k in need for k in PROBE):
        fails.append("instrument blind: probe nodes not found: %r" % [k for k in PROBE if k not in need])
    for dn, tag in sorted(need - have):
        fails.append("%s/%s says sekkulaath and no SW patch replaces it" % (dn, tag))
    if fails:
        print("FAIL (%d)" % len(fails))
        for m in fails:
            print("  - " + m)
        return 1
    print("OK: %d sekkulaath-bearing nodes, all replaced by a SW patch" % len(need))
    return 0


if __name__ == "__main__":
    sys.exit(main())
