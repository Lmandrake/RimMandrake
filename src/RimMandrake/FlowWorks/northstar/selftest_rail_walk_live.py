#!/usr/bin/env python3
"""Offline test of rail_walk_live.py's judges (RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY): no bridge, no game."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rail_walk_live as R  # noqa: E402


def main():
    fails = []

    def check(ok, msg):
        if not ok:
            fails.append(msg)

    kv = R.parse_kv("WALK rail=True isRail=True guards=True floorRefuses=True prefixPass=False door=rail falls=True expect=putback forced=False")
    check(kv["door"] == "rail" and kv["prefixPass"] == "False", "parse_kv reads the hook's answer")
    check(R.judge_floor(kv, True), "railed: rail door refuses")
    check(not R.judge_floor(kv, False), "a rail answer is not the unrailed verdict")
    un = R.parse_kv("WALK rail=False isRail=False guards=False floorRefuses=True prefixPass=False door=floor falls=True expect=fell forced=False")
    check(R.judge_floor(un, False), "unrailed: the floor holds it")
    check(not R.judge_floor(R.parse_kv("WALK rail=False door=none prefixPass=True"), False), "a walked-off step is a FAIL")
    check(not R.judge_floor({}, True), "no answer is never a pass")
    lip = (121, 203)
    b = {"descents": "4", "pos": "121,203"}
    check(R.judge_forced(kv, b, {"descents": "4", "pos": "121,203"}, lip, True), "railed: put back, no descent")
    check(not R.judge_forced(kv, b, {"descents": "5", "pos": "122,203"}, lip, True), "railed but fell is a FAIL")
    check(R.judge_forced(un, b, {"descents": "5", "pos": "122,203"}, lip, False), "unrailed control falls")
    check(not R.judge_forced(un, b, {"descents": "4", "pos": "121,203"}, lip, False), "a control that does not fall is a FAIL (the old A3)")
    check(not R.judge_forced(un, b, {"descents": "x"}, lip, False), "an unreadable count is never a pass")
    for f in fails:
        print("FAIL", f)
    print("%s %d/%d" % ("PASS" if not fails else "FAIL", 11 - len(fails), 11))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
