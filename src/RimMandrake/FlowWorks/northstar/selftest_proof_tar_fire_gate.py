#!/usr/bin/env python3
"""Offline check of proof_tar_fire_gate.py's pure verdicts (SUMP_TAR_FIRE_NETWORK_1): the FIRECELL parser and the A1-A3
verdicts, each with a case that must FAIL and one that must be UNMEASURED, so a blind instrument cannot read as PASS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proof_tar_fire_gate as P  # noqa: E402


def c(b, p=False):
    return {"x": 0, "z": 0, "burning": b, "pending": p}


def main():
    bad = []

    def check(cond, what):
        if not cond:
            bad.append(what)

    got = P.parse_cell("FIRECELL 12,-3 burning=True pending=False due=-1 hops=0 now=500")
    check(got == {"x": 12, "z": -3, "burning": True, "pending": False}, "parse FIRECELL: %r" % (got,))
    check(P.parse_cell("REFUSED: arg must be x,z") is None and P.parse_cell(None) is None, "parse refuses junk")

    check(P.v_gate_holds([c(True)] * 6, [c(False)] * 6)[0] == "PASS", "A1 pass")
    check(P.v_gate_holds([c(True)] * 6, [c(False)] * 5 + [c(True)])[0] == "FAIL", "A1 far burning fails")
    check(P.v_gate_holds([c(True)] * 6, [c(False, True)] + [c(False)] * 5)[0] == "FAIL", "A1 far pending fails")
    check(P.v_gate_holds([c(False)] * 6, [c(False)] * 6)[0] == "UNMEASURED", "A1 never lit is blind")
    check(P.v_gate_holds([c(True)] * 5 + [None], [c(False)] * 6)[0] == "UNMEASURED", "A1 read failure is blind")

    check(P.v_gate_passes([c(True)] * 6)[0] == "PASS", "A2 pass")
    check(P.v_gate_passes([c(True)] * 5 + [c(False)])[0] == "FAIL", "A2 one dark fails")

    six = [c(True)] * 6
    check(P.v_belch(six, six, [c(True), c(False)], [1, 0])[0] == "PASS", "A3 pass")
    check(P.v_belch(six, [c(False)] + [c(True)] * 5, [c(True)], [1])[0] == "FAIL", "A3 belch put a square out fails")
    check(P.v_belch(six, six, [c(False), c(False)], [1, 1])[0] == "FAIL", "A3 wet arm unlit fails")
    check(P.v_belch(six, six, [c(False)], [0])[0] == "UNMEASURED", "A3 no tar arrived is blind")
    check(P.v_belch([c(False)] * 6, six, [c(True)], [1])[0] == "UNMEASURED", "A3 canal not burning before is blind")

    for b in bad:
        print("FAIL  " + b)
    print("selftest_proof_tar_fire_gate: %d/%d" % (17 - len(bad), 17))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
