#!/usr/bin/env python3
"""selftest_swbestiary.py -- offline proof for SWBestiary's beast-mechanics chains (metal eating, scrap hoarding).

Run bare: python3 src/RimStarWars/SWBestiary/selftest_swbestiary.py   (exit 0 = clean)

A mock jawa/static_call answers RSW_BeastMechanicsProof the way the shipped C# does on a healthy game. Clean must
PASS; a hungry eater given nothing, a fed eater still eating, a toggle that does not gate, a hoarder carrying to the
wrong place, a proof that errors and a stale DLL with no such method must each turn exactly their component red.
The C# side is checked statically: the proof file is in the csproj compile list (EnableDefaultCompileItems is off,
so a file missing there compiles into nothing) and calls the shipped giver's own TryGiveJob.
"""
import os
import re
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
BM = os.path.join(HERE, "Source", "BeastMechanics")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF_TYPE:
            return None
        m = p.get("method")
        if "stale" in brk:
            return {"success": False, "message": "no public static method %s" % m}
        if m == "ProofMetalEat":
            if "eat_error" in brk:
                return {"success": True, "result": "ERROR no open non-home cell"}
            hungry = "none" if "eat_never" in brk else "RSW_EatMetal|target=Steel|targetB=-"
            fed = "RSW_EatMetal|target=Steel|targetB=-" if "eat_fed" in brk else "none"
            off = "RSW_EatMetal|target=Steel|targetB=-" if "eat_ungated" in brk else "none"
            return {"success": True, "result": "eater=RSW_Khorrak food=Steel hungry=%s fed=%s off=%s" % (hungry, fed, off)}
        if m == "ProofHoard":
            on = "RSW_HoardScrap|target=ComponentIndustrial|targetB=RSW_ScrapNest"
            if "hoard_wrong_nest" in brk:
                on = "RSW_HoardScrap|target=ComponentIndustrial|targetB=-"
            off = on if "hoard_ungated" in brk else "none"
            return {"success": True, "result": "hoarder=RSW_ScrapNestBird nest=RSW_ScrapNest scrap=ComponentIndustrial "
                                               "on=%s off=%s" % (on, off)}
        raise RuntimeError("mock: unknown method %s" % m)
    return ext


def run(brk=()):
    suite = Suite("SWBestiaryBeasts")
    suite.chain("metal_eater_seeks_its_metal")(V.metal_eater_seeks_its_metal)
    suite.chain("scrap_hoarder_carries_to_its_nest")(V.scrap_hoarder_carries_to_its_nest)
    game = MockGame()
    game.ext = make_ext(set(brk))
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return dict((c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"])


def main():
    proj = open(os.path.join(BM, "RimMandrakeBeastMechanicsRSW.csproj"), encoding="utf-8").read()
    check("RSW_BeastMechanicsProof.cs is in the csproj compile list",
          '<Compile Include="RSW_BeastMechanicsProof.cs" />' in proj)
    src = open(os.path.join(BM, "RSW_BeastMechanicsProof.cs"), encoding="utf-8").read()
    check("the proofs call the SHIPPED givers (subclass + TryGiveJob), not a copy",
          re.search(r"class EatProbe : JobGiver_EatMetal", src) and re.search(r"class HoardProbe : JobGiver_HoardScrap", src)
          and src.count("TryGiveJob(p)") == 2)
    check("both toggles are restored in a finally",
          "RSW_BeastMechanicsSettings.metalEatingEnabled = was;" in src
          and "RSW_BeastMechanicsSettings.scrapHoardingEnabled = was;" in src)

    EAT = "a_hungry_eater_is_sent_to_the_metal_beside_it"
    HOARD = "a_rested_hoarder_takes_scrap_to_its_nest"
    got = run()
    check("clean: both PASS", got == {EAT: "PASS", HOARD: "PASS"}, got)
    for brk, red in (("eat_never", EAT), ("eat_fed", EAT), ("eat_ungated", EAT), ("eat_error", EAT),
                     ("hoard_wrong_nest", HOARD), ("hoard_ungated", HOARD)):
        got = run((brk,))
        want = {EAT: "PASS", HOARD: "PASS"}
        want[red] = "FAIL"
        check("break %-16s reddens exactly %s" % (brk, red), got == want, got)
    got = run(("stale",))
    check("break stale DLL (no method) reddens both", got == {EAT: "FAIL", HOARD: "FAIL"}, got)

    if FAILS:
        print("\n%d SWBestiary selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall SWBestiary beast-mechanics selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
