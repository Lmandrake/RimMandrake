#!/usr/bin/env python3
"""A build's mod list holds only mods: a src/<tier>/<dir> a commit touched is a mod folder, a folded source, or the
compose shell (which stands for its composed mod). A tooling dir (Utils, bridgetools, rimflow) is not a mod.

OPS_CHURN_DIAGNOSE_PLAYER_YGLE_IHKT (2026-11-05): PLAYER_START_SITE_1 passed offline and was then held in the game phase.
Its batch `modlist_swap.py --enable` listed Utils, bridgetools and BiomesShell, all taken from riders' touched paths, and
modlist_swap refused the whole load ("no About.xml with a packageId in the game folder or the repo"). 20 game-phase items
carried such names. The staging half (a refused batch stages the item alone) is
selftest_relentless_game.t_modlist_rider_refusal_stages_alone.
Offline and deterministic: the repo's mod folders and compose manifest only; no game folder is read."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import relentless_live_round as R  # noqa: E402

fails = []
n_ok = 0


def ok(cond, what):
    global n_ok
    if cond:
        n_ok += 1
        print("ok   " + what)
    else:
        fails.append(what)
        print("FAIL " + what)


def t_pure():
    mods, shells = {"FlowWorks", "LeaningScrub"}, {"BiomesShell": "RimMandrake.Biomes"}
    got = R.loadable({"Utils", "bridgetools", "BiomesShell", "FlowWorks", "LeaningScrub", "rimflow"}, mods, shells)
    ok(got == ["FlowWorks", "LeaningScrub", "RimMandrake.Biomes"], "pure: tooling dropped, shell mapped: %s" % got)
    ok(R.loadable(set(), mods, shells) == [], "pure: nothing touched, no mods")


class Fx(R.RoundFx):
    """The real RoundFx naming (repo discovery), with the commit's touched paths given."""

    def __init__(self, touched):
        R.RoundFx.__init__(self, books=REPO, seat="BENCH")
        self._t = touched

    def touched(self, sha):
        return self._t


def t_real_repo():
    # the instance: the touched paths behind the refused list (BiomesShell's DLL, a Utils helper, the bridge's source)
    fx = Fx(["src/RimMandrake/Utils/modlist_swap.py",
             "src/RimMandrake/bridgetools/build.py",
             "src/RimMandrake/BiomesShell/Assemblies/RimMandrake.Biomes.dll",
             "src/RimUtinni/StructureInjectionsRUT/Defs/x.xml",
             "src/RimMandrake/LeaningScrub/Defs/y.xml"])
    got = fx.mods_of("any")
    ok("Utils" not in got and "bridgetools" not in got and "BiomesShell" not in got,
       "instance: no tooling dir and no shell is a mod: %s" % got)
    ok("RimMandrake.Biomes" in got, "the compose shell stands for the composed mod: %s" % got)
    ok("StructureInjectionsRUT" in got and "LeaningScrub" in got, "a repo mod and a folded source stay: %s" % got)
    mods, shells = fx.mod_names()
    ok(len(mods) > 50 and "FlowWorks" in mods, "sanity: the instrument sees the repo's mods (%d)" % len(mods))
    ok(shells.get("BiomesShell") == "RimMandrake.Biomes", "sanity: the manifest's shell is read: %s" % shells)


def main():
    t_pure()
    t_real_repo()
    print("selftest_live_mods_tooling_dirs: %s (%d ok)" % ("FAIL %d" % len(fails) if fails else "PASS", n_ok))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
