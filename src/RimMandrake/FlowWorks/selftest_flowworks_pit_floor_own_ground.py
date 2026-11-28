#!/usr/bin/env python3
"""RIMMANDRAKE_DARKEN_PIT_FLOOR_BELOW_GROUND_SLATE_DRAWS_BRIGHTER: a dry pit floor prints the ground it was dug in.

Measured live 2026-11-23 (build 81ee41df54, northstar/pit_floor_ground_live.py): the floor drew 60-65 grey at 0.5 m on every
ground, because the depth tone (RM_PitReliefMath.StepK) was laid over the one gravel floor terrain (RM_Channel_*). On rich
soil, marsh, mud and slate the 0.5 m floor was as bright as its ground or brighter. The fix (build B of the item): the walls
layer prints the recorded ground (RM_MapComponent_Excavation.OriginalTerrainAt) over the dry floor, and the floor's shade is
the "on its own ground" one, so the floor draws StepK of THAT ground. The numbers are the C# case
PitStepped_floor_on_its_own_ground_draws_under_that_ground (selftest_flowworks_stock.py); this checks the wiring.

CAN IT FAIL: each wire taken out of a copy of the source must go red (run at the end). `--rev <git rev>` reads the files at
that commit instead (the parent of the fix reads RED).

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_pit_floor_own_ground.py [--rev HEAD~1]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "Source"
sys.path.insert(0, str(HERE))
from selftest_flowworks_underliquid_parity import mask_comments, method_body  # noqa: E402

FILES = {"walls": SRC / "Superdeep" / "RM_ExcavationWalls.cs", "math": SRC / "RM_PitReliefMath.cs",
         "face": SRC / "Superdeep" / "RM_FaceMaterial.cs", "cases": SRC / "SelfTest" / "PitSteppedReliefChecks.cs"}


def checks(t: dict) -> list[tuple[str, bool]]:
    walls, math, face = mask_comments(t["walls"]), mask_comments(t["math"]), mask_comments(t["face"])
    regen = method_body(walls, r"public override void Regenerate\(\)")
    gmat = method_body(walls, r"private static Material FloorGroundMat\(Map map, RM_MapComponent_Excavation eng, IntVec3 c, bool materialLook\)")
    relief = method_body(walls, r"private void ReliefCell\(Map map, RM_MapComponent_Excavation eng, IntVec3 c, int d, "
                                r"RM_PitReliefMath\.StepPlan sp, bool dry, float sc, float y,\s*bool onGround\)")
    water = method_body(walls, r"private void WaterSurface\([^)]*Material groundFloor\)")
    prints = method_body(math, r"public static bool FloorPrintsGround\(bool materialLook, bool laidFloorOnTop, bool groundPrintable\)")
    return [
        ("the rule is Verse-free and needs all three conditions", bool(prints) and "using Verse" not in math
         and "materialLook && !laidFloorOnTop && groundPrintable" in prints),
        ("the ground is the terrain recorded before the first cut", bool(gmat) and "eng.OriginalTerrainAt(c)" in gmat),
        ("a floor laid on the square is never printed over", "top.layerable" in gmat and "RM_PitReliefMath.FloorPrintsGround(" in gmat),
        ("a liquid ground is never printed as a floor", "!g.IsWater" in gmat and "RM_FluidIdentity.FluidOfTerrain(g) == null" in gmat),
        ("the print is the ground as vanilla draws it there (polluted look)", "map.terrainGrid.GetMaterial(g, polluted" in gmat
         and "c.IsPolluted(map)" in gmat and "RM_FaceMaterial.FaceMat(" in gmat),
        ("the layer asks for the ground on a dry square, gated by the material look",
         bool(regen) and "FloorGroundMat(map, eng, c, material)" in regen),
        ("a dry floor prints the ground over the whole square under the faces",
         "Quad(ground, c.x, c.z, 1f, 1f, y - 0.0008f, Opaque, Opaque, UvWorld);" in regen),
        ("the stepped rule's shade is the on-its-ground one", bool(relief)
         and "RM_PitReliefMath.StepFloorShade(d, onGround)" in relief and "ReliefCell(map, eng, c, d, sp, note == 0 || sheet, sc, y, ground != null)" in regen),
        ("the lip band follows the printed ground", "LipBands(c, d, sp, y + 0.0005f, onGround)" in relief),
        ("the old law's shade is the on-its-ground one", "RM_PitReliefMath.FloorShade(d, ground != null)" in regen),
        ("the dry pit under a clear sheet shows the same ground", bool(water) and "groundFloor ??" in water
         and "relief, y - 0.0008f, ground);" in regen),
        ("a polluted square re-meshes the floor", "MapMeshFlagDefOf.Pollution" in walls),
        ("the face material takes a terrain material variant", "public static Material FaceMat(Material terrainMat)" in face),
        ("the C# case exists", '"PitStepped_floor_on_its_own_ground_draws_under_that_ground"' in t["cases"]),
    ]


def run(rows) -> int:
    bad = 0
    for name, ok in rows:
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    return bad


def read(rev: str | None) -> dict:
    out = {}
    for k, p in FILES.items():
        if rev is None:
            out[k] = p.read_text(encoding="utf-8") if p.exists() else ""
            continue
        rel = p.relative_to(HERE.parents[2]).as_posix()
        r = subprocess.run(["git", "-C", str(HERE), "show", "%s:%s" % (rev, rel)], capture_output=True, text=True)
        out[k] = r.stdout if r.returncode == 0 else ""
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev", default=None, help="read the files at this git revision")
    a = ap.parse_args(argv)
    t = read(a.rev)
    bad = run(checks(t))
    if a.rev is None:
        plants = [
            ("the print removed", "walls", "Quad(ground, c.x, c.z, 1f, 1f, y - 0.0008f, Opaque, Opaque, UvWorld);", ""),
            ("the dug terrain kept as the ground", "walls", "eng.OriginalTerrainAt(c);\n\t\t\tbool printable", "top;\n\t\t\tbool printable"),
            ("the laid-floor guard removed", "walls", "top != null && top.layerable", "false"),
            ("the stepped shade back on gravel", "walls", "RM_PitReliefMath.StepFloorShade(d, onGround)", "RM_PitReliefMath.StepFloorShade(d)"),
            ("the old-law shade back on gravel", "walls", "RM_PitReliefMath.FloorShade(d, ground != null)", "RM_PitReliefMath.FloorShade(d)"),
            ("the sheet's floor back on gravel", "walls", "groundFloor ??", "null ??"),
            ("the material-look gate dropped", "math", "materialLook && !laidFloorOnTop", "!laidFloorOnTop"),
        ]
        for name, key, old, new in plants:
            if old not in t[key]:
                print("FAIL can-fail: " + name + " (the planted text is gone from the source)")
                bad += 1
                continue
            t2 = dict(t)
            t2[key] = t[key].replace(old, new)
            caught = any(not ok for _, ok in checks(t2))
            print(("PASS " if caught else "FAIL ") + "can-fail: " + name + " goes red")
            bad += not caught
    print("RESULT", "GREEN" if not bad else "RED %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
