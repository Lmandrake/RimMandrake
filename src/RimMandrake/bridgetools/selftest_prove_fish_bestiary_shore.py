#!/usr/bin/env python3
"""Offline selftest of prove_fish_bestiary_live.py's shore rows (SEA_FLOOR_AND_CATCH_PASS_1 A2), no game.

The live row generates a map beside each sea and reads its salt water's fish. Two choices made offline decide what it
reads: which water terrain on that map is the sea's (the sea's RM_SeaShoreExtension, or vanilla ocean when the extension
sets none), and which catches count (the sea's own fishTypes). This test reads both off the shipped BiomeDefs and off a
planted defs folder whose answers are known.
"""
import os
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "Utils"))
import prove_fish_bestiary_live as P  # noqa: E402

SEAS = {"Twilight": "RM_TwilightSea", "Scald": "RM_TheScald", "Grey": "RM_GreySea", "Chill": "RM_TheChill"}

PLANTED = """<?xml version="1.0" encoding="utf-8"?>
<Defs>
  <BiomeDef><defName>RM_TwilightSea</defName>
    <modExtensions><li Class="RimMandrake.SeaShores.RM_SeaShoreExtension" /></modExtensions>
    <fishTypes><saltwater_Common><RM_ACatch>1</RM_ACatch></saltwater_Common>
      <rareCatchesSetMaker>X</rareCatchesSetMaker></fishTypes></BiomeDef>
  <BiomeDef><defName>RM_TheChill</defName>
    <modExtensions><li Class="Other.Ext" /><li Class="RimMandrake.SeaShores.RM_SeaShoreExtension">
      <deepTerrain>D</deepTerrain><shallowTerrain>S</shallowTerrain></li></modExtensions>
    <fishTypes><freshwater_Uncommon><RM_BCatch>1</RM_BCatch><RM_CCatch>2</RM_CCatch></freshwater_Uncommon></fishTypes></BiomeDef>
</Defs>
"""


def main():
    bad = []
    rows = {label: biome for label, biome, _, mode in P.WATERS if mode == "shore"}
    if rows != SEAS:
        bad.append("shore rows are %s, want the four seas %s" % (rows, SEAS))
    for label in SEAS:
        if label not in P.SHORE_SEAS:
            continue
        if not P.sea_catches(label):
            bad.append("%s: no catches read from its shipped BiomeDef" % label)
        water = P.sea_shore_water(label)
        if not water:
            bad.append("%s: no shore water terrain" % label)
    if P.SHORE_SEAS.get("Chill") and P.sea_shore_water("Chill")[0] != "RM_PropaneShallow":
        bad.append("Chill: shore water is %s, want RM_PropaneShallow first" % (P.sea_shore_water("Chill"),))
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "planted.xml").write_text(PLANTED, encoding="utf-8")
        dd = pathlib.Path(d)
        if P.sea_shore_water("Twilight", dd) != P.VANILLA_SEA_WATER:
            bad.append("a bare extension does not fall back to vanilla ocean water: %s" % (P.sea_shore_water("Twilight", dd),))
        if P.sea_shore_water("Chill", dd) != ("S", "D"):
            bad.append("the extension's terrains are not read shallow first: %s" % (P.sea_shore_water("Chill", dd),))
        if P.sea_catches("Twilight", dd) != {"RM_ACatch"}:
            bad.append("the rare-catch maker is counted as a catch, or a catch is lost: %s" % P.sea_catches("Twilight", dd))
        if P.sea_catches("Chill", dd) != {"RM_BCatch", "RM_CCatch"}:
            bad.append("planted Chill catches read as %s" % P.sea_catches("Chill", dd))
        if P.sea_catches("Scald", dd) != set():
            bad.append("a sea absent from the defs reads catches")
    # the exit: a sea with no shore tile (0 tiles before the paint) is no reading, never a FAIL
    for res, want in (({"A": {"water": True, "verdict": "PASS"}}, 0), ({"A": {"water": True, "verdict": "FAIL"}}, 1),
                      ({"A": {"unmeasured": "x"}}, 2), ({"A": {"water": True, "verdict": "PASS"}, "B": {"unmeasured": "x"}}, 2),
                      ({"A": {"water": True, "verdict": "FAIL"}, "B": {"unmeasured": "x"}}, 1), ({}, 2), ({"A": None}, 1)):
        if P.exit_code(res) != want:
            bad.append("exit_code(%s) = %s, want %s" % (res, P.exit_code(res), want))
    for b in bad:
        print("FAIL:", b)
    print("RESULT:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
