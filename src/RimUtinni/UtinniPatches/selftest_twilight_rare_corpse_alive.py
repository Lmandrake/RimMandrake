#!/usr/bin/env python3
"""COLOCLAW_DECIDE_APEX_ALIVE_OR_CORPSE_ONLY (offline, XML parsed): every Corpse_<race> that a Twilight rare
table (RM_RareTwilightCatches, RUT_RareTwilightCatches) can land has <race> living on the RM_TwilightSea floor,
inline in the BiomeDef or patch-added by WildAnimals_TwilightSea.xml. Owner 2026-09-26: "All the fishables
should also be alive and moving around in the depths (this is true for ALL seas)." Goes red, in a temp copy,
when the colo claw fish row is removed. Live spawn is UNMEASURED here (needs the seabed floor generator).

    python3 src/RimUtinni/UtinniPatches/selftest_twilight_rare_corpse_alive.py
"""
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", ".."))
BIOME = os.path.join(SRC, "RimMandrake", "TerminalBiomes", "Defs", "BiomeDefs", "RM_TwilightSea.xml")
TABLES = [os.path.join(SRC, "RimMandrake", "TerminalBiomes", "Defs", "ThingSetMakerDefs", "RM_RareTwilightCatches.xml"),
          os.path.join(HERE, "Defs", "ThingSetMakerDefs", "RUT_RareTwilightCatches.xml")]
PATCH = os.path.join(HERE, "Patches", "WildAnimals_TwilightSea.xml")
FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def floor_animals(patch=PATCH):
    """Node names in RM_TwilightSea wildAnimals: the BiomeDef's own plus every patch-added value."""
    out = set()
    for d in ET.parse(BIOME).getroot():
        if d.tag == "BiomeDef" and d.findtext("defName") == "RM_TwilightSea" and d.find("wildAnimals") is not None:
            out |= {c.tag for c in d.find("wildAnimals")}
    for o in ET.parse(patch).getroot().iter():
        if (o.findtext("xpath") or "").endswith('defName="RM_TwilightSea"]/wildAnimals') and o.find("value") is not None:
            out |= {c.tag for c in o.find("value")}
    return out


def corpse_races():
    out = set()
    for t in TABLES:
        for li in ET.parse(t).getroot().iter("li"):
            if (li.text or "").strip().startswith("Corpse_"):
                out.add(li.text.strip()[len("Corpse_"):])
    return out


def problems(patch=PATCH):
    floor, races = floor_animals(patch), corpse_races()
    bad = []
    if len(floor) < 3:
        bad.append("sanity probe: only %d Twilight floor animals parsed" % len(floor))
    if not races:
        bad.append("sanity probe: no Corpse_ option parsed from the Twilight rare tables")
    bad += ["%s lands as a corpse but is not alive on the RM_TwilightSea floor" % r for r in sorted(races - floor)]
    return bad


def main():
    floor = floor_animals()
    check("probe: mee and faa (known rows) are seen on the floor", {"RSW_Mee", "RSW_Faa"} <= floor, sorted(floor))
    check("probe: the colo claw corpse is seen in a rare table", "RSW_ColoClawFish" in corpse_races(), sorted(corpse_races()))
    shipped = problems()
    check("shipped: every Twilight rare corpse has a living floor body", not shipped, shipped)
    tmp = tempfile.mkdtemp(prefix="coloclaw_")
    try:
        p = os.path.join(tmp, "WildAnimals_TwilightSea.xml")
        shutil.copy(PATCH, p)
        s = open(p, encoding="utf-8").read()
        row = '        <RSW_ColoClawFish MayRequire="mandrake.rsw.swbestiary">0.03</RSW_ColoClawFish>\n'
        check("mutant setup: the colo claw row is present", row in s)
        open(p, "w", encoding="utf-8").write(s.replace(row, "", 1))
        got = problems(p)
        check("mutant: dropping the colo claw row turns red", any("RSW_ColoClawFish" in g for g in got), got)
    finally:
        shutil.rmtree(tmp)
    print("FAILS: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
