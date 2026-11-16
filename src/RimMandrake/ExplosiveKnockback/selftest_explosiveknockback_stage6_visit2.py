#!/usr/bin/env python3
"""Offline guards for the proof-scene faults Stage 6 visit 2 found live (2026-11-15,
design/concepts/ExplosiveKnockback/version/in_game/visit_2/SUMMARY.md). Read from the C# source, since the scenes only run
in a game:
  B1 SITE: a quicktest map's natural pond leaves FlowWorks a dry bed (bedGrid, depth 2 or 4) under the scene origin.
     Prepare paints the water to Soil but the bed stays, so the relative climb rule reads the takeoff cell at depth 4 and a
     colonist thrown into a depth-5 pit drops one notch: no descent (sc_pit_fall FAIL descents=0 at origin 12,12 on a
     BorealForest map; the same scene at a clean origin passed). Origins skips a candidate whose scene rect holds natural
     water, a lakebed or a natural bed (FlowWorks' IsNaturalBed), and Stage refuses INVALID when any cell of the prepared
     rect still reads a FlowWorks climb depth.
  G1 HARNESS: gas_into_pit_off lights the same cloud with the gas chain unhooked; vanilla fire then sets the colonist
     alight and a burning colonist runs (live: "Burning (fire size 31)", "Moving.", 4 to 9 cells, 2 of 4 runs). The
     control still refuses any burst, launch, descent or pit; it allows cells moved only when the colonist burned, and
     reports burned and cells.
  O1 HARNESS: goods_obstacles' lanes S and W blast at O(0, +-5), but WantCells measured each component's distance from the
     scene origin (5.1 cells, outside the 2.9 radius): want=0, INVALID on every run. The lane's want is measured from its own
     blast centre (WantCellsFrom).
  P1 HARNESS: storeroom_bomb_pit planned the cover stack against the uncovered pit (a pit stops a throw on its first cell),
     then re-planned with the cover built (a covered cell does not stop it), so no stack ever matched: INVALID on every run.
     The cover goes on first, and the stack is searched with it in place.
  F1 SITE: pit_goods_fetch runs 60000 ticks; FlowWorks' rain filled both 3x3 pits to 2 m (WaterDeep, measured live), and
     dug water 2 m deep is swum (owner R12), so the hauler swam into the raised-ladder control pit and carried its steel
     out (sc_pit_fetch FAIL, visit 1 and visit 2). The scene turns rainFillsExcavationsEnabled off and restores it.
  R1 HARNESS: validation.py's walk (sc_walk_raid) required mandrake.rm.cauldron in activeMods, but the Cauldron is folded
     into mandrake.rm.biomes (Biomes.compose.json) and the owner's full list has no mandrake.rm.cauldron: W_PRECONDITIONS
     could never pass. MODS_NEEDED names no folded member's packageId and names the composite.
  R2 HARNESS: the walk's _pos read a thing's cell from a `position` dict, but jawa/list_things answers top-level x/z
     (measured live), so every pre-shell census crashed (NoneType - int) and the walk read "no game reachable". _pos
     reads both shapes and returns None when neither is there.
  R3 HARNESS: the walk lit its gas with jawa/map_fire on the --lit cell; on bare soil it answered firesStarted 0 (measured
     twice), so the gas rows read FAIL "0 bursts" when the walk never lit anything. A refused fire gets one wood log of
     kindling and a second try; a gas act whose fire never started is UNMEASURED, not FAIL.

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_stage6_visit2.py [--src DIR]
--src reads the mod's Source/ from DIR (laid out like this folder).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(code, ok, what):
    print("%s %s %s" % ("PASS" if ok else "FAIL", code, what))
    if not ok:
        fails.append(code)


def method(src, signature):
    """The body of the first method whose declaration contains `signature`, to its closing brace at that indent."""
    i = src.find(signature)
    if i < 0:
        return ""
    m = re.compile(r"\n        \}\n").search(src, i)
    return src[i:m.end()] if m else src[i:]


def main():
    root = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else HERE
    src = os.path.join(root, "Source")
    proof = open(os.path.join(src, "RM_KnockbackProof.cs"), encoding="utf-8").read()
    compat = open(os.path.join(src, "RM_KnockbackCompat.cs"), encoding="utf-8").read()
    origins = method(proof, "public static string Origins(")
    if "PondSite(" in origins:
        origins += method(proof, "private static bool PondSite(")
    stage = method(proof, "public static string Stage(")
    check("B1a", '"ClimbDepthAt"' in compat and '"IsNaturalBed"' in compat,
          "compat resolves FlowWorks' ClimbDepthAt and IsNaturalBed by name")
    check("B1b", "public static int ClimbDepthAt(Map" in compat and "public static bool NaturalBedAt(Map" in compat,
          "compat exposes ClimbDepthAt(map, c) and NaturalBedAt(map, c)")
    check("B1c", "NaturalBedAt(" in origins and "IsWater" in origins and "RM_Lakebed" in origins,
          "Origins skips a scene rect with natural water, a lakebed or a natural bed")
    prep = stage.find("Prepare(s.o")
    after = stage[prep:] if prep >= 0 else ""
    check("B1d", prep >= 0 and "ClimbDepthAt(" in after and "INVALID" in after[:after.find("Build(s)")] if "Build(s)" in after
          else False, "Stage reads every prepared cell's climb depth and refuses INVALID before Build")
    i = proof.find('if (sc.name == "gas_into_pit_off")')
    off = proof[i:i + 900] if i >= 0 else ""
    ret = off[off.find("return Result("):off.find(";", off.find("return Result("))] if "return Result(" in off else ""
    check("G1", "burned" in off and "cells == 0 || burned" in ret and "launch.Count == 0" in ret and "!inPit" in ret
          and "desc.Count == 0" in ret and "bursts == 0" in ret,
          "gas_into_pit_off allows a fire run (burned) but still refuses burst, launch, descent and pit")
    go = open(os.path.join(src, "RM_KnockbackProof_GoodsObstacles.cs"), encoding="utf-8").read()
    check("O1", "private static int WantCellsFrom(" in proof and "WantCellsFrom(s, k, O(s, 0, ObstacleLaneZ[i]), 2.9f)" in go
          and "WantCells(s, k, 2.9f)" not in go, "goods_obstacles measures each lane's want from that lane's blast centre")
    sb = open(os.path.join(src, "RM_KnockbackProof_StoreroomBombPit.cs"), encoding="utf-8").read()
    j = sb.find("IntVec3 coverFrom = IntVec3.Invalid")
    blk = sb[j:sb.find("no floor stack within two cells whose planned throw ends on a covered", j)] if j >= 0 else ""
    b, pl = blk.find('Build("RM_PitCover_WovenScrap"'), blk.find("PlanGood(")
    check("P1", b >= 0 and pl > b, "storeroom_bomb_pit builds the cover before it plans the stack that must land on it")
    pf = proof[proof.find('case "pit_goods_fetch"'):]
    pf = pf[:pf.find("s.verdict = sc =>")]
    check("F1", '"rainFillsExcavationsEnabled"' in pf and "SetValue(null, false)" in pf and "rfWas" in pf
          and pf.find("s.restore") >= 0, "pit_goods_fetch keeps rain out of its pits for the run and restores the setting")
    val = open(os.path.join(root, "validation.py"), encoding="utf-8").read()
    m = re.search(r"MODS_NEEDED = \(([^)]*)\)", val)
    needed = re.findall(r'"([^"]+)"', m.group(1)) if m else []
    rm = os.path.abspath(os.path.join(root, ".."))
    folded = set()
    comp = os.path.join(rm, "Biomes.compose.json")
    if os.path.exists(comp):
        import json
        for e in json.load(open(comp, encoding="utf-8")).get("entries", []):
            about = os.path.join(rm, e.get("source", ""), "About", "About.xml")
            if os.path.exists(about):
                pm = re.search(r"<packageId>([^<]+)</packageId>", open(about, encoding="utf-8").read())
                if pm:
                    folded.add(pm.group(1).strip().lower())
    check("R1", bool(needed) and bool(folded) and not (set(n.lower() for n in needed) & folded)
          and "mandrake.rm.biomes" in needed, "the walk's MODS_NEEDED %s names no folded member (%d read) and the composite"
          % (needed, len(folded)))
    sys.path.insert(0, root)
    try:
        import validation as V
        got = (V._pos({"x": 3, "z": 4}), V._pos({"position": {"x": 5, "z": 6}}), V._pos({"def": "Steel"}))
    except Exception as ex:  # noqa: BLE001
        got = ("raised %s" % ex,)
    check("R2", got == ((3, 4), (5, 6), None), "the walk's _pos reads top-level x/z and position{x,z}, None otherwise: %r" % (got,))
    ga = val[val.find("def gas_act("):val.find("def judge_gas(")]
    jg = val[val.find("def judge_gas("):val.find("def judge_gas(") + 2500]
    check("R3", "firesStarted" in ga and "WoodLog" in ga and "self.fire_ok" in ga and "fire_ok" in jg and "UNMEASURED" in jg,
          "the walk's gas act retries a refused fire with kindling and its judge reads UNMEASURED when no fire started")
    print("explosiveknockback stage6 visit2: %d failed" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
