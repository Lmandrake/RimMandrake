#!/usr/bin/env python3
"""selftest_flowworks_fuel_moat.py — CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (owner by card, 2026-10-15).

WHY: chemfuel and astrofuel had canal FluidDefs (FlowWorks_PitFluids.xml) but no LiquidDef named them as its
canalFluid, so a tank of either could not be pumped or hosed into a dug channel: it spilled (RM_LiquidSpill)
instead (C9-F1). A missing <canalFluid> logs nothing, so only a read of the data catches it.

What is checked here (the data half; the burn arithmetic is the C# SelfTest's FuelFireChecks):
  1. the generated registry's RM_Liquid_Chemfuel names RM_Fluid_Chemfuel as canalFluid, and the generator
     table says so too (the registry is regenerated from it);
  2. the astrofuel adoption patch's LiquidDef names RM_Fluid_Astrofuel;
  3. every named canal fluid exists, owns all four fill terrains, and those terrains exist;
  4. chemfuel burns as an Inferno, astrofuel as a Detonation (the two fire kinds the owner asked for);
  5. the Verse half of RM_LiquidFire.cs holds the shapes the C# SelfTest cannot reach: the detonation queue runs every
     tick inside both per-tick budgets, a planned cell is never re-queued, the inferno burns at its own rate, and both
     fires raise RM_FuelFireEvents.

CAN IT FAIL: each case runs once against an in-memory copy with the fix taken back out and must go RED there.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_fuel_moat.py
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MOD = Path(__file__).resolve().parent
REGISTRY = MOD / "Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml"
GENERATOR = MOD / "Tools/generate_liquid_suite.py"
ASTRO = MOD / "Patches/LiquidTypes/RM_LiquidDef_AstrofuelAdoption.xml"
FLUIDS = MOD / "Defs/Canals/FluidDefs/FlowWorks_PitFluids.xml"
TERRAIN = MOD / "Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml"
FIRE = MOD / "Source/RM_LiquidFire.cs"

# (needle that must be present, a splice that takes it back out)
FIRE_SHAPES = [
    ("if (detTick.Count > 0)\n\t\t\t{\n\t\t\t\tRunDetonation(map, ex, now);\n\t\t\t}\n\t\t\tif (now < nextCheckTick)",
     "the detonation queue runs every tick, before the 30-tick gate"),
    ("(kind == 0 && cells >= RM_FuelFireMath.MaxCellsConsumedPerTick) || (kind == 1 && blasts >= RM_FuelFireMath.MaxBlastsPerTick)",
     "RunDetonation stops at both per-tick budgets"),
    ("if (burning.ContainsKey(i) || detonating.Contains(i))", "a cell already planned to detonate is never re-queued"),
    ("? RM_FuelFireMath.InfernoTicksPerLevelAt(RimMandrakeFlowWorksSettings.chemfuelBurnRate) : notchTicks;",
     "an inferno canal cell burns at the chemfuel rate"),
    ("RM_FuelFireEvents.RaiseAstrofuelDetonation(map, origin, count);", "a detonation is announced"),
    ("RM_FuelFireEvents.RaiseLargeChemfuelFire(", "a large chemfuel fire is announced"),
]

LIQUID_TAG = "RimMandrake.FlowWorks.LiquidTypes.LiquidDef"
FLUID_TAG = "RimMandrake.FlowWorks.FluidDef"


def liquid_canal(xml_text: str, def_name: str) -> str | None:
    root = ET.fromstring(xml_text)
    for el in root.iter(LIQUID_TAG):
        if el.findtext("defName") == def_name:
            return el.findtext("canalFluid")
    return None


def fluids(xml_text: str) -> dict[str, ET.Element]:
    return {el.findtext("defName"): el for el in ET.fromstring(xml_text).iter(FLUID_TAG)}


def terrain_names(xml_text: str) -> set[str]:
    return {el.findtext("defName") for el in ET.fromstring(xml_text).iter("TerrainDef")}


def case_registry(reg: str, gen: str) -> list[str]:
    errs = []
    if liquid_canal(reg, "RM_Liquid_Chemfuel") != "RM_Fluid_Chemfuel":
        errs.append("registry: RM_Liquid_Chemfuel has no canalFluid RM_Fluid_Chemfuel")
    block = gen.split('"chemfuel": {', 1)[-1].split("},", 1)[0]
    if '"canalFluid": "RM_Fluid_Chemfuel"' not in block:
        errs.append("generator table: the chemfuel row does not name RM_Fluid_Chemfuel (a regenerate would drop it)")
    return errs


def case_astro(astro: str) -> list[str]:
    return [] if liquid_canal(astro, "RM_Liquid_Astrofuel") == "RM_Fluid_Astrofuel" else [
        "astrofuel adoption patch: RM_Liquid_Astrofuel has no canalFluid RM_Fluid_Astrofuel"]


def case_fluids(fl: str, ter: str) -> list[str]:
    errs = []
    f = fluids(fl)
    t = terrain_names(ter)
    want = {"RM_Fluid_Chemfuel": "Inferno", "RM_Fluid_Astrofuel": "Detonation"}
    for name, kind in want.items():
        el = f.get(name)
        if el is None:
            errs.append(name + ": FluidDef missing")
            continue
        if el.findtext("fireKind") != kind:
            errs.append(name + ": fireKind " + str(el.findtext("fireKind")) + ", want " + kind)
        for slot in ("floodTerrain", "fillTerrainHalf", "fillTerrainBrim", "fillTerrainSuperdeep"):
            tn = el.findtext(slot)
            if not tn or tn not in t:
                errs.append(name + ": " + slot + " " + str(tn) + " is not a TerrainDef in " + TERRAIN.name)
    return errs


def main() -> int:
    reg, gen, astro = REGISTRY.read_text("utf-8"), GENERATOR.read_text("utf-8"), ASTRO.read_text("utf-8")
    fl, ter = FLUIDS.read_text("utf-8"), TERRAIN.read_text("utf-8")
    fire = FIRE.read_text("utf-8").replace("\r\n", "\n")
    cases = [
        ("chemfuel_registry_names_canal_fluid", lambda: case_registry(reg, gen),
         lambda: case_registry(reg.replace("<canalFluid>RM_Fluid_Chemfuel</canalFluid>", ""), gen)),
        ("astrofuel_patch_names_canal_fluid", lambda: case_astro(astro),
         lambda: case_astro(astro.replace("<canalFluid>RM_Fluid_Astrofuel</canalFluid>", ""))),
        ("fuel_fluids_exist_with_fire_kinds", lambda: case_fluids(fl, ter),
         lambda: case_fluids(fl.replace("<fireKind>Inferno</fireKind>", "<fireKind>Detonation</fireKind>"), ter)),
    ]
    for needle, why in FIRE_SHAPES:
        cases.append(("fire_shape: " + why, lambda n=needle, w=why: [] if n in fire else [w + " (missing)"],
                      lambda n=needle, w=why: [w] if n not in fire.replace(n, "") else []))
    failed = 0
    for name, run, undo in cases:
        errs = run()
        red = undo()
        if errs:
            failed += 1
            print("FAIL " + name + ": " + "; ".join(errs))
        elif not red:
            failed += 1
            print("FAIL " + name + ": stays green with the fix taken out (cannot fail)")
        else:
            print("PASS " + name)
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
