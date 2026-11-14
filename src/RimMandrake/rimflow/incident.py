#!/usr/bin/env python3
"""incident.py -- one incident, from told to recovered (OP3, OP4, RO4; design/RimMandrake/operating_requirements_2026-11-01.md).

told.jsonl beside ops_watch's alarms.json is append-only deltas: a row with `ev` updates incident `id`; a row with no
`ev` is a SIGNAL, an alarm that has no sane reading (relentless.told, or a Dispatcher alarm), taken once by line number.
Rows are deltas so an ack written from any clone between a tick's read and its write is not lost.

The Dispatcher tick runs step() in decide (pure) and execute() in its execute pass (the only writer of rings):
  * a distressed or emergency reading, an OPEN ops alarm, or a signal joins the open incident of its cause, else
    reopens the same-cause incident closed inside relapse_h that held one of its metrics (relapse_of), else opens one.
    One cause, one ring, one run.
  * an ACK is `rimflow ack <id> --plan` or the reader's action on the named item. It gives ownership and sets recover_by.
    A ring, a read or a consumed doorbell writes no ack row and cannot make one.
  * past the rung's ack time, or past recover_by acked or not, the incident moves up the chain: the route's reader,
    Conductor, a fresh Operations run, him; a rung asking the reader's own role again is skipped (next_rung). The last agent writes his line (`rimflow incident-line`); with none, the
    fixed template goes out marked unread, his accepted exception. A rung does not move while the readings are sane.
  * it closes only on reading: every metric seen sane for sustain_min (event_quiet_min for a signal no reader
    covers; a Dispatcher alarm whose reader records what stands is read like any metric, and a stale reading is
    unknown, never quiet: standing_of, RELAPSE_HELPERS_FIX_DIED_TWICE).
  * at his rung it is never left to sit: past recover_by (acked) or owner_revisit_min after it reached him or was last
    revisited (unacked), it is REVISITED -- the ack and plan go, and a fresh Operations run is rung to re-read it and
    resolve it, re-ack it with a current plan, or rewrite his line (OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS: seven
    incidents sat at rung 3 for a day with recover_by long past, because nothing came after him).
    A revisit is rung only when there is news (revisit_news); with none it is re-armed with no run and a revisit_quiet
    row says so, for at most revisit_quiet_max_min. One run takes every revisit due inside revisit_batch_min
    (INCIDENT_REVISIT_TAME_SAME_NEWS_HOURLY: 9 of 15 Operations runs in a day re-read incidents that had not moved).
  * a RELAPSE is a fix that died: an incident that recovered and CLOSED, then came back (a `reopened` row). Joining an
    open incident, a dip back to bad before it closed (`relapsing`) and an ack are not. The tame_relapses-th relapse of a
    cause inside tame_window_h TAMES it (INCIDENT_RELAPSE_TAME_STOP_FULL_READS; strategy 2026-11-02 section 4): it buys
    no more full Operations reads (no alarm-run key, no fresh_run ring; a `withheld` row says each one), and one
    structural item is filed quoting its acks (a `structural` ring until a `structural_filed` row). It stays open and
    climbs its ladder: the Conductor's quick run and his line still come.
incidents.json is the snapshot stamped every tick: pulse reads its `owner` rows, the deadman reads its age.
"""
import fnmatch
import json
import os
import re
import time
try:                                    # whole text, never a silent cut (RIMMANDRAKE_STORE_TEXT_WHOLE_NO_CUTS)
    from . import fulltext
except ImportError:
    # loaded by file path (testq steward._incident_mod): its folder is not on sys.path, and without this the steward's
    # receiver check failed on every pass and it filed nothing (STEVE lane BRAKED unowned, 2026-11-12)
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fulltext  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROUTES = os.path.join(HERE, "alarm_routes.json")
REAL_OPS = "/mnt/d/ClaudeWork/rimmandrake/ops_watch"
REAL_STATE = "/mnt/d/ClaudeWork/rimmandrake/dispatcher"
BAD = ("distressed", "emergency")
ACTIONS = ("claim", "start", "close", "implemented", "drop")     # a note is not one: the 2026-11-01 diagnosis was a note
NOT_READERS = ("DISPATCHER", "RUNNER", "RELENTLESS")
OWNER_RUNG = 3
CLOCK_UNIT_S = {"min": 60, "h": 3600, "s": 1}         # a metric ending _<unit> reads "how long", unless NOT_CLOCK says it is a rate or a peak
NOT_CLOCK = re.compile(r"(_per_h|_max_s)$")
NEWS_EVS = ("joined", "sane", "relapsing", "reopened", "escalated")
FULL_READS = ("alarm_run", "fresh_run")      # a whole Operations run (~450k, plan-20261101164253): what a tamed incident stops buying


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
    pts = status.get("points") or {}
    for k, p in pts.items():
        if not isinstance(p, dict) or "class" not in p:
            continue
        if p.get("judged_by") in pts:              # ops_watch judges this one by another point (a retired belt's readings)
            seen[k] = True
            continue
        if p.get("m") == "MEASURED" and p["class"] in BAD:
            bad[k] = {"class": p["class"], "item": None, "ack": p.get("ack_within_min")}
        seen[k] = p.get("m") == "MEASURED" and p["class"] in ("sane", "idle")
    alarms = status.get("alarms")
    if isinstance(alarms, dict) and "_alarm_state" in alarms:
        # alarms.json unreadable: ops_watch held every filing and every alarm below goes unread. One fixed incident
        # says so (OPS_ALARM_FIX_CLOSED_TICKET_SILENCES_FAULT, plan B4), instead of the alarms vanishing in silence
        bad["ops_watch.alarm_state"] = {"class": None, "item": None, "ack": None}
    else:
        seen["ops_watch.alarm_state"] = True
    alarms = alarms if isinstance(alarms, dict) and "_alarm_state" not in alarms else None
    for aid, a in (alarms or {}).items():
        if isinstance(a, dict) and ":" in aid and a.get("state") in ("OPEN", "PENDING"):
            k = aid.split(":", 1)[1]
            bad.setdefault(k, {"class": None, "item": None, "ack": None})["item"] = a.get("item")
    for k in (status.get("points") or {}):        # an alarm key with no ranges class is sane when no alarm stands on it
        if k not in seen and k not in bad and alarms is not None:
            seen[k] = True
    seen["ops_watch.blind"] = True                # a fresh status is its own reading; without this a blind incident never closes
    return bad, True, seen


def chain_of(table, inc):
    return [inc["reader"]] + table["policy"]["chain"]


def role_of(reader):
    """The role a chain entry asks: a fresh Operations run is still Operations."""
    return str(reader).split(":", 1)[0]


def next_rung(table, inc, rung=None):
    """The rung an escalation moves to. A policy rung asking the route's reader's own role again is skipped
    (INCIDENT_CHAIN_DEDUPE_OPERATIONS_RUNG: an Operations-read route went Operations, Conductor, fresh Operations, him;
    the fresh run asked the same role twice), so its next rung is the Conductor and then him. His rung is never skipped."""
    rung = inc["rung"] if rung is None else rung
    chain = chain_of(table, inc)
    r = rung + 1
    while r < OWNER_RUNG and role_of(chain[r]) == role_of(chain[0]):
        r += 1
    return r


def next_due(table, inc):
    """Epoch of the next move up the chain, or None at the top. The time is the TARGET rung's: a skipped rung moves
    nothing earlier, so he is reached at the ladder's own minute."""
    rung = inc["rung"]
    pol = table["policy"]
    if rung >= OWNER_RUNG:                  # his rung: revisited, never climbed; an ack lengthens the wait, never shortens it
        if not pol.get("owner_revisit_min"):
            return None
        floor = inc["rung_t"] + pol["owner_revisit_min"] * 60
        return max(floor, inc["recover_by_t"]) if inc.get("acked_t") else floor
    if inc.get("acked_t"):
        return inc["recover_by_t"]
    to = next_rung(table, inc)
    at = inc["ack_min"] if to == 1 else pol["ladder"][inc["class"]][to - 2]
    if rung == 0:
        at = max(at, inc["ack_min"])
    return max(inc["told_t"] + at * 60, inc["rung_t"] + (pol["min_step_min"] * 60 if rung else 0))


def ring_of(table, inc, now, rung=None):
    rung = inc["rung"] if rung is None else rung
    reader = chain_of(table, inc)[rung]
    head = "INCIDENT %s (%s, rung %d, %s): %s" % (inc["id"], inc["class"], rung, reader, ", ".join(sorted(inc["metrics"])))
    how = {"Operations": "alarm_run", "Conductor": "quick_run", "Operations:fresh": "fresh_run", "owner": "owner"}.get(reader)
    why = head + ". rimflow incidents; rimflow ack %s --plan \"<next>\"." % inc["id"]
    if reader != "owner" and rung < OWNER_RUNG and next_rung(table, inc, rung) == OWNER_RUNG:   # the last agent before him
        why += " This incident reaches him next: write his line, rimflow incident-line %s \"<line>\"." % inc["id"]
    return {"id": inc["id"], "how": how or "doorbell", "reader": reader, "seat": None if how else reader, "text": why}


def revisit_ring(inc, was_plan, news=()):
    """The ring of an incident at his rung whose plan ran out: one fresh Operations run, batched with the pass's other
    fresh rings (dispatcher.incident_execute). The news comes first: the run's `why` is cut at 300 characters."""
    i = inc["id"]
    return {"id": i, "how": "fresh_run", "reader": "Operations:fresh", "seat": None, "revisit": True, "text": (
        "INCIDENT %s (%s, at his rung, revisit %d). News: %s. Its plan ran out%s. Re-read it now: fixed, say so (it closes "
        "on its readings); else rimflow ack %s --plan \"<the current next step>\" [--recover-min N]; and rewrite his line, "
        "rimflow incident-line %s \"<line>\". Metrics: %s." % (
            i, inc["class"], inc.get("revisits", 0), "; ".join(news) or "none recorded",
            " (was: %s)" % str(was_plan)[:60] if was_plan else "", i, i, ", ".join(sorted(inc["metrics"]))))}


def revisit_reads(inc, status, bad, signals):
    """What this incident's metrics read now: {metric: [standing?, class, value, measured?, signals fired so far]}."""
    points = (status.get("points") or {}) if isinstance(status, dict) else {}
    fired = {}
    for _, r in signals:
        kind = r.get("metric") or r.get("kind")
        fired[kind] = fired.get(kind, 0) + 1
    out = {}
    for m in inc["metrics"]:
        p = points.get(m) if isinstance(points.get(m), dict) else {}
        out[m] = [m in bad, p.get("class"), p.get("v"), p.get("m") == "MEASURED", fired.get(m, 0)]
    return out


def clock_unit_s(metric):
    """Seconds per unit of a metric whose value is "how long", or None for a plain value."""
    return None if NOT_CLOCK.search(metric) else CLOCK_UNIT_S.get(metric.rsplit("_", 1)[-1])


def reading_moved(metric, old, new, elapsed_s=None, slack_s=0):
    """Did one metric move? A signal fired, a standing alarm came or went, its class or measured mark changed, its value
    changed. A clock metric that rose by the status time elapsed (within slack_s) only aged; any other change means it
    reset or stalled: 60 to 70 over a 240 min floor is progress that re-aged, and a value on a sane metric counts too."""
    if old is None or new is None:
        return old != new
    if old[0] != new[0] or old[1] != new[1] or old[3] != new[3] or old[4] != new[4]:
        return True
    if old[2] == new[2]:
        return False
    unit = clock_unit_s(metric)
    if unit and elapsed_s is not None and isinstance(old[2], (int, float)) and isinstance(new[2], (int, float)):
        return abs((new[2] - old[2]) * unit - elapsed_s) > slack_s
    return True


def revisit_news(inc, reads, fresh, rows, out, now, pol, events=None, status_t=None):
    """-> why this revisit needs a run, or [] when nothing moved since the last one. Anything not known to be unchanged is
    news: no earlier look, a blind status, no plan a run wrote (an auto-ack from an item action is not an answer)."""
    seen_t = inc.get("revisit_seen_t")
    if not seen_t or inc.get("revisit_read") is None:
        return ["no earlier revisit to compare with"]
    if not fresh:
        return ["status not fresh: the readings cannot be compared"]
    news = []
    if not inc.get("plan") or inc.get("auto_ack"):
        news.append("no run has answered: no plan of its own")
    elif inc.get("revisit_plan") and inc["plan"] != inc["revisit_plan"]:
        news.append("the plan changed")
    old = inc["revisit_read"]
    was_t = inc.get("revisit_status_t")          # both readings' own times: a status may lag the pass that read it
    elapsed = status_t - was_t if status_t and was_t else now - seen_t
    slack = pol.get("revisit_clock_slack_min", 0) * 60
    moved = sorted(m for m in set(old) | set(reads) if reading_moved(m, old.get(m), reads.get(m), elapsed, slack))
    if moved:
        news.append("readings moved: %s%s" % (", ".join(moved[:4]), " +%d more" % (len(moved) - 4) if len(moved) > 4 else ""))
    if any(r.get("id") == inc["id"] and r.get("ev") in NEWS_EVS and r.get("t", 0) > seen_t for r in list(rows) + out):
        news.append("its state moved since the last look")
    hit = item_acted(events(), inc.get("items") or (), iso(seen_t)) if events is not None and inc.get("items") else None
    if hit:
        news.append("%s on %s" % (hit[2], hit[0]))
    if now - inc.get("revisit_t", 0) >= pol.get("revisit_quiet_max_min", 1440) * 60:
        news.append("no run has read it for %d min, the most a quiet incident waits" % ((now - inc.get("revisit_t", 0)) // 60))
    return news


def relapse_of(incs, cause, metrics, now, relapse_h):
    """The closed incident of this cause that `metrics` reopen: the newest one closed inside relapse_h that held one of
    them. A cause is a routing family (every ops:* alarm is ops_watch), so a different metric under it is a new problem,
    not that incident's fix dying (RELAPSE_OPS_WATCH_FIX_DIED_TWICE: three unrelated, each-fixed ops_watch alarms were
    joined into one incident and tamed as two relapses)."""
    hits = [x for x in incs.values() if x.get("cause") == cause and x.get("state") == "closed"
            and now - (x.get("closed_t") or 0) <= relapse_h * 3600 and set(x.get("metrics") or ()) & set(metrics)]
    return max(hits, key=lambda x: x.get("closed_t") or 0) if hits else None


def relapse_rows(rows, ids, now, window_h):
    """The relapses of these incident ids inside the window: `reopened` rows, nothing else (joins, dips, acks are not)."""
    return [r for r in rows if r.get("ev") == "reopened" and r.get("id") in ids and r.get("t", 0) > now - window_h * 3600]


def ack_quotes(rows, ids, n=6):
    """The acks of these incidents, newest last: who, when, the plan. What a structural item must quote."""
    acks = [r for r in rows if r.get("ev") == "acked" and r.get("id") in ids and r.get("plan")]
    return ["%s by %s: %s" % (r.get("at"), r.get("ack_by"), str(r["plan"])) for r in acks[-n:]]


def structural_name(cause):
    """The one structural item of a cause: SUBJECT_INTENT_TWIST, at most 44 characters (rimflow namecheck)."""
    subj = re.sub(r"[^A-Z0-9]+", "_", str(cause).upper()).strip("_")[:21].strip("_") or "UNROUTED"
    return "RELAPSE_%s_FIX_DIED_TWICE" % subj


def structural_ring(inc):
    acks = inc.get("acks") or []
    title = "Incident %s relapsed %d times in %d h: each ack's fix died; make the fix structural" % (
        inc["id"], inc.get("relapses", 0), inc.get("tame_window_h", 24))
    text = ("Incident %s (cause %s) recovered, closed and came back %d times inside %d h, so it buys no more full "
            "Operations reads; it stays open on its ladder. The acks whose fixes died: %s" % (
                inc["id"], inc["cause"], inc.get("relapses", 0), inc.get("tame_window_h", 24),
                " | ".join(acks) if acks else "none recorded (no run acked it)"))
    return {"id": inc["id"], "how": "structural", "reader": None, "seat": None, "item": inc["structural"],
            "title": fulltext.fit(title, 200), "text": fulltext.fit(text, 1800)}


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


REPAIRED = ("close", "implemented")     # a drop or supersede is not a repair: the incident waits on its readings


def repaired(events, items, since):
    """Every named item closed (close / implemented) at or after iso `since` -> {item: event ts}, else None.
    OPSWATCH_BUILD_ALARMS_KEYED_BY_CAUSE: an incident row closes with its repair."""
    done = {}
    for e in events or ():
        if e.get("id") in items and e.get("event") in REPAIRED and str(e.get("ts") or "") >= since:
            done.setdefault(e["id"], e.get("ts"))
    return done if items and set(items) <= set(done) else None


def ack_since(inc):
    """-> iso time from which an item action can auto-ack: the latest of told_at, the last revisit and the last ack
    cleared by an escalation. An action already read before the ack was cleared is old news and acks nothing again."""
    t = max(inc.get("revisit_t") or 0, inc.get("ack_cleared_t") or 0)
    return max(inc["told_at"], iso(t)) if t else inc["told_at"]


def standing_of(standing, metric, now, max_age_s):
    """A Dispatcher alarm's own reading of its source (RELAPSE_HELPERS_FIX_DIED_TWICE). `standing` is the tick state's
    {scope: {t, keys}}: what the reader of `scope` (a family such as long_helper, or one exact key such as budget:failed)
    saw standing when it last ran. -> True (its source still stands), False (read and gone), "stale" (its reader has not
    run for max_age_s: unknown, never quiet), or None (no reader covers it: the event_quiet_min rule). A `<scope>:reader`
    metric is the reader failing and is never judged by the reading it failed to make."""
    if metric.endswith(":reader"):
        return None
    for scope, r in (standing or {}).items():
        if metric == scope or metric.startswith(scope + ":"):
            if not isinstance(r, dict) or not isinstance(r.get("t"), (int, float)) or now - r["t"] > max_age_s:
                return "stale"
            return metric in (r.get("keys") or ())
    return None


def step(table, rows, status, now, cursor=0, events=None, standing=None):
    """Pure. -> {rows, rings, keys, cursor, snapshot}. `events`: a callable -> ledger events, called only when an
    unacked incident names an item. `standing`: the Dispatcher's readings of its own alarms' sources (standing_of): a
    signal metric a reader covers is judged by it, held open while its source stands and closed on sustain_min once it
    is gone, instead of closing on event_quiet_min of silence while the source still stands (helpers-20261101162643,
    2026-11-02 11:29Z: helper_lost:3378fb18 closed on quiet across a 5.6 h tick gap, its receipt unacked, and the same
    tick's repeat reopened it as a fix that died)."""
    pol = table["policy"]
    incs, signals = fold(rows)
    out, rings = [], []

    def emit(ev, inc, **f):
        inc.update(f)
        out.append(dict(f, ev=ev, id=inc["id"], at=iso(now), t=now))

    def ring(inc, r):
        if inc.get("tamed") and r["how"] in FULL_READS:     # its ladder still moves; only the full read is not bought
            emit("withheld", inc, withheld=r["how"], why="tamed after %d relapses: no full read; structural item %s" % (
                inc.get("relapses", 0), inc.get("structural")))
        else:
            rings.append(r)

    def revisit(inc, reads, news):
        was = inc.get("plan")
        emit("revisited", inc, rung_t=now, acked_t=None, ack_by=None, plan=None, last_plan=was, recover_by=None,
             recover_by_t=None, ack_cleared_t=now, revisits=inc.get("revisits", 0) + 1, revisit_t=now, revisit_seen_t=now, revisit_read=reads,
             revisit_status_t=status_t, revisit_plan=None, auto_ack=False, quiet_revisits=0, news=news)
        ring(inc, revisit_ring(inc, was, news))

    looked = set()
    status_t = status.get("t") if isinstance(status, dict) else None
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
        inc = relapse_of(incs, cause, g["metrics"], now, pol["relapse_h"])
        if inc:
            ids = {x["id"] for x in incs.values() if x.get("cause") == cause      # the same problem: one of its metrics
                   and set(x.get("metrics") or ()) & set(g["metrics"])}
            win = pol.get("tame_window_h", 24)
            n = len(relapse_rows(rows, ids, now, win)) + 1          # + this one
            tame = n >= pol.get("tame_relapses", 2)
            emit("reopened", inc, reopens=inc.get("reopens", 0) + 1, tamed=tame, **fields)
            if tame:
                emit("tamed", inc, relapses=n, tame_window_h=win, tamed_t=now, structural=structural_name(cause),
                     structural_filed=None, acks=ack_quotes(rows, ids))
        else:
            inc = {"id": "%s-%s" % (cause, time.strftime("%Y%m%d%H%M%S", time.gmtime(now))), "cause": cause}
            incs[inc["id"]] = inc
            by_cause[cause] = inc
            emit("opened", inc, cause=cause, reopens=0, **fields)
        ring(inc, ring_of(table, inc, now))

    for inc in sorted(incs.values(), key=lambda x: x["id"]):
        if inc["state"] != "open":
            continue
        if inc["items"] and not inc.get("acked_t") and events is not None:
            hit = item_acted(events(), inc["items"], ack_since(inc))
            if hit:
                emit("acked", inc, acked_t=now, ack_by=hit[1], plan="%s on %s" % (hit[2], hit[0]), auto_ack=True,
                     recover_by_t=now + pol["recover_min"] * 60, recover_by=iso(now + pol["recover_min"] * 60))
        if inc["items"] and events is not None and not any(m in bad or m in fired for m in inc["metrics"]):
            # its repair item(s) closed and no metric reads bad now: closed with the repair, not after sustain_min
            done = repaired(events(), inc["items"], inc["told_at"])
            if done:
                emit("closed", inc, state="closed", closed_t=now, closed_by="repair", repaired=done)
                continue
        states, quiet = [], False
        for m, v in inc["metrics"].items():
            sr = standing_of(standing, m, now, pol["status_max_age_min"] * 60) if v.get("event") else None
            if m in bad or m in fired or sr is True:
                states.append(False)
            elif sr == "stale":
                states.append(None)
            elif sr is False:
                states.append(True)
            elif v.get("event"):
                states.append(True)
                quiet = True
            else:
                states.append(seen.get(m) if fresh else None)
        if all(s is True for s in states):
            if not inc.get("sane_since"):
                emit("sane", inc, sane_since=now)
            need = pol["event_quiet_min"] if quiet else pol["sustain_min"]
            if now - inc["sane_since"] >= need * 60:
                emit("closed", inc, state="closed", closed_t=now)
                continue
        elif False in states and inc.get("sane_since"):
            emit("relapsing", inc, sane_since=None)
        due = next_due(table, inc)
        if due is not None and now >= due and not inc.get("sane_since") and inc["rung"] >= OWNER_RUNG:
            looked.add(inc["id"])
            reads = revisit_reads(inc, status, bad, signals)
            news = revisit_news(inc, reads, fresh, rows, out, now, pol, events, status_t)
            if news:
                revisit(inc, reads, news)
            else:
                emit("revisit_quiet", inc, rung_t=now, revisit_seen_t=now, revisit_read=reads, revisit_status_t=status_t, revisit_plan=inc["plan"],
                     quiet_revisits=inc.get("quiet_revisits", 0) + 1, news=None,
                     why="readings and plan unchanged since %s: re-armed, no run" % iso(inc["revisit_t"]))
        elif due is not None and now >= due and not inc.get("sane_since"):
            r = next_rung(table, inc)
            f = dict(rung=r, rung_t=now, acked_t=None, ack_by=None, plan=None, recover_by=None, recover_by_t=None)
            was = bool(inc.get("acked_t"))
            if was:
                f["ack_cleared_t"] = now
            inc.update(f)
            d = next_due(table, inc)
            emit("escalated", inc, was_acked=was, ack_due=iso(d) if d else None, ack_due_t=d, **f)
            ring(inc, ring_of(table, inc, now, r))
    if any(r["how"] == "fresh_run" for r in rings):      # a run is going: it takes every revisit about to fall due
        for inc in sorted(incs.values(), key=lambda x: x["id"]):
            if (inc["state"] != "open" or inc["rung"] < OWNER_RUNG or inc["id"] in looked or inc.get("sane_since")
                    or inc.get("tamed")):            # a tamed one is not pulled into a run it may not buy
                continue
            due = next_due(table, inc)
            if due is None or due - now > pol.get("revisit_batch_min", 0) * 60:
                continue
            reads = revisit_reads(inc, status, bad, signals)
            news = revisit_news(inc, reads, fresh, rows, out, now, pol, events, status_t)
            if news:                                     # with none it waits for its own time and is re-armed then
                revisit(inc, reads, news)
    live = [x for x in incs.values() if x["state"] == "open"]
    for x in sorted(live, key=lambda a: a["id"]):          # filed once: retried every pass until a structural_filed row
        if x.get("tamed") and x.get("structural") and not x.get("structural_filed"):
            rings.append(structural_ring(x))
    keys = sorted("incident:%s#%d" % (x["id"], x.get("reopens", 0)) for x in live
                  if x["rung"] == 0 and x["reader"] == "Operations" and not x.get("tamed"))
    owner = [dict(id=x["id"], line=x.get("line") or template(x), unread=not x.get("line"), since=x["told_t"],
                  **{"class": x["class"]}) for x in live if x["rung"] >= OWNER_RUNG]
    snap = {"t": now, "at": iso(now), "fresh": fresh, "open": sorted(
        ({k: x.get(k) for k in ("id", "class", "cause", "rung", "reader", "told_at", "ack_due", "recover_by", "ack_by", "plan",
                                "revisits", "quiet_revisits", "tamed", "structural")}
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
    row = {"ev": "acked", "id": iid, "at": iso(now), "t": now, "acked_t": now, "ack_by": seat, "plan": plan.strip(), "auto_ack": False,
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
    row = {"ev": "line", "id": iid, "at": iso(now), "t": now, "line": line.strip(), "line_by": seat}
    append([row], path)
    return row


def signal(sch, kind, why, now, path=None):
    """A Dispatcher alarm that fired -> a signal row, unless the table contains it. -> True when written."""
    if not (sch.get("incident") or {}).get("enabled"):
        return False
    table = load_table()
    rt = route_of(table, kind)
    if rt is None or rt["route"] != "program":
        append([{"kind": kind, "metric": kind, "why": str(why), "told_at": iso(now), "class": (rt or {}).get("class")}], path)
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
            and (needs in (relentless.get("pool_needs") or [])
                 or ((relentless.get("game") or {}).get("enabled")     # relentless_game: the game mode drains these too
                     and needs in ((relentless.get("game") or {}).get("pool_needs") or [])))):
        return None
    table = table or load_table()
    r = table["readers"].get(seat)
    if r is None or r.get("seat") != seat:
        return ("no program wakes %s for needs=%s: relentless drains %s for %s%s, and %s is no doorbell reader in %s"
                % (seat, needs, relentless.get("pool_seats"), relentless.get("pool_needs"),
                   "" if relentless.get("enabled") else " (relentless is off)", seat, ROUTES))
    return reader_problem(seat, sch, table)
