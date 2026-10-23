#!/usr/bin/env python3
"""Selftest: solar insolation is a pure function of sun elevation (VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT).

design/RimMandrake/vee_port_plan_2026-10-22.md §4; One Direct Sun (owner 2026-09-29 / 2026-10-19: "no biome-specific
sun. It's a matter of geometry"). Checks, offline:
  1. solar_insolation.py's constants equal RM_InsolationKernel.cs's (parsed from the C#), so the port cannot drift;
  2. the factor: 1 at low sun, 1 + bonus from 35°, monotone and continuous, 1 everywhere with bonus 0;
  3. on all 21,872 tiles of world/world_tiles_sub7b.csv: label == f(e), cross-checked against an INDEPENDENT arc
     implementation (world_physics_audit.arc_deg) as the old paint's arc rule (<= 55° / >= 125°), with no biome
     exclusion; the sanity probe re-applies the 2026-08-26 paint's biome blacklist and must find it removing tiles,
     so a 0-exclusions result is meaningful;
  4. the two label defs are worker-free, extension-free, number-free, worldgen-closed;
  5. the panel patch reads no biome and no mutator (planted negative proves the scan can see).
"""
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solar_insolation as S  # noqa: E402
import world_physics_audit as A  # noqa: E402

DEFS_XML = os.path.join(S.REPO, "src", "RimMandrake", "SolarMirrors", "Defs", "TileMutatorDefs", "RM_SolarInsolation.xml")
PATCH_CS = os.path.join(S.REPO, "src", "RimMandrake", "SolarMirrors", "Source", "RM_InsolationPatch.cs")
OLD_BLACKLIST = {"Glowforest", "AB_RockyCrags"}  # world/audit_2026-08-26/plan.py solarBL (plus water)
HOME = 17011


def _cs_const(text, name):
    m = re.search(r"public const float %s = (-?[0-9.]+)f;" % name, text)
    return float(m.group(1)) if m else None


def _forbidden_reads(code):
    """Biome/mutator reads in C# code, comments stripped."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.findall(r"\.Biome\b|BiomeDef|Mutator|\.Mutators\b", code)


def main():
    fails = []
    kernel = open(S.KERNEL_CS, encoding="utf-8").read()
    for cs, py in (("RampStartDegrees", S.RAMP_START), ("RampFullDegrees", S.RAMP_FULL),
                   ("StrongInsolationMinDegrees", S.STRONG_MIN), ("SunlessMaxDegrees", S.SUNLESS_MAX),
                   ("DefaultHighSunBonus", S.DEFAULT_BONUS)):
        v = _cs_const(kernel, cs)
        if v is None or abs(v - py) > 1e-9:
            fails.append(f"constant {cs}: C# {v} != python {py}")

    # 2. the factor
    prev = None
    for i in range(-900, 901):
        e = i / 10.0
        f = S.insolation_factor(e)
        if prev is not None and (f < prev - 1e-12 or f - prev > 0.01):
            fails.append(f"factor not monotone/continuous at e={e}: {prev} -> {f}")
            break
        prev = f
    if S.insolation_factor(20.0) != 1.0 or S.insolation_factor(-10.0) != 1.0:
        fails.append("factor is not 1 at low sun")
    if abs(S.insolation_factor(35.0) - 1.25) > 1e-9 or abs(S.insolation_factor(89.0) - 1.25) > 1e-9:
        fails.append("factor is not 1.25 at high sun (VEE_MoreSolarPower's x1.25)")
    if any(S.insolation_factor(e, 0.0) != 1.0 for e in (-50, 0, 30, 90)):
        fails.append("bonus 0 does not give vanilla output")

    # 3. label == f(e) on every tile, by an independent arc
    tiles = S.load_tiles()
    if len(tiles) != 21872:
        fails.append(f"geometry CSV has {len(tiles)} tiles, expected 21,872")
    lab = S.tiles_by_label(tiles)
    strong, sunless = set(lab["RM_StrongInsolation"]), set(lab["RM_Sunless"])
    ind_strong = {t for t, (la, lo) in tiles.items() if A.arc_deg(la, lo) <= 55.0}
    ind_sunless = {t for t, (la, lo) in tiles.items() if A.arc_deg(la, lo) >= 125.0}
    if strong != ind_strong or sunless != ind_sunless:
        fails.append(f"label != f(e): strong {len(strong ^ ind_strong)} / sunless {len(sunless ^ ind_sunless)} tiles differ "
                     "from the independent arc rule")
    if strong & sunless:
        fails.append(f"{len(strong & sunless)} tiles carry both labels")
    belt = len(tiles) - len(strong) - len(sunless)
    if not strong or not sunless or belt <= 0:
        fails.append(f"degenerate split: strong {len(strong)}, sunless {len(sunless)}, belt {belt}")
    if HOME not in strong or abs(S.insolation_factor(S.elevation_deg(*tiles[HOME])) - 1.25) > 1e-9:
        fails.append(f"home tile {HOME} is not strong sun at x1.25")
    # sanity probe: the old paint's biome blacklist DOES remove tiles on this instrument (CSV biome column, a record)
    import csv
    biome = {int(r["tile"]): r["biome"] for r in csv.DictReader(open(S.TILES, encoding="utf-8"))}
    old_strong = {t for t in ind_strong if biome.get(t) not in OLD_BLACKLIST and biome.get(t) not in A_WATER}
    if len(old_strong) >= len(ind_strong):
        fails.append("sanity: the old biome blacklist removes nothing here, so 'no exclusions' proves nothing")

    # 4. the label defs
    root = ET.parse(DEFS_XML).getroot()
    defs = {e.findtext("defName"): e for e in root.findall("TileMutatorDef")}
    for name in S.LABELS.values():
        e = defs.get(name)
        if e is None:
            fails.append(f"TileMutatorDef {name} missing from {DEFS_XML}")
            continue
        for tag in ("workerClass", "modExtensions", "biomeWhitelist", "biomeBlacklist", "extraGenSteps"):
            if e.find(tag) is not None:
                fails.append(f"{name} carries <{tag}>: a derived label has no mechanism and no biome list")
        if (e.findtext("chanceOnNonLandmarkTile") or "").strip() != "0":
            fails.append(f"{name}: chanceOnNonLandmarkTile must be 0 (no worldgen)")
        text = (e.findtext("label") or "") + " " + (e.findtext("description") or "")
        if re.search(r"\d", text):
            fails.append(f"{name}: label/description carries a number ({text.strip()!r}); labels are number-free")

    # 5. the patch reads geometry only
    if _forbidden_reads("var b = map.Biome; // x") != [".Biome"]:
        fails.append("sanity: the biome/mutator scan cannot see a planted map.Biome")
    hits = _forbidden_reads(open(PATCH_CS, encoding="utf-8").read())
    if hits:
        fails.append(f"RM_InsolationPatch.cs reads {sorted(set(hits))}: the factor must be a function of elevation only")

    print(f"tiles {len(tiles)}  strong {len(strong)}  sunless {len(sunless)}  belt {belt}  "
          f"old-paint strong (blacklist on this CSV) {len(old_strong)}")
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"{len(fails)} FAIL")
    return 1 if fails else 0


A_WATER = {"Ocean", "Lake", "SeaIce"}

if __name__ == "__main__":
    sys.exit(main())
