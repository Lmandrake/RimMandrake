"""Offline checks of trench_cover_proof.py's pure verdicts (no bridge): the bar follows the target's body size.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_trench_cover_proof.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trench_cover_proof as T  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


check(abs(T.trench_bar(1.0) - 0.441) < 0.001, "adult human (size 1) square-on bar is the design's 0.441")
# live 20261023T044826: a teenager colonist (HumanlikeTeenager bodySizeFactor 0.8) read trench=0.493, one_back 0.164
check(abs(T.trench_bar(0.8) - 0.493) < 0.001, "a teenager (size 0.8) bar is 0.493, the live read the fixed bar called a FAIL")
check(abs(T.trench_bar(0.8) * 0.3333 - 0.164) < 0.001, "one_back for the same teenager is 0.164, as read live")
check(abs(T.trench_bar(0.2) - 0.75) < 1e-9, "a target shorter than the 1 m wall is fully screened: 0.75 cap")
check(T.trench_bar(None) is None and T.trench_bar("x") is None and T.trench_bar(0) is None, "an unread size is no bar")
kv = T.parse("TRENCH trench=0.493 vanilla=0.000 combined=0.493 hit=0.416 hitNoTrench=0.626 cage=False target=22,20 "
             "shooter=22,30 size=0.800")
check(kv.get("size") == "0.800" and T.near_verdict(kv, "trench", T.trench_bar(kv["size"]), 0.02) == "PASS",
      "the live teenager read PASSes against its own bar")
check(T.near_verdict(kv, "trench", T.trench_bar(1.0), 0.02) == "FAIL", "can-fail: the same read against the adult bar FAILs")

print("PASS: 0 failure(s)" if not FAILS else "FAIL: %d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
