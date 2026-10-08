#!/usr/bin/env python3
"""selftest_seashores_proofs.py -- offline proof for SeaShores' sea_shore_rules chain (SEASHORES_COVERAGE_GAPS_1).

Run bare: python3 src/RimMandrake/SeaShores/selftest_seashores_proofs.py   (exit 0 = clean)

A mock jawa/static_call answers RM_SeaShoresProof.ProofShore the way the shipped C# does. Clean must PASS (the planet-
dependent bars UNMEASURED, never PASS, when no land tile sits beside a modded sea; the map-generation stub always
UNMEASURED; a stale DLL UNMEASURED); each planted break must redden its component. Statically, planted source breaks
(a gate removed, a Harmony seam retargeted, the transpiler's cell push dropped, the proof left out of the csproj) must
redden static_findings, and the shipped source must be clean.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
CHAIN = "sea_shore_rules"


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def proof_text(brk, tiles=True, heal_setting=True, map_=True):
    d = dict(seas=2, heal_setting=heal_setting, coast_def=True, rare_orig_biome_loads=2, rare_redirects=2, rare_biome_loads_left=0,
             shore_suppressed_when_on=False, shore_suppressed_when_off=True)
    if "transpiler_noop" in brk:
        d.update(rare_redirects=0, rare_biome_loads_left=2)
    if "transpiler_partial" in brk:
        d.update(rare_redirects=1, rare_biome_loads_left=1)
    if "shore_ignored" in brk:
        d["shore_suppressed_when_off"] = False
    if map_:
        d.update(fish_off_is_land=("fish_off_ignored" not in brk), fish_centre_is_sea_water=False, fish_on_is_land_when_not_sea=("fish_on_wrong" not in brk))
    else:
        d.update(fish_off_is_land="-", fish_on_is_land_when_not_sea="-")
    if not tiles:
        d.update(tiles_beside_sea=0, coast_on="-", coast_off="-", sub_sea="-", sub_other_mutator="-", sub_vanilla="-",
                 heal_left=0, heal_stale_left=0, heal_already=0)
    else:
        d.update(tiles_beside_sea=7, coast_on=("seas_ignored" not in brk), coast_off=("off_ignored" in brk),
                 sub_sea=("no_sub" not in brk), sub_other_mutator=("sub_all" not in brk), sub_vanilla=("vanilla_replaced" not in brk),
                 heal_left=3 if "heal_leaves" in brk else 0, heal_stale_left=0, heal_already=7)
    return " ".join("%s=%s" % kv for kv in d.items())


def make_ext(brk, stale=False, **kw):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF:
            return None
        if stale:
            return {"success": False, "message": "no public static method ProofShore"}
        return {"success": True, "result": proof_text(brk, **kw)}
    return ext


def run(brk=(), stale=False, **kw):
    suite = Suite("SeaShoresProofs")     # only the proof chain: the legacy chain screenshots the real desktop
    suite.chain(CHAIN)(V.sea_shore_rules)
    game = MockGame()
    game.ext = make_ext(set(brk), stale=stale, **kw)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])


def main():
    srcs = V.load_sources()
    check("static_findings clean on the shipped source", V.static_findings(srcs) == [], V.static_findings(srcs))

    clean = run()
    stub = "sea_water_catch_and_fresh_shore_terrain_state_read"
    check("clean: every non-stub bar PASSes", all(v == "PASS" for k, v in clean.items() if k != stub), clean)
    check("clean: the map-generation stub is UNMEASURED, never PASS", clean[stub] == "UNMEASURED", clean)
    got = run(tiles=False)
    tile_bars = ["seasCountAsCoast_makes_land_beside_a_sea_coastal_and_off_restores_vanilla",
                 "worldgen_prefix_swaps_coast_for_sea_coast_only_beside_a_sea", "healer_leaves_nothing_to_heal_after_load"]
    check("no tile beside a sea: the 3 tile bars UNMEASURED, never PASS", all(got[k] == "UNMEASURED" for k in tile_bars), got)
    check("no tile beside a sea: the always-readable bars still PASS", got["generateSeaShores_switch_suppresses_the_shore"] == "PASS"
          and got["rare_catch_transpiler_rewrote_the_patched_il"] == "PASS", got)
    check("heal setting off: healer bar UNMEASURED", run(heal_setting=False)["healer_leaves_nothing_to_heal_after_load"] == "UNMEASURED")
    check("no current map: fish bar UNMEASURED", run(map_=False)["seaCatchTables_off_arm_returns_the_land_biome_and_land_cells_stay_land"] == "UNMEASURED")
    check("stale DLL: proof bars UNMEASURED, never PASS", run(stale=True)["generateSeaShores_switch_suppresses_the_shore"] == "UNMEASURED")

    for brk, comp in (("transpiler_noop", "rare_catch_transpiler_rewrote_the_patched_il"), ("transpiler_partial", "rare_catch_transpiler_rewrote_the_patched_il"),
                      ("shore_ignored", "generateSeaShores_switch_suppresses_the_shore"),
                      ("fish_off_ignored", "seaCatchTables_off_arm_returns_the_land_biome_and_land_cells_stay_land"),
                      ("fish_on_wrong", "seaCatchTables_off_arm_returns_the_land_biome_and_land_cells_stay_land"),
                      ("seas_ignored", "seasCountAsCoast_makes_land_beside_a_sea_coastal_and_off_restores_vanilla"),
                      ("off_ignored", "seasCountAsCoast_makes_land_beside_a_sea_coastal_and_off_restores_vanilla"),
                      ("no_sub", "worldgen_prefix_swaps_coast_for_sea_coast_only_beside_a_sea"),
                      ("sub_all", "worldgen_prefix_swaps_coast_for_sea_coast_only_beside_a_sea"),
                      ("vanilla_replaced", "worldgen_prefix_swaps_coast_for_sea_coast_only_beside_a_sea"),
                      ("heal_leaves", "healer_leaves_nothing_to_heal_after_load")):
        got = run((brk,))
        check("break %-18s reddens %s" % (brk, comp), got.get(comp) == "FAIL", got.get(comp))

    def mutate(fn, old, new, tag, must):
        mut = dict(srcs)
        check("source break (%s) is findable in the shipped text" % tag, old in mut[fn], old)
        mut[fn] = mut[fn].replace(old, new)
        got = V.static_findings(mut)
        check("source break %-26s reddens static_findings" % tag, any(must in g for g in got), got)

    H = "RM_SeaShoresHarmony.cs"
    mutate(H, "!RM_SeaShoresSettings.Cur.seasCountAsCoast", "false", "coast switch ignored", "[seasCountAsCoast]")
    mutate("RM_SeaShoreUtility.cs", "!RM_SeaShoresSettings.Cur.seaCatchTables", "false", "FishBiomeFor switch ignored", "[seaCatchTables]")
    mutate(H, "if (!RM_SeaShoresSettings.Cur.seaCatchTables || __instance?.map == null)", "if (__instance?.map == null)", "SetFishTypes switch ignored", "[seaCatchTables]")
    mutate("RM_TileMutatorWorker_SeaCoast.cs", "RM_SeaShoresSettings.Cur.generateSeaShores,", "false,", "shore switch ignored", "[generateSeaShores]")
    mutate("RM_WorldComponent_SeaShoreHealer.cs", "!RM_SeaShoresSettings.Cur.healFrozenWorldOnLoad", "false", "heal switch ignored", "[healFrozenWorldOnLoad]")
    mutate(H, "nameof(World.CoastDirectionAt)", "nameof(World.CoastAngleAt)", "coast hook retargeted", "[wiring]")
    mutate(H, "ci.opcode = OpCodes.Ldarg_1;", "ci.opcode = OpCodes.Ldarg_0;", "transpiler cell push dropped", "[wiring]")
    mutate(H, "mutator = RM_SeaShoresDefOf.RM_SeaCoast;", "", "prefix no longer substitutes", "[wiring]")
    mutate(H, "mutator != TileMutatorDefOf.Coast", "false", "prefix rewrites every mutator", "[wiring]")
    mutate("RM_WorldComponent_SeaShoreHealer.cs", "Heal(world.grid.Surface, true,", "Heal(world.grid.Surface, false,", "healer no longer applies", "[wiring]")
    mutate("RM_TileMutatorWorker_SeaCoast.cs", "return ShoreSuppressed ? null : base.CoastTerrainAt(cell, map);", "return base.CoastTerrainAt(cell, map);", "suppressed shore lays coast", "[wiring]")
    mutate("RM_SeaShoresSettings.cs", 'Scribe_Values.Look(ref seaCatchTables, "seaCatchTables", true);', "", "setting unscribed", "[settings]")
    mutate("RM_SeaShores.csproj", 'Compile Include="RM_SeaShoresProof.cs"', 'Compile Include="X.cs"', "proof left out of csproj", "[wiring]")

    if FAILS:
        print("\n%d SeaShores proof selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall SeaShores proof selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
