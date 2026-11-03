#!/usr/bin/env python3
"""The escalation route (EXPEDITE_LANE_BUILD_JUMPS_THE_GAME_QUEUE). Owner's card, 2026-11-03: "No limits on how many can
be requested, leaves the live game alone unless it needs it (last slot to take). Should have a switch: is it
Interrupt-level urgency (very rare, only for imminent threats to machine safety or panicked user requests), or 'next
available slot' expedited. Otherwise agree." Kept from the proposal: Operations or the Conductor set it, never Relentless
on its own work; 4 h expiry unless renewed; every use in the daily digest.

  interrupt   above everything in the line; when every place is taken it stops one running worker to make room
  expedited   above everything in the line; takes the next place that comes free, stops nothing

The request is one line in store/expedite.jsonl, written by `relentless.py expedite`; each tick folds the log onto the
item's state (`st["expedite"]`), which is what the order reads, so an expiry needs nobody. No cap on count. Neither level
stops the live game, or a worker iterating on it: an item that needs the game gets a worker place first, like any other,
and then the next turn in the game line. The digest hears through the ledger: each use is a note with a `delegated:` why
(delegated_digest.py lists those), written by the tick, so the runner's own shard publishes it."""
import json

LOG = "expedite.jsonl"
TOLD = "expedite_told.json"
TTL_S = 4 * 3600
LEVELS = ("interrupt", "expedited")     # best first
SETTERS = ("Operations", "Conductor")
# a Relentless worker, checker or consult carries these: it may not raise its own work
WORKER_ENV = ("RELENTLESS_GEN", "RELENTLESS_HELP_NONCE", "RELENTLESS_ROOT", "RELENTLESS_SUPERVISOR")


def worker_refusal(env):
    """Why this process may not set a level (it is Relentless itself), or None."""
    hit = [k for k in WORKER_ENV if env.get(k)]
    return "a Relentless run may not expedite work (%s set): Operations or the Conductor sets it" % hit[0] if hit else None


def read_log(store):
    try:
        with open(store.p(LOG), encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return []
    rows = []
    for ln in lines:
        try:
            row = json.loads(ln)
        except ValueError:      # one torn line loses that line, never the record around it
            continue
        if isinstance(row, dict) and row.get("item"):
            rows.append(row)
    return rows


def fold(rows, now):
    """-> {item: {level, by, why, at, until}}: the requests standing at `now`. Pure."""
    live = {}
    for row in rows:
        item, verb = row["item"], row.get("verb")
        if verb == "set":
            live[item] = {k: row.get(k) for k in ("level", "by", "why", "at")}
            live[item]["until"] = row.get("at", 0) + TTL_S
        elif verb == "renew" and item in live:
            live[item].update(until=row.get("at", 0) + TTL_S, level=row.get("level") or live[item]["level"])
        elif verb == "clear":
            live.pop(item, None)
    return {i: e for i, e in live.items() if e["until"] > now}


def rank(e):
    """The sort key inside the expedite tier: interrupt before expedited, then the older request."""
    return (LEVELS.index(e["level"]) if e.get("level") in LEVELS else len(LEVELS), e.get("at") or 0)


def request(store, verb, item, now, env, level=None, by=None, why=None):
    """Append one use. -> the standing request (None after a clear). Raises ValueError with the refusal."""
    refusal = worker_refusal(env)
    if refusal:
        raise ValueError(refusal)
    if by not in SETTERS:
        raise ValueError("--by must be one of %s, got %r" % ("/".join(SETTERS), by))
    if not (why or "").strip():
        raise ValueError("--why is required: it goes in the daily digest")
    standing = fold(read_log(store), now)
    if verb == "set" and level not in LEVELS:
        raise ValueError("--level must be one of %s, got %r" % ("/".join(LEVELS), level))
    if verb == "renew":
        if item not in standing:
            raise ValueError("%s has no standing request to renew (expired or cleared): set it again" % item)
        if level is not None and level not in LEVELS:
            raise ValueError("--level must be one of %s, got %r" % ("/".join(LEVELS), level))
    if verb == "clear" and item not in standing:
        raise ValueError("%s has no standing request to clear" % item)
    if verb not in ("set", "renew", "clear"):
        raise ValueError("unknown verb %r" % verb)
    store._append(store.p(LOG), json.dumps({"verb": verb, "item": item, "level": level, "by": by, "why": why, "at": now},
                                           sort_keys=True))
    store.journal({"do": "expedite", "verb": verb, "item": item, "level": level, "by": by, "why": why})
    return fold(read_log(store), now).get(item)


def _told(store):
    try:
        with open(store.p(TOLD), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"rows": 0}


def _note(fx, item, text):
    say = getattr(fx, "expedite_note", None)
    return say(item, text) if say else None


def sync(store, fx, now, acts):
    """Each tick: the log onto the states, and every use not yet in the ledger into it. A note that fails is tried again
    next tick (the count moves only past what landed); the order never waits for it."""
    rows = read_log(store)
    live = fold(rows, now)
    for item in store.items():
        with store.lock():
            st = store.load(item)
            if not st:
                continue
            want = live.get(item)
            had = st.get("expedite")
            if want == had:
                continue
            if want:
                st["expedite"] = want
            else:
                st.pop("expedite", None)
            store.save(st)
        if had and not want and not any(r["item"] == item and r.get("verb") == "clear" and r.get("at", 0) >= had.get("at", 0)
                                        for r in rows):
            acts.append({"do": "expedite_expired", "item": item, "level": had.get("level")})
            _note(fx, item, "expedite: %s by %s lapsed after 4 h with no renewal" % (had.get("level"), had.get("by")))
    told = _told(store)
    n = told.get("rows", 0)
    for row in rows[n:]:
        failed = _note(fx, row["item"], "expedite %s: %s by %s: %s" % (row.get("verb"), row.get("level") or "-", row.get("by"),
                                                                       (row.get("why") or "")[:300]))
        if failed:
            acts.append({"do": "expedite_note_failed", "item": row["item"], "why": str(failed)[:200]})
            break
        n += 1
    if n != told.get("rows", 0):
        store._write(store.p(TOLD), json.dumps({"rows": n}))
    return live


def victims(states, first):
    """Who an interrupt may stop, first choice first: content before system, later in Operations' order first, the newest
    enrolled first. Never an expedited item, and never a worker on the live game (the game is left alone). Pure."""
    can = [s for s in states if s["status"] == "running" and not s.get("expedite") and not s.get("live_iter")
           and not s.get("reserving")]
    return sorted(can, key=lambda s: (s["item"] in first, -first.get(s["item"], 0), -s.get("enrolled_at", 0), s["item"]))


def make_room(store, fx, r, now, acts, active, why_not, fail):
    """Stop one running worker per interrupt that has no place coming. `active`: the places taken now, as lease counts them;
    `why_not`: admission's answer at that count. Only a full house is cured by stopping someone: an open breaker, a pause or
    low memory stops nobody. A stopped item keeps its place in the world: it returns to the top of its own tier."""
    states = store.states()
    waiting = sorted((s for s in states if s["status"] == "queued" and (s.get("expedite") or {}).get("level") == "interrupt"),
                     key=lambda s: rank(s["expedite"]))
    if not waiting or not why_not:
        return []
    if why_not != "max_workers":
        acts.append({"do": "wait", "why": "interrupt %s waits: %s" % (waiting[0]["item"], why_not)})
        return []
    coming = sum(1 for s in states if s["status"] == "stopping")    # a place already on its way back
    first = getattr(fx, "first", None) or {}
    stopped = []
    for want, victim in zip(waiting[coming:], victims(states, first)):
        with store.lock():
            cur = store.load(victim["item"])
            if cur["status"] != "running":
                continue
            fail(store, cur, "interrupted", "stopped for INTERRUPT %s (%s): %s" % (
                want["item"], want["expedite"].get("by"), (want["expedite"].get("why") or "")[:200]), r, now, time_not_work=True)
        store.journal({"do": "expedite_interrupted", "item": victim["item"], "for": want["item"]})
        acts.append({"do": "expedite_interrupted", "item": victim["item"], "for": want["item"]})
        _note(fx, want["item"], "expedite interrupt stopped the running worker of %s to make room" % victim["item"])
        stopped.append(victim["item"])
    if waiting[coming:] and not stopped:
        acts.append({"do": "wait", "why": "interrupt %s waits: nothing it may stop" % waiting[coming]["item"]})
    return stopped


def listing(store, now):
    """One line per standing request, best first; the use count all told."""
    rows = read_log(store)
    live = fold(rows, now)
    out = ["%s %s by %s, %d min left: %s" % (i, e["level"], e["by"], (e["until"] - now) // 60, e["why"])
           for i, e in sorted(live.items(), key=lambda kv: rank(kv[1]))]
    return out or ["no standing request (%d uses on the log)" % len(rows)]
