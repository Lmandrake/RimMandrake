#!/usr/bin/env python3
"""selftest_armoury.py -- offline proof for Armoury's melee_ladder_landed chain.

Run bare: python3 src/RimStarWars/Armoury/selftest_armoury.py   (exit 0 = clean)

A mock get_defs serves every patched weapon with the patch's own tool powers (donor OuterRim_* defs absent, as
on a list without that mod). Clean must PASS; a power that did not land, one of our absorbed weapons missing, a
non-numeric power and a blind patch parse must each turn the component red.
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


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk):
    targets = V.melee_targets()

    def ext(game, tool, p):
        if tool != "jawa/get_defs":
            return None
        want = [s.split("/", 1)[1] for s in str(p.get("defs") or "").split(";") if "/" in s]
        rows, missing = [], []
        for n in want:
            if n.startswith("OuterRim_") or ("lost" in brk and n == "guy762_vsword"):
                missing.append(n)
                continue
            tools = [{"label": lb, "power": pw, "cooldownTime": 2.0} for lb, pw in sorted(targets[n].items())]
            if "not_landed" in brk and n == "guy762_vglaive":
                tools[0]["power"] = 9.0
            if "garbage" in brk and n == "RSW_JDSA_Vibroaxe":
                tools[0]["power"] = "n/a"
            rows.append({"defName": n, "fields": {"tools": tools}})
        return {"success": True, "foundCount": len(rows), "notFound": missing, "defs": rows}
    return ext


def run(brk=()):
    suite = Suite("ArmouryMelee")
    suite.chain("melee_ladder_landed")(V.melee_ladder_landed)
    game = MockGame()
    game.ext = make_ext(set(brk))
    saved = V.melee_targets
    if "blind" in brk:
        V.melee_targets = lambda path=None: {}
    try:
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(suite, s, anchor=None, mod=None)
    finally:
        V.melee_targets = saved
    return [(c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"]]


def main():
    m = V.melee_targets()
    check("the generated melee patch parses (>= 15 weapons, >= 40 tool powers; 18/49 on 2026-10-03)",
          len(m) >= 15 and sum(len(v) for v in m.values()) >= 40, (len(m), sum(len(v) for v in m.values())))
    check("guy762_vsword carries handle 10 / point 25 / edge 30",
          m.get("guy762_vsword") == {"handle": 10.0, "point": 25.0, "edge": 30.0}, m.get("guy762_vsword"))
    want = [("melee_patch_powers_are_live", "PASS")]
    check("clean: PASS with the donor's defs absent", run() == want, run())
    for brk in ("not_landed", "lost", "garbage", "blind"):
        got = run((brk,))
        check("break %-10s turns the component FAIL" % brk, got == [("melee_patch_powers_are_live", "FAIL")], got)
    if FAILS:
        print("\n%d Armoury selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall Armoury melee-ladder selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
