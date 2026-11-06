#!/usr/bin/env python3
"""PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO guard: RM_PitFillEffects.ProofDrown must read water through the natural-aware
reader (Swimming.RM_SwimWater.WaterMetresAt), the one RM_Swim.Tick uses, never the excavation component's dug-cells-only
ex.WaterMetresAt — which read 0.00 on natural brine where the swim tick read 2.00.

Reads the C# source: the body of ProofDrown, from its signature to the next `public static`. Exit 0 PASS, 1 FAIL.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs"
SWIM = ROOT / "src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs"


def body(text: str, sig: str) -> str:
    i = text.find(sig)
    if i < 0:
        return ""
    j = text.find("public static", i + len(sig))
    return text[i:j if j > 0 else len(text)]


def main() -> int:
    fails = []
    src = SRC.read_text(encoding="utf-8")
    b = body(src, "public static string ProofDrown(")
    # sanity probe: the instrument can see the method and its water read at all
    if not b or "WaterMetresAt" not in b:
        print(f"FAIL: ProofDrown or its water read not found in {SRC}")
        return 1
    code = "\n".join(l.split("//", 1)[0] for l in b.splitlines())
    if re.search(r"(?<![\w.])ex\.WaterMetresAt\(", code):
        fails.append("ProofDrown still reads ex.WaterMetresAt (dug cells only)")
    if "RM_SwimWater.WaterMetresAt(map, ex, c)" not in code:
        fails.append("ProofDrown does not read Swimming.RM_SwimWater.WaterMetresAt(map, ex, c)")
    swim = SWIM.read_text(encoding="utf-8")
    if "public static float WaterMetresAt(Map map, RM_MapComponent_Excavation ex, IntVec3 c)" not in swim:
        fails.append("RM_SwimWater.WaterMetresAt(Map, ex, IntVec3) signature not found in RM_Swim.cs")
    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print("PASS: ProofDrown reads the natural-aware RM_SwimWater.WaterMetresAt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
