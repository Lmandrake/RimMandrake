#!/usr/bin/env python3
"""Offline selftest: no armour-tier op in Armour_Ratings.xml targets apparel that is not armour
(SCORCHBACKPACK_FIX_NOT_BESKAR).
    python3 src/RimMandrake/Utils/selftest_armour_tier_not_armour.py [--ratings PATH]

gen_armour_patch.py tiers apparel by substring over defName + label, so "mando" (beskar) matches inside
"commando". guy762_Backpack_scorch ("backpack, commando's", own stats 0.1/0.1/0.1) was emitted as beskar
1.00/0.90/1.20; the op was dead behind a retired-donor FindMod until 61dcf6562d made it live.
1. Every def an op in Armour_Ratings.xml targets is resolved to its label in src/; none may be a backpack
   or be listed in gen_armour_patch.NOT_ARMOUR (read by ast: the generator runs on import).
2. NOT_ARMOUR names guy762_Backpack_scorch and the tier loop skips it, so a re-run cannot re-emit it.
3. The instrument can see: >= 50 target defs, and every one of our own (>= 10 guy762_) resolves to a label.
--ratings runs check 1 against another copy (e.g. `git show 61dcf6562d:...` -> red).
"""
import argparse
import ast
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ARMOURY = os.path.join(REPO, "src", "RimStarWars", "Armoury")
RATINGS = os.path.join(ARMOURY, "Patches", "Armour_Ratings.xml")
GEN = os.path.join(ARMOURY, "Source", "gen_armour_patch.py")
DEF_ROOTS = [os.path.join(REPO, "src")]
TARGET_RE = re.compile(r'defName="([^"]+)"\]/statBases/ArmorRating_')

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def not_armour_tuple():
    tree = ast.parse(open(GEN, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "NOT_ARMOUR" for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    return None


def labels_for(names):
    out = {}
    for root in DEF_ROOTS:
        for dp, _dn, fn in os.walk(root):
            if os.sep + "Defs" not in dp + os.sep:
                continue
            for f in fn:
                if not f.endswith(".xml"):
                    continue
                p = os.path.join(dp, f)
                try:
                    raw = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                if not any(n in raw for n in names):
                    continue
                try:
                    defs = ET.fromstring(raw.encode("utf-8"))
                except ET.ParseError:
                    continue
                for el in defs:
                    dn = el.findtext("defName")
                    if dn in names and dn not in out:
                        out[dn] = (el.findtext("label") or "").lower()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", default=RATINGS)
    a = ap.parse_args(argv)
    targets = set(TARGET_RE.findall(open(a.ratings, encoding="utf-8").read()))
    labels = labels_for(targets)
    check(len(targets) >= 50, "instrument blind: only %d target defs in %s" % (len(targets), a.ratings))
    # third-party targets (VFE warcaskets, cataphract/marine) live outside src/; our absorbed guy762_ ones must resolve
    ours = sorted(dn for dn in targets if dn.startswith("guy762_"))
    check(len(ours) >= 10 and all(dn in labels for dn in ours),
          "instrument blind: guy762_ targets unresolved in src/: %r" % [dn for dn in ours if dn not in labels])
    na = not_armour_tuple()
    check(na is not None and "guy762_Backpack_scorch" in na, "gen_armour_patch.NOT_ARMOUR missing or lacks the scorch backpack: %r" % (na,))
    gen = open(GEN, encoding="utf-8").read()
    check("dn in NOT_ARMOUR" in gen, "gen_armour_patch tier loop does not consult NOT_ARMOUR")
    for dn in sorted(targets):
        lab = labels.get(dn, "")
        check("backpack" not in lab and "backpack" not in dn.lower(),
              "%s (label %r) is a backpack but gets an armour-tier op" % (dn, lab))
        check(dn not in (na or ()), "%s is in NOT_ARMOUR but Armour_Ratings.xml still tiers it" % dn)
    if FAILS:
        print("FAIL (%d)" % len(FAILS))
        for m in FAILS:
            print("  - " + m)
        return 1
    print("OK: %d tier targets, %d labelled, none a backpack or NOT_ARMOUR" % (len(targets), len(labels)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
