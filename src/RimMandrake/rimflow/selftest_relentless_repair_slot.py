#!/usr/bin/env python3
"""The reserved repair slot in enrol (relentless_repair_slot, RELENTLESS_REWIRE_ENROL_BY_FAN_IN; owner-ordered pipeline
redesign 2026-11-06, redesign_final.md G8). Acceptance: a repair with >= 3 dependents is enrolled within one wake while
the caps hold for everything else. Planted, with the owner's pipeline-only pause on and the line full (enrol_per_tick and
max_queued spent by system items): the repair with the most dependents is enrolled past the caps, alone; a smaller system
item and content are not; a repair under the threshold is not; a slot already held (a queued repair) admits nothing more;
two candidates give one, the heavier; a content item with many dependents (not system) never takes it; the switch off
gives nothing; a concept-refused candidate is passed over, as is one the pool leaves out; the real fan-in path
(ops_health.fan_in over a ledger replay) drives it.
No units, no network."""
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=1.0,
             max_workers=3, enrol_per_tick=1, max_queued=2, staffing=None, one_builder_per_mod=False)
ON = {"pipeline_only": True, "pipeline_prefixes": ["LIGHTSPEED_"]}
NOW = 1_000_000.0
DIRS = []


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


class Fx:
    def __init__(self, order, first, fan=None, refused=(), world=None):
        self.order, self.first, self.plan = list(order), first, {}
        self.degraded, self.pause_scope = False, None
        self.owner_pause_rule = ON
        self._fan, self._refused, self._world = fan, set(refused), world
        if fan is not None:
            self.repair_fan_in = lambda now: dict(self._fan)
        if world is not None:
            self.ledger_items = lambda: ([], self._world)

    def pool_order(self, r):
        return list(self.order), None

    def item_state(self, item, fresh=False):
        return None

    def owner_ruled_at(self, item):
        return None

    def concept_refusal(self, item):
        return "no tree" if item in self._refused else None


def q(item, status="queued"):
    return dict(R.new_state(item, 1.0, ""), status=status)


def run(fx, queued=("S_A", "S_B"), r=RULES, extra=()):
    d = tempfile.mkdtemp(prefix="rlslot-")
    DIRS.append(d)
    s = R.Store(d)
    for i in queued:
        s.save(q(i))
    for st in extra:
        s.save(st)
    return R.enrol(s, fx, r, NOW), s


FIRST = {"S_A": 0, "S_B": 1, "S_C": 2, "REP": 3, "REP2": 4}
ORDER = ["S_A", "S_B", "S_C", "REP", "C1", "CBIG"]

# 1. the line is full of system items: caps hold, the slot takes the repair with >= 3 dependents
took, s = run(Fx(ORDER, FIRST, fan={"REP": (4, 9.0), "S_C": (1, 2.0), "CBIG": (9, 50.0)}))
ok(took == ["REP"], "a repair with 4 dependents enrols past spent caps, alone (S_C and content stay out)", took)
ok((s.load("REP") or {}).get("status") == "queued", "the slot's item is queued in the store", s.load("REP"))
journal = open(s.p("journal.jsonl")).read() if os.path.exists(s.p("journal.jsonl")) else ""
ok('"slot": "repair"' in journal, "the journal says the enrol came through the repair slot", journal[-300:])
ok(s.load("S_C") is None and s.load("C1") is None and s.load("CBIG") is None, "every other item still obeys the caps")

# 2. exactly at the threshold, and under it
took, _ = run(Fx(ORDER, FIRST, fan={"REP": (3, 3.0)}))
ok(took == ["REP"], "3 dependents is enough", took)
took, _ = run(Fx(ORDER, FIRST, fan={"REP": (2, 90.0)}))
ok(took == [], "2 dependents is not, however old they are", took)

# 3. the slot is held while a repair stands queued: nothing more past the caps
took, _ = run(Fx(ORDER + ["REP2"], FIRST, fan={"REP": (4, 9.0), "REP2": (6, 12.0)}), queued=("S_A", "S_B", "REP"))
ok(took == [], "a queued repair holds the slot: REP2 waits for the caps", took)

# 4. two candidates: one, the heaviest (age-weighted)
took, _ = run(Fx(ORDER + ["REP2"], FIRST, fan={"REP": (5, 9.0), "REP2": (4, 30.0)}))
ok(took == ["REP2"], "two candidates give one, the heavier weight wins over the bigger count", took)

# 5. a content item with many dependents is not a system item: never through the slot (the owner's pause stands)
took, _ = run(Fx(ORDER, FIRST, fan={"CBIG": (12, 80.0)}))
ok(took == [], "content with 12 dependents does not take the slot", took)

# 6. the switch off; a concept-refused candidate is passed over to the next
took, _ = run(Fx(ORDER, FIRST, fan={"REP": (4, 9.0)}), r=dict(RULES, repair_slot=False))
ok(took == [], "repair_slot false: no slot", took)
took, _ = run(Fx(ORDER + ["REP2"], FIRST, fan={"REP": (4, 9.0), "REP2": (5, 20.0)}, refused={"REP2"}))
ok(took == ["REP"], "a refused candidate is passed over, the next one takes the slot", took)

took, _ = run(Fx(ORDER, FIRST, fan={"REP2": (7, 40.0)}))
ok(took == [], "a repair the pool leaves out (blocked, claimed) does not take the slot", took)

# 7. room in the line: the walk enrols the repair itself and the slot adds nothing twice
took, _ = run(Fx(["REP", "S_C"], FIRST, fan={"REP": (4, 9.0)}), queued=(), r=dict(RULES, enrol_per_tick=1, max_queued=5))
ok(took == ["REP"], "with room the walk takes the repair; the slot does not enrol it again", took)

# 8. the real path: ops_health.fan_in over a ledger replay (transitive, deduped)


def it(i, on=None, also=(), created="2026-11-01T00:00:00Z"):
    return types.SimpleNamespace(id=i, open=True, blocked=bool(on), blocked_on=on, blocked_also=tuple(also),
                                 blocked_kind="item" if on else None, created_at=created, caused_by=None, kind="task")


world = types.SimpleNamespace(items={x.id: x for x in [it("REP"), it("D1", "REP"), it("D2", "D1"), it("D3", "D1", ("REP",)),
                                                         it("S_C"), it("E1", "S_C")]})
took, _ = run(Fx(ORDER, FIRST, world=world))
ok(took == ["REP"], "ops_health.fan_in over the ledger: REP has 3 transitive dependents (D3 counted once) and enrols", took)

for d in DIRS:
    shutil.rmtree(d, ignore_errors=True)
print("%d failure(s)" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
