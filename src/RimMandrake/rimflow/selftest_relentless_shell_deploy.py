#!/usr/bin/env python3
"""selftest_relentless_shell_deploy.py -- GAMEENV_FIX_DEPLOY_590E0C49_ITEMS_WAIT: a build touching only the compose
settings shell (BiomesShell/Assemblies/RimMandrake.Biomes.dll) is deployable and checkable by the live lane.

The instance: WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE at c4fe891da8b0 changed only the shell DLL and its .srchash. The
lane's folded map (deploy_custom_mods.folded) holds compose ENTRIES, not the shell, so deploy_args planned `--mod
BiomesShell`, the plan's shell line ("compose  (settings shell)  BiomesShell ...") matched no section regex, and every
run read "the deploy plan does not cover BiomesShell: name it in --deploy". No game, bridge or ledger here.

    python3 src/RimMandrake/rimflow/selftest_relentless_shell_deploy.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless_live as L                 # noqa: E402
import relentless_live_round as RR          # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import deploy_custom_mods as D              # noqa: E402

FAILS = []


def ok(cond, what):
    print("%s  %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


FILES = [("BiomesShell", "Assemblies/RimMandrake.Biomes.dll"), ("BiomesShell", "Assemblies/RimMandrake.Biomes.dll.srchash")]
PLAN = """compose: biomes  (manifest src/RimMandrake/Biomes.compose.json)
  compose  BlueDesert           mandrake.rm.bluedesert                9 file(s) -> Biomes/BlueDesert
  compose  (settings shell)     BiomesShell                           2 file(s) -> Assemblies/
repo : /x/src
RimMandrake.Biomes mandrake.rm.biomes         5 file(s) HELD
Everything in sync.
"""
DRIFT_PLAN = """compose: biomes  (manifest src/RimMandrake/Biomes.compose.json)
  compose  (settings shell)     BiomesShell                           2 file(s) -> Assemblies/
RimMandrake.Biomes mandrake.rm.biomes         5 file(s) HELD
    ~ Assemblies/RimMandrake.Biomes.dll
Drift found. Re-run with --apply to deploy.
"""


def main():
    # 1. the real manifest names the shell, and the lane's folded map now carries it
    shells = L.compose_shells(D.SRC_ROOT)
    ok(shells.get("BiomesShell") == "RimMandrake.Biomes", "compose_shells reads BiomesShell -> RimMandrake.Biomes: %r" % shells)
    real = D.folded()
    ok("BiomesShell" not in real, "deploy_custom_mods.folded() itself still omits the shell (the instance's cause)")
    folded = L.with_shell(real, shells)
    ok(folded.get("BiomesShell") == ("RimMandrake.Biomes", "RimMandrake.Biomes"), "with_shell adds (target, target)")
    ok(all(folded[k] == v for k, v in real.items()), "with_shell keeps every compose entry as it was")
    ok(RR.RoundFx.folded(RR.RoundFx.__new__(RR.RoundFx)).get("BiomesShell") == ("RimMandrake.Biomes",) * 2,
       "RoundFx.folded carries the shell")
    # plain L.Fx is what relentless_live.run (deploy_gap(..., fx.folded())) and relentless_game preflight/carry use
    fx_map = L.Fx.__new__(L.Fx).folded()
    ok(fx_map.get("BiomesShell") == ("RimMandrake.Biomes",) * 2, "Fx.folded carries the shell: %r" % (fx_map.get("BiomesShell"),))
    ok(L.deploy_gap(FILES, 0, PLAN, (), fx_map) is None, "Fx.folded's map reads the in-sync shell plan as covered")

    # 2. the instance: deploy_args composes, the plan covers, drift is seen
    args = RR.deploy_args(["BiomesShell"], folded)
    ok(args.startswith("--compose biomes") and "BiomesShell" not in args, "deploy_args composes the shell: %r" % args)
    ok(RR.deploy_args(["BiomesShell"], real) == "--mod BiomesShell", "without the shell the old args were --mod BiomesShell")
    before = L.deploy_gap(FILES, 0, PLAN, (), real)
    ok(before and "does not cover BiomesShell" in before, "the old folded map reproduces the instance: %r" % before)
    ok(L.deploy_gap(FILES, 0, PLAN, (), folded) is None, "the shell-aware map reads the in-sync plan as covered")
    gap = L.deploy_gap(FILES, 1, DRIFT_PLAN, (), folded)
    ok(gap and "out of date" in gap and "BiomesShell/Assemblies/RimMandrake.Biomes.dll" in gap,
       "a drifting shell DLL is caught, named by its source: %r" % gap)
    ok(L.deploy_gap(FILES, 0, "nothing here\nEverything in sync.\n", (), folded), "a plan with no compose is still a gap")

    # 3. the game copy is found at Mods/<target>/<rel>, not Mods/<target>/Biomes/<key>
    with tempfile.TemporaryDirectory() as mods:
        dll = os.path.join(mods, "RimMandrake.Biomes", "Assemblies", "RimMandrake.Biomes.dll")
        os.makedirs(os.path.dirname(dll))
        open(dll, "wb").close()
        ok(L.deployed_paths(mods, "BiomesShell", "Assemblies/RimMandrake.Biomes.dll", folded) == [dll],
           "deployed_paths finds the shell DLL in the composed mod's root")
        ok(L.deployed_paths(mods, "BiomesShell", "Assemblies/RimMandrake.Biomes.dll", real) == [],
           "the old map found no game copy")
        bd = os.path.join(mods, "RimMandrake.Biomes", "Biomes", "BlueDesert", "About.txt")
        os.makedirs(os.path.dirname(bd))
        open(bd, "w").close()
        if "BlueDesert" in folded:
            ok(L.deployed_paths(mods, "BlueDesert", "About.txt", folded) == [bd], "a compose entry still maps to Biomes/<key>")

    print("FAILS: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
