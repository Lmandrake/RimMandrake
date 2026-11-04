#!/usr/bin/env python3
"""relentless.py obeying Operations' health verdict (PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF). Owner 2026-11-03: system
items before content; Operations judges, Relentless asks; card: "System work immediately but existing non system work
continues. If all system tickets are already being worked non system work can be selected." Planted: a fresh, a
degraded, a stale and a missing verdict; system items enrol past a full share and lead the line; degraded pauses new
content and stops nothing running; when every system item is worked, content goes; the real Effects reads the file
and reorders the real pool. No units, no network."""
import json
import os
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=0.5, max_workers=2,
             enrol_per_tick=50, max_queued=50, staffing=None, one_builder_per_mod=False)


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


class Fx:
    """Only what enrol and lease read before a start."""
    def __init__(self, order, first=None, degraded=False, plan=None):
        self.order, self.first, self.degraded, self.plan = order, first or {}, degraded, plan or {}

    def pool_order(self, r):
        return list(self.order), None

    def item_state(self, item):
        return None         # unpublished: lease walks past it without starting anything


def q(item, status="queued", **kw):
    return dict(R.new_state(item, 1.0, ""), status=status, **kw)


# --- the pure order
order = [s["item"] for s in R.queue_order([q("C_FRESH"), q("C_BACK", returned_at=5.0), q("P_LIST"), q("S2"), q("S1"),
                                          q("S_RUN", status="running")], {"P_LIST": 0}, {"S1": 0, "S2": 1})]
ok(order == ["S1", "S2", "P_LIST", "C_BACK", "C_FRESH"], "queue: system first in the verdict's order, then the list, "
   "returned, fresh; running work is not in the line", order)
ok([s["item"] for s in R.queue_order([q("B"), q("A")])] == ["A", "B"], "queue: no verdict keeps the old order")

# --- health_order: what Relentless obeys
h = R.health_order({"state": "healthy", "system_items": ["S1", "S2"], "why": "ok"}, "fresh: healthy", lambda: ["X"])
ok(h["first"] == {"S1": 0, "S2": 1} and h["fresh"] and not h["degraded"], "health: a fresh verdict's items lead", h)
h = R.health_order({"state": "degraded", "system_items": ["S1"], "why": "spent"}, "fresh: degraded", lambda: [])
ok(h["degraded"] and "spent" in h["why"], "health: degraded is carried, with Operations' reason", h)
h = R.health_order(None, "health verdict stale: as_of x", lambda: ["S9", "S8"])
ok(h["first"] == {"S9": 0, "S8": 1} and not h["fresh"] and not h["degraded"] and "stale" in h["why"]
   and "at once" in h["why"], "health: stale -> every open system item first at once, content never paused, said", h)


def boom():
    raise OSError("rules gone")


h = R.health_order(None, "no health verdict at p", boom)
ok(h["first"] == {} and "ordinary order" in h["why"] and "rules gone" in h["why"], "health: no classifier -> ordinary order, said", h)
h = R.health_order({"state": "degraded", "system_items": None, "why": "no ledger"}, "fresh: degraded", lambda: ["S3"])
ok(h["first"] == {"S3": 0} and h["degraded"], "health: a verdict with no item list keeps its state, asks the classifier", h)

# --- the owner's token pause: system, expedited and live iteration go on, content waits, and off means off
on = {"only_system_and_live": True}
ok(R.owner_hold(on, "C1", {"S1": 0}), "owner hold: content waits")
ok(R.owner_hold(on, "C1", {"S1": 0}, {"item": "C1"}), "owner hold: queued content waits")
ok(not R.owner_hold(on, "S1", {"S1": 0}), "owner hold: a system item goes")
ok(not R.owner_hold(on, "C1", {}, {"expedite": {"level": "expedited"}}), "owner hold: an expedited item goes")
ok(not R.owner_hold(on, "C1", {}, {"live_iter": {"round": 1}}), "owner hold: a live iteration goes")
ok(not R.owner_hold({}, "C1", {"S1": 0}), "owner hold: off stops nothing")

# --- content_paused
fx = Fx([], {"S1": 0}, degraded=True)
ok(R.content_paused(fx, [q("S1")]), "paused: degraded and a system item waits in line")
ok(not R.content_paused(fx, [q("S1", status="running")], ["S1"], {"S1"}),
   "paused: degraded but every system item is being worked -> content may go")
ok(R.content_paused(fx, [], ["S1"], set()), "paused: degraded and a system item not yet enrolled")
ok(not R.content_paused(Fx([], {"S1": 0}), [q("S1")]), "paused: healthy never pauses")
ok(not R.content_paused(Fx([], {}, degraded=True), [q("C1")]), "paused: degraded with no system item at all does not idle")


def store():
    d = tempfile.mkdtemp(prefix="rlhealth-")
    return d, R.Store(d)


# --- enrol: a system item waits for no share
d, s = store()
for i in ("C_A", "C_B"):
    st = R.new_state(i, 1.0, "")
    s.save(st)
r = dict(RULES, share=0.01)        # the share is full: ceil(0.01 * pool) is 1, and two run already
fx = Fx(["S1", "C_C"], {"S1": 0})
took = R.enrol(s, fx, r, 100.0)
ok(took == ["S1"], "enrol: a system item enrols past a full share; content does not", took)
shutil.rmtree(d, ignore_errors=True)

d, s = store()
fx = Fx(["S1", "C_C", "C_D"], {"S1": 0}, degraded=True)
took = R.enrol(s, fx, dict(RULES, share=1.0), 100.0)
ok(took == ["S1"], "enrol: degraded enrols the system item and no content while it waits", took)
fx = Fx(["S1", "C_C", "C_D"], {"S1": 0}, degraded=False)
took = R.enrol(s, fx, dict(RULES, share=1.0), 100.0)
ok(took == ["C_C", "C_D"], "enrol: healthy, content follows the system item", took)
shutil.rmtree(d, ignore_errors=True)

d, s = store()
s.save(q("S_RUN", status="running"))
fx = Fx(["S_RUN", "C_C"], {"S_RUN": 0}, degraded=True)
took = R.enrol(s, fx, dict(RULES, share=1.0), 100.0)
ok(took == ["C_C"], "enrol: degraded, but the only system item is already worked -> content enrols", took)
shutil.rmtree(d, ignore_errors=True)

d, s = store()
s.save(R.new_state("S_Q", 1.0, ""))
s.save(dict(R.new_state("C_Q", 1.0, ""), enrolled_at=0.5))
run = q("C_RUN", status="running")
s.save(run)
acts = []
R.lease(s, Fx([], {"S_Q": 0}, degraded=True), dict(RULES, share=1.0), 100.0, acts)
ok(any(a.get("why", "").startswith("health degraded") for a in acts) and s.load("C_Q")["status"] == "queued",
   "lease: degraded, content in line waits, said", acts)
ok(s.load("C_RUN")["status"] == "running", "lease: running content is never stopped")
acts = []
R.lease(s, Fx([], {"S_Q": 0}, degraded=False), dict(RULES, share=1.0), 100.0, acts)
ok(not any("health" in a.get("why", "") for a in acts), "lease: healthy never waits on health", acts)
shutil.rmtree(d, ignore_errors=True)

# --- the real Effects: reads the file, reorders the real pool
vd = tempfile.mkdtemp(prefix="rlhealth-v-")
os.environ["RM_OPS_WATCH_DIR"] = vd
d, s = store()
base = dict(RULES, pool_seats=["BENCH"], pool_needs=["offline"], pool_targets=["v1"], pool_kinds_exclude=[], pool_ids_exclude=[])
fx = R.Effects(base, s)
plain, w = fx.pool_order(base)
ok(fx._health and not fx._health["fresh"] and "no health verdict" in fx._health["why"],
   "real: no file -> not fresh, said", fx._health and fx._health["why"])
ok(len(plain) > 2, "real: the pool has items to reorder", len(plain))
tail = plain[-2:][::-1]
now = time.time()
with open(os.path.join(vd, "health.json"), "w") as f:
    json.dump({"schema": "rm.ops_health/1", "as_of": R.iso(now), "t": now, "state": "degraded", "system_items": tail,
               "max_age_min": 45, "why": "planted"}, f)
fx = R.Effects(base, s)
got, _ = fx.pool_order(base)
ok(got[:2] == tail and set(got) == set(plain) and fx.degraded, "real: a fresh verdict's items lead the real pool, none lost",
   got[:3])
with open(os.path.join(vd, "health.json"), "w") as f:
    json.dump({"schema": "rm.ops_health/1", "as_of": R.iso(now - 7200), "t": now - 7200, "state": "degraded",
               "system_items": tail, "max_age_min": 45, "why": "planted"}, f)
fx = R.Effects(base, s)
fx.pool_order(base)
ok(not fx.degraded and "stale" in fx._health["why"] and "at once" in fx._health["why"],
   "real: a stale verdict pauses nothing and asks Operations' classifier", fx._health["why"])
shutil.rmtree(d, ignore_errors=True)
shutil.rmtree(vd, ignore_errors=True)

print("selftest_relentless_health: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
