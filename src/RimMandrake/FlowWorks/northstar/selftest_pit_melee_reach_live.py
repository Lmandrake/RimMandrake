#!/usr/bin/env python3
"""Offline checks for pit_melee_reach_live.py's pure verdicts. No bridge."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pit_melee_reach_live as P  # noqa: E402

fails = []


def check(name, ok):
    print("%-4s  %s" % ("ok" if ok else "FAIL", name))
    if not ok:
        fails.append(name)


LINE = "MELEE strikes=False worth=False aDepth=6 tDepth=0 k=2 size=1.00 adjacent=True"
kv = P.parse(LINE)
check("the proof line parses", kv == {"strikes": "False", "worth": "False", "aDepth": "6", "tDepth": "0", "k": "2", "size": "1.00", "adjacent": "True"})
check("a refusal parses to nothing", P.parse("REFUSED: arg must be melee:") == {} and P.parse(None) == {})
check("no hit seen is 'none'", P.leg(kv, [], 6, True) == "none")
check("a hit is 'hit'", P.leg(kv, ["Human1"], 6, True) == "hit")
check("a refused recorder is could-not-look", P.leg(kv, None, 6, True) is None)
check("the wrong depth is could-not-look", P.leg(kv, [], 4, True) is None and P.leg(kv, [], 6, False) is None)
check("not adjacent is could-not-look", P.leg(dict(kv, adjacent="False"), [], 6, True) is None)
check("neither direction: PASS", P.verdict("none", "none", "none", "none")[0] == "PASS")
check("can-fail: a stab out of the pit", P.verdict("hit", "none", "none", "none")[0] == "FAIL")
check("can-fail: a stab down into it", P.verdict("none", "hit", "none", "none")[0] == "FAIL")
check("can-fail: the blanket rule (the thrumbo cannot reach down)", P.verdict("none", "none", "none", "hit")[0] == "FAIL")
check("can-fail: the control lands nothing", P.verdict("none", "none", "hit", "hit")[0] == "FAIL")
check("one leg unread: UNMEASURED, never PASS", P.verdict("none", None, "none", "none")[0] == "UNMEASURED")
check("one leg unread and one wrong: FAIL", P.verdict("hit", None, "none", "none")[0] == "FAIL")
check("a leg outside the row is ignored", P.verdict("hit", None, "hit", None)[0] == "PASS")
print("selftest_pit_melee_reach_live: %s" % ("FAIL" if fails else "PASS"))
sys.exit(1 if fails else 0)
