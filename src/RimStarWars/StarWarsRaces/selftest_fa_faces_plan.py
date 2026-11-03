#!/usr/bin/env python3
"""Pins RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM's 'one of each RSW_ humanlike': fa_faces_live.plan() must spawn
exactly one subject per RSW_ XenotypeDef defined under src/ (census read from the def XML, not from the opt-out
list), plus the Baseliner sanity probe and 2 Jawa from RUT_Jawa_Colonist. A plan that drops, duplicates or
invents a xenotype exits 1.
    python3 src/RimStarWars/StarWarsRaces/selftest_fa_faces_plan.py
"""
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import fa_faces_live as F  # noqa: E402


def census(root=os.path.join(REPO, "src")):
    """Every concrete RSW_ XenotypeDef defName in src/ XML (abstract defs excluded)."""
    names = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".xml"):
                continue
            try:
                r = ET.parse(os.path.join(dp, f)).getroot()
            except ET.ParseError:
                continue
            for d in r.iter("XenotypeDef"):
                if (d.get("Abstract") or "").lower() == "true":
                    continue
                n = (d.findtext("defName") or "").strip()
                if n.startswith("RSW_"):
                    names.append(n)
    return names


def main():
    defs = census()
    assert len(defs) >= 60, "census blind: %d RSW_ XenotypeDefs" % len(defs)          # sanity: instrument sees
    assert len(defs) == len(set(defs)), "duplicate defName in src/: %s" % [n for n, c in Counter(defs).items() if c > 1]
    listed = F.listed_xenotypes()
    unlisted = [x for x in F.UNLISTED if x not in listed and x != F.JAWA_XENO]
    p = F.plan(listed)
    xenos = [s[3] for s in p if s[0] in ("listed", "unlisted")]
    jawa = [s for s in p if s[0] == "jawa"]
    sanity = [s for s in p if s[0] == "sanity"]
    assert len(sanity) == 1 and sanity[0][3] == "Baseliner", "sanity probe missing"
    assert len(jawa) == 2 and all(s[1] == F.JAWA_KIND and s[2] is None and s[3] == F.JAWA_XENO for s in jawa), \
        "the 2 unforced Jawa are not planned"
    dup = [n for n, c in Counter(xenos).items() if c > 1]
    assert not dup, "xenotype planned twice: %s" % dup
    covered = set(xenos) | {F.JAWA_XENO}
    missing, extra = sorted(set(defs) - covered), sorted(covered - set(defs))
    assert not missing, "RSW_ humanlike(s) never spawned: %s" % missing
    assert not extra, "planned xenotype(s) not defined in src/: %s" % extra
    assert len(p) == len(listed) + 3 + len(unlisted), "plan size %d != %d" % (len(p), len(listed) + 3 + len(unlisted))
    print("plan PASS: %d RSW_ XenotypeDefs in src/, all planned once; %d subjects" % (len(defs), len(p)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as e:
        print("plan FAIL: %s" % e)
        sys.exit(1)
