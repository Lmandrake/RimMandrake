#!/usr/bin/env python3
"""ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES: two role_launch review leftovers (review g2r2,
D:\\ClaudeWork\\rimmandrake\\ops_memory_wire\\review_rl_g2r2.md).

  F1 a degraded ops reading (degraded_reading_ok) is judged by the MOST CAUTIOUS configured band, picked explicitly:
     a stricter week_left_pct_lt FLOOR band is no longer bypassed by a made-up healthy week_left (it was 100.0), and
     when another band is stricter than FLOOR, that one is picked.
  F2 a roles entry whose name is not a nonempty string, or whose after_role is not a string, is skipped with one
     alarm; roles_by_name / decide_order / supervise_roles / decide_roles never raise TypeError on it, and every other
     role is still supervised and decided.
Pure: no systemd, no files beyond selftest_dispatcher's tmp dir.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ["TZ"] = "UTC"
import time  # noqa: E402
time.tzset()
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def collector():
    acts = []
    return acts, lambda **kw: acts.append(kw)


T = SD.at_local("08:00")          # the Conductor's first slot of the day
DEGRADED = {"state": "MEASURED", "degraded": "status.json missing", "account": None, "at": "UNREADABLE",
            "runway": 0.0, "runway_m": "UNMEASURED", "week_left": 0.0, "week_left_m": "UNMEASURED"}


def f1_band_unit():
    c = SD.conductor()
    check(RL.band(c, DEGRADED)[0] == "FLOOR", "F1 degraded reading, FLOOR is the strictest (slots none) -> FLOOR")
    # the bug's shape: a degraded reading with a HEALTHY week_left must still get FLOOR (no value decides it)
    check(RL.band(c, dict(DEGRADED, week_left=100.0, runway=9.0))[0] == "FLOOR",
          "F1 degraded reading with placeholder week_left 100 / runway 9 -> still FLOOR (values not consulted)")
    stricter = {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
                "RED": {"runway_ge": 0.0, "quick_cap_x": 0.4, "slots": "none"},
                "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 1.0, "slots": "first"}}
    check(RL.band({"throttle_bands": stricter}, DEGRADED)[0] == "RED",
          "F1 a band stricter than FLOOR (slots none vs first) is the one picked")
    tie = {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
           "RED": {"runway_ge": 0.0, "quick_cap_x": 1.0, "slots": "all"},
           "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 1.0, "slots": "all"}}
    check(RL.most_cautious_band(tie)[0] == "FLOOR", "F1 full tie on slots and factor -> the FLOOR band")
    cap = {"A": {"runway_ge": 1.0, "quick_cap_x": 0.5, "slots": "all"},
           "B": {"runway_ge": 0.0, "quick_cap_x": 0.8, "slots": "all"}}
    check(RL.most_cautious_band(cap)[0] == "A", "F1 same slots -> the smaller quick_cap_x")
    # a MEASURED reading is unchanged: healthy -> GREEN, low week_left -> FLOOR
    ok = {"state": "MEASURED", "runway": 2.0, "week_left": 40.0}
    check(RL.band(c, ok)[0] == "GREEN" and RL.band(c, dict(ok, week_left=5.0))[0] == "FLOOR",
          "F1 measured readings keep their band (GREEN; FLOOR under the line)")


def f1_decide_not_advisory():
    # strict caps (caps_advisory false) + degraded_reading_ok + no status.json: before the fix the made-up
    # week_left 100 / runway 0 chose RED (slots first), so the 08:00 first slot LAUNCHED past a FLOOR of slots none
    c = SD.conductor(caps_advisory=False, degraded_reading_ok=True)
    acts, act = collector()
    st = {"roles": {}}
    RL.decide_roles({"roles": [c]}, st, SD.robs(None), T, act, set(), None)
    launched = [a for a in acts if a.get("do") == "role_launch"]
    held = [a for a in acts if a.get("do") == "role_hold" and "band FLOOR" in a.get("why", "")]
    check(not launched, "F1 strict caps, degraded reading: nothing launched (got %d launches)" % len(launched))
    check(len(held) == 1, "F1 strict caps, degraded reading: held by band FLOOR (%s)"
          % [a.get("why", "")[:90] for a in acts])
    # advisory caps (the default) still launch on the degraded reading: FLOOR is read as all slots
    acts2, act2 = collector()
    RL.decide_roles({"roles": [SD.conductor(degraded_reading_ok=True)]}, {"roles": {}}, SD.robs(None), T, act2,
                    set(), None)
    check(any(a.get("do") == "role_launch" for a in acts2), "F1 advisory caps, degraded reading: still launches")


def f2_names():
    good = SD.conductor()
    odd = [SD.conductor(name=["Conductor"]), SD.conductor(name={"n": 1}), SD.conductor(name=""),
           SD.conductor(name=None), SD.conductor(name="Odd", after_role=["Conductor"]),
           SD.conductor(name="Odder", after_role={"r": 1})]
    sch = {"roles": odd + [good]}
    try:
        by = RL.roles_by_name(sch)
        check(set(by) == {"Conductor", "Odd", "Odder"}, "F2 roles_by_name keeps only string names: %s" % sorted(by))
    except TypeError as e:
        check(False, "F2 roles_by_name raised TypeError: %s" % e)
    try:
        order = RL.decide_order(odd + [good])
        check(len(order) == len(odd) + 1, "F2 decide_order orders every entry without raising")
    except TypeError as e:
        check(False, "F2 decide_order raised TypeError: %s" % e)
    for r in odd:
        check(RL.role_shape_error(r) is not None, "F2 role_shape_error refuses name %r after_role %r"
              % (r.get("name"), r.get("after_role")))
    check(RL.role_shape_error(good) is None and RL.role_shape_error(SD.conductor(after_role=None)) is None,
          "F2 role_shape_error passes a good role (after_role absent or null)")
    # supervision: the good role's running run is still checked (its unit inactive -> finished)
    st = {"roles": {"Conductor": {"done": {}, "runs": [{"state": "running", "unit": "u1", "at": T - 60,
                                                         "mode": "quick", "budget": 1000, "item": "ROLES_ITEM_X",
                                                         "seat": "BENCH", "run_max_s": 1800, "day": RL.day_of(T),
                                                         "scope": "sc-u1"}]}}}
    acts, act = collector()
    try:
        RL.supervise_roles(sch, st, SD.robs(SD.ops_status(T), unit="inactive"), T, act)
        check(st["roles"]["Conductor"]["runs"][0]["state"] != "running",
              "F2 supervise_roles still finishes the good role's run beside malformed entries")
    except TypeError as e:
        check(False, "F2 supervise_roles raised TypeError: %s" % e)
    # decide: one alarm names the malformed entries, the good role still launches its 08:00 slot
    acts, act = collector()
    try:
        RL.decide_roles(sch, {"roles": {}}, SD.robs(SD.ops_status(T)), T, act, set(), None)
    except TypeError as e:
        check(False, "F2 decide_roles raised TypeError: %s" % e)
    shape = [a for a in acts if a.get("kind") == "role:schedule:shape"]
    check(len(shape) == 1 and "6 roles entr" in shape[0]["why"], "F2 one shape alarm for the 6 malformed entries")
    check([a.get("role") for a in acts if a.get("do") == "role_launch"] == ["Conductor"],
          "F2 the good role is still decided and launched (launches: %s)"
          % [a.get("role") for a in acts if a.get("do") == "role_launch"])


f1_band_unit()
f1_decide_not_advisory()
f2_names()
print("\n%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
