#!/usr/bin/env python3
"""selftest_seed_trust_weak_reading.py - the two modules delivery_metrics reads, moved out of relentless_trust.py and
relentless_wall.py (RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES). The cases are the ones
selftest_relentless_seeds.py and selftest_relentless.py held for these functions, carried over before those tests go.

    python3 src/RimMandrake/rimflow/selftest_seed_trust_weak_reading.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import seed_trust as T      # noqa: E402
import weak_reading as W    # noqa: E402

FAILS = []
STRONG_WEAK = " STRONG: rerun selftest_x with hunk 2 put back. LETS THROUGH: the pump pours back into the tank"


def check(what, ok, got=""):
    print(("ok   " if ok else "FAIL ") + what + ("" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def r(item, cls, verdict, **kw):
    return dict(item=item, cls=cls, verdict=verdict, contaminated=[], **kw)


def test_counting():
    res = [r("a", "hunk_red", "FAIL", path="x/foo.py", reasons="foo.py loses the guard"),
           r("b", "hunk_red", "FAIL", path="x/foo.py", reasons="the proof crashed"),
           r("c", "hunk_red", "PASS", path="x/foo.py"),
           r("b2", "hunk_red", "FAIL", path="x/foo.py", reasons="myfoo.py is wrong, as is foo.pyc"),
           r("e", "hunk_green", "PASS", path="x/g.py"),
           r("f", "hunk_green", "PASS", path="x/g.py"),
           r("g", "hunk_green", None),
           dict(r("h", "hunk_green", "PASS"), contaminated=["books"]),
           r("i", "control", "PASS"), r("j", "control", "FAIL", reasons="bad"), r("k", "escaped", "FAIL", reasons="z")]
    keys = [dict(item=x["item"], cls=x["cls"]) for x in res] + [dict(item="d", cls="hunk_green"), dict(item="z", cls="hunk_green")]
    reads = {"d": "equivalent", "e": "observable", "f": "observable", "g": "observable", "h": "observable"}
    c = T.compute(res, reads, keys)
    x = c["classes"]["hunk_red"]
    check("caught counts FAIL; on target is the whole name", (x["caught"], x["n"], x["on_target"]) == (3, 4, 1), x)
    g = c["classes"]["hunk_green"]
    check("equivalent never ran and is listed", (g["caught"], g["n"], g["removed"]) == (0, 2, 1) and c["removed_equivalent"] == ["d"], g)
    check("a planned case with no result is unrun, in neither count", g["unrun"] == 1 and c["unread"] == ["z"], g)
    check("planned adds up", g["planned"] == g["n"] + g["unrun"] + g["lost"] + g["contaminated"] + g["removed"], g)
    check("lost is neither caught nor a miss", c["lost"] == ["g"])
    check("contaminated is dropped and listed", c["contaminated"] == ["h"])
    check("control false fail, with reasons", (c["control"]["false_fail"], c["control"]["n"]) == (1, 2)
          and c["control"]["reasons"] == {"j": "bad"})
    check("escaped has no on-target test", c["classes"]["escaped"]["on_target"] is None)
    check("on target: a name with a space", T.on_target({"path": "src/a b.py", "reasons": "Regression in src/a b.py"}))
    check("on target: a Windows path", T.on_target({"path": "src/a.py", "reasons": r"Regression in C:\repo\src\a.py"}))
    check("on target: another file is no hit", not T.on_target({"path": "src/a.py", "reasons": "b.py and ba.py and a.pyc"}))
    check("on target: a longer extension is no hit", not T.on_target({"path": "src/a.py", "reasons": "in a.py.bak and a.py-old"}))
    check("on target: end of sentence is a hit", T.on_target({"path": "src/a.py", "reasons": "the guard in a.py."}))
    lo, hi = T.wilson(0, 30)
    check("Wilson is Wilson at zero, not 3/n", lo == 0.0 and 0.11 < hi < 0.12, hi)
    check("Wilson of no cases is None, never 0", T.wilson(0, 0) is None)


def test_weak_reading():
    check("an invented mutant is no gap under the narrow rule", W.narrow_word("WEAK", " gap:other a mutant I wrote") == "PASS")
    check("a hunk of the diff stays WEAK", W.narrow_word("WEAK", "GAP:DIFF hunk 2 put back, proof green") == "WEAK")
    check("an untagged WEAK is never guessed", W.narrow_word("WEAK", "ran it") == "UNTAGGED")
    check("only WEAK moves", W.narrow_word("FAIL", "GAP:OTHER") == "FAIL" and W.narrow_word("PASS", "") == "PASS")
    check("a WEAK that names no strong proof is a PASS", W.acted_weak("WEAK", "GAP:DIFF hunk 2 put back, proof green") == "PASS")
    check("a WEAK naming STRONG and LETS THROUGH holds", W.acted_weak("WEAK", "GAP:DIFF hunk 2 put back." + STRONG_WEAK) == "WEAK")
    check("STRONG alone, no defect named, is a PASS", W.acted_weak("WEAK", "GAP:DIFF hunk 2. STRONG: rerun selftest_x reverted") == "PASS")
    check("GAP:OTHER stays a PASS whatever it names", W.acted_weak("WEAK", "GAP:OTHER mine." + STRONG_WEAK) == "PASS")
    check("an untagged WEAK naming its strong proof holds", W.acted_weak("WEAK", "ran it." + STRONG_WEAK) == "WEAK")


if __name__ == "__main__":
    test_counting()
    test_weak_reading()
    print("selftest_seed_trust_weak_reading: " + ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
