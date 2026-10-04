#!/usr/bin/env python3
"""selftest_starwarspatches.py -- offline proof that the patch_xpaths_land chain grades the replay honestly.

modcheck.patch_targets is proven on fixtures by its own selftest; here its check_mod is replaced by canned
results so the chain's verdict mapping is tested in seconds: clean -> PASS, one silent no-op -> FAIL,
broken sanity probe -> FAIL, no ops parsed -> FAIL, an unmodelled class -> UNMEASURED.
Pass --real to also run the chain against the installed game (about a minute with a warm cache).
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
from modcheck import patch_targets as PT                       # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def run_chain():
    suite = Suite("SWPatchXpaths")
    fn = [f for n, f in V.suite.chains if n == "patch_xpaths_land"][0]
    suite.chain("patch_xpaths_land")(fn)
    s = FastSession(transport=MockTransport(MockGame()), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return [c["verdict"] for ch in res["chains"] for c in ch["components"]]


def canned(results, sane=True, files=3):
    good = PT.DefIndex([])
    if sane:
        from lxml import etree
        good.root.append(etree.fromstring('<ThingDef><defName>Steel</defName><statBases/></ThingDef>'))
    return lambda *a, **k: (results, {"files": files, "index": good, "donors": [], "located": [],
                                      "missing_wanted": [], "defs_files": 1})


def main():
    real = PT.check_mod
    ok = {"where": "a.xml#0", "class": "PatchOperationAdd", "xpath": "/Defs/X", "status": "PASS", "why": "", "matched": 1}
    no = dict(ok, status="FAIL", why="matches nothing", matched=0)
    um = dict(ok, status="UNMEASURED", why="not modelled", **{"class": "PatchOperationAttributeSet"})
    try:
        if os.path.isdir(PT.GAME_DATA):
            for name, fake, want in (("clean replay PASSes", canned([ok, ok]), ["PASS"]),
                                     ("one silent no-op FAILs", canned([ok, no]), ["FAIL"]),
                                     ("a blind sanity probe FAILs", canned([ok], sane=False), ["FAIL"]),
                                     ("zero ops parsed FAILs (blind parse)", canned([], files=0), ["FAIL"]),
                                     ("an unmodelled op class is UNMEASURED", canned([ok, um]), ["UNMEASURED"])):
                PT.check_mod = fake
                got = run_chain()
                check(name, got == want, got)
        else:
            got = run_chain()
            check("no game Data -> UNMEASURED", got == ["UNMEASURED"], got)
    finally:
        PT.check_mod = real
    if "--real" in sys.argv:
        got = run_chain()
        check("REAL: the shipped patches all land", got == ["PASS"], got)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
