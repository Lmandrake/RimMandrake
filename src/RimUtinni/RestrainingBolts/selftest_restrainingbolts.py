#!/usr/bin/env python3
"""selftest_restrainingbolts.py -- offline proof for RestrainingBolts' goodwill-cap chain (RESTRAININGBOLTS_COVERAGE_GAPS_1).

Run bare: python3 src/RimUtinni/RestrainingBolts/selftest_restrainingbolts.py   (exit 0 = clean)

A mock jawa/static_call answers RestrainingBoltsProof.ProofCap the way the shipped C# does. Clean must PASS
(and the real-worker bar must read UNMEASURED, never PASS, when the Enclaves faction is absent); each planted
break (no floor, toggle ignored, penalty ignored, floor ignored, real worker uncapped, stale DLL) must redden
its component. Statically: the proof file is compiled (EnableDefaultCompileItems is off) and calls the shipped
CeilingFor, which GetMaxGoodwill also calls.
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
SRC = os.path.join(HERE, "Source")
CHAIN = "goodwill_cap_follows_bolted_count"
NAMES = ["formula_caps_by_bolted_count_and_floors", "enabled_off_restores_vanilla_100",
         "penalty_setting_scales_the_cap", "floor_setting_clamps_the_cap", "real_worker_caps_the_enclaves"]


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def cap(n, enabled=True, penalty=2.5, floor=-70.0, brk=()):
    """Mirror of the shipped C# with planted breaks."""
    if not enabled and "toggle_ignored" not in brk:
        return 100
    if "penalty_ignored" in brk:
        penalty = 2.5
    v = 100 - int(round(penalty * n))
    if "no_floor" in brk:
        return v
    if "floor_ignored" in brk:
        floor = -70.0
    return max(int(round(floor)), v)


def make_ext(brk, fde):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V._PROOF_TYPE:
            return None
        if "stale" in brk:
            return {"success": False, "message": "no public static method %s" % p.get("method")}
        s = " ".join("%s=%d" % (k, cap(n, brk=brk)) for k, n in (("n0", 0), ("n1", 1), ("n4", 4), ("n40", 40), ("n1000", 1000)))
        s += " off4=%d pen5n4=%d floorm50n1000=%d" % (cap(4, enabled=False, brk=brk), cap(4, penalty=5.0, brk=brk),
                                                      cap(1000, floor=-50.0, brk=brk))
        if not fde:
            return {"success": True, "result": s + " fde=False hediff=False live_count=- live_max=- live_off=-"}
        live = 100 if "worker_uncapped" in brk else cap(3, brk=brk)
        return {"success": True, "result": s + " fde=True hediff=True live_count=3 live_max=%d live_off=100" % live}
    return ext


def run(brk=(), fde=True):
    suite = Suite("RestrainingBoltsCap")
    suite.chain(CHAIN)(V.goodwill_cap_follows_bolted_count)
    game = MockGame()
    game.ext = make_ext(set(brk), fde)
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return [c["verdict"] for ch in res["chains"] for c in ch["components"]]


def main():
    proj = open(os.path.join(SRC, "RimMandrake.Utinni.RestrainingBolts.csproj"), encoding="utf-8").read()
    check("RestrainingBoltsProof.cs is in the csproj compile list", '<Compile Include="RestrainingBoltsProof.cs" />' in proj)
    proof = open(os.path.join(SRC, "RestrainingBoltsProof.cs"), encoding="utf-8").read()
    worker = open(os.path.join(SRC, "GoodwillSituationWorker_RestrainingBolts.cs"), encoding="utf-8").read()
    check("the proof reads the SHIPPED CeilingFor and the real worker", proof.count("CeilingFor(") >= 8 and "GetMaxGoodwill(fde)" in proof)
    check("GetMaxGoodwill itself returns CeilingFor(BoltedCount())", "return CeilingFor(BoltedCount());" in worker)
    check("settings restored in a finally", all(x in proof for x in (
        "RestrainingBoltsSettings.enabled = wasEnabled;", "penaltyPerBoltedDroid = wasPenalty;", "goodwillFloor = wasFloor;")))
    check("formula oracle: 1 bolted rounds 2.5 to 2 (banker's, as Mathf.RoundToInt)", V.expected_ceiling(1) == 98)

    clean = ["PASS"] * 5
    check("clean with the Enclaves present: all PASS", run() == clean, run())
    got = run(fde=False)
    check("Enclaves absent: real-worker bar UNMEASURED, never PASS", got == ["PASS"] * 4 + ["UNMEASURED"], got)
    for brk, idx in (("no_floor", 0), ("toggle_ignored", 1), ("penalty_ignored", 2), ("floor_ignored", 3), ("worker_uncapped", 4)):
        got = run((brk,))
        check("break %-16s reddens %s" % (brk, NAMES[idx]), got[idx] == "FAIL", got)
    got = run(("stale",))
    check("stale DLL (no method) reddens the formula bar", got[0] == "FAIL", got)

    if FAILS:
        print("\n%d RestrainingBolts selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall RestrainingBolts selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
