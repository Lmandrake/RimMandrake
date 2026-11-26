#!/usr/bin/env python3
"""The plant check of DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES spec 6 (design/RimMandrake/unified_direct_sun_heat_2026-10-19.md §3).

Air heat is a vanilla temperature-offset condition, so a hot-air biome's plants feel it too. For each hot-air biome
this reads its wild-plant roster (the BiomeDef's <wildPlants>, parsed as elements, plus any Utinni WildPlants patch),
each plant's growth band after the generated refit (src/RimUtinni/UtinniPatches/Patches/PlantTolerances_*.xml, else the
plant's own <plant> fields, else vanilla's PlantProperties defaults 0/6/42/58), and reports how growth at the biome's
median air temperature changes when the condition's offset is added. Growth factor = vanilla
PlantUtility.GrowthRateFactorFor_Temperature (RimSage, 1.6): 1 between the optimal bounds, an InverseLerp to 0 at the
growth bounds.

    python3 src/RimMandrake/Utils/direct_sun_air_heat_plant_check.py
Medians are the biome sheets' (design doc §1); the offsets are each condition def's temperatureOffset. Each biome prints
two readings: "as loaded" (the bands with no fit) and "natives fitted" (Creature Behaviors' RM_AirHeatNatives.Fit: the
upper bounds raised by the offset, widen only). A measurement for tuning, not a check: it prints numbers and exits 0, or
exits 2 when it could not look.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SRC = os.path.join(REPO, "src")
# biome defName -> (median air C from its sheet, condition defName)
BIOMES = {"RM_TheForge": (49.0, "RM_ForgeAirHeat"), "RM_TheScald": (52.5, "RM_ScaldAirHeat"),
          "RM_Greentide": (45.5, "RM_GreentideAirHeat"), "RM_FeverWood": (45.5, "RM_FeverWoodAirHeat")}
DEFAULTS = {"minGrowthTemperature": 0.0, "minOptimalGrowthTemperature": 6.0, "maxOptimalGrowthTemperature": 42.0,
            "maxGrowthTemperature": 58.0}


def defs(tag):
    out = {}
    for f in glob.glob(os.path.join(SRC, "**", "*.xml"), recursive=True):
        try:
            r = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for d in r.iter(tag):
            n = d.findtext("defName")
            if n:
                out[n] = d
    return out


def refits():
    out = {}
    for f in glob.glob(os.path.join(SRC, "RimUtinni", "UtinniPatches", "Patches", "PlantTolerances_*.xml")):
        r = ET.parse(f).getroot()
        for op in r.iter("Operation"):
            if op.get("Class") != "PatchOperationConditional":
                continue
            m = re.match(r'/Defs/ThingDef\[defName="(\w+)"\]/plant$', (op.findtext("xpath") or "").strip())
            if not m:
                continue
            for v in op.iter("value"):
                for c in v:
                    if c.tag in DEFAULTS:
                        out.setdefault(m.group(1), {})[c.tag] = float(c.text)
    return out


def factor(b, t):
    if t < b["minOptimalGrowthTemperature"]:
        lo, hi = b["minGrowthTemperature"], b["minOptimalGrowthTemperature"]
        return max(0.0, min(1.0, (t - lo) / (hi - lo))) if hi > lo else 0.0
    if t > b["maxOptimalGrowthTemperature"]:
        lo, hi = b["maxGrowthTemperature"], b["maxOptimalGrowthTemperature"]
        return max(0.0, min(1.0, (t - lo) / (hi - lo))) if hi != lo else 0.0
    return 1.0


def main():
    biomes, things, conds, ref = defs("BiomeDef"), defs("ThingDef"), defs("GameConditionDef"), refits()
    if not biomes or not things:
        print("COULD NOT LOOK: no BiomeDef or ThingDef parsed under src/")
        return 2
    for name, (median, cond) in sorted(BIOMES.items()):
        b = biomes.get(name)
        if b is None:
            print("%s: BiomeDef not found" % name)
            continue
        c = conds.get(cond)
        off = float(c.findtext("temperatureOffset")) if c is not None and c.findtext("temperatureOffset") else None
        wp = b.find("wildPlants")
        roster = [x.tag for x in wp] if wp is not None else []
        if not roster:
            print("%s: empty wildPlants roster" % name)
            continue
        if off is None:
            print("%s: no condition %s yet (held or unbuilt); roster %d plants" % (name, cond, len(roster)))
            continue
        for fitted in (False, True):
            report(name, median, off, roster, things, ref, fitted)
    return 0


def report(name, median, off, roster, things, ref, fitted):
    if True:
        hurt, dead = [], []
        for p in roster:
            band = dict(DEFAULTS)
            pd = things.get(p)
            if pd is not None and pd.find("plant") is not None:
                for k in DEFAULTS:
                    v = pd.find("plant").findtext(k)
                    if v:
                        band[k] = float(v)
            band.update(ref.get(p, {}))
            before = factor(band, median)
            if fitted:
                band = dict(band, maxOptimalGrowthTemperature=band["maxOptimalGrowthTemperature"] + off,
                            maxGrowthTemperature=band["maxGrowthTemperature"] + off)
            after = factor(band, median + off)
            if after <= 0.0:
                dead.append("%s (max %.1f)" % (p, band["maxGrowthTemperature"]))
            elif after < before - 1e-6:
                hurt.append("%s %.2f->%.2f" % (p, before, after))
        print("%s (%s): median %.1f C + %.0f C air heat = %.1f C; %d roster plants: %d stop growing, %d grow slower"
              % (name, "natives fitted" if fitted else "as loaded", median, off, median + off, len(roster), len(dead), len(hurt)))
        if dead:
            print("  stop growing: " + ", ".join(dead))
        if hurt:
            print("  grow slower:  " + ", ".join(hurt))


if __name__ == "__main__":
    sys.exit(main())
