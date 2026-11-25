#!/usr/bin/env python3
"""Offline oracle of sc_save_in_air's judgment (proof/scene_save_in_air.py: census and judge), no game.

One good evidence set must read PASS on every row; each planted fault must turn its own row, and only a non-PASS:
  S1  good evidence: all five rows PASS
  S2  a thing counted twice in the loaded arm (spawned and in a carrier)   -> SA_EACH_ONCE FAIL
  S3  both loads lack a thing the live arm holds (SAVE_DROPS_STATE)        -> SA_EACH_ONCE FAIL
  S4  two loads disagree (LOAD_NONDETERMINISTIC)                           -> SA_EACH_ONCE UNMEASURED, never PASS
  S5  nothing in a carrier at the save                                     -> SA_IN_AIR FAIL, later rows UNMEASURED
  S6  a load lost the flight (no carrier after load C)                     -> SA_AIR_AT_LOAD FAIL
  S7  a carrier still in the air at the end                                -> SA_LANDED FAIL
  S8  the Steel stack lands short                                          -> SA_LANDED FAIL
  S9  the stage refused                                                    -> SA_PRE FAIL, the rest UNMEASURED
  S10 census: a thing born after the shell (id > hi) is not counted; a thing listed and in a carrier is a duplicate
  S11 the live arm misses a staged thing (the rect missed it)              -> SA_EACH_ONCE UNMEASURED, never PASS

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_save_in_air.py
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "proof"))
import scene_save_in_air as S  # noqa: E402

IDS = ["101", "102", "103"]           # steel, comp, heavy


def arm(ids=IDS, dup=()):
    return {"ids": sorted(ids), "dup": sorted(dup), "stack": {"101": "in_air", "102": "in_air", "103": 1}}


GOOD = {
    "stage": "STAGED items at 40,40 tick=1000", "staged_ids": IDS, "steel_id": "101", "load_slack": 3,
    "air_at_save": [{"innerId": "101", "left": 11}, {"innerId": "102", "left": 9}],
    "air_at_load": [[{"innerId": "101", "left": 10}, {"innerId": "102", "left": 8}],
                    [{"innerId": "101", "left": 10}, {"innerId": "102", "left": 8}]],
    "arms": {"A": arm(), "B": arm(), "C": arm()},
    "triplet": {"verdict": "IDENTICAL", "target": 1012},
    "landed": {"ticks": 20, "carriers_left": [], "census": {"ids": IDS, "dup": [], "stack": {"101": 75, "102": 1, "103": 1}}},
}


def plant(fn):
    ev = copy.deepcopy(GOOD)
    fn(ev)
    return S.judge(ev)


def main():
    fails = []

    def expect(case, rows, want):
        for rid in S.ROWS:
            st = rows.get(rid, ("MISSING",))[0]
            w = want.get(rid, "PASS")
            if st != w:
                fails.append("%s: %s is %s, want %s (%s)" % (case, rid, st, w, rows.get(rid)))

    expect("S1", S.judge(copy.deepcopy(GOOD)), {})
    expect("S2", plant(lambda e: e["arms"].__setitem__("B", arm(dup=["101"]))), {"SA_EACH_ONCE": "FAIL"})

    def drops(e):
        e["arms"]["B"] = arm(ids=IDS[:2])
        e["arms"]["C"] = arm(ids=IDS[:2])
        e["triplet"]["verdict"] = "SAVE_DROPS_STATE"
    expect("S3", plant(drops), {"SA_EACH_ONCE": "FAIL"})
    expect("S4", plant(lambda e: e["triplet"].__setitem__("verdict", "LOAD_NONDETERMINISTIC")), {"SA_EACH_ONCE": "UNMEASURED"})
    expect("S5", plant(lambda e: e.__setitem__("air_at_save", [])),
           {"SA_IN_AIR": "FAIL", "SA_AIR_AT_LOAD": "UNMEASURED", "SA_EACH_ONCE": "UNMEASURED", "SA_LANDED": "UNMEASURED"})
    expect("S6", plant(lambda e: e["air_at_load"].__setitem__(1, [])), {"SA_AIR_AT_LOAD": "FAIL"})
    expect("S7", plant(lambda e: e["landed"].__setitem__("carriers_left", [{"innerId": "101", "left": 3}])), {"SA_LANDED": "FAIL"})
    expect("S8", plant(lambda e: e["landed"]["census"]["stack"].__setitem__("101", 74)), {"SA_LANDED": "FAIL"})
    expect("S9", plant(lambda e: e.__setitem__("stage", "INVALID items site: climb depth 2")),
           {"SA_PRE": "FAIL", "SA_IN_AIR": "UNMEASURED", "SA_AIR_AT_LOAD": "UNMEASURED", "SA_EACH_ONCE": "UNMEASURED",
            "SA_LANDED": "UNMEASURED"})
    c = S.census([{"id": "Steel101", "stackCount": 75}, {"id": "Filth200", "stackCount": 1}],
                 "RM_ThingFlyer_Knockback9 inner=Steel x75 innerId=Steel101 at=1,1 dest=4,1 left=7 bounces=0", 103)
    if c["ids"] != ["101"] or c["dup"] != ["101"]:
        fails.append("S10: census %s, want ids ['101'] and dup ['101']" % c)
    expect("S11", plant(lambda e: [e["arms"].__setitem__(k, arm(ids=IDS[:2])) for k in "ABC"]),
           {"SA_EACH_ONCE": "UNMEASURED", "SA_LANDED": "PASS"})
    for f in fails:
        print("FAIL " + f)
    print("explosive knockback save in air judgment: %s (%d of 11 cases wrong)" % ("PASS" if not fails else "FAIL", len(
        set(f.split(":")[0] for f in fails))))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
