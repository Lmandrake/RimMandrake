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
  - `fence_run`, from the sweep: a RUNNING worker whose item becomes blocked is stopped and fenced, never left to
    finish and land (RELENTLESS_FIX_PARKED_RUN_WORKS_ON_ANYWAY). The off switch (share 0) still lets runs finish.
  - the ledger is the only record of what it waits on: `rimflow show <ID>` prints it.
  - `diff` (RIMFLOW_FIX_BLOCKS_LIFT_ON_CLOSE, step 1 of 2): the store's `blocked` status is a COPY of the ledger block.
    `python3 relentless_block.py diff` appends one reading of where the two disagree; the store field may be deleted
    only once `ready_to_delete` sees 0 on 3 runs on 3 distinct UTC days. Until then it stays, read-only in spirit.
"""
import datetime
import glob
import json
import os
import re
import sys

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
    named = [x for x in pending.get("on") or [] if x != item]
    # a wait on an id the ledger has never seen can never be released by a close: refused here, at write
    # (RIMFLOW_FIX_BLOCKS_LIFT_ON_CLOSE; the 285-row incident_refused loop waited on one)
    unfiled = [x for x in named if item_state(x) is None]
    kind, ons = pending["kind"], [x for x in named if x not in unfiled]
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
    if unfiled:
        reason = "never filed, not waited on: %s. " % ", ".join(unfiled) + reason
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


def fence_run(store, fx, item, led, now, acts, iso):
    """A worker whose item is blocked on the ledger while it works is stopped at once (RELENTLESS_FIX_PARKED_RUN_WORKS_
    ON_ANYWAY: the owner's card parks an item to say "stop now", and a run left to finish may still land and be
    checked). Fence first: gen moves, so the worker's next beat/finish is refused. No strike and no failed approach:
    the block is not the item's fault. The run settles to `queued`, and leave_line (here or in lease()) parks it."""
    with store.lock():
        cur = store.load(item)
        if cur["status"] != "running" or cur.get("reserving"):
            return False
        run = cur.get("run")
        cur["gen"] += 1
        cur["status"] = "stopping"
        cur["stopping_since"] = now
        cur["returned_at"] = now        # back at the top once the block ends
        store.attempt(item, {"at": iso(now), "gen": cur["gen"] - 1, "end": "blocked_while_running",
                             "detail": (led.get("block") or "ledger block")[:600]})
        store.save(cur)
    if run:
        fx.stop(run, force=False)
    store.journal({"at": iso(now), "do": "fenced_blocked", "item": item, "why": led.get("block") or "ledger block"})
    acts.append({"do": "fenced_blocked", "item": item})
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
        if s == "running" and not st.get("reserving"):
            led = fx.item_state(item)
            if ledger_holds(led):
                fence_run(store, fx, item, led, now, acts, iso)
            continue
        if s not in ("queued", "blocked"):
            continue
        led = fx.item_state(item)
        holds = ledger_holds(led)
        if s == "queued" and holds:
            leave_line(store, item, led, now, acts, iso)
        elif s == "blocked" and st.get("wait") and (led or {}).get("state") not in LEDGER_DEAD:
            # a candidate kept through an unattributed failure (relentless_attrib): only evidence moves it, and it
            # resumes its own sha, never a new builder; a holding block or a pending attribution keeps it here
            if not holds:
                import relentless_attrib
                relentless_attrib.release(store, fx, st, now, acts)
        elif s == "blocked" and not holds:
            with store.lock():
                cur = store.load(item)
                if cur["status"] != "blocked" or cur.get("block_pending"):
                    continue
                cur.pop("wait", None)       # the item itself ended in the ledger: nothing left to resume
                cur["status"] = "queued"
                cur["returned_at"] = now        # back at the top of the returned items
                cur["not_before"] = 0
                store.save(cur)
            store.journal({"at": iso(now), "do": "unblocked", "item": item})
            acts.append({"do": "unblocked", "item": item})


# ---- store/ledger diff (step 1 of the two-step migration) --------------------------------------------------------------
DIFF_LOG = os.environ.get("RM_STORE_LEDGER_DIFF",
                          "/mnt/d/ClaudeWork/rimmandrake/relentless_agent/store_ledger_diff.jsonl")
DIFF_RUNS = 3


def diff(states, item_state):
    """-> {"compared", "in_transit", "disagree": [{item, store, ledger}], "count"}. Compares every queued/blocked store
    row with the ledger: the store says blocked exactly when the ledger block holds. A block still being written
    (`block_pending`) is in transit, not a disagreement. Pure."""
    out, transit, n = [], 0, 0
    for st in states:
        s = st.get("status")
        if s not in ("queued", "blocked"):
            continue
        if st.get("block_pending"):
            transit += 1
            continue
        n += 1
        led = item_state(st["item"])
        holds = ledger_holds(led)
        if (s == "blocked") != holds:
            out.append({"item": st["item"], "store": s + ("+wait" if st.get("wait") else ""),
                        "ledger": "never filed" if led is None else ("%s, block %s" % (
                            led.get("state"), "holds" if holds else "does not hold"))})
    return {"compared": n, "in_transit": transit, "disagree": out, "count": len(out)}


def ready_to_delete(path=None, runs=DIFF_RUNS):
    """-> (bool, why). True only when the last `runs` UTC days that have readings exist and every reading on them is 0
    (one clean reading a day is not enough if a later one that day was not)."""
    rows = []
    try:
        with open(path or DIFF_LOG, encoding="utf-8") as f:
            rows = [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError) as e:
        return False, "no readable diff log: %s" % e
    by_day = {}
    for r in rows:
        by_day.setdefault((r.get("at") or "")[:10], []).append(r)
    days = sorted(d for d in by_day if d)[-runs:]
    if len(days) < runs:
        return False, "%d day(s) of readings, %d needed" % (len(days), runs)
    bad = [(d, r["count"]) for d in days for r in by_day[d] if r.get("count") != 0]
    if bad:
        return False, "non-zero readings in the last %d days: %s" % (runs, bad[:5])
    return True, "0 on every reading of %s" % ", ".join(days)


def _live_item_state():
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(here))
    from rimflow import model, priority
    w = model.replay(model.read())
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    def item_state(iid):
        it = w.items.get(iid)
        if it is None:
            return None
        return {"state": it.state, "block_holds": priority.block_holds(w, it, now)}
    return item_state


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="store/ledger block diff (RIMFLOW_FIX_BLOCKS_LIFT_ON_CLOSE)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("diff", help="append one reading")
    d.add_argument("--root", default=os.environ.get("RELENTLESS_ROOT", os.path.expanduser("~/rm/relentless")))
    d.add_argument("--log", default=DIFF_LOG)
    r = sub.add_parser("ready", help="may the store field be deleted? (0 on %d runs, distinct days)" % DIFF_RUNS)
    r.add_argument("--log", default=DIFF_LOG)
    a = ap.parse_args(argv)
    if a.cmd == "ready":
        okay, why = ready_to_delete(a.log)
        print(("READY: " if okay else "NOT READY: ") + why)
        return 0 if okay else 1
    states = []
    for p in sorted(glob.glob(os.path.join(a.root, "store", "items", "*", "state.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                states.append(json.load(f))
        except (OSError, ValueError):
            continue
    if not states:
        print("UNMEASURED: no store rows under %s" % a.root)
        return 2
    rec = dict(diff(states, _live_item_state()), at=datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"), rows=len(states), root=a.root)
    with open(a.log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print("store/ledger diff: %d of %d compared (%d in transit, %d store rows) -> %s"
          % (rec["count"], rec["compared"], rec["in_transit"], rec["rows"], a.log))
    for x in rec["disagree"][:20]:
        print("  %s  store=%s  ledger=%s" % (x["item"], x["store"], x["ledger"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
