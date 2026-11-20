#!/usr/bin/env python3
"""selftest_designate_harvest_wood.py - designate_batch HarvestPlant takes a grown tree, as vanilla does.

RIMMANDRAKE_LET_BRIDGE_CHOP_TREES_NOT_ONLY_CROPS, measured live 2026-11-14 on RM_Nogtyl growth 1:
CutPlant and HarvestPlant both gave skippedWrongType=1, so no bridge route marked a grown tree for
cutting. Vanilla 1.6 gives the HarvestPlant designation from TWO designators (read by RimSage):
Designator_PlantsHarvest (HarvestableNow && harvestTag == "Standard") and
Designator_PlantsHarvestWood (HarvestableNow && IsTree, refused when CompPlantPreventCutting says so).
CanDesignateThingByType in JawaBenchMapTools.cs copied only the first.

The behaviour needs a running game; this pins the SOURCE shape offline (the companion is compiled by
build.py, which needs Windows dotnet). Mutation probes prove each check can fail.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "JawaBench.BridgeTools" / "JawaBenchMapTools.cs"


def harvest_case(text: str) -> str:
    fn = text.index("private static bool CanDesignateThingByType(")
    start = text.index('case "HarvestPlant":', fn)
    end = text.index("case ", start + len('case "HarvestPlant":'))
    return text[start:end]


def problems(case: str) -> list[str]:
    out = []
    flat = re.sub(r"\s+", " ", case)
    if "HarvestableNow" not in flat:
        out.append("HarvestPlant does not require HarvestableNow")
    if 'harvestTag == "Standard"' not in flat:
        out.append("HarvestPlant lost the crop branch (harvestTag == \"Standard\")")
    if "IsTree" not in flat:
        out.append("HarvestPlant has no tree branch (Designator_PlantsHarvestWood: IsTree)")
    if "PreventCutting" not in flat:
        out.append("tree branch does not refuse CompPlantPreventCutting.PreventCutting")
    # The two branches must be alternatives, not both required: a tree has harvestTag Wood.
    if "IsTree" in flat and 'harvestTag == "Standard"' in flat and "||" not in flat:
        out.append("crop and tree branches are joined by && only, so a tree (harvestTag Wood) is still refused")
    return out


GOOD = '''case "HarvestPlant":
    return t.def.plant != null && t is Plant hp && hp.HarvestableNow
        && (hp.def.plant.harvestTag == "Standard"
            || (hp.def.plant.IsTree
                && !(hp.TryGetComp(out CompPlantPreventCutting hpc) && hpc.PreventCutting)));
'''
MUTANTS = {
    "crop only (the base bug)": '''case "HarvestPlant":
    return t.def.plant != null && t is Plant hp
        && hp.HarvestableNow && hp.def.plant.harvestTag == "Standard";
''',
    "no PreventCutting guard": GOOD.replace("&& !(hp.TryGetComp(out CompPlantPreventCutting hpc) && hpc.PreventCutting)", ""),
    "branches ANDed": GOOD.replace("||", "&&"),
    "no HarvestableNow": GOOD.replace("hp.HarvestableNow", "true"),
}


def main() -> int:
    fails = 0
    if problems(GOOD):
        print(f"FAIL probe: the good shape reads as broken: {problems(GOOD)}")
        fails += 1
    for name, m in MUTANTS.items():
        if not problems(m):
            print(f"FAIL probe: mutant '{name}' was not caught")
            fails += 1
    try:
        case = harvest_case(SRC.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"UNMEASURED: could not read the HarvestPlant case in {SRC}: {e}")
        return 2
    for p in problems(case):
        print(f"FAIL source: {p}")
        fails += 1
    print(f"{'FAIL' if fails else 'PASS'}: designate_batch HarvestPlant tree branch "
          f"({len(MUTANTS)} mutants, {fails} failure(s))")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
