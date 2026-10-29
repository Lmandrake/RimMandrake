#!/usr/bin/env python3
"""selftest for helper_budget.py (HELPER_BUDGET_MIGRATE_INTO_DISPATCHER): the Dispatcher publishes the helper budget,
the spawn hook reads it.

    python3 src/RimMandrake/rimflow/selftest_helper_budget.py
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import helper_budget as HB  # noqa: E402

FAILS = []
NOW = 1793050000.0


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


class FakeSA(object):
    """The slot_allocator surface helper_budget uses; compute() counts its calls."""
    def __init__(self, seats, streams, raise_=None):
        self.seats, self.streams, self.raise_, self.calls = seats, streams, raise_, 0

    def streams_dir(self):
        from pathlib import Path
        return Path(self.streams)

    def load_rules(self):
        return {"seats": ["BENCH", "FOUNDRY"]}

    def compute(self, now, rules, seat="BENCH"):
        self.calls += 1
        if self.raise_:
            raise self.raise_
        return {"t": now, "at": "x", "mode": "CRUISE", "presence": "AFK", "seats": dict(self.seats),
                "why": "v3: machine total 2 -> FOUNDRY 2", "override": None}

    @staticmethod
    def seat_label(k):
        return {"BENCH": "CONDUCTOR"}.get(k, k)


root = tempfile.mkdtemp()
streams = tempfile.mkdtemp()
sa = FakeSA({"BENCH": 0, "FOUNDRY": 2}, streams)

# ---- publish
rec = HB.publish(root, NOW, sa=sa)
p = os.path.join(root, "helper_budget.json")
check("publish writes helper_budget.json under the Dispatcher's state root", os.path.exists(p), p)
disk = json.load(open(p))
check("seats are published under v3 names: CONDUCTOR, FOUNDRY (no BENCH)", disk["seats"] == {"CONDUCTOR": 0, "FOUNDRY": 2},
      disk["seats"])
check("the record says the Dispatcher published it, when, and why", disk["by"] == "dispatcher" and disk["t"] == NOW
      and "machine total" in disk["why"], disk)
check("compute() ran once, fresh this tick (presence is re-read every 2 min, not every 15)", sa.calls == 1, sa.calls)

# ---- read (the hook's side)
r = HB.read(root, NOW + 60, sa=sa)
check("read: a fresh budget is returned", r is not None and r["seats"]["FOUNDRY"] == 2, r)
check("read: older than max_age_s -> None (the hook falls back)", HB.read(root, NOW + HB.MAX_AGE_S + 1, sa=sa) is None)
ov = os.path.join(streams, "slot_override.json")
open(ov, "w").write("{}")
os.utime(ov, (NOW + 30, NOW + 30))
check("read: his word written after the budget -> None (the hook computes with it)", HB.read(root, NOW + 60, sa=sa) is None)
os.utime(ov, (NOW - 30, NOW - 30))
check("read: his word older than the budget -> the budget", HB.read(root, NOW + 60, sa=sa) is not None)
open(p, "w").write("{not json")
check("read: a torn file -> None, never a raise", HB.read(root, NOW + 60, sa=sa) is None)
check("read: no file -> None", HB.read(tempfile.mkdtemp(), NOW) is None)
json.dump({"t": NOW, "seats": {"FOUNDRY": "x"}}, open(p, "w"))
check("read: a non-count seat value -> None", HB.read(root, NOW + 1, sa=sa) is None)
json.dump({"t": NOW + 10 * 3600, "seats": {"FOUNDRY": 2}}, open(p, "w"))
check("read: a budget stamped in the future -> None", HB.read(root, NOW, sa=sa) is None)

json.dump({"t": NOW + 6, "seats": {"FOUNDRY": 2}}, open(p, "w"))
check("r1#4 read: a budget stamped even 6 s ahead -> None (only clock jitter is forgiven)", HB.read(root, NOW, sa=sa) is None)

# ---- seat names
check("seat_for: BENCH window, bench and CONDUCTOR all mean the Conductor's budget",
      HB.budget_seat("BENCH") == "CONDUCTOR" and HB.budget_seat("bench") == "CONDUCTOR"
      and HB.budget_seat("CONDUCTOR") == "CONDUCTOR" and HB.budget_seat("FOUNDRY") == "FOUNDRY")

# ---- the tick step never raises and journals a failure once per alarm window
jr = []
st = {}
ON = {"alarm_every_s": 3600, "helper_budget": {"enabled": True}}
none_root = tempfile.mkdtemp()
counting = FakeSA({"FOUNDRY": 1}, streams)
HB.tick_step({"alarm_every_s": 3600}, {}, none_root, NOW, sa=counting, journal=jr.append)
check("tick_step: a schedule with no helper_budget block publishes nothing and computes nothing (fixture schedules "
      "never read the real transcripts)", counting.calls == 0 and not os.listdir(none_root), counting.calls)
live = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
check("the live dispatcher_schedule.json opts in: helper_budget.enabled true",
      (live.get("helper_budget") or {}).get("enabled") is True, live.get("helper_budget"))
bad = FakeSA({}, streams, raise_=RuntimeError("meter gone"))
out = HB.tick_step(ON, st, root, NOW, sa=bad, journal=lambda rec: jr.append(rec))
check("tick_step: a failing compute returns an alarm, does not raise", out and out["do"] == "alarm"
      and out["kind"] == "budget:failed" and "meter gone" in out["why"], out)
check("tick_step: the alarm is journalled", len(jr) == 1, jr)
HB.tick_step(ON, st, root, NOW + 120, sa=bad, journal=lambda rec: jr.append(rec))
check("tick_step: the same failure 2 min later is not journalled again", len(jr) == 1, jr)
HB.tick_step(ON, st, root, NOW + 3700, sa=bad, journal=lambda rec: jr.append(rec))
check("tick_step: ... but is after alarm_every_s", len(jr) == 2, jr)
def boom(rec):
    raise OSError("disk full")


try:
    out = HB.tick_step(ON, {}, root, NOW, sa=bad, journal=boom)
    check("r1#2 tick_step: a journal that raises on the alarm path still does not raise", out and out["do"] == "alarm", out)
except Exception as e:  # noqa: BLE001
    check("r1#2 tick_step: a journal that raises on the alarm path still does not raise", False, repr(e))
ok = HB.tick_step(ON, st, root, NOW + 3800, sa=sa, journal=lambda rec: jr.append(rec))
check("tick_step: a good compute publishes and returns None", ok is None and json.load(open(p))["t"] == NOW + 3800, ok)
check("tick_step: recovery clears the alarm stamp", "budget:failed" not in (st.get("alarms") or {}), st)
off = HB.tick_step({"helper_budget": {"enabled": False}}, st, root, NOW + 4000, sa=sa, journal=lambda rec: jr.append(rec))
check("tick_step: helper_budget.enabled false -> nothing published", off is None and json.load(open(p))["t"] == NOW + 3800)

# ---- dispatcher wires it into the tick
src = open(os.path.join(HERE, "dispatcher.py")).read()
check("dispatcher.tick calls helper_budget.tick_step", "HB.tick_step(" in src)

# ---- the hook reads the Dispatcher's budget first
hook = open(os.path.join(HERE, "..", "..", "..", ".claude", "hooks", "block_agent_over_slots.py")).read()
check("the spawn hook reads helper_budget.read", "helper_budget" in hook and ".read(" in hook)

print("\n%s: %d failed" % ("GREEN" if not FAILS else "RED", len(FAILS)))
sys.exit(1 if FAILS else 0)
