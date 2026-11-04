#!/usr/bin/env python3
"""relentless_block.py — a blocked item leaves Relentless's line, as data (PLAN_BUILD_BLOCKED_BY_IS_TEXT_ONLY).

Owner, 2026-11-02: "we need to have queued items correctly state what they are blocked on and to not ever be offered to
Relentless if blocked, that's just obvious and a dispatch-level question."

Measured before this (relentless_vs_foundry_2026-11-02.md): 8 items had 3 or 4 generations end on the same non-work
cause for 16.0M tokens; STONE_BUILDSTATS_TUNE_GRANITE_GETS_RIVALS was restaffed three times to read that its
predecessor was still open, because a worker's `snag --class blocked_by_predecessor` only went back in line.

The moves, all here so relentless.py carries hooks only:
  - `from_snag`: a worker's snag of a blocker class (or naming --on / --blocker) becomes a pending structured block;
    the worker is fenced and the item does not go back in line.
  - `sweep`, every tick: a pending block is written to the ledger (`rimflow block --kind ... --on ...`) and the item
    waits as `blocked`, out of the line and the count. A queued item whose LEDGER block holds (someone else blocked
    it) moves there too. When the ledger block stops holding (priority.block_holds: the predecessor reached its level,
    the date passed, or someone unblocked) it is back in line at the top, unprompted.
  - `leave_line`, from lease() too: the sweep runs before the tick's steps, so a run ending in a step comes back to
    `queued` after it looked, its item `doing` and out of eligible()'s reach (RELENTLESS_FIX_PARKED_ITEM_STILL_STAFFED:
    an item the owner's card parked was leased again five minutes later). lease() reads the block before any launch.
  - the ledger is the only record of what it waits on: `rimflow show <ID>` prints it.
"""
import re

ID_RX = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b")
KINDS = ("item", "owner", "judge", "live", "time", "external", "other")
LEDGER_DEAD = ("done", "dropped", "superseded")
LEDGER_OPEN = ("proposed", "ready", "doing", "built", "validated")


def blocker_kind(klass, r, on=None, kind=None):
    """-> the block kind a snag asks for, or None when it is an ordinary failure. Explicit beats the class table."""
    if kind:
        if kind not in KINDS:
            raise ValueError("--blocker must be one of %s (got %r)" % ("|".join(KINDS), kind))
        if kind == "time":
            raise ValueError("a wait on time is `snag --wait-hours N`, not a block")
        return kind
    if on:
        return "item"
    table = r.get("blocker_classes") or {}
    k = (klass or "").lower()
    if k in table:
        return table[k]
    if k.startswith("blocked_"):
        return "item"       # resolved at the sweep: no filed predecessor named makes it `external`
    return None


def from_snag(klass, detail, r, on=None, kind=None):
    """-> the pending block a snag writes, or None."""
    k = blocker_kind(klass, r, on, kind)
    if k is None:
        return None
    return {"kind": k, "on": list(on or []), "class": klass, "detail": (detail or "")[:600]}


def resolve(pending, item, item_state):
    """-> (kind, [on ids], reason) for the ledger. An `item` block with no --on takes the open filed ids its detail
    names; none found and it is `external`, said so in the reason (a person names the predecessor or unblocks)."""
    kind, ons = pending["kind"], [x for x in pending.get("on") or [] if x != item]
    if kind == "item" and not ons:
        for x in ID_RX.findall(pending.get("detail") or ""):
            led = item_state(x) if x != item else None
            if led and led.get("state") in LEDGER_OPEN and x not in ons:
                ons.append(x)
        if not ons:
            kind = "external"
    reason = "relentless snag %s: %s" % (pending.get("class") or "-", pending.get("detail") or "")
    if pending["kind"] == "item" and kind == "external":
        reason = "no open predecessor id found in the snag; name it with `rimflow block --on` or unblock. " + reason
    return kind, ons, reason[:600]


def ledger_holds(led):
    """`led` is fx.item_state's row: True while its ledger block holds on an item still open."""
    return bool(led and led.get("state") not in LEDGER_DEAD and led.get("block_holds"))


def leave_line(store, item, led, now, acts, iso):
    """A queued item blocked on the ledger waits as `blocked`. -> True when it moved."""
    with store.lock():
        cur = store.load(item)
        if cur["status"] != "queued":
            return False
        cur["status"] = "blocked"
        cur["blocked_at"] = now
        store.save(cur)
    store.journal({"at": iso(now), "do": "blocked", "item": item, "why": led.get("block") or "ledger block"})
    acts.append({"do": "blocked", "item": item, "why": "ledger"})
    return True


def sweep(store, fx, now, acts, iso):
    """Under the tick lock. Pending blocks go to the ledger; queued items blocked there leave the line; blocked items
    whose ledger block ended come back at the top."""
    for st in store.states():
        item, s = st["item"], st["status"]
        if s == "blocked" and st.get("block_pending"):
            kind, ons, reason = resolve(st["block_pending"], item, fx.item_state)
            why = fx.ledger_block(item, kind, ons, reason)
            if why:
                acts.append({"do": "block_write_failed", "item": item, "why": why})
                continue
            with store.lock():
                cur = store.load(item)
                cur.pop("block_pending", None)
                cur["blocked_at"] = now
                store.save(cur)
            store.journal({"at": iso(now), "do": "blocked", "item": item, "kind": kind, "on": ons})
            acts.append({"do": "blocked", "item": item, "kind": kind, "on": ons})
            continue
        if s not in ("queued", "blocked"):
            continue
        led = fx.item_state(item)
        holds = ledger_holds(led)
        if s == "queued" and holds:
            leave_line(store, item, led, now, acts, iso)
        elif s == "blocked" and not holds:
            with store.lock():
                cur = store.load(item)
                if cur["status"] != "blocked" or cur.get("block_pending"):
                    continue
                cur["status"] = "queued"
                cur["returned_at"] = now        # back at the top of the returned items
                cur["not_before"] = 0
                store.save(cur)
            store.journal({"at": iso(now), "do": "unblocked", "item": item})
            acts.append({"do": "unblocked", "item": item})
