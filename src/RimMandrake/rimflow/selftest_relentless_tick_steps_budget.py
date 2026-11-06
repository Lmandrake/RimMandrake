#!/usr/bin/env python3
"""OPS_RELENTLESS_READING_RESTORE_IUUR (outage of 2026-11-06 06:25Z). reading.json is written when a tick ends, and a 572 s
tick (steps 351 s, enrol_lease 131 s) left it 693 s old against relentless.tick_age_s's 600 s. Only game items had a
budget. A tick now stops stepping the others past tick_steps_budget_s, serves what waited first on the next tick, and
makes no new clones past tick_lease_budget_s, so a tick's length has a bound however many items run slow.

    python3 src/RimMandrake/rimflow/selftest_relentless_tick_steps_budget.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import selftest_relentless as T  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


class Slow:
    """R.step, recording who it served, each one costing `each` seconds on the tick's wall clock."""

    def __init__(self, x, each):
        self.clock, self.each, self.served = [0.0], each, []
        x.w.wall = lambda: self.clock[0]
        self.keep = R.step

        def step(store, fx, r, item, now, acts):
            self.served.append(item)
            self.clock[0] += self.each
        R.step = step

    def off(self):
        R.step = self.keep


def rig(names, **rules):
    x = T.Rig(n=0, share=1.0, **rules)
    for name in names:
        T.parked(x, name, "running", "/c/" + name)
    return x


def t_slow_steps_stop_at_the_budget():
    """The instance: eight items at 100 s each would hold the tick 800 s; the budget stops it after three."""
    names = ["S%d" % i for i in range(8)]
    x = rig(names, tick_steps_budget_s=240)
    s = Slow(x, 100)
    try:
        acts = x.tick()
        first = list(s.served)
        ok(first == names[:3], "steps stop once 240 s are spent (100, 200, 300): %s" % first)
        said = [a for a in acts if a.get("do") == "tick_steps_budget"]
        ok(said and said[0].get("deferred") == 5, "the tick says how many waited: %s" % said)
        s.served[:], s.clock[0] = [], 0.0
        x.tick()
        ok(s.served[:3] == names[3:6], "what waited goes first on the next tick: %s" % s.served)
        s.served[:], s.clock[0] = [], 0.0
        x.tick()
        ok(s.served[:2] == names[6:8], "and nothing starves, the tail reaches the top in turn: %s" % s.served)
    finally:
        s.off()
        x.done()


def t_stopping_item_is_never_deferred():
    """A stopping item is holding a place: it is served however late, or the belt loses the place for a tick."""
    x = rig(["A0", "A1", "Z9"], tick_steps_budget_s=50)
    T.parked(x, "Z9", "stopping", "/c/Z9")
    s = Slow(x, 100)
    try:
        x.tick()
        ok(s.served[0] == "A0" and "A1" not in s.served, "the plain item waits: %s" % s.served)
        ok("Z9" in s.served, "the stopping one is served past the budget: %s" % s.served)
    finally:
        s.off()
        x.done()


def t_no_rule_no_deferral():
    """A rig with no budget steps everything: a missing rule never starves an item."""
    names = ["N%d" % i for i in range(4)]
    x = rig(names, tick_steps_budget_s=None)
    s = Slow(x, 1000)
    try:
        acts = x.tick()
        ok(s.served == names, "every item stepped: %s" % s.served)
        ok(not [a for a in acts if a.get("do") == "tick_steps_budget"], "and nothing said")
        ok(not os.path.exists(x.s.p(R.STEPS_DEFERRED)), "and no memo left behind")
    finally:
        s.off()
        x.done()


def t_a_late_lease_makes_no_clone():
    """Past tick_lease_budget_s no new clone starts: each costs up to a minute, and the next tick is 15 s away."""
    for late, clones in ((True, 0), (False, 2)):
        x = T.Rig(n=2, share=1.0, tick_lease_budget_s=360)
        clock = [0.0]
        x.w.wall = lambda: clock[0]
        keep = R.launch_proved

        def before_lease(store, now):
            if late:
                clock[0] = 400.0
            return keep(store, now)
        R.launch_proved = before_lease
        try:
            acts = x.tick()
        finally:
            R.launch_proved = keep
        tried = sum(1 for a in acts if a.get("do") == "clone_try")
        ok(tried == clones, "%s lease: %d clones tried, wants %d" % ("late" if late else "on-time", tried, clones))
        said = [a for a in acts if a.get("do") == "tick_lease_budget"]
        ok(bool(said) == late, "the late one says why: %s" % said)
        x.done()


def t_live_rules_fit_the_alarm():
    """The live numbers: budgets plus the phases that follow them fit the alarm's limit, timer gap included."""
    live = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
    ops = os.path.join(os.path.dirname(R.HERE), "Utils", "ops_watch_rules.json")
    with open(ops, encoding="utf-8") as f:
        rule = json.load(f)["ranges"]["relentless.tick_age_s"]
    limit = rule["max_age_min"] * 60
    steps, lease = live.get("tick_steps_budget_s"), live.get("tick_lease_budget_s")
    ok(bool(steps) and bool(lease) and steps < lease, "both budgets are set, steps first: %s, %s" % (steps, lease))
    # 2026-11-06 medians and tails: a clone 40 s past the lease budget, staffing_live 100 s, flush 45 s, the timer's 15 s
    ok(bool(lease) and lease + 40 + 100 + 45 + 15 <= limit, "the lease budget plus what follows fits %d s: %s" % (limit, lease))
    ok("2 min" not in rule["why"], "the rule no longer quotes the timer's old 2 min pause")


if __name__ == "__main__":
    for t in (t_slow_steps_stop_at_the_budget, t_stopping_item_is_never_deferred, t_no_rule_no_deferral,
              t_a_late_lease_makes_no_clone, t_live_rules_fit_the_alarm):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a raise is a failed clause, the other tests still say theirs
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, str(e)[:300]))
    print("selftest_relentless_tick_steps_budget: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
    sys.exit(1 if FAILS else 0)
