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
    only once `ready_to_delete` sees a measured 0 (rows compared, none unreadable) on 3 distinct UTC days. Until then
    it stays, read-only in spirit. rm-store-ledger-diff.timer takes the nightly reading; `fired` counts the nights it did.
  - `stale`: an open item's item-block that has ended on the books or can never end (a blocker done or dropped, one
    never filed); `stale --ids` is the reading RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY closed its 12 stale blocks on.
"""
import datetime
import glob
import json
import os
import re
import sys

ID_RX = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b")
KINDS = ("item", "owner", "judge", "live", "time", "external")     # `rimflow block` refuses `other`: it names no lift event
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
    # ... and a wait that names one never cannot narrow to the filed rest: the close of `A` would resume an item still
    # waiting on unfiled `B` (RELENTLESS_BLOCK_HARDEN_MIGRATION_GATE). It goes `external`: a person files B or unblocks.
    unfiled = [x for x in named if item_state(x) is None]
    kind, ons = pending["kind"], [x for x in named if x not in unfiled]
    if unfiled and kind == "item":
        kind, ons = "external", []
    elif kind != "item":
        ons = []        # `rimflow block --on` is --kind item only: a judge/live/owner wait keeps its ids in the reason
    elif not ons:
        for x in ID_RX.findall(pending.get("detail") or ""):
            led = item_state(x) if x != item else None
            if led and led.get("state") in LEDGER_OPEN and x not in ons:
                ons.append(x)
        if not ons:
            kind = "external"
    reason = "relentless snag %s: %s" % (pending.get("class") or "-", pending.get("detail") or "")
    if pending["kind"] == "item" and kind == "external" and not unfiled:
        reason = "no open predecessor id found in the snag; name it with `rimflow block --on` or unblock. " + reason
    if pending["kind"] != "item" and named:
        reason = "also named: %s. " % ", ".join(named) + reason
    if unfiled:
        filed = [x for x in named if x not in unfiled]
        reason = "never filed: %s; the wait cannot lift by a close, so a person files it or unblocks%s. " % (
            ", ".join(unfiled), (" (also named, filed: %s)" % ", ".join(filed)) if filed else "") + reason
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
DIFF_TIMER = "rm-store-ledger-diff.timer"


def diff(states, item_state, unreadable=0):
    """-> {"compared", "in_transit", "unreadable", "disagree": [{item, store, ledger}], "count"}. Compares every
    queued/blocked store row with the ledger: the store says blocked exactly when the ledger block holds. A block still
    being written (`block_pending`) is in transit, not a disagreement; `unreadable` store rows are carried so the gate
    can refuse a reading that could not see them. Pure."""
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
    return {"compared": n, "in_transit": transit, "unreadable": unreadable, "disagree": out, "count": len(out)}


def reading_clean(r):
    """-> None when one diff reading is a measured 0, else why not. A 0 is clean only when it saw something: no
    unreadable store row (a skipped row may be the disagreeing one), and at least one row compared (every row in
    transit measures no agreement at all). A reading without the `unreadable` field predates that count: unmeasured."""
    if r.get("count") != 0:
        return "count %s" % r.get("count")
    if r.get("unreadable") is None:
        return "no unreadable-row count (older reading)"
    if r.get("unreadable"):
        return "%s unreadable store row(s)" % r["unreadable"]
    if not r.get("compared"):
        return "0 compared (%s in transit)" % r.get("in_transit", 0)
    return None


def ready_to_delete(path=None, runs=DIFF_RUNS):
    """-> (bool, why). True only when the last `runs` UTC days that have readings exist and every reading on them is a
    measured 0 (`reading_clean`; one clean reading a day is not enough if a later one that day was not). A line that
    does not parse is not skipped: it makes the log unreadable."""
    rows = []
    try:
        with open(path or DIFF_LOG, encoding="utf-8") as f:
            rows = [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError) as e:
        return False, "no readable diff log: %s" % e
    odd = [r for r in rows if not isinstance(r, dict) or len(str(r.get("at") or "")) < 10]
    if odd:
        return False, "%d diff log line(s) are not a dated reading: %s" % (len(odd), str(odd[0])[:80])
    by_day = {}
    for r in rows:
        by_day.setdefault((r.get("at") or "")[:10], []).append(r)
    days = sorted(d for d in by_day if d)[-runs:]
    if len(days) < runs:
        return False, "%d day(s) of readings, %d needed" % (len(days), runs)
    bad = [(r.get("at"), why) for d in days for r in by_day[d] for why in [reading_clean(r)] if why]
    if bad:
        return False, "readings in the last %d days that are not a measured 0: %s" % (runs, bad[:5])
    return True, "a measured 0 on every reading of %s" % ", ".join(days)


def timer_fired(path=None, by=DIFF_TIMER):
    """-> (sorted UTC days the timer recorded a reading, None), or (None, why) when the log cannot be read. A reading
    without `by`, taken by hand, is not a firing; a line that does not parse makes the whole log unreadable."""
    try:
        with open(path or DIFF_LOG, encoding="utf-8") as f:
            rows = [json.loads(ln) for ln in f if ln.strip()]
    except (OSError, ValueError) as e:
        return None, "no readable diff log: %s" % e
    return sorted({str(r.get("at") or "")[:10] for r in rows if isinstance(r, dict) and r.get("by") == by}), None


def stale_block(world, it, now):
    """-> why `it`'s item-block is stale, else None (no block, the item is closed, another kind, or a real wait). Stale:
    the books keep a block that has ended, or one that no close can end: a dropped blocker nobody answered, one never
    filed. The other kinds lift by `unblock` alone, so nothing here can call them ended."""
    from rimflow import priority
    if not it.blocked or it.state not in LEDGER_OPEN or priority.block_kind(it) != "item":
        return None
    if not priority.block_holds(world, it, now):
        return "ended, still on the books: %s" % (priority.release_reason(world, it, now) or "no longer holds")
    for on in priority.block_ons(it):
        b, _why = priority.follow(world, on)
        if b is None:
            return "waits on %s, which can never deliver (%s)" % (on, _why or "never filed")
        if b.state in priority.DEAD and not priority.ended_by_drop(b):
            return "waits on %s, %s with no one answering for the wait" % (on, b.state)
    return None


def _world():
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(here))
    from rimflow import model
    return model.replay(model.read())


def stale_report(world, ids, now):
    """-> (exit code, lines). `ids` empty: every open item. A named id the ledger has never seen is UNMEASURED (2): this
    world cannot speak for it. Pure over `world`."""
    rows, rc = [], 0
    for iid in ids or sorted(i for i, it in world.items.items() if it.state in LEDGER_OPEN):
        it = world.items.get(iid)
        if it is None:
            rows.append("UNMEASURED: %s has never been filed in this ledger" % iid)
            rc = 2
            continue
        why = stale_block(world, it, now)
        if why:
            rc = rc or 1
            rows.append("STALE %s (%s): %s" % (iid, it.state, why))
        elif ids:
            rows.append("ok    %s (%s): %s" % (iid, it.state, "block holds, a real wait" if it.blocked else "no block"))
    return rc, rows


def _live_item_state():
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(here))
    from rimflow import priority
    w = _world()
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
    d.add_argument("--by", help="the unit taking this reading (rm-store-ledger-diff.service); by hand: leave it off")
    r = sub.add_parser("ready", help="may the store field be deleted? (0 on %d runs, distinct days)" % DIFF_RUNS)
    r.add_argument("--log", default=DIFF_LOG)
    f = sub.add_parser("fired", help="did %s record a reading on --need distinct UTC days? 0 yes, 1 no, 2 UNMEASURED" % DIFF_TIMER)
    f.add_argument("--log", default=DIFF_LOG)
    f.add_argument("--need", type=int, default=DIFF_RUNS)
    t = sub.add_parser("stale", help="stale item-blocks in the ledger: 0 none, 1 some, 2 a named id is unknown")
    t.add_argument("--ids", default="", help="comma-separated; default every open item")
    a = ap.parse_args(argv)
    if a.cmd == "ready":
        okay, why = ready_to_delete(a.log)
        print(("READY: " if okay else "NOT READY: ") + why)
        return 0 if okay else 1
    if a.cmd == "fired":
        days, why = timer_fired(a.log)
        if why:
            print("UNMEASURED: " + why)
            return 2
        print("%s recorded a reading on %d day(s), %d needed: %s" % (DIFF_TIMER, len(days), a.need, ", ".join(days) or "none"))
        return 0 if len(days) >= a.need else 1
    if a.cmd == "stale":
        rc, rows = stale_report(_world(), [x for x in a.ids.split(",") if x],
                                int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
        print("\n".join(rows) if rows else "no stale item-block on any open item")
        return rc
    states, bad = [], []
    for p in sorted(glob.glob(os.path.join(a.root, "store", "items", "*", "state.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                row = json.load(f)
            if not isinstance(row, dict) or "item" not in row:
                raise ValueError("not a store row")
            states.append(row)
        except (OSError, ValueError) as e:
            bad.append((p, str(e)[:120]))
    if not states and not bad:
        print("UNMEASURED: no store rows under %s" % a.root)
        return 2
    rec = dict(diff(states, _live_item_state(), unreadable=len(bad)),
               at=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               rows=len(states) + len(bad), root=a.root, unreadable_rows=[p for p, _ in bad[:20]])
    if a.by:
        rec["by"] = a.by
    with open(a.log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print("store/ledger diff: %d of %d compared (%d in transit, %d unreadable, %d store rows) -> %s"
          % (rec["count"], rec["compared"], rec["in_transit"], rec["unreadable"], rec["rows"], a.log))
    for p, why in bad[:20]:
        print("  UNREADABLE %s: %s" % (p, why))
    for x in rec["disagree"][:20]:
        print("  %s  store=%s  ledger=%s" % (x["item"], x["store"], x["ledger"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
