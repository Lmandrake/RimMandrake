#!/usr/bin/env python3
"""selftest_ask_lane.py - the promises of design/specs/2026-11-24-ask-lane-after-host-facts/boundary.md, one check each."""
import os
import sys
import json
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import host_facts as HF  # noqa: E402
import ask as ASK  # noqa: E402

F = {"mods": ["a.b"], "saves": ["NS_x"], "python": {"numpy": True, "lxml": False}, "companions": ["h1"], "free_gb": 9, "logins": {"lukas": 100, "steven": 9 * 86400}}
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def pl(**kw):
    b = dict(item="I", facts=F, stale=False, live_proofs={"A1": "x"}, table={}, tiers={"mods__base": ["a.b"]})
    b.update(kw)
    return ASK.plan(**b)


def t_old_facts_are_stale():
    p = os.path.join(tempfile.mkdtemp(), "f.json")
    json.dump({"at": 0, "facts": F}, open(p, "w"))
    check(not HF.read(p, 10)["stale"] and HF.read(p, HF.MAX_AGE_S + 1)["stale"] and HF.read(p + "x", 1)["facts"] is None, "old facts are stale")


def t_absent_is_measured():
    check(HF.lacks({"mods": ["c"], "python": ["lxml", "numpy"]}, F, False) == [("mods", "c", "absent"), ("python", "lxml", "absent")], "absent is measured")


def t_stale_never_says_absent():
    check({w for _, _, w in HF.lacks({"mods": ["c"]}, F, True)} == {"could not look"}, "stale never says absent")


def t_no_driver_is_cannot():
    check(pl(live_proofs={})["verdict"] == "CANNOT" and pl(table={"P": {"live_check_owed": True}})["verdict"] == "CANNOT", "no driver is CANNOT")


def t_a_missing_tier_mod_is_cannot():
    p = pl(tiers={"t": ["zz.q"]})
    check(p["verdict"] == "CANNOT" and "zz.q" in str(p["why"]), "a missing tier mod is CANNOT")


def t_stale_facts_are_could_not_look():
    check(pl(stale=True)["verdict"] == "COULD NOT LOOK" and pl(facts=None)["verdict"] == "COULD NOT LOOK", "stale facts are COULD NOT LOOK")


def t_an_ask_is_the_whole_line():
    a = pl()["argv"]
    check(pl()["verdict"] == "ASK" and a[:2] == ["submit", "I"] and "--sha" in a and "A1" in a and "--purpose" not in a, "an ask is the whole line")


def t_a_login_low_on_time_is_named():
    check(HF.logins_low(F) == ["lukas"], "a login low on time is named")


def main():
    for t in (t_old_facts_are_stale, t_absent_is_measured, t_stale_never_says_absent, t_no_driver_is_cannot, t_a_missing_tier_mod_is_cannot,
              t_stale_facts_are_could_not_look, t_an_ask_is_the_whole_line, t_a_login_low_on_time_is_named):
        t()
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
