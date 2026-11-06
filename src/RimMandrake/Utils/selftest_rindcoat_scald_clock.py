#!/usr/bin/env python3
"""RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL: the rind coat is near-immune to the Scald steam clock, never immune.

Owner by card 2026-11-06: "Royal Rind coat vs. the Scald's steam: what should the rind coat do against steam? ->
Near-immune: tiny floor." RM_ScaldExposure reads the summed ArmorRating_Heat of worn apparel (SCALD_FOLD_INTO_HEAT_1)
with GetStatValue, so Core's StatPart_Quality scales it, then clamps the sum to 1 and floors the drive at 8%
(minDriveFactor 0.08, Ban 3 of the frozen Scald sheet: gear never zeroes it). So the coat alone, at EVERY quality,
must sit on that floor, the floor must be above zero, and its extreme heat and cold insulation (the owner's
2026-09-25 rind ruling) must stay. The offline model also states the done-bar's reading: exposure after two
unbroken steam days in the coat is 0.08x the unprotected figure.

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
CLOCK = os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes", "Defs", "HediffDefs", "RM_ScaldExposure.xml")
SPEC = os.path.join(REPO, "design", "RimMandrake", "scald_steam_and_hazards_spec.md")
DECISION_TAG = "RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL"
FLOOR = 0.08
# Core's ArmorRatingBase StatPart_Quality (Data/Core/Defs/Stats/Stats_Apparel.xml, read 2026-11-05). The coat
# derives from ApparelMakeableBase, so it is quality-rolled, and the clock's SumApparelStat uses GetStatValue.
QUALITY = {"Awful": 0.60, "Poor": 0.80, "Normal": 1.00, "Good": 1.15, "Excellent": 1.30, "Masterwork": 1.45,
           "Legendary": 1.80}
ARMOR_MAX = 2.0  # ArmorRatingBase maxValue
# Core's Human statBases (Data/Core/Defs/ThingDefs_Races/Races_Humanlike.xml, read 2026-11-06): the comfort band
# before apparel. The Scald's ambient is 55 C (exposure_gear_matrix_spec.md: the coat "makes the 55 C ambient
# comfortable").
HUMAN_COMFY_MAX = 26.0
SCALD_AMBIENT_C = 55.0
# The shipped extreme-cold figure (owner 2026-09-25: "immune to heat and cold to extreme levels"); lowering it
# loosens his ruling, so this is a bar, not a tuning knob.
RIND_COLD_MIN = 35.0
STEAM_DAYS = 2.0


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
    # HazardTargeting.ProtectionDriveFactor (holdThreshold 0): max(floor, 1 - clamp01(protection))
    return max(floor, 1.0 - min(1.0, max(0.0, protection)))


def worn_armor(base, quality):
    return min(ARMOR_MAX, base * QUALITY[quality])


def check(coat_root, clock_root, spec_text, coat_text):
    errs = []
    comp = clock_comp(clock_root)
    if comp.findtext("protectionStat") != "ArmorRating_Heat":
        errs.append("RM_ScaldExposure protectionStat is not ArmorRating_Heat")
    floor = float(comp.findtext("minDriveFactor") or 0)
    if abs(floor - FLOOR) > 1e-9:
        errs.append(f"minDriveFactor {floor} is not Ban 3's {FLOOR}: never zero, and the card's tiny floor")
    rate = float(comp.findtext("severityPerDayExposed") or 0)
    if rate <= 0:
        errs.append("severityPerDayExposed is not positive: the unprotected clock does not run")
    coat = thing(coat_root, "RM_Apparel_RindCoat")
    heat = stat(coat, "ArmorRating_Heat")
    off = {q: round(drive(worn_armor(heat, q), floor), 4) for q in QUALITY if drive(worn_armor(heat, q), floor) > floor + 1e-9}
    if off:
        errs.append(f"rind coat heat armor {heat} leaves these qualities above the {floor} floor: {off}")
    if not drive(worn_armor(heat, "Legendary"), floor) > 0:
        errs.append("the rind coat zeroes the clock (Ban 3)")
    # The done-bar's reading, modelled: two unbroken steam days, coat vs. unprotected.
    naked, rind = rate * STEAM_DAYS, rate * STEAM_DAYS * drive(worn_armor(heat, "Awful"), floor)
    ratio = rind / naked if naked else 0
    if not 0 < ratio <= FLOOR + 1e-9:
        errs.append(f"modelled exposure after {STEAM_DAYS:g} steam days is {rind:.3f} in the coat vs {naked:.3f} "
                    f"unprotected ({ratio:.2f}x), not the {FLOOR}x floor")
    if HUMAN_COMFY_MAX + stat(coat, "Insulation_Heat") < SCALD_AMBIENT_C:
        errs.append("rind coat Insulation_Heat does not make the Scald's 55 C ambient comfortable")
    if stat(coat, "Insulation_Cold") < RIND_COLD_MIN:
        errs.append(f"rind coat Insulation_Cold {stat(coat, 'Insulation_Cold')} is below the extreme-cold {RIND_COLD_MIN}")
    for name, text in (("coat def", coat_text), ("spec", spec_text)):
        if DECISION_TAG not in text:
            errs.append(f"{name} does not record the {DECISION_TAG} ruling")
    # The reversed agent decision is deleted, not superseded.
    for name, text, stale in (("spec", spec_text, "Decided 2026-11-06"), ("coat def", coat_text, "0.4x")):
        if stale in text:
            errs.append(f"{name} still carries the reversed 0.4x decision ({stale!r})")
    for name, text in (("coat def", coat_text), ("clock def", ET.tostring(clock_root, encoding="unicode"))):
        if "<RM_ScaldProtection>" in text or ">RM_ScaldProtection<" in text:
            errs.append(f"{name} still names the deleted RM_ScaldProtection stat")
    return errs, ratio


def main():
    read = lambda p: open(p, encoding="utf-8").read()  # noqa: E731
    coat_text, spec_text = read(COAT), read(SPEC)
    coat_root, clock_root = (ET.parse(p).getroot() for p in (COAT, CLOCK))
    errs, ratio = check(coat_root, clock_root, spec_text, coat_text)
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1

    # Planted defects: each must be caught.
    def planted(mutate):
        c, k = copy.deepcopy(coat_root), copy.deepcopy(clock_root)
        r = mutate(c, k)
        s, t = r if r else (spec_text, coat_text)
        return check(c, k, s, t)[0]

    def set_coat(c, name, v):
        thing(c, "RM_Apparel_RindCoat").find(f"statBases/{name}").text = v

    def set_comp(k, name, v):
        clock_comp(k).find(name).text = v

    plants = {
        "coat heat armor 0.60 (the reversed 0.4x rung)": lambda c, k: set_coat(c, "ArmorRating_Heat", "0.60"),
        "coat heat armor 0.92 (floors at Normal only)": lambda c, k: set_coat(c, "ArmorRating_Heat", "0.92"),
        "clock floor 0 (immunity)": lambda c, k: set_comp(k, "minDriveFactor", "0"),
        "clock floor 0.4": lambda c, k: set_comp(k, "minDriveFactor", "0.4"),
        "clock reads RM_ScaldProtection": lambda c, k: set_comp(k, "protectionStat", "RM_ScaldProtection"),
        "cold insulation dropped": lambda c, k: set_coat(c, "Insulation_Cold", "10"),
        "heat insulation dropped": lambda c, k: set_coat(c, "Insulation_Heat", "5"),
        "ruling missing from spec": lambda c, k: (spec_text.replace(DECISION_TAG, "X"), coat_text),
        "reversed decision left in spec": lambda c, k: (spec_text + "\n- **Decided 2026-11-06 (x)**", coat_text),
    }
    missed = [n for n, m in plants.items() if not planted(m)]
    for n in missed:
        print("FAIL planted defect not caught:", n)
    if missed:
        return 1
    heat = stat(thing(coat_root, "RM_Apparel_RindCoat"), "ArmorRating_Heat")
    print(f"PASS rind coat heat armor {heat}: clock {FLOOR}x at every quality (awful {worn_armor(heat, 'Awful'):.3f}), "
          f"2 steam days {ratio:.2f}x unprotected, never zero; insulation kept; {len(plants)} planted defects caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
