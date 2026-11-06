#!/usr/bin/env python3
"""relentless_cause.py — a backoff ends when its cause closes, not when a clock runs out (RELENTLESS_REWIRE_BACKOFFS_ON_CAUSE_CLOSE).

Owner, 2026-11-05: "Please stop building arbitrary pauses into the system". RELENTLESS_WIRE_WAKE_ON_STATE_CHANGE turned
the event waits into wakes; four backoffs stayed clocks because nothing linked a backoff to its cause
(relentless_wake.json clock_keys, kind backoff_owed). This is that link. Each backoff records WHAT it waits on beside its
clock; `sweep`, run by the tick next to relentless_block.sweep (at the prelude and in every wake serve, so a
relentless_wake.poke reaches it in seconds), ends the backoff the moment that cause reads closed. The clock stays only
as the upper bound for a cause nobody can read.

The causes (`of`), each from text measured in the journal 2026-10-31..11-06:
  - clone_exists  "scratch_clone: FAILED: <path> already exists": closed when <path> is gone.
  - publickey     "Permission denied (publickey)": closed by a `publish` poke after the failure (that push used the
                  same ssh key, so the key works again).
  - items         ids a snag or a blind check names that were OPEN on the ledger when first read: closed when every one
                  of them is done, dropped or superseded. Ids already closed when first read are history, not a cause.
  - poke          any state change (a relentless_wake poke) after the backoff began: the ledger start refusal, whose
                  cause is ledger state that only a landed commit changes.

The backoffs:
  breaker_cool_s / breaker_cool_max_s   store breaker.json `cause` (launch_failed): the breaker closes, opens kept.
  breaker_cool_s (start_again_at)       item `start_again_cause` (a ledger start refusal).
  snag_again_wait_h (not_before)        item `not_before_cause` (a repeat snag; a worker's own --wait-hours is time, no cause).
  unmeasured_recheck_s (recheck_at)     item `recheck_cause` (the legacy reach_repair-false route).
"""
import json
import os
import re

import relentless_wake

ID_RX = re.compile(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b")
CLONE_RX = re.compile(r"(/\S+?)'? already exists")
LEDGER_DEAD = ("done", "dropped", "superseded")
# the item fields each backoff keeps: (clock field, cause field, what the clock is reset to when the cause closes)
ITEM_BACKOFFS = (("start_again_at", "start_again_cause", 0), ("not_before", "not_before_cause", 0),
                 ("recheck_at", "recheck_cause", None))


def of(why, item=None, poke=False, items=True):
    """-> the cause a failure text names, or None when it names none a sweep can read. `poke`: no specific cause
    found, so any later state change ends the wait (only for a wait whose cause is known to be ledger state).
    `items` False: ids in the text are not a cause (a launcher's error names runs, not predecessors)."""
    text = str(why or "")
    m = CLONE_RX.search(text)
    if m and ("scratch_clone" in text or "/clones/" in m.group(1)):
        return {"kind": "clone_exists", "path": m.group(1).rstrip(".:,;'\"")}
    if "(publickey)" in text:
        return {"kind": "publickey"}
    ids = [x for x in dict.fromkeys(ID_RX.findall(text)) if x != item and "_" in x and len(x) >= 8]
    if ids and items:
        return {"kind": "items", "on": ids[:12], "read": False}
    return {"kind": "poke"} if poke else None


def closed(cause, since, sdir, item_state=None, exists=os.path.exists):
    """-> why the cause reads closed now, or None while it holds (or cannot be read). `since`: when the backoff began.
    An `items` cause is pruned in place on its first read (the ids open then are the cause)."""
    k = (cause or {}).get("kind")
    if k == "clone_exists":
        return None if exists(cause["path"]) else "the clone %s is gone" % cause["path"]
    if k in ("publickey", "poke"):
        new = [p for p in relentless_wake.pokes(sdir) if p["at"] > since
               and (k == "poke" or p.get("source") == "publish")]
        if not new:
            return None
        p = max(new, key=lambda x: x["at"])
        return ("a publish after the failure pushed over ssh (%s)" if k == "publickey"
                else "a state change after the wait began (%s)") % p.get("source", "?")
    if k == "items" and item_state:
        if not cause.get("read"):
            cause["on"] = [x for x in cause.get("on") or []
                           if (item_state(x) or {}).get("state") not in (None,) + LEDGER_DEAD]
            cause["read"] = True
        on = cause.get("on") or []
        if not on:
            return None
        rows = [(x, (item_state(x) or {}).get("state")) for x in on]
        if all(s in LEDGER_DEAD for _, s in rows):
            return "named item%s closed: %s" % ("s" if len(rows) > 1 else "", ", ".join("%s %s" % r for r in rows))
    return None


def sweep(store, fx, now, acts, iso):
    """Under the tick lock. Every backoff whose recorded cause reads closed ends now. -> number ended."""
    sdir = store.dir
    item_state = getattr(fx, "item_state", None)
    n = 0
    br = _breaker(store)
    if br.get("until", 0) > now and br.get("cause"):
        why = closed(br["cause"], br.get("at", 0), sdir, item_state)
        if why:
            store._write(store.p("breaker.json"), json.dumps({"opens": br["opens"]} if br.get("opens") else {}))
            store.journal({"at": iso(now), "do": "backoff_cause_closed", "key": "breaker_cool_s",
                           "cause": br["cause"].get("kind"), "why": why[:300]})
            acts.append({"do": "backoff_cause_closed", "key": "breaker_cool_s", "why": why[:300]})
            n += 1
    for st in store.states():
        if not any(st.get(c) for _, c, _ in ITEM_BACKOFFS):
            continue
        item = st["item"]
        with store.lock():
            cur = store.load(item)
            if not cur:
                continue
            ended, dirty = [], False
            for clock, cfield, reset in ITEM_BACKOFFS:
                cause = cur.get(cfield)
                if not cause:
                    continue
                if not (cur.get(clock) or 0) > now:     # the clock ran out first: the cause record has nothing to end
                    cur.pop(cfield, None)
                    dirty = True
                    continue
                before = dict(cause)
                why = closed(cause, float(cause.get("since") or 0), sdir, item_state)
                if cause != before:
                    dirty = True
                if why:
                    if reset is None:
                        cur.pop(clock, None)
                    else:
                        cur[clock] = reset
                    cur.pop(cfield, None)
                    ended.append((clock, cause.get("kind"), why))
                    dirty = True
            if dirty:
                store.save(cur)
        for clock, kind, why in ended:
            store.journal({"at": iso(now), "do": "backoff_cause_closed", "item": item, "key": clock, "cause": kind,
                           "why": why[:300]})
            acts.append({"do": "backoff_cause_closed", "item": item, "key": clock, "why": why[:300]})
            n += 1
    return n


def record(st, cfield, cause, now):
    """Set (or clear, when `cause` is None) an item backoff's cause beside its clock."""
    if cause:
        st[cfield] = dict(cause, since=now)
    else:
        st.pop(cfield, None)


def _breaker(store):
    try:
        with open(store.p("breaker.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}
