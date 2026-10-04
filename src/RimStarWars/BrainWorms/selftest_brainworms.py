#!/usr/bin/env python3
"""selftest_brainworms.py -- offline proof for BrainWorms' ruin_loot_patch_target chain and its resolver.

Run bare: python3 src/RimStarWars/BrainWorms/selftest_brainworms.py   (exit 0 = clean)

The resolver must say True for a present def+child, False for a missing def or child, None for an unreachable root
or a non-simple xpath; the chain must PASS on the shipped patch against the installed game Data (UNMEASURED where
Data is unreachable) and FAIL when the patch's xpath is pointed at a def that does not exist.
"""
import os
import shutil
import sys
import tempfile

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


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def run_chain(here=None):
    suite = Suite("BrainWormsRuinLoot")
    fn = [f for n, f in V.suite.chains if n == "ruin_loot_patch_target"][0]
    suite.chain("ruin_loot_patch_target")(fn)
    saved = V.HERE
    if here:
        V.HERE = here
    try:
        s = FastSession(transport=MockTransport(MockGame()), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        V.HERE = saved
    return [(c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"]]


def main():
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "Data", "Defs"))
        with open(os.path.join(tmp, "Data", "Defs", "a.xml"), "w") as fh:
            fh.write('<Defs><ThingSetMakerDef><defName>TS_A</defName><root><options><li/></options></root>'
                     '</ThingSetMakerDef></Defs>')
        data = os.path.join(tmp, "Data")
        r = V.patch_target_resolves
        check("present def + child -> True", r('/Defs/ThingSetMakerDef[defName="TS_A"]/root/options', [data]) is True)
        check("missing child -> False", r('/Defs/ThingSetMakerDef[defName="TS_A"]/root/nope', [data]) is False)
        check("missing def -> False", r('/Defs/ThingSetMakerDef[defName="TS_B"]/root/options', [data]) is False)
        check("wrong def type -> False", r('/Defs/ThingDef[defName="TS_A"]/root/options', [data]) is False)
        check("unreachable root -> None", r('/Defs/ThingSetMakerDef[defName="TS_A"]/root', [tmp + "/nope"]) is None)
        check("non-simple xpath -> None", r('/Defs/ThingDef[recipes/li="X"]/recipes', [data]) is None)

        game_ok = os.path.isdir(V.GAME_DATA)
        want = "PASS" if game_ok else "UNMEASURED"
        got = run_chain()
        check("shipped patch: chain records %s" % want, got == [("ruin_loot_patch_target_exists", want)], got)
        if game_ok:
            fake = os.path.join(tmp, "Mod")
            os.makedirs(os.path.join(fake, "Patches"))
            src = open(os.path.join(HERE, "Patches", "BrainWormEggs_RuinLoot.xml"), encoding="utf-8").read()
            with open(os.path.join(fake, "Patches", "BrainWormEggs_RuinLoot.xml"), "w", encoding="utf-8") as fh:
                fh.write(src.replace("MapGen_AncientComplexRoomLoot_Default", "MapGen_AncientComplexRoomLoot_Gone"))
            got = run_chain(here=fake)
            check("a patch aimed at a def that does not exist FAILs", got == [("ruin_loot_patch_target_exists", "FAIL")], got)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if FAILS:
        print("\n%d BrainWorms selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall BrainWorms ruin-loot selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
