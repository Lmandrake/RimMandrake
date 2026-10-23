#!/usr/bin/env python3
"""selftest for joint_check.judge (offline, no game): a clean answer passes; a gap, a non-port end, a shared nozzle, an
undrawn pose, a silent probe and reels-with-no-joints never read as PASS."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import joint_check as J  # noqa: E402

fails = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)


def ans(*joints, reels=2):
    return {"success": True, "cmd": "joints", "tolerance": 0.05, "reels": reels, "joints": list(joints)}


def j(kind, ok, gap=0.0):
    return {"reel": 1, "at": [3, 4], "rot": 1, "look": "Scrapper", "kind": kind, "ok": ok, "gap": gap, "where": "[1,2]", "note": "n"}


check(J.judge(ans(j("reel_end", True), j("free_port_end", True, 0.01), j("feed_under_reel", True)))[0] == "PASS", "clean joints pass")
check(J.judge(ans(j("reel_end", True), j("free_port_end", False, 0.38)))[0] == "FAIL", "a 0.38-cell flange gap fails")
check(J.judge(ans(j("feed_nozzle_shared", False)))[0] == "FAIL", "two hoses from one nozzle fails")
check(J.judge(ans(j("feed_port_end", False)))[0] == "FAIL", "an end at no port fails")
check(J.judge(ans(j("reel_end", True), j("pose", None)))[0] == "UNMEASURED", "an undrawn laid hose is UNMEASURED, not a pass")
check(J.judge({"success": False, "error": "timeout"})[0] == "UNMEASURED", "a silent probe is UNMEASURED")
check(J.judge(ans(reels=3))[0] == "UNMEASURED", "reels on the map but no joints measured is UNMEASURED")
check(J.judge(ans(reels=0))[0] == "PASS", "a map with no reels passes (nothing to join)")
v, lines = J.judge(ans(j("free_port_end", False, 0.38)))
check(any("0.380" in ln and "free_port_end" in ln for ln in lines), "a FAIL line names the joint kind and its gap")
print("joint_check selftest: %d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
