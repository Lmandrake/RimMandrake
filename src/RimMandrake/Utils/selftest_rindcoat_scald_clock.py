#!/usr/bin/env python3
"""RINDCOAT_SCALD_TUNE_STILL_SLOWLY_POACHED: the rind coat slows the Scald steam clock, it never stops it.

The owner's 2026-09-25 rind ruling ("would render you immune to heat and cold to extreme levels") is about
TEMPERATURE, which is insulation. The steam clock is a separate thing: RM_ScaldExposure reads ArmorRating_Heat
(SCALD_FOLD_INTO_HEAT_1 deleted RM_ScaldProtection) under a clamp and an 8% floor, and Ban 3 of the frozen
Scald sheet says gear never zeroes it. So the coat keeps the clock running (0.4x at heat armor 0.60), between
the scald wrap and the boil-suit, and that decision is written in spec section 5a and in the coat's def.

Offline and static. Each check is also run against a planted defect, which it must catch.

    python3 src/RimMandrake/Utils/selftest_rindcoat_scald_clock.py
"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
COAT = os.path.join(REPO, "src", "RimMandrake", "Greentide", "Defs", "ThingDefs", "RM_GreatboleHarvest_Items.xml")
GEAR = os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes", "Defs", "ThingDefs_Apparel", "RM_ScaldGear.xml")
CLOCK = os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes", "Defs", "HediffDefs", "RM_ScaldExposure.xml")
SPEC = os.path.join(REPO, "design", "RimMandrake", "scald_steam_and_hazards_spec.md")
DECISION_TAG = "RINDCOAT_SCALD_TUNE_STILL_SLOWLY_POACHED"
# Core's Human statBases (Data/Core/Defs/ThingDefs_Races/Races_Humanlike.xml, read 2026-11-06): the comfort band
# before apparel. The Scald's ambient is 55 C (exposure_gear_matrix_spec.md: the coat "makes the 55 C ambient
# comfortable").
HUMAN_COMFY_MAX = 26.0
SCALD_AMBIENT_C = 55.0


def thing(root, defname):
    for el in root.iter():
        if el.findtext("defName") == defname:
            return el
    raise AssertionError(f"{defname} not found")


def stat(el, name):
    v = el.find(f"statBases/{name}")
    return float(v.text) if v is not None else 0.0


def clock_comp(root):
    hd = thing(root, "RM_ScaldExposure")
    for li in hd.findall("comps/li"):
        if li.get("Class", "").endswith("HediffCompProperties_EnvironmentalExposure"):
            return li
    raise AssertionError("RM_ScaldExposure has no exposure comp")


def drive(protection, floor):
    # HazardTargeting.ProtectionDriveFactor: max(floor, 1 - clamp01(protection))
    return max(floor, 1.0 - min(1.0, max(0.0, protection)))


def check(coat_root, gear_root, clock_root, spec_text, coat_text):
    errs = []
    comp = clock_comp(clock_root)
    if comp.findtext("protectionStat") != "ArmorRating_Heat":
        errs.append("RM_ScaldExposure protectionStat is not ArmorRating_Heat")
    floor = float(comp.findtext("minDriveFactor") or 0)
    if abs(floor - 0.08) > 1e-9:
        errs.append(f"minDriveFactor {floor} is not Ban 3's 0.08")
    coat = thing(coat_root, "RM_Apparel_RindCoat")
    heat = stat(coat, "ArmorRating_Heat")
    wrap = stat(thing(gear_root, "RM_Apparel_ScaldWrap"), "ArmorRating_Heat")
    suit = stat(thing(gear_root, "RM_Apparel_BoilSuit"), "ArmorRating_Heat")
    if not heat < 1.0:
        errs.append(f"rind coat ArmorRating_Heat {heat} reaches the clamp: the coat alone would pin the clock to its floor")
    if not wrap < heat < suit:
        errs.append(f"rind coat heat armor {heat} is not between wrap {wrap} and boil-suit {suit}")
    if not drive(heat, floor) > floor:
        errs.append("rind coat drive factor sits on the floor")
    if HUMAN_COMFY_MAX + stat(coat, "Insulation_Heat") < SCALD_AMBIENT_C:
        errs.append("rind coat Insulation_Heat does not make the Scald's 55 C ambient comfortable")
    for name, text in (("coat def", coat_text), ("spec", spec_text)):
        if DECISION_TAG not in text:
            errs.append(f"{name} does not record the {DECISION_TAG} decision")
    for name, text in (("coat def", coat_text), ("clock def", ET.tostring(clock_root, encoding="unicode"))):
        if "<RM_ScaldProtection>" in text or ">RM_ScaldProtection<" in text:
            errs.append(f"{name} still names the deleted RM_ScaldProtection stat")
    return errs


def main():
    read = lambda p: open(p, encoding="utf-8").read()
    coat_text, spec_text = read(COAT), read(SPEC)
    coat_root, gear_root, clock_root = (ET.parse(p).getroot() for p in (COAT, GEAR, CLOCK))
    errs = check(coat_root, gear_root, clock_root, spec_text, coat_text)
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1

    # Planted defects: each must be caught.
    def planted(mutate):
        c, k = copy.deepcopy(coat_root), copy.deepcopy(clock_root)
        s, t = spec_text, coat_text
        r = mutate(c, k)
        if r:
            s, t = r
        return check(c, gear_root, k, s, t)

    def set_heat(c, k, v):
        thing(c, "RM_Apparel_RindCoat").find("statBases/ArmorRating_Heat").text = v

    def set_floor(k, v):
        clock_comp(k).find("minDriveFactor").text = v

    plants = {
        "coat heat armor 1.0 (immunity)": lambda c, k: set_heat(c, k, "1.0"),
        "coat heat armor below the wrap": lambda c, k: set_heat(c, k, "0.30"),
        "clock floor 0": lambda c, k: set_floor(k, "0"),
        "clock reads RM_ScaldProtection": lambda c, k: setattr(clock_comp(k).find("protectionStat"), "text", "RM_ScaldProtection"),
        "decision missing from spec": lambda c, k: (spec_text.replace(DECISION_TAG, "X"), coat_text),
    }
    missed = [n for n, m in plants.items() if not planted(m)]
    for n in missed:
        print("FAIL planted defect not caught:", n)
    if missed:
        return 1
    print(f"PASS rind coat clock {drive(stat(thing(coat_root, 'RM_Apparel_RindCoat'), 'ArmorRating_Heat'), 0.08):.2f}x, "
          f"floor 0.08 holds; {len(plants)} planted defects caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
