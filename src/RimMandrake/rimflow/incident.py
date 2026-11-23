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
import calendar
import fnmatch
import json
import os
import re
import sys
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
CLOCK_UNIT_S = {"min": 60, "h": 3600, "s": 1, "d": 86400, "days": 86400}   # a metric ending _<unit> reads "how long", unless NOT_CLOCK says it is a rate or a peak
NOT_CLOCK = re.compile(r"(_per_h|_max_s)$")
DAYS_CLOCK = re.compile(r"(^|[._])days_since_")    # plan.days_since_advance: a day clock whose unit is not its last word
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


REMOVED_FAMILIES = ("relentless", "plan", "health")    # ops_watch.REMOVED_FAMILIES: collectors taken out


def retired_sane(status, metric):
    """A reading of a family whose collector was removed (ops_watch no longer writes any of its keys) is the removal, not a
    blind instrument, as ops_watch.andon reads it. -> True for such a key absent from the status, else None. Without it an
    incident holding such a key never closes on its readings (work_belt-20261101160557: 56 churn keys absent, at his rung
    for good after the Relentless retirement)."""
    pts = (status or {}).get("points") or {}
    if metric.split(".", 1)[0] in REMOVED_FAMILIES and metric not in pts:
        return True
    # a nightly red group's key exists only while the group is red: absent while the collector reports the night (or the
    # held nightly reads 0) is the group cleared, as ops_watch.andon reads it (testing-20261101162433: 145 such keys)
    k = pts.get("testing.nightly_known_reds") or {}
    if metric.startswith("testing.red_") and metric not in pts and k.get("m") == "MEASURED" and k.get("v") is not None:
        return True
    return None


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


def revisit_ring(inc, was_plan, news=(), was_trigger=None, deep=False):
    """The ring of an incident at his rung whose plan ran out: one fresh Operations run, batched with the pass's other
    fresh rings (dispatcher.incident_execute). The news comes first: the run's `why` is cut at 300 characters. Every
    one asks for a trigger line (the incident clerk reads it; a plan with none keeps model revisits)."""
    i = inc["id"]
    r = {"id": i, "how": "fresh_run", "reader": "Operations:fresh", "seat": None, "revisit": True, "text": (
        "INCIDENT %s (%s, at his rung, revisit %d). News: %s. Its plan ran out%s. Re-read it now: fixed, say so (it closes "
        "on its readings); else rimflow ack %s --plan \"<the current next step>\" --trigger \"<metric> <op> <number>[; "
        "after <YYYY-MM-DDTHH:MMZ>]\" [--recover-min N] (a program re-reads the line and calls a run only when it is "
        "crossed%s); and rewrite his line, rimflow incident-line %s \"<line>\". Metrics: %s." % (
            i, inc["class"], inc.get("revisits", 0), "; ".join(news) or "none recorded",
            " (was: %s)" % str(was_plan)[:60] if was_plan else "", i,
            "; the last plan had no line, so it kept model revisits" if not was_trigger else "", i,
            ", ".join(sorted(inc["metrics"]))))}
    if deep:
        r["deep"] = True
    return r


def observed_t(p):
    """The epoch a status point was itself observed at (its x.observed_at), or None."""
    x = p.get("x") if isinstance(p, dict) else None
    return _epoch(x["observed_at"]) if isinstance(x, dict) and x.get("observed_at") else None


def revisit_reads(inc, status, bad, signals):
    """What this incident's metrics read now: {metric: [standing?, class, value, measured?, signals fired so far,
    observed at]}. The last is the point's own observation epoch: a collector's reading lags the status pass by up to
    its max age, so a clock is graded over its own time (a 6 h revisit read plan.list_age_h 5 to 8 min off the status
    time, 2026-11-16..17)."""
    points = (status.get("points") or {}) if isinstance(status, dict) else {}
    fired = {}
    for _, r in signals:
        kind = r.get("metric") or r.get("kind")
        fired[kind] = fired.get(kind, 0) + 1
    out = {}
    for m in inc["metrics"]:
        p = points.get(m) if isinstance(points.get(m), dict) else {}
        out[m] = [m in bad, p.get("class"), p.get("v"), p.get("m") == "MEASURED", fired.get(m, 0), observed_t(p)]
    return out


def clock_unit_s(metric):
    """Seconds per unit of a metric whose value is "how long", or None for a plain value. A clock is graded by its rate:
    one rising at one unit per unit of time only aged (lesson 20261119T033457Z-CONDUCTOR). plan.days_since_advance ages
    1/24 an hour and was read as news every hour (RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS: 6 of 42 incident
    launches named it)."""
    if NOT_CLOCK.search(metric):
        return None
    if DAYS_CLOCK.search(metric):
        return 86400
    return CLOCK_UNIT_S.get(metric.rsplit("_", 1)[-1])


def in_band(band, v):
    """True when v is a number inside band ({min, max}, inclusive, either may be absent), else False."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    return not ((isinstance(band.get("min"), (int, float)) and v < band["min"])
                or (isinstance(band.get("max"), (int, float)) and v > band["max"]))


def reading_moved(metric, old, new, elapsed_s=None, slack_s=0, band=None):
    """Did one metric move? A signal fired, a standing alarm came or went, its class or measured mark changed, its value
    changed. A clock metric that rose by the status time elapsed (within slack_s) only aged; any other change means it
    reset or stalled: 60 to 70 over a 240 min floor is progress that re-aged, and a value on a sane metric counts too.
    A metric whose route states a `band` (a flapping count: wrapup.debris_standing, 8 of 42 incident launches) moves
    only when it leaves the band or its reading goes unmeasured: inside it, its alarm coming and going is not news."""
    if old is None or new is None:
        return old != new
    if band:
        return old[3] != new[3] or old[4] != new[4] or not new[3] or in_band(band, old[2]) != in_band(band, new[2])
    if old[0] != new[0] or old[1] != new[1] or old[3] != new[3] or old[4] != new[4]:
        return True
    if old[2] == new[2]:
        return False
    unit = clock_unit_s(metric)
    seen = [r[5] if len(r) > 5 and isinstance(r[5], (int, float)) else None for r in (old, new)]
    if unit and None not in seen and seen[1] > seen[0]:
        elapsed_s = seen[1] - seen[0]           # both points' own observation times (revisit_reads)
    if unit and elapsed_s is not None and isinstance(old[2], (int, float)) and isinstance(new[2], (int, float)):
        # one step of a value's decimal rounding is not movement: days_since_advance is written to 0.01 d (864 s), so
        # an hour reads 0.04 or 0.05 d. Whole numbers keep the slack alone (a minute clock is graded to the minute);
        # capped at half the time elapsed
        steps = [x for x in (value_step(old[2]), value_step(new[2])) if 0 < x < 1]    # 18.0 beside 17.96 is 0.01 too
        quantum = min(max(steps) * unit, abs(elapsed_s) / 2.0) if steps else 0.0
        return abs((new[2] - old[2]) * unit - elapsed_s) > slack_s + quantum + 1e-6
    return True


def value_step(v):
    """The rounding step a value was written at, from its shortest repr: 17.96 -> 0.01, 5 -> 1, an unrounded float -> 0."""
    s = repr(float(v))
    if "e" in s or "." not in s:
        return 0.0
    frac = s.split(".", 1)[1].rstrip("0")
    return 10.0 ** -len(frac) if len(frac) < 10 else 0.0


def revisit_news(inc, reads, fresh, rows, out, now, pol, events=None, status_t=None, table=None):
    """-> why this revisit needs a run, or [] when nothing moved since the last one. Anything not known to be unchanged is
    news: no earlier look, a blind status, no plan a run wrote (an auto-ack from an item action is not an answer).
    `table`: the routing table whose routes' `band`s grade a banded metric (reading_moved)."""
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
    moved = sorted(m for m in set(old) | set(reads) if reading_moved(m, old.get(m), reads.get(m), elapsed, slack,
                                                                     band_of(table, m)))
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


def band_of(table, metric):
    """The `band` the route of `metric` states, or None (no table, no route, or a route with no band)."""
    b = (route_of(table, metric) or {}).get("band") if table else None
    return b if isinstance(b, dict) and b else None


def program_answer(rt, point):
    """A banded program route (RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS: a repeat alarm the agent always
    answered "nothing to fix") -> ("program", why) while its status point is MEASURED inside the band: the program
    writes the route's runbook note and no agent is called; ("agent", why) when the reading is outside the band or could
    not be read (never "in band" on a blind reading); None for any other route (role, owner, or program with no band)."""
    if not rt or rt.get("route") != "program" or not isinstance(rt.get("band"), dict) or not rt["band"]:
        return None
    b = rt["band"]
    span = "[%s, %s]" % (b.get("min", "-inf"), b.get("max", "inf"))
    if not isinstance(point, dict):
        return "agent", "no reading of it in status.json: could not look, so the band does not answer"
    v = point.get("v")
    if point.get("m") != "MEASURED":
        return "agent", "its reading is %s, not MEASURED: the band does not answer" % point.get("m")
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return "agent", "its reading %r is not a number: the band does not answer" % (v,)
    if in_band(b, v):
        return "program", "reading %s inside its band %s" % (v, span)
    return "agent", "reading %s left its band %s" % (v, span)


TRIGGER_OPS = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b,
               "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
TRIGGER_METRIC = re.compile(r"^([A-Za-z0-9_.:\-]+)\s*(<=|>=|==|!=|<|>)\s*(-?\d+(?:\.\d+)?)$")
TRIGGER_AFTER = re.compile(r"^after\s+(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?)Z$", re.I)
CLERK_NEWS_EVS = ("reopened", "escalated")      # a rung change: the only state move a held trigger line does not answer


def parse_trigger(text):
    """A plan's trigger line (`rimflow ack --trigger`) -> [("metric", key, op, number) | ("after", epoch, iso)], one per
    `;` part; the line is crossed when any part is true. Raises ValueError naming the part that does not parse
    (design/specs/2026-11-19-incident-clerk/boundary.md, a-trigger-line)."""
    parts = [x.strip() for x in str(text or "").split(";") if x.strip()]
    if not parts:
        raise ValueError("--trigger: an empty line; write <metric> <op> <number> or after <YYYY-MM-DDTHH:MMZ>, joined by ;")
    out = []
    for part in parts:
        m, a = TRIGGER_METRIC.match(part), TRIGGER_AFTER.match(part)
        if m:
            out.append(("metric", m.group(1), m.group(2), float(m.group(3))))
        elif a:
            ts = a.group(1) + (":00" if len(a.group(1)) == 16 else "")
            out.append(("after", _epoch(ts), ts + "Z"))
        else:
            raise ValueError("--trigger: %r is neither <metric> <op> <number> (op one of %s) nor after "
                             "<YYYY-MM-DDTHH:MMZ> (UTC)" % (part, " ".join(TRIGGER_OPS)))
    return out


def trigger_state(clauses, status, now, fresh, since=None):
    """-> ("crossed" | "blind" | "held", [one text per clause that decided it]). Crossed when any clause is true; else
    blind when any metric clause could not be read (a stale status, an absent, unmeasured or non-number point: never
    "held" on a reading nobody made); else held, each clause's reading named. `since` is the ack's epoch: a point whose
    own observation (x.observed_at) is older than it is the reading the ack already planned around, so it is held as
    not yet re-read, never crossed (maturation-20261120030922, 2026-11-21: a run was called 80 s after an ack on the
    11:54Z reading that the ack itself answered). A collector that never reads again is ops_watch's blind alarm's."""
    points = (status.get("points") or {}) if isinstance(status, dict) else {}
    crossed, blind, held = [], [], []
    for c in clauses:
        if c[0] == "after":
            (crossed if now >= c[1] else held).append("after %s%s" % (c[2], ": the time came" if now >= c[1] else ""))
            continue
        _, key, op, n = c
        p = points.get(key)
        v = p.get("v") if isinstance(p, dict) else None
        if not fresh:
            blind.append("%s: status not fresh" % key)
        elif not isinstance(p, dict):
            blind.append("%s: no reading in status.json" % key)
        elif p.get("m") != "MEASURED":
            blind.append("%s: its reading is %s, not MEASURED" % (key, p.get("m")))
        elif not isinstance(v, (int, float)) or isinstance(v, bool):
            blind.append("%s: its reading %r is not a number" % (key, v))
        elif since and (observed_t(p) or since) < since:
            held.append("%s %s, read before the ack, not yet read again (line %s %s)" % (key, v, op, "%g" % n))
        elif TRIGGER_OPS[op](v, n):
            crossed.append("%s reads %s (%s %s)" % (key, v, op, "%g" % n))
        else:
            held.append("%s %s (line %s %s)" % (key, v, op, "%g" % n))
    if crossed:
        return "crossed", crossed
    if blind:
        return "blind", blind
    return "held", held


def clerk_trigger(inc, status, now, fresh):
    """The incident clerk's reading of an incident's trigger line -> trigger_state, or None when its plan has none (an
    auto-ack's plan is no run's and carries none). A stored line that does not parse is blind, never held."""
    line = inc.get("trigger")
    if not line or inc.get("auto_ack") or not inc.get("plan"):
        return None
    try:
        clauses = parse_trigger(line)
    except ValueError as e:
        return "blind", ["its stored line does not parse: %s" % e]
    return trigger_state(clauses, status, now, fresh, since=inc.get("acked_t"))


def clerk_news(inc, tstate, rows, out, now, pol):
    """-> why a revisit whose plan carries a trigger line needs a run, or []. Only the line crossed or blind, a rung
    change, a metric that joined since the last look, or a day unread is news: a moved reading the line does not name, a
    rewritten plan or an item action is not (the run that wrote the line said what matters; boundary
    a-change-the-trigger-does-not-name)."""
    news = []
    if tstate[0] == "crossed":
        news.append("trigger crossed: %s" % "; ".join(tstate[1]))
    elif tstate[0] == "blind":
        news.append("its trigger line could not be read: %s" % "; ".join(tstate[1]))
    seen_t = inc.get("revisit_seen_t") or 0
    moved = sorted({r["ev"] for r in list(rows) + out if r.get("id") == inc["id"] and r.get("ev") in CLERK_NEWS_EVS
                    and r.get("t", 0) > seen_t})
    if moved:
        news.append("its rung moved since the last look (%s)" % ", ".join(moved))
    read = inc.get("revisit_read")
    new = sorted(set(inc["metrics"]) - set(read)) if isinstance(read, dict) else []
    if new:
        news.append("a metric joined since the last look: %s" % ", ".join(new))
    if now - inc.get("revisit_t", 0) >= pol.get("revisit_quiet_max_min", 1440) * 60:
        news.append("no run has read it for %d min, the most a quiet incident waits" % ((now - inc.get("revisit_t", 0)) // 60))
    return news


def deep_read_at(pol, now):
    """Epoch of today's deep read (policy deep_read_local "HH:MM", this machine's local time), or None when unset."""
    hhmm = pol.get("deep_read_local")
    if not hhmm:
        return None
    hh, mm = (int(x) for x in str(hhmm).split(":", 1))
    lt = time.localtime(now)
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hh, mm, 0, 0, 0, -1))


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

    def revisit(inc, reads, news, deep=False):
        was, line = inc.get("plan"), (inc.get("trigger") if not inc.get("auto_ack") else None)
        f = dict(deep=True) if deep else {}
        emit("revisited", inc, rung_t=now, acked_t=None, ack_by=None, plan=None, last_plan=was, recover_by=None,
             recover_by_t=None, ack_cleared_t=now, revisits=inc.get("revisits", 0) + 1, revisit_t=now, revisit_seen_t=now, revisit_read=reads,
             revisit_status_t=status_t, revisit_plan=None, auto_ack=False, quiet_revisits=0, news=news,
             trigger=None, last_trigger=line, trigger_owed=not line, **f)
        ring(inc, revisit_ring(inc, was, news, line, deep))

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
            ans = program_answer(rt, (status.get("points") or {}).get(metric) if fresh else None)
            if ans is None or ans[0] == "program":
                continue
            rt = dict(rt, route="role")          # out of its band or unread: the agent is called, as a role route
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

    deep_t = deep_read_at(pol, now)
    if deep_t is not None and now >= deep_t and not any(
            r.get("ev") == "revisited" and r.get("deep") and r.get("t", 0) >= deep_t for r in rows):
        # the daily deep read (owner's card 2026-11-19, "one deep Opus run a day stays"): every open untamed incident at
        # his rung that is not recovering is re-read by one Opus run, whatever its trigger line says
        for inc in sorted(incs.values(), key=lambda x: x["id"]):
            if (inc["state"] == "open" and inc["rung"] >= OWNER_RUNG and not inc.get("sane_since")
                    and not inc.get("tamed")):
                looked.add(inc["id"])
                revisit(inc, revisit_reads(inc, status, bad, signals),
                        ["the daily deep read (once a day, on Opus), whatever its trigger line says"], deep=True)
    for inc in sorted(incs.values(), key=lambda x: x["id"]):
        if inc["state"] != "open":
            continue
        if inc["items"] and not inc.get("acked_t") and events is not None:
            hit = item_acted(events(), inc["items"], ack_since(inc))
            if hit:
                emit("acked", inc, acked_t=now, ack_by=hit[1], plan="%s on %s" % (hit[2], hit[0]), auto_ack=True, trigger=None,
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
                states.append(seen.get(m, retired_sane(status, m)) if fresh else None)
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
        at_his = inc["rung"] >= OWNER_RUNG and not inc.get("sane_since") and inc["id"] not in looked
        tstate = clerk_trigger(inc, status, now, fresh) if at_his else None     # the incident clerk: its plan's line
        if tstate and tstate[0] == "crossed":
            # a crossing does not wait for the revisit: the plan said this is what calls a run (and the line goes with it)
            looked.add(inc["id"])
            revisit(inc, revisit_reads(inc, status, bad, signals), clerk_news(inc, tstate, rows, out, now, pol))
        elif due is not None and now >= due and at_his:
            looked.add(inc["id"])
            reads = revisit_reads(inc, status, bad, signals)
            if tstate:
                news = clerk_news(inc, tstate, rows, out, now, pol)
            else:
                news = revisit_news(inc, reads, fresh, rows, out, now, pol, events, status_t, table)
            if news:
                revisit(inc, reads, news)
            elif tstate:
                still = "still %s, no change" % "; ".join(tstate[1])
                emit("revisit_quiet", inc, rung_t=now, revisit_seen_t=now, revisit_read=reads, revisit_status_t=status_t, revisit_plan=inc["plan"],
                     quiet_revisits=inc.get("quiet_revisits", 0) + 1, news=None, clerk=True, still=still, trigger_owed=False,
                     why="the clerk: trigger line %r not crossed, %s: re-armed, no run" % (inc["trigger"], still))
            else:
                emit("revisit_quiet", inc, rung_t=now, revisit_seen_t=now, revisit_read=reads, revisit_status_t=status_t, revisit_plan=inc["plan"],
                     quiet_revisits=inc.get("quiet_revisits", 0) + 1, news=None, clerk=False, still=None, trigger_owed=True,
                     why="readings and plan unchanged since %s: re-armed, no run; no trigger line, so its revisits stay "
                         "model reads until a run acks with --trigger" % iso(inc["revisit_t"]))
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
            tstate = clerk_trigger(inc, status, now, fresh)        # a plan with a line is graded by the clerk here too
            news = (clerk_news(inc, tstate, rows, out, now, pol) if tstate else
                    revisit_news(inc, reads, fresh, rows, out, now, pol, events, status_t, table))
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


def ack(iid, seat, plan, recover_min=None, path=None, now=None, trigger=None):
    """The ack verb. -> the row. Raises ValueError on an unknown or closed id, or no plan: an ack names what is next.
    `trigger`: the plan's line a program can check (parse_trigger; refused when it does not parse). An ack without one
    stores none: a new plan never inherits the old plan's line."""
    if not (plan or "").strip():
        raise ValueError("--plan: an ack says what happens next")
    if trigger is not None:
        parse_trigger(trigger)
        trigger = "; ".join(x.strip() for x in trigger.split(";") if x.strip())
    now = time.time() if now is None else now
    rows = read_rows(path)
    if rows is None:
        raise ValueError("told.jsonl does not read")
    inc = fold(rows)[0].get(iid)
    if not inc or inc.get("state") != "open":
        raise ValueError("%s is not an open incident (rimflow incidents)" % iid)
    mins = recover_min or load_table()["policy"]["recover_min"]
    row = {"ev": "acked", "id": iid, "at": iso(now), "t": now, "acked_t": now, "ack_by": seat, "plan": plan.strip(), "auto_ack": False,
           "trigger": trigger, "recover_by_t": now + mins * 60, "recover_by": iso(now + mins * 60)}
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


def receiver_problem(seat, needs, sch=None, table=None, tag=None):
    """T2 (ALARMS_REWIRE_OFF_RETIRED_BENCH). -> why nobody picks up an alarm item filed `--for seat --needs needs`, or
    None. Every program that files an alarm (ops_watch, the dead-man, the steward) asks this before it spawns.
    A needs=owner alarm goes to OWNER, the Conductor's sitting. Any other alarm needs a live program that drains it, a
    `drainers` row of the RO4 table (alarm_routes.json) matching its seat, needs and (when the row names tags) the
    alarm's tag, or a reader in that table that is woken: a seat with neither is not a receiver, and the old fallback
    (BENCH, whose sittings no program rings) is refused for it.
    RIMMANDRAKE_FIX_ALARM_RECEIVER_TRUSTS_RETIRED_RELENTLESS_POOL: this answered None for every BENCH offline alarm while
    run_rules.json said the Relentless pool was enabled, but that pool's tick is retired (masked 2026-11-13) and nothing
    worked through what ops_watch, the dead-man and the steward filed there. The retired pool's rules are no longer read."""
    if needs == "owner":
        return None if seat == "OWNER" else "a needs=owner alarm goes to OWNER, not %s" % seat
    table = table or load_table()
    for d in table.get("drainers") or []:
        if d.get("seat") == seat and needs in (d.get("needs") or []) and (not d.get("tags") or tag in d["tags"]):
            return None
    r = table["readers"].get(seat)
    if r is None or r.get("seat") != seat:
        return ("no program wakes %s for needs=%s%s: no drainer in %s takes it (the Relentless pool that drained BENCH "
                "offline is retired), and %s is no doorbell reader there"
                % (seat, needs, " (tag %s)" % tag if tag else "", ROUTES, seat))
    return reader_problem(seat, sch, table)


# ------------------------------------------------------------------ an ask he has since answered
# RIMMANDRAKE_STOP_ANSWERED_ASKS_RERAISED_THIRD_TIME_TO_HIM (2026-11-15): the plan of refusals-20261115061558 (acked
# 22:42Z) brought "the Pyrelands giant criterion" to him by card; he answered at 23:52:53Z and the work was built, but no
# one re-acked the plan, and a fresh Conductor window read it from `rimflow incidents` and raised it to him twice more
# ("This is the third time this has come to me."). So a plan that asks him something is checked, at read time, against
# the cards he answered and his --owner-said words AFTER the plan was written: enough shared subject words -> the plan is
# stale, `rimflow incidents` says so under it and `rimflow incident-line` refuses a line on it. Re-acking with a current
# plan clears it. The threshold is measured: over every acked plan in told.jsonl x every card answered within a day after
# it (2026-11-15), each pair sharing 7+ words was a genuine answer to that plan (the giant case shares 9); pairs at 6
# or fewer were mixed or unrelated.
ASK_RE = re.compile(r"\b(card|cards|him|his|owner|owner's)\b(?!-)", re.I)   # "owner-passed" asks nothing
ANSWER_MIN_SHARED = 7
ANSWER_STOP = frozenset("""that this with from what when where which while their there them they then than have been
were will would could should into onto over under only also each every other more most some such none nothing next plan
measured owner owners card cards conductor operations reads read reading item items run runs rows row alarm alarms closes
close closed open opened today just still about after before since until does done here your yours mandrake answer
answers answered asked question questions option options picked recommended because same once rimmandrake rimmaster""".split())


def subject_words(text):
    s = (text or "").lower().replace("'", "").replace("’", "")
    return {w for w in re.split(r"[^a-z0-9]+", s) if len(w) >= 4 and w not in ANSWER_STOP and not w.isdigit()}


def _epoch(ts):
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except ValueError:
        return None


def _flat(text):
    return " ".join(re.split(r"[^a-z0-9]+", (text or "").lower().replace("'", "").replace("’", ""))).strip()


def answered_since(inc, cards, owner_events, min_shared=ANSWER_MIN_SHARED):
    """-> the latest answer he gave AFTER this incident's plan on the plan's subject, or None:
    {"by": "card"|"owner-said", "at", "what", "shared": [...]}. Only a plan that asks him (ASK_RE) is checked."""
    plan = inc.get("plan") or ""
    t0 = inc.get("acked_t") or inc.get("told_t")
    if not plan or t0 is None or not ASK_RE.search(plan):
        return None
    pw, best, quoted = subject_words(plan), None, _flat(plan)
    for card in cards or ():
        t = _epoch(card.get("answered"))
        if t is None or t <= t0:
            continue
        for q in card.get("questions") or ():
            text = " ".join([q.get("question") or "", q.get("answer") or "", q.get("his_words") or ""]
                            + [p.get("description") or "" for p in q.get("picked") or ()])
            shared = pw & subject_words(text)
            if _flat(q.get("answer")) and _flat(q.get("answer")) in quoted:     # the plan already carries his pick
                continue
            if len(shared) >= min_shared and (best is None or t > best[0]):
                best = (t, {"by": "card", "at": card.get("answered"), "shared": sorted(shared),
                            "what": "%s → %s" % (" ".join((q.get("question") or "").split()), q.get("answer") or "")})
    for ev in owner_events or ():
        t = _epoch(ev.get("ts"))
        said = ev.get("ownerSaid") or ""
        if t is None or t <= t0 or not said or _flat(said) in quoted:      # a plan quoting his words knew them
            continue
        shared = pw & subject_words(said + " " + (ev.get("id") or ""))   # his words, never our title (live false hit, 03:29Z)
        if len(shared) >= min_shared and (best is None or t > best[0]):
            best = (t, {"by": "owner-said", "at": ev.get("ts"), "shared": sorted(shared),
                        "what": "%s (on %s)" % (said, ev.get("id"))})
    return best[1] if best else None


def owner_events_path():
    env = os.environ.get("RM_OWNER_EVENTS")
    if env:
        return env
    return os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "ledger", "events", "OWNER.jsonl")


def load_answers():
    """-> (cards, owner events with his words). Raises OSError/ValueError when a store cannot be read whole: a torn
    store may be missing the very card, so the check says it did not run rather than reading 'unanswered'."""
    sys.path.insert(0, HERE)
    import card_capture
    cards, evs = [], []
    try:
        f = open(card_capture.store_path(), encoding="utf-8")
    except FileNotFoundError:
        f = None
    if f is not None:
        with f:
            cards = [json.loads(x) for x in f if x.strip()]
    try:
        with open(owner_events_path(), encoding="utf-8") as f:
            for x in f:
                if '"ownerSaid"' in x:
                    evs.append(json.loads(x))
    except FileNotFoundError:
        pass
    return cards, evs


def answered_line(inc, hit):
    return ("⛔ ANSWERED after this plan: by %s at %s: \"%s\". Do not raise this to him again; re-read what was done and "
            "re-ack with a current plan: rimflow ack %s --plan \"...\"" % (hit["by"], hit["at"], hit["what"], inc["id"]))
