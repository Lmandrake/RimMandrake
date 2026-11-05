#!/usr/bin/env python3
"""relentless_pool_why.reasons (RELENTLESS_POOL_DIAGNOSE_SYSTEM_NEVER_ENROLS): every clause that keeps a system item out
of the Relentless pool is named, an admissible item gets none, and the concept gate and first-touch hold are asked only
of an item the filters admit (pool_order's order). Planted items, the real rules file; then the real survey on this
tree's ledger must explain every system item. No units, no network."""
import os
import sys
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_pool_why as P  # noqa: E402

FAILS = []
RULES = R.rules(os.path.join(R.HERE, "relentless_rules.json"))
NOW = 1_800_000_000


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def item(i="SYS_THING_FIX_IT", **kw):
    base = dict(id=i, owner=RULES["pool_seats"][0], state="proposed", needs=RULES["pool_needs"][0], kind="task",
                target=None, lease=None, blocked=False, blocked_reason=None, blocked_on=None, blocked_kind=None,
                blocked_until=None, blocked_lift_at=None, blocked_also=(), title="")
    base.update(kw)
    return NS(**base)


W = NS(items={})
asked = []


def refused(i):
    asked.append(("refused", i))
    return "no tree"


def held(i):
    asked.append(("ft", i))
    return "names FlowWorks"


ok(P.reasons(item(), W, RULES, NOW) == [], "an admissible item has no clause")
ok(P.reasons(None, W, RULES, NOW) == ["not_filed"], "an id the ledger lacks is not_filed")
ok(P.reasons(item(state="built"), W, RULES, NOW) == ["state=built"], "built is out by state")
ok(P.reasons(item(owner="OWNER"), W, RULES, NOW) == ["owner=OWNER"], "an OWNER item is out by owner")
ok(P.reasons(item(needs="owner"), W, RULES, NOW) == ["needs=owner"], "needs=owner is out")
ok(P.reasons(item(kind="design"), W, RULES, NOW) == ["kind=design"], "an excluded kind is out")
ok(P.reasons(item(lease={"by": "x"}), W, RULES, NOW) == ["lease"], "a held lease is out")
ok(P.reasons(item(target="v2"), W, RULES, NOW) == ["target=v2"], "another target is out")
ok(P.reasons(item(needs="harvest"), W, RULES, NOW) == ["needs=harvest"], "a need outside pool_needs is out")
ok(P.reasons(item("SYS_PARKED_LIST_ID"), W, dict(RULES, pool_ids_exclude=["SYS_PARKED_LIST_ID"]), NOW) == ["pool_excluded"],
   "an id the rules exclude is pool_excluded")
FR = dict(RULES, pool_seats=["BENCH", "FOUNDRY"], staffing={"foreign_seat": "FOUNDRY", "foreign_kinds_exclude": ["mod"]})
ok(P.reasons(item(owner="FOUNDRY", kind="mod"), W, FR, NOW) == ["foreign"], "a foreign item of an excluded class is foreign")
ok(P.reasons(item(owner="FOUNDRY"), W, FR, NOW) == [], "a takeable foreign item with nothing unheard is admitted")
ok(P.reasons(item(owner="FOUNDRY"), W, FR, NOW, words={"SYS_THING_FIX_IT"}) == ["foreign_unpublished"],
   "a foreign item its seat has unpublished word on is out")
ok(P.reasons(item(owner="FOUNDRY"), W, FR, NOW, words=None) == ["foreign_unpublished"], "an unreadable foreign tree holds it")
park = item(blocked=True, blocked_reason="PARKED by owner card (old workflow). Reverse with rimflow unblock.")
ok(P.reasons(park, W, RULES, NOW) == ["parked_by_owner"], "an owner-card park is its own class")
ok(P.reasons(item(blocked=True, blocked_reason="needs bridge"), W, RULES, NOW) == ["blocked"], "any other block is blocked")
lifted = item(blocked=True, blocked_kind="time", blocked_lift_at="2020-01-01T00:00:00Z")
ok(P.reasons(lifted, W, RULES, NOW) == [], "a block whose date passed no longer holds", P.reasons(lifted, W, RULES, NOW))
both = P.reasons(item(state="validated", blocked=True, blocked_reason="PARKED by owner"), W, RULES, NOW)
ok(both == ["state=validated", "parked_by_owner"], "every clause is named, state first", both)
asked.clear()
ok(P.reasons(item(kind="mod"), W, RULES, NOW, refused, held) == ["concept_refused"], "a mod with no tree is concept_refused")
ok(P.reasons(item(), W, RULES, NOW, refused, held) == ["first_touch"], "a task naming an unpassed mod is first_touch")
ok(("refused", "SYS_THING_FIX_IT") in asked and asked.count(("refused", "SYS_THING_FIX_IT")) == 1,
   "the concept gate is asked of a mod only", asked)
asked.clear()
P.reasons(item(state="built"), W, RULES, NOW, refused, held)
ok(asked == [], "an item the filters already refuse is not asked the gates (pool_order never asks them)", asked)
ok(P.primary([]) == "in_pool" and P.primary(["state=doing", "lease"]) == "state=doing", "tallied by the first clause")

# the real tree: Operations' system items against the real pool_order, nothing unexplained
rows, why = P.survey(RULES)
bad = [x for x in rows if x[4].startswith("UNEXPLAINED")]
ok(len(rows) > 0, "the survey sees system items (%s)" % why, len(rows))
ok(not bad, "every system item on this ledger is explained", bad[:3])

print("\n%d failed" % len(FAILS) if FAILS else "\nall passed")
sys.exit(1 if FAILS else 0)
