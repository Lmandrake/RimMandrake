#!/usr/bin/env python3
"""selftest_dustveil.py -- DUSTVEIL_FLIGHT_BUILD_A_MOTH_THAT_WALKED (owner, by question card 2026-10-22, Rot Q5).

Offline proof that The Rot's dustveil bar can see: the shipped RM_Dustveil.xml passes validation.dustveil_checks,
and each planted defect (grounded, laboratory origin restored, shearing lost, flip-book prefix with no frames) turns
it red. No game, no bridge; flight itself is never driven here.
    python3 src/RimMandrake/TheRot/Tools/selftest_dustveil.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import validation  # noqa: E402


def main():
    res = validation.planted_dustveil()
    fails = []
    for name, ok in res:
        print("%s %s" % ("ok  " if ok else "FAIL", name))
        if not ok:
            fails.append(name)
    if len(res) < 5:
        fails.append("only %d planted cases ran (sanity probe failed)" % len(res))
    if fails:
        print("selftest_dustveil: FAIL (%s)" % ", ".join(fails))
        return 1
    print("selftest_dustveil: PASS (%d/%d)" % (len(res), len(res)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
