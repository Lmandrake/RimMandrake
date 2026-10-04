#!/usr/bin/env python3
"""selftest_gravshiplanding.py -- offline proof for GravshipLanding's arrival_map_reveal chain (GRAVSHIPLANDING_COVERAGE_GAPS_1).

Run bare: python3 src/RimMandrake/GravshipLanding/selftest_gravshiplanding.py   (exit 0 = clean)

A mock jawa/static_call answers GravshipLandingProof.ProofReveal the way the shipped C# does. Clean must PASS;
a partial reveal, a reveal that leaks into the roofed room, a toggle that does not gate, a non-arrival map that
reveals, an ERROR and a stale DLL must each redden their bar; REFUSED (no open rect) must read UNMEASURED, never
PASS. Statically: the proof is compiled and calls the shipped RevealIfArrival, which the postfix also calls.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
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


def make_ext(brk):
    def ext(game, tool, p):
        if tool != "jawa/static_call" or p.get("type") != V.PROOF_TYPE:
            return None
        if "stale" in brk:
            return {"success": False, "message": "no public static method %s" % p.get("method")}
        if "refused" in brk:
            return {"success": True, "result": "REFUSED: no open unroofed 21x21 rect within 60 cells of the map centre"}
        if "error" in brk:
            return {"success": True, "result": "ERROR NullReferenceException: x"}
        return {"success": True, "result": "outdoor=%d/416 interiorFogged=%d/9 off_unfogged=%d nonarrival_unfogged=%d" % (
            200 if "partial" in brk else 416, 4 if "leak" in brk else 9,
            416 if "ungated" in brk else 0, 416 if "nonarrival" in brk else 0)}
    return ext


def run(brk=()):
    suite = Suite("GravshipLandingReveal")
    suite.chain("arrival_map_reveal")(dict(V.suite.chains)["arrival_map_reveal"])
    game = MockGame()
    game.ext = make_ext(set(brk))
    s = FastSession(transport=MockTransport(game), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return [c["verdict"] for ch in res["chains"] for c in ch["components"]]


def main():
    src = os.path.join(HERE, "Source")
    proj = open(os.path.join(src, "RM_GravshipLanding.csproj"), encoding="utf-8").read()
    check("GravshipLandingProof.cs compiled", '<Compile Include="GravshipLandingProof.cs" />' in proj)
    proof = open(os.path.join(src, "GravshipLandingProof.cs"), encoding="utf-8").read()
    patch = open(os.path.join(src, "Patch_GenStep_GravshipMarker.cs"), encoding="utf-8").read()
    check("proof calls the shipped RevealIfArrival three times", proof.count("Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(") == 3)
    check("the postfix runs RevealIfArrival on the whole map", "RevealIfArrival(map, parms.gravship != null, map.BoundsRect())" in patch)
    check("setting, walls, roof and fog restored in finally",
          all(x in proof.split("finally", 1)[1] for x in ("revealOutdoorsBeforeLanding = was", "Destroy(", "SetRoof(c, null)", "Unfog(")))
    check("static_checks clean", V.static_checks() == [], V.static_checks())

    check("clean: all PASS", run() == ["PASS"] * 4, run())
    for brk, idx in (("partial", 0), ("leak", 1), ("ungated", 2), ("nonarrival", 3), ("error", 0), ("stale", 0)):
        got = run((brk,))
        check("break %-10s reddens bar %d" % (brk, idx), got[idx] == "FAIL", got)
    got = run(("refused",))
    check("REFUSED reads UNMEASURED on every bar, never PASS", got == ["UNMEASURED"] * 4, got)

    if FAILS:
        print("\n%d GravshipLanding selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall GravshipLanding selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
