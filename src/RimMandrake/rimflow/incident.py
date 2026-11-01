#!/usr/bin/env python3
"""incident.py -- one incident, from told to recovered (OP3, OP4, RO4; design/RimMandrake/operating_requirements_2026-11-01.md).

told.jsonl beside ops_watch's alarms.json is append-only deltas: a row with `ev` updates incident `id`; a row with no
`ev` is a SIGNAL, an alarm that has no sane reading (relentless.told, or a Dispatcher alarm), taken once by line number.
Rows are deltas so an ack written from any clone between a tick's read and its write is not lost.

The Dispatcher tick runs step() in decide (pure) and execute() in its execute pass (the only writer of rings):
  * a distressed or emergency reading, an OPEN ops alarm, or a signal joins the open incident of its cause, else
    reopens a same-cause incident closed inside relapse_h, else opens one. One cause, one ring, one run.
  * an ACK is `rimflow ack <id> --plan` or the reader's action on the named item. It gives ownership and sets recover_by.
    A ring, a read or a consumed doorbell writes no ack row and cannot make one.
  * past the rung's ack time, or past recover_by acked or not, the incident moves up the chain: the route's reader,
    Conductor, a fresh Operations run, him. The last agent writes his line (`rimflow incident-line`); with none, the
    fixed template goes out marked unread, his accepted exception. A rung does not move while the readings are sane.
  * it closes only on reading: every metric seen sane for sustain_min (event_quiet_min for a signal).
incidents.json is the snapshot stamped every tick: pulse reads its `owner` rows, the deadman reads its age.
"""
import fnmatch
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTES = os.path.join(HERE, "alarm_routes.json")
REAL_OPS = "/mnt/d/ClaudeWork/rimmandrake/ops_watch"
REAL_STATE = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
BAD = ("distressed", "emergency")
ACTIONS = ("claim", "start", "close", "implemented", "drop")     # a note is not one: the 2026-11-01 diagnosis was a note
NOT_READERS = ("DISPATCHER", "RUNNER", "RELENTLESS")
OWNER_RUNG = 3


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def load_table(path=None):
    with open(path or os.environ.get("RIMFLOW_ROUTES") or ROUTES, encoding="utf-8") as f:
        return json.load(f)


def route_of(table, kind):
    """The first route matching `kind`, or None: selftest_incident fails on a kind that reads None."""
    return next((r for r in table["routes"] if fnmatch.fnmatchcase(kind, r["match"])), None)


def ops_dir():
    return os.environ.get("RM_OPS_WATCH_DIR") or REAL_OPS


def told_path(d=None):
    return os.path.join(d or ops_dir(), "told.jsonl")


def snapshot_path(d=None):
    return os.path.join(d or ops_dir(), "incidents.json")


def guard(path):
    """A test process (it points RM_DISPATCHER_STATE at a temp dir) never writes the real ledger: the 1970 alarms."""
    if (os.path.abspath(path).startswith(REAL_OPS + os.sep)
            and os.environ.get("RM_DISPATCHER_STATE", REAL_STATE) != REAL_STATE):
        raise RuntimeError("refusing to write the real told ledger from a test process: %s" % path)


def append(rows, path=None):
    path = path or told_path()
    guard(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        f.flush()
        os.fsync(f.fileno())


def read_rows(path=None):
    """-> the rows, or None when the file is there and a line does not parse: a torn ledger is said, never guessed at."""
    try:
        with open(path or told_path(), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None


def fold(rows):
    """-> ({id: incident}, [(line, signal row)])."""
    incs, signals = {}, []
    for i, r in enumerate(rows):
        if "ev" not in r:
            signals.append((i, r))
        else:
            incs.setdefault(r["id"], {"id": r["id"]}).update(
                {k: v for k, v in r.items() if k not in ("ev", "id", "at", "t")})
    return incs, signals


def worst(*cs):
    return "emergency" if "emergency" in cs else "distressed"


def readings(table, status, now):
    """status.json -> ({metric: {class, item, ack}}, fresh, {metric: sane?}). A status not fresh sees nothing: its
    own metric ops_watch.blind is bad and no other reading is judged."""
    pol = table["policy"]
    t = status.get("t") if isinstance(status, dict) else None
    fresh = isinstance(t, (int, float)) and now - t <= pol["status_max_age_min"] * 60
    if not fresh:
        return {"ops_watch.blind": {"class": None, "item": None, "ack": None}}, False, {}
    bad, seen = {}, {}
    for k, p in (status.get("points") or {}).items():
        if not isinstance(p, dict) or "class" not in p:
            continue
        if p.get("m") == "MEASURED" and p["class"] in BAD:
            bad[k] = {"class": p["class"], "item": None, "ack": p.get("ack_within_min")}
        seen[k] = p.get("m") == "MEASURED" and p["class"] in ("sane", "idle")
    alarms = status.get("alarms")
    alarms = alarms if isinstance(alarms, dict) and "_alarm_state" not in alarms else None
    for aid, a in (alarms or {}).items():
        if isinstance(a, dict) and ":" in aid and a.get("state") in ("OPEN", "PENDING"):
            k = aid.split(":", 1)[1]
            bad.setdefault(k, {"class": None, "item": None, "ack": None})["item"] = a.get("item")
    for k in (status.get("points") or {}):        # an alarm key with no ranges class is sane when no alarm stands on it
        if k not in seen and k not in bad and alarms is not None:
            seen[k] = True
    return bad, True, seen


def chain_of(table, inc):
    return [inc["reader"]] + table["policy"]["chain"]


def next_due(table, inc):
    """Epoch of the next move up the chain, or None at the top."""
    rung = inc["rung"]
    if rung >= OWNER_RUNG:
        return None
    if inc.get("acked_t"):
        return inc["recover_by_t"]
    pol = table["policy"]
    at = inc["ack_min"] if rung == 0 else pol["ladder"][inc["class"]][rung - 1]
    return max(inc["told_t"] + at * 60, inc["rung_t"] + (pol["min_step_min"] * 60 if rung else 0))


def ring_of(table, inc, now, rung=None):
    rung = inc["rung"] if rung is None else rung
    reader = chain_of(table, inc)[rung]
    head = "INCIDENT %s (%s, rung %d, %s): %s" % (inc["id"], inc["class"], rung, reader, ", ".join(sorted(inc["metrics"])))
    how = {"Operations": "alarm_run", "Conductor": "quick_run", "Operations:fresh": "fresh_run", "owner": "owner"}.get(reader)
    why = head + ". rimflow incidents; rimflow ack %s --plan \"<next>\"." % inc["id"]
    if reader == "Operations:fresh":
        why += " This incident reaches him next: write his line, rimflow incident-line %s \"<line>\"." % inc["id"]
    return {"id": inc["id"], "how": how or "doorbell", "reader": reader, "seat": None if how else reader, "text": why}


def template(inc):
    return "RimMandrake %s since %s: %s. No agent could read this; fixed template." % (
        inc["class"], iso(inc["told_t"]), ", ".join(sorted(inc["metrics"])))


def item_acted(events, items, since):
    """The first seat action on a named item at or after iso `since` -> (item, seat, event), or None."""
    for e in events or ():
        if (e.get("id") in items and e.get("event") in ACTIONS and str(e.get("ts") or "") >= since
                and str(e.get("seat") or "").upper() not in NOT_READERS):
            return e["id"], e.get("seat"), e["event"]
    return None


def step(table, rows, status, now, cursor=0, events=None):
    """Pure. -> {rows, rings, keys, cursor, snapshot}. `events`: a callable -> ledger events, called only when an
    unacked incident names an item."""
    pol = table["policy"]
    incs, signals = fold(rows)
    out, rings = [], []

    def emit(ev, inc, **f):
        inc.update(f)
        out.append(dict(f, ev=ev, id=inc["id"], at=iso(now), t=now))

    bad, fresh, seen = readings(table, status, now)
    fired = {}
    for i, r in signals:
        kind = r.get("metric") or r.get("kind")
        if i >= cursor and kind:
            fired[kind] = {"class": r.get("class"), "item": r.get("item"), "ack": None, "event": True}
    groups = {}
    for metric, b in sorted(dict(bad, **fired).items()):
        rt = route_of(table, metric) or {"route": "role", "reader": "Operations", "cause": "unrouted"}
        if rt["route"] == "program":
            continue
        cls = b["class"] or rt.get("class") or "distressed"
        cause = rt.get("cause") or metric
        g = groups.setdefault(cause, {"metrics": {}, "reader": "owner" if rt["route"] == "owner" else rt["reader"],
                                      "class": cls, "ack": None, "items": []})
        g["metrics"][metric] = {"class": cls, "event": bool(b.get("event"))}
        g["class"] = worst(g["class"], cls)
        g["ack"] = min(x for x in (g["ack"], b["ack"], pol["ack_within_min"]) if x)
        if b["item"]:
            g["items"].append(b["item"])

    by_cause = {}
    for inc in incs.values():           # newest incident of each cause
        if inc["cause"] not in by_cause or inc["told_t"] >= by_cause[inc["cause"]]["told_t"]:
            by_cause[inc["cause"]] = inc
    for cause, g in sorted(groups.items()):
        inc = by_cause.get(cause)
        if inc and inc["state"] == "open":
            f = {}
            metrics = dict(inc["metrics"], **g["metrics"])
            if metrics != inc["metrics"]:
                f["metrics"] = metrics
            if worst(inc["class"], g["class"]) != inc["class"]:
                f["class"] = worst(inc["class"], g["class"])
            if set(g["items"]) - set(inc["items"]):
                f["items"] = sorted(set(inc["items"]) | set(g["items"]))
            if inc.get("sane_since"):
                f["sane_since"] = None
            if f:
                emit("joined", inc, **f)
            continue
        fields = dict(state="open", rung=0, rung_t=now, told_t=now, told_at=iso(now), metrics=g["metrics"],
                      metric=sorted(g["metrics"])[0], reader=g["reader"], ack_min=g["ack"], ack_due=iso(now + g["ack"] * 60),
                      ack_due_t=now + g["ack"] * 60, recover_by=None, recover_by_t=None, acked_t=None, ack_by=None,
                      plan=None, sane_since=None, closed_t=None, items=sorted(set(g["items"])), **{"class": g["class"]})
        if g["reader"] == "owner":
            fields.update(rung=OWNER_RUNG)
        if inc and now - (inc.get("closed_t") or 0) <= pol["relapse_h"] * 3600:
            emit("reopened", inc, reopens=inc.get("reopens", 0) + 1, **fields)
        else:
            inc = {"id": "%s-%s" % (cause, time.strftime("%Y%m%d%H%M%S", time.gmtime(now))), "cause": cause}
            incs[inc["id"]] = inc
            by_cause[cause] = inc
            emit("opened", inc, cause=cause, reopens=0, **fields)
        rings.append(ring_of(table, inc, now))

    for inc in sorted(incs.values(), key=lambda x: x["id"]):
        if inc["state"] != "open":
            continue
        if inc["items"] and not inc.get("acked_t") and events is not None:
            hit = item_acted(events(), inc["items"], inc["told_at"])
            if hit:
                emit("acked", inc, acked_t=now, ack_by=hit[1], plan="%s on %s" % (hit[2], hit[0]),
                     recover_by_t=now + pol["recover_min"] * 60, recover_by=iso(now + pol["recover_min"] * 60))
        states = []
        for m, v in inc["metrics"].items():
            if m in bad or m in fired:
                states.append(False)
            elif v.get("event"):
                states.append(True)
            else:
                states.append(seen.get(m) if fresh else None)
        if all(s is True for s in states):
            if not inc.get("sane_since"):
                emit("sane", inc, sane_since=now)
            need = pol["event_quiet_min"] if any(v.get("event") for v in inc["metrics"].values()) else pol["sustain_min"]
            if now - inc["sane_since"] >= need * 60:
                emit("closed", inc, state="closed", closed_t=now)
                continue
        elif False in states and inc.get("sane_since"):
            emit("relapsing", inc, sane_since=None)
        due = next_due(table, inc)
        if due is not None and now >= due and not inc.get("sane_since"):
            r = inc["rung"] + 1
            f = dict(rung=r, rung_t=now, acked_t=None, ack_by=None, plan=None, recover_by=None, recover_by_t=None)
            was = bool(inc.get("acked_t"))
            inc.update(f)
            d = next_due(table, inc)
            emit("escalated", inc, was_acked=was, ack_due=iso(d) if d else None, ack_due_t=d, **f)
            rings.append(ring_of(table, inc, now, r))
    live = [x for x in incs.values() if x["state"] == "open"]
    keys = sorted("incident:%s#%d" % (x["id"], x.get("reopens", 0)) for x in live
                  if x["rung"] == 0 and x["reader"] == "Operations")
    owner = [dict(id=x["id"], line=x.get("line") or template(x), unread=not x.get("line"), since=x["told_t"],
                  **{"class": x["class"]}) for x in live if x["rung"] >= OWNER_RUNG]
    snap = {"t": now, "at": iso(now), "fresh": fresh, "open": sorted(
        ({k: x.get(k) for k in ("id", "class", "cause", "rung", "reader", "told_at", "ack_due", "recover_by", "ack_by", "plan")}
         for x in live), key=lambda a: a["id"]), "owner": sorted(owner, key=lambda a: a["id"])}
    return {"rows": out, "rings": rings, "keys": keys, "cursor": len(rows), "snapshot": snap}


def ack(iid, seat, plan, recover_min=None, path=None, now=None):
    """The ack verb. -> the row. Raises ValueError on an unknown or closed id, or no plan: an ack names what is next."""
    if not (plan or "").strip():
        raise ValueError("--plan: an ack says what happens next")
    now = time.time() if now is None else now
    rows = read_rows(path)
    if rows is None:
        raise ValueError("told.jsonl does not read")
    inc = fold(rows)[0].get(iid)
    if not inc or inc.get("state") != "open":
        raise ValueError("%s is not an open incident (rimflow incidents)" % iid)
    mins = recover_min or load_table()["policy"]["recover_min"]
    row = {"ev": "acked", "id": iid, "at": iso(now), "t": now, "acked_t": now, "ack_by": seat, "plan": plan.strip(),
           "recover_by_t": now + mins * 60, "recover_by": iso(now + mins * 60)}
    append([row], path)
    return row


def write_line(iid, seat, line, path=None, now=None):
    """The line he sees first. Never an ack: the rung goes on."""
    now = time.time() if now is None else now
    if not (line or "").strip():
        raise ValueError("an empty line")
    rows = read_rows(path)
    inc = fold(rows or [])[0].get(iid)
    if not inc or inc.get("state") != "open":
        raise ValueError("%s is not an open incident" % iid)
    row = {"ev": "line", "id": iid, "at": iso(now), "t": now, "line": line.strip()[:300], "line_by": seat}
    append([row], path)
    return row


def signal(sch, kind, why, now, path=None):
    """A Dispatcher alarm that fired -> a signal row, unless the table contains it. -> True when written."""
    if not (sch.get("incident") or {}).get("enabled"):
        return False
    table = load_table()
    rt = route_of(table, kind)
    if rt is None or rt["route"] != "program":
        append([{"kind": kind, "metric": kind, "why": str(why)[:300], "told_at": iso(now), "class": (rt or {}).get("class")}], path)
        return True
    return False


def line_owed(key, said, path=None):
    """ops_watch's direct Conductor line: the first of a cause, in this pass (`said`, a set it adds to) and while no
    incident of that cause is open. One outage is one line however many metrics it trips."""
    rt = route_of(load_table(), key) or {}
    cause = rt.get("cause") or key
    if cause in said:
        return False
    said.add(cause)
    return not any(x["cause"] == cause and x["state"] == "open" for x in fold(read_rows(path))[0].values())


def write_snapshot(snap, path=None):
    path = path or snapshot_path()
    guard(path)
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(snap, f, indent=1)
    os.replace(tmp, path)


def reader_problem(reader, sch=None, table=None):
    """RO4. -> why nothing wakes this reader, or None. A doorbell reader also needs its seat's wake on."""
    table = table or load_table()
    r = table["readers"].get(reader)
    if r is None:
        return "no routing table entry wakes %s (%s)" % (reader, ROUTES)
    seat = r.get("seat")
    cfg = ((sch or {}).get("seats") or {}).get(seat) if seat else None
    if sch and seat and not (cfg and cfg.get("enabled", True) and cfg.get("wake", True)):
        return "%s is a doorbell reader whose waking is off in the schedule" % reader
    return None


RELENTLESS_RULES = os.path.join(HERE, "relentless_rules.json")


def receiver_problem(seat, needs, sch=None, table=None, relentless=None):
    """T2 (ALARMS_REWIRE_OFF_RETIRED_BENCH). -> why nobody picks up an alarm item filed `--for seat --needs needs`, or
    None. Every program that files an alarm (ops_watch, the dead-man, the steward) asks this before it spawns.
    An offline alarm is picked up when relentless is on and drains that seat's pool for that needs (the 10-31
    re-measure, D2: relentless workers repair alarms; it drains BENCH and FOUNDRY offline). A needs=owner alarm goes
    to OWNER, the Conductor's sitting. Any other alarm needs a reader in the RO4 table (alarm_routes.json) that is
    woken: a seat with no such reader is not a receiver, and the old fallback (BENCH, whose sittings no program
    rings) is refused for it."""
    if relentless is None:
        try:
            with open(os.environ.get("RIMFLOW_RELENTLESS_RULES") or RELENTLESS_RULES, encoding="utf-8") as f:
                relentless = json.load(f)
        except (OSError, ValueError):
            relentless = {}
    if needs == "owner":
        return None if seat == "OWNER" else "a needs=owner alarm goes to OWNER, not %s" % seat
    if (relentless.get("enabled") and seat in (relentless.get("pool_seats") or [])
            and needs in (relentless.get("pool_needs") or [])):
        return None
    table = table or load_table()
    r = table["readers"].get(seat)
    if r is None or r.get("seat") != seat:
        return ("no program wakes %s for needs=%s: relentless drains %s for %s%s, and %s is no doorbell reader in %s"
                % (seat, needs, relentless.get("pool_seats"), relentless.get("pool_needs"),
                   "" if relentless.get("enabled") else " (relentless is off)", seat, ROUTES))
    return reader_problem(seat, sch, table)
