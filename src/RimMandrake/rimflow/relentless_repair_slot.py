"""relentless_repair_slot.py -- the one reserved repair slot in enrol (RELENTLESS_REWIRE_ENROL_BY_FAN_IN).

Owner-ordered pipeline redesign 2026-11-06 (redesign_final.md G8): a repair that many items wait on must not wait behind
`enrol_per_tick` / `max_queued` with the rest of the line. Instead of letting every such item past the caps, enrol keeps
ONE place beyond them: each wake, when no repair already holds it, the open system item (Operations' `fx.first`) with the
most transitive dependents (ops_health.fan_in: deduped, cycle-safe, weighted by the dependents' age) is enrolled, if it
has at least `repair_slot_min_dependents` (rules, default 3). Every other item still obeys the caps.

The slot is held while a queued item in the line is such a repair (enrolled by the slot or by the ordinary walk), so at
most one item ever stands past the caps on its account. Pure apart from reading fx (no store write here: enrol writes).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_DEPENDENTS = 3


def fan(fx, now):
    """-> {id: (dependents, weight)}: fx.repair_fan_in(now) when the Fx has one (a test's), else ops_health.fan_in over
    this tick's ledger replay (fx.ledger_items). {} when neither can say."""
    own = getattr(fx, "repair_fan_in", None)
    if own is not None:
        return own(now) or {}
    led = getattr(fx, "ledger_items", None)
    if led is None:
        return {}
    utils = os.path.join(os.path.dirname(HERE), "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import ops_health
    return ops_health.fan_in(led()[1], now)


def pick(fx, r, live, ours, now, order=None):
    """-> (item, dependents) for the reserved repair slot this wake, or None. `live`: the store's open states; `ours`: ids
    the store already holds (or enrolled this tick); `order`: this tick's pool (a candidate must stand in it: an item the
    pool leaves out, blocked or claimed, cannot start). None when the rules turn the slot off (`repair_slot` false), no
    system item is known, a queued item already holds the slot, or no unenrolled system item reaches the threshold. A
    candidate the concept gate refuses (fx.concept_refusal) is passed over: it would only park."""
    if r.get("repair_slot") is False:
        return None
    first = getattr(fx, "first", None) or {}
    if not first:
        return None
    need = int(r.get("repair_slot_min_dependents", MIN_DEPENDENTS))
    f = fan(fx, now)
    big = {i for i in first if f.get(i, (0, 0.0))[0] >= need}
    if not big or any(s["status"] == "queued" and s["item"] in big for s in live):
        return None
    refused = getattr(fx, "concept_refusal", None)
    pool = None if order is None else set(order)
    cands = [i for i in big if i not in ours and (pool is None or i in pool) and not (refused and refused(i))]
    if not cands:
        return None
    best = min(cands, key=lambda i: (-f[i][1], -f[i][0], first[i], i))
    return best, f[best][0]
