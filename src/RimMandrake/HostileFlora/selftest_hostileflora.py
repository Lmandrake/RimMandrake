#!/usr/bin/env python3
"""selftest_hostileflora.py -- the static_doctrine chain is green on the shipped defs and red on a finding."""
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


def run():
    suite = Suite("HFStatic")
    suite.chain("static_doctrine")([f for n, f in V.suite.chains if n == "static_doctrine"][0])
    with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return [c["verdict"] for ch in res["chains"] for c in ch["components"]]


def main():
    check("shipped defs: static_doctrine PASSes", run() == ["PASS"], run())
    real_root = V.HERE
    orig = V.SHIPPED
    try:
        V.SHIPPED = []
        check("a blind parse (no defs) FAILs", run() == ["FAIL"], run())
    finally:
        V.SHIPPED = orig
        V.HERE = real_root
    import xml.etree.ElementTree as ET
    real_parse = ET.parse

    def plant(path, *a, **k):
        tree = real_parse(path, *a, **k)
        if path.endswith("RM_Gallowroot.xml"):
            tree.getroot().find("ThingDef/race/manhunterOnDamageChance").text = "0.5"
        return tree
    V.ET.parse = plant
    try:
        check("manhunterOnDamageChance != 0 FAILs", run() == ["FAIL"], run())
    finally:
        V.ET.parse = real_parse
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
