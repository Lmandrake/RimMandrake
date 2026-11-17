#!/usr/bin/env python3
"""live_flip_fresh.py's verdict, and that the mod's dirty-event patch sends a liveness flip to the on/off-screen rule.

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_flip_fresh.py      # exit 0 = every check passes
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import live_flip_fresh as L  # noqa: E402


def c(flips=1, missing=0, extra=0, different=0, edges=1):
    return {"flips": flips, "fresh": {"edges": edges, "missing": missing, "extra": extra, "different": different}}


def main():
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    check(L.verdict([c()] * 12)[0] == "PASS", "twelve flips, every compare equal: passes")
    check(L.verdict([c(), c(missing=1, extra=1)] * 6)[0] == "FAIL", "planted: the reading of the build before the fix (missing 1, extra 1 every other flip) fails")
    check(L.verdict([c(), c(different=1)])[0] == "FAIL", "planted: a cord that differs in shape fails")
    check(L.verdict([c(), c(flips=0)])[0] == "UNMEASURED", "a poll that saw no flip measures nothing")
    check(L.verdict([c(), {"flips": 1, "fresh": {"success": False}}])[0] == "UNMEASURED", "a compare with no counters measures nothing")
    check(L.verdict([c(edges=0)])[0] == "UNMEASURED", "no cord at the site measures nothing")
    check(L.verdict([])[0] == "UNMEASURED", "no cycle measures nothing")
    src = open(os.path.join(os.path.dirname(HERE), "Source", "RM_MapComponent_CordGraph.cs"), encoding="utf-8").read()
    check("if ((dirtyFlags & mask) == 0UL && !flip)" in src and "bool flip = (dirtyFlags & (ulong)GimmeSomeSlackDefOf.RM_MessyCords) != 0UL && !RM_MapComponent_CordGraph.OwnDirty;" in src,
          "the dirty-event patch lets a liveness flip through to the on/off-screen rule")
    print("PASS" if not fails else "FAIL: %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
