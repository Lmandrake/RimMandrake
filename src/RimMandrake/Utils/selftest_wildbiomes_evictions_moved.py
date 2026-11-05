#!/usr/bin/env python3
"""selftest_wildbiomes_evictions_moved.py -- the eviction generator canonicalizes moved RSW_ names, and
neither the shipped evictions file nor the rosters still name a creature the SWB->RM moves renamed.

Offline, no capture needed: reads RM_SWBRehome_Aliases.xml, the shipped evictions XML and the roster JSONs."""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "design", "Jawa", "fauna"))
import biome_wildbiomes_evictions as E  # noqa: E402

FAILS = []


def check(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


mv = E.moved_names()
check(mv.get("RSW_Ikee") == "RM_Ikee", "alias map: RSW_Ikee -> RM_Ikee")
check(mv.get("Corpse_RSW_Baseopsis") == "Corpse_RM_Baseopsis", "alias map: corpse names too")
check("RSW_Tellurox" not in mv, "ThingDef map holds no PawnKind-only alias (RSW_Tellurox)")
mvk = E.moved_names(("ThingDef", "PawnKindDef"))
check(mvk.get("RSW_Tellurox") == "RM_Tellurox",
      "kind map: PawnKind-only rename RSW_Tellurox -> RM_Tellurox")
check(mvk.get("RSW_TelluroxRace") == "RM_TelluroxRace", "kind map keeps ThingDef aliases")
check(len(mv) >= 40, "alias map reads the whole file (%d entries)" % len(mv))

xml = os.path.join(E.REPO, "src", "RimUtinni", "UtinniPatches", "Patches", "BiomeCastEvictions_WildBiomes.xml")
txt = open(xml, encoding="utf-8").read()
named = set(re.findall(r'defName="([^"]+)"', txt))
stale = sorted(n for n in named if n in mv)
check(not stale, "evictions file names no moved (old) def: %s" % stale[:5])

bad = []
for fp in glob.glob(os.path.join(E.ROSTERS, "*.json")):
    for f in (json.load(open(fp, encoding="utf-8")).get("fauna") or []):
        if f.get("def") in mvk:
            bad.append((os.path.basename(fp), f["def"]))
check(not bad, "rosters name no moved (old) def: %s" % bad[:5])

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
