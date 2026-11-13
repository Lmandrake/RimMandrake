#!/usr/bin/env python3
"""selftest_flyer_state_read_guard.py - flyer_tier_three_state_read.py refuses unless the game is paused and no tick
passed during the read (owner by card 2026-11-12 ~8:25 PM PST: paused reads allowed, no ticks, no pictures).

Offline, pure: drives paused_read_guard() with the shapes the bridge returns. Exit 0 = all pass, 1 = a case failed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flyer_tier_three_state_read as T  # noqa: E402

P = {"state": {"paused": True}}
CASES = [
    # (label, status before, ticks before, status after, ticks after, expect refusal)
    ("paused, clock still", P, 1000, P, 1000, False),
    ("running before the read", {"state": {"paused": False}}, 1000, P, 1000, True),
    ("unpaused during the read", P, 1000, {"state": {"paused": False}}, 1000, True),
    ("one tick passed", P, 1000, P, 1001, True),
    ("clock ran backwards (another map or a load)", P, 1000, P, 999, True),
    ("pause state unreadable", {}, 1000, P, 1000, True),
    ("pause state not a bool", {"state": {"paused": "yes"}}, 1000, P, 1000, True),
    ("clock unreadable before", P, None, P, 1000, True),
    ("clock unreadable after", P, 1000, P, None, True),
    ("no status at all", None, 1000, None, 1000, True),
]


def main():
    bad = 0
    for label, s0, t0, s1, t1, refuse in CASES:
        why = T.paused_read_guard(s0, t0, s1, t1)
        ok = bool(why) == refuse
        bad += not ok
        print("%s %-45s -> %s" % ("ok  " if ok else "FAIL", label, why or "allowed"))
    if not T.paused_read_guard(P, 5, P, 5) is None:
        bad += 1
        print("FAIL a clean read must return None")
    print("PASS %d/%d" % (len(CASES) - bad, len(CASES)) if not bad else "FAIL %d of %d" % (bad, len(CASES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
