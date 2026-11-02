#!/usr/bin/env python3
"""selftest_flowworks_hot_wet_terrain.py — HOT_RELEASE_FIX_OWN_WET_TERRAIN (GPT finding FA_core_sim_1.4).

WHY: a hot freshwater release fills a dug channel with the freshwater ladder, but RM_HotLiquid.IsFillOf asked only
OwnsFillTerrain, which excludes the ladder: no scald, no steam. The fix: IsFillOf(map, cell, fluid) accepts the
fluid's fill tiers anywhere, and OwnsWetTerrain (ladder included) on a DUG cell only — an undug rung is a lake.
Verse-bound code, so this reads the production .cs (comments blanked) and asserts the fixed shape.

CAN IT FAIL: each check also runs against the pre-fix shape (UNDO) and must go red there.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_hot_wet_terrain.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CS = Path(__file__).resolve().parent / "Source" / "Machinery" / "Kits" / "RM_HotLiquid.cs"

UNDO = """		public static bool IsFillOf(TerrainDef t, FluidDef fluid)
		{
			return t != null && fluid != null && fluid.OwnsFillTerrain(t);
		}
	}
	class X { void A() { if (!RM_HotLiquid.IsFillOf(map.terrainGrid.TerrainAt(pawn.Position), p.fluid)) {} }
	void B() { if (c.InBounds(map) && RM_HotLiquid.IsFillOf(map.terrainGrid.TerrainAt(c), p.fluid)) {} } }
"""


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def is_fill_of_body(text: str) -> str:
    m = re.search(r"public static bool IsFillOf\(([^)]*)\)\s*\{", text)
    if not m:
        return ""
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return m.group(1) + "|" + text[m.end():i]


def checks(text: str) -> list[str]:
    fails = []
    body = is_fill_of_body(text)
    if not body:
        return ["IsFillOf not found"]
    sig = body.split("|", 1)[0]
    if not re.search(r"\bMap\s+map\b", sig) or not re.search(r"\bIntVec3\s+c\b", sig):
        fails.append("IsFillOf does not take (Map, IntVec3, FluidDef)")
    if "OwnsWetTerrain" not in body:
        fails.append("IsFillOf never asks OwnsWetTerrain: the freshwater ladder is not recognised")
    if "IsDugRaw" not in body:
        fails.append("IsFillOf does not gate the ladder on a dug cell: an undug lake would scald")
    if "OwnsFillTerrain" not in body:
        fails.append("IsFillOf dropped OwnsFillTerrain: temp-layer spills over open water are lost")
    calls = re.findall(r"RM_HotLiquid\.IsFillOf\(([^;]*?)\)\)?", text)
    if len(calls) < 2:
        fails.append(f"expected the scald and steam call sites, found {len(calls)}")
    if "IsFillOf(map.terrainGrid" in text:
        fails.append("a call site still passes a bare TerrainDef")
    return fails


def main() -> int:
    text = strip_comments(CS.read_text(encoding="utf-8"))
    fails = checks(text)
    undo_fails = checks(strip_comments(UNDO))
    if not undo_fails:
        fails.append("CAN-IT-FAIL: the pre-fix shape passed every check")
    for f in fails:
        print("FAIL", f)
    print("PASS selftest_flowworks_hot_wet_terrain" if not fails else f"FAILED {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
