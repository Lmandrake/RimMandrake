#!/usr/bin/env python3
"""selftest_brake_release_plans.py - a brake_release pass plans lazily, so its cost does not grow with the roster
(RIMMANDRAKE_SHORTEN_BRAKE_PASS_STEWARD_MISSED_ITS_BEAT). Parent incident: one fill_plan per mod made a pass over 120 s,
brake_release.json ran 38 min stale and steward.json missed its heartbeat twice. fill_plan is stubbed and COUNTED.
The record keeps four answers apart: planned and braked / planned and not braked / not planned this pass / could not plan."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
tmp = tempfile.mkdtemp(prefix="rf_brake_plans_")
os.environ.update(TESTQ_QUEUE=os.path.join(tmp, "q"), TESTQ_INGEST_PUSH="0", RM_DATA_ROOT=os.path.join(tmp, "data"))
os.makedirs(os.environ["TESTQ_QUEUE"])
import brake_release as BR  # noqa: E402
import testq as T  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


calls = []
verdicts = {}


def stub_plan(mod, n, cap, *, now=None):
    calls.append(mod)
    v = verdicts.get(mod, "busy")
    if isinstance(v, Exception):
        raise v
    return {"verdict": v, "text": "%s says %s" % (mod, v), "tail": []}


T.brake_tail = lambda mine: [object()]      # the lane is braked
T.filler_jobs = lambda: []
T.fill_plan = stub_plan
BR.causes_of = lambda tails, now: {}
BR.tail_ids = lambda tails: ["J1", "J2"]
BR.spent_on = lambda tails: None
T.companion_hold = lambda: "stub hold"      # stops decide() before it would submit: not the point here
T.job_of = lambda t: {"id": "J"}

mods = ["M%02d" % i for i in range(40)]

# A3 + A1: the braked mod is the first braked one, as before (the others are held, the one verdict that is per mod),
# and a pass over 40 mods plans only until it is found
verdicts.clear(); verdicts.update({m: "held" for m in mods}); verdicts.update({"M03": "brake", "M09": "brake"})
calls.clear()
r = BR.decide(1000.0, mods)
check(calls == ["M00", "M01", "M02", "M03"], "stops planning at the first braked mod (calls: %s)" % calls)
check(r.get("state") == "wait" and r.get("reason") == "stub hold", "and the braked mod M03 is the one acted on: %s" % r)

# A1: a mod-independent non-brake verdict (the lane is busy for every mod) costs one plan, not 40
verdicts.clear()
calls.clear()
r = BR.decide(1000.0, mods)
check(len(calls) == 1, "no brake and nothing mod-specific: %d plan call(s) over %d mods" % (len(calls), len(mods)))
check(r["state"] == "none" and r["planned"] == ["M00"] and len(r["not_planned"]) == 39,
      "the record says M00 was looked at and found not braked, and 39 were NOT planned: %s" % {k: r.get(k) for k in ("planned", "not_planned")})

# a held mod is skipped cheaply and the next mod is planned; held is mod-specific so planning goes on past it
verdicts.clear(); verdicts.update({"M00": "held", "M01": "held"})
calls.clear()
r = BR.decide(1000.0, mods)
check(calls == ["M00", "M01", "M02"], "held mods do not settle the lane's verdict; the first non-held does: %s" % calls)

# A2: a fill_plan that cannot run is UNMEASURED, not 'no brake'
verdicts.clear(); verdicts.update({"M00": RuntimeError("boom")})
calls.clear()
r = BR.decide(1000.0, mods)
check(r["state"] == "none" and r.get("unmeasured", {}).get("M00", "").startswith("RuntimeError"),
      "a plan that raised is named under unmeasured: %s" % r.get("unmeasured"))
check("M00" not in r["planned"] and r["planned"] == ["M01"], "and the next mod is still planned: %s" % r["planned"])

# every plan failing: UNMEASURED state, not 'none'
verdicts.clear(); verdicts.update({m: RuntimeError("down") for m in mods})
r = BR.decide(1000.0, mods)
check(r["state"] == "unmeasured" and "none" != r["state"], "no mod could be planned: state %s" % r["state"])

# a braked mod found after an earlier failure is still acted on
verdicts.clear(); verdicts.update({"M00": RuntimeError("x"), "M01": "brake"})
r = BR.decide(1000.0, mods)
check(r["state"] == "wait", "a failure before the braked mod does not hide the brake: %s" % r["state"])

print("fails: %d" % len(FAILS))
sys.exit(1 if FAILS else 0)
