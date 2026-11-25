#!/usr/bin/env python3
"""follow_through.py: the weekly follow-through audit. How much of what was asked in a week reached its result?

Item RIMMANDRAKE_BUILD_FOLLOW_THROUGH_AUDIT_LOWER_RATE_IS_HEADLINE, step 5 of
design/specs/2026-11-22-coordination-every-agent-must-use/plan.md (§The measurement). Page:
design/specs/2026-11-23-follow-through-audit/boundary.md. Tests: selftest_follow_through.py (one per promise) and
src/RimMandrake/rimflow/acceptance/step5_follow_through_accept.py (the contract of sample, rates and hands_off).

Two streams of needs that started in the week: his typed words in the Conductor window (talk), and run ends that named
a next act, the `LEFT OPEN:` notes (pipe). A seeded draw of N from each. A fresh reader judges each need against the
real file or run; the lower of the two rates is the headline. Beside it: the Conductor window's acts on list work and
the share of items closed with none; Conductor debts ripe over a day and still open; waits past their date with no
event since; his typed messages of the last 3 days with no home; and the week's planted need, filed a week before.

    python3 src/RimMandrake/Utils/follow_through.py sample [--week-ending D] [--write]   the draw (dry: printed only)
    python3 src/RimMandrake/Utils/follow_through.py rates  [--week-ending D] [--write]   the rates from the record
    python3 src/RimMandrake/Utils/follow_through.py judged --week-ending D               the reader item's check: 0|1|2
    python3 src/RimMandrake/Utils/follow_through.py tick [--apply]                       the timer: file, plant, launch
    python3 src/RimMandrake/Utils/follow_through.py plant --week-ending D [--apply]      file the need that D's audit reads

D defaults to the latest Sunday (Pacific) on or before today. Exit codes: 0 done, 1 fails (named), 2 could not read
(named), 3 refused to overwrite verdicts. No model call here; the reader is a launched run.
"""
import argparse
import datetime as dt
import json
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RIMFLOW = os.path.join(REPO, "src", "RimMandrake", "rimflow")
for _p in (HERE, RIMFLOW, os.path.join(REPO, "src", "RimMandrake")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from zoneinfo import ZoneInfo
    PAC = ZoneInfo("America/Los_Angeles")
except Exception:                                   # noqa: BLE001 - no tz database: week() refuses by name
    PAC = None

ITEM = "RIMMANDRAKE_BUILD_FOLLOW_THROUGH_AUDIT_LOWER_RATE_IS_HEADLINE"
UNIT = "rm-follow-through.service"
FAMILY = "follow_through"
SEAT = "BENCH"
PAGE_DIR = os.path.join("design", "specs", "2026-11-23-follow-through-audit")
AUDIT_DIR = os.path.join(PAGE_DIR, "audit")
BRIEF = os.path.join(HERE, "follow_through_reader.md")
FIRST_WEEK = "2026-11-29"   # the plan's first reading (plan §The measurement); the tick does nothing for earlier weeks
N = 20                      # needs per stream: the plan's number. Danger: too few to show a difference, too many to judge
RIPE_S = 86400              # a debt is a drop when ripe over a day (census of 2026-11-22); younger reads as in flight
HOMELESS_S = 3 * 86400      # typed messages with no home are read over 3 days (the census's window)
READER_CAP_USD = 12         # runaway reader spend, stopped from outside (list_dispatch.json opus_cap_usd); never in a brief
LAUNCH_TIMEOUT_S = 10800      # hang guard: one detached_helper.py launch (a clone sync, a fetch) # budget: class=launch
CLI_TIMEOUT_S = 21600         # hang guard: one rimflow write with --publish # budget: class=publish
VERDICTS = ("outcome", "disposed", "moved", "nothing", "not_a_need")
FOLLOWED = ("outcome", "disposed")
WINDOW_HANDS = ("BENCH", "CONDUCTOR", "AGENT")
WINDOW_SEATS = ("BENCH", "CONDUCTOR")
CLOSING = ("close", "drop", "supersede")
CLOSED_STATES = ("done", "dropped", "superseded")
LEFT_OPEN_RX = re.compile(r"^[\s*_]*LEFT OPEN:", re.I)    # detached_helper.LEFT_OPEN, at the start of the note
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STREAMS = ("talk", "pipe")


# ---- the contract (pure) ----------------------------------------------------------------------------------------

def sample(streams, n=N, seed=0):
    """{name: [need] | None} -> {name: [need] | None}: n needs from each stream (all of them when it has fewer), none
    twice, kept in stream order; the same draw for the same seed and stream. None (could not read) stays None."""
    out = {}
    for name, needs in streams.items():
        if needs is None:
            out[name] = None
            continue
        needs = list(needs)
        if len(needs) <= n:
            out[name] = needs
            continue
        rng = random.Random("%s|%s" % (seed, name))
        out[name] = [needs[i] for i in sorted(rng.sample(range(len(needs)), n))]
    return out


def rates(judged):
    """{name: [verdict] | None} -> {"by_stream", "headline", "unmeasured"}. outcome and disposed follow through; moved
    and nothing do not; not_a_need leaves the count. No verdict to count -> None and named unmeasured. The headline is
    the lower rate, None while any stream is unmeasured. An unknown verdict raises ValueError."""
    by, unm = {}, []
    for name, vs in judged.items():
        if vs is None:
            by[name] = None
            unm.append(name)
            continue
        bad = [v for v in vs if v not in VERDICTS]
        if bad:
            raise ValueError("stream %s: verdict %r is not one of %s" % (name, bad[0], ", ".join(VERDICTS)))
        counted = [v for v in vs if v != "not_a_need"]
        if not counted:
            by[name] = None
            unm.append(name)
            continue
        by[name] = sum(1 for v in counted if v in FOLLOWED) / float(len(counted))
    headline = None if (unm or not by) else min(by.values())
    return {"by_stream": by, "headline": headline, "unmeasured": unm}


def hands_off(items):
    """[{closed, window_acts}] -> {"share", "closed", "hands_off"}: of the closed items, the share with no act by the
    Conductor window. An unreadable count (None) makes the share None; no closed item is None, never 0."""
    closed = [i for i in items if i.get("closed")]
    ho = sum(1 for i in closed if i.get("window_acts") == 0)
    if not closed or any(i.get("window_acts") is None for i in closed):
        return {"share": None, "closed": len(closed), "hands_off": ho}
    return {"share": ho / float(len(closed)), "closed": len(closed), "hands_off": ho}


def window_act(ev):
    """-> True when the event was the Conductor window's hands, False when a launched run's, another seat's or his own,
    None when it names no seat (could not read)."""
    if str(ev.get("role_unit") or "").strip():
        return False
    hands = str(ev.get("ranBy") or "").strip().upper()
    if hands:
        return hands in WINDOW_HANDS
    seat = str(ev.get("seat") or "").strip().upper()
    if not seat:
        return None
    return seat in WINDOW_SEATS


def week(date):
    """'YYYY-MM-DD' -> (lo, hi) epochs: 00:00 Pacific seven days before the date, and 00:00 Pacific on it."""
    if not isinstance(date, str) or not DATE_RX.match(date):
        raise ValueError("week-ending %r is not YYYY-MM-DD" % (date,))
    if PAC is None:
        raise ValueError("no time-zone database: the Pacific week cannot be placed")
    d = dt.date.fromisoformat(date)
    hi = dt.datetime(d.year, d.month, d.day, tzinfo=PAC).timestamp()
    s = d - dt.timedelta(days=7)
    lo = dt.datetime(s.year, s.month, s.day, tzinfo=PAC).timestamp()
    return lo, hi


def latest_sunday(now=None):
    d = dt.datetime.fromtimestamp(time.time() if now is None else now, PAC).date()
    return (d - dt.timedelta(days=(d.weekday() + 1) % 7)).isoformat()


def pac(t):
    if t is None:
        return "(no time)"
    d = dt.datetime.fromtimestamp(t, PAC)
    return "%s %s %s" % (d.strftime("%Y-%m-%d"), d.strftime("%I:%M %p").lstrip("0"), d.strftime("%Z"))


def _t(e):
    if "_ts" in e:
        return e["_ts"]
    import seat_restart as SR
    return SR._ts(e.get("ts"))


def _order(e):
    """Sort key: an event with no readable time sorts first (it is placed in no week; see each reader)."""
    t = _t(e)
    return (float("-inf") if t is None else t, e.get("tsn") if e.get("tsn") is not None else 0)


def _after(e, t0):
    """An event at or after t0. An event with no readable time is never placed after anything."""
    t = _t(e)
    return t is not None and t >= t0


def _ref(e):
    return "%s:%s" % (e.get("_shard") or e.get("seat") or "?", e.get("tsn") or e.get("ts") or "?")


# ---- the streams ------------------------------------------------------------------------------------------------

def pipe_needs(events, lo, hi):
    """-> one need per item: its first note in [lo, hi) whose text starts LEFT OPEN:, oldest first."""
    seen = {}
    for e in sorted(events, key=_order):
        if e.get("event") != "note" or not e.get("id"):
            continue
        t = _t(e)
        if t is None or not (lo <= t < hi):
            continue
        text = str(e.get("text") or "")
        if not LEFT_OPEN_RX.match(text) or e["id"] in seen:
            continue
        seen[e["id"]] = {"id": "pipe:%s" % e["id"], "item": e["id"], "ts": t, "when": pac(t), "ref": _ref(e),
                         "text": text}
    return list(seen.values())


PROBE = os.path.join(REPO, "src", "RimMandrake", "Utils", "probe_his_words.py")


def machine_rx():
    """-> the probe's MACHINE rule (probe_his_words.py): text that a program sent into the window (a wake or restart
    prompt, a /command, a task notification), not his typing. The wake's reader keeps these; the audit drops them."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("probe_his_words", PROBE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MACHINE


def _conductor_cfg():
    import seat_restart as SR
    return SR.config(SR._schedule()).get(SEAT)


def talk_needs(lo, hi, cfg=None, now_paths=None):
    """-> (needs, cause, notes): his typed messages in [lo, hi) in the Conductor window's transcripts, read by the
    wake's own reader. (None, cause, notes) when nothing could be read; ([], None, notes) when he typed nothing."""
    import wake_words as WW
    cfg = cfg if cfg is not None else _conductor_cfg()
    if not cfg:
        return None, "the restart schedule names no Conductor seat %s (seat_restart off?)" % SEAT, []
    try:
        machine = machine_rx()
    except Exception as e:                                   # noqa: BLE001 - could not look, said by name
        return None, "the machine-text rule %s cannot be read (%s: %s)" % (PROBE, type(e).__name__, e), []
    try:
        paths = now_paths if now_paths is not None else WW.window_transcripts(cfg, lo)
    except WW.Unmeasured as e:
        return None, str(e), []
    if not paths:
        return None, "no transcript of a %s window was written since %s" % (cfg.get("session_name"), pac(lo)), []
    msgs, blind = WW.typed_since(paths, lo)
    if blind and len([b for b in blind if b.endswith(": unreadable")]) == len(paths):
        return None, "no Conductor window transcript could be read (%d tried)" % len(paths), blind
    notes = list(blind)
    untimed = [m for m in msgs if m["ts"] is None]
    if untimed:
        notes.append("%d typed messages carry no time and are not placed in the week" % len(untimed))
    sent = [m for m in msgs if machine.match((m["text"] or "").strip())]
    if sent:
        notes.append("%d messages are machine text (a wake prompt, a /command), not his typing, and are left out"
                     % len(sent))
    needs = [{"id": "talk:%s:%d" % (m["window"], int(m["ts"])), "ts": m["ts"], "when": pac(m["ts"]),
              "window": m["window"], "text": m["text"]}
             for m in msgs if m["ts"] is not None and lo <= m["ts"] < hi and m not in sent]
    return needs, None, notes


# ---- beside the headline ----------------------------------------------------------------------------------------

def _by_item(events):
    out = {}
    for e in events:
        if e.get("id"):
            out.setdefault(e["id"], []).append(e)
    for v in out.values():
        v.sort(key=_order)
    return out


def window_load(events, lo, hi):
    """-> {"acts", "unreadable"}: events on an item in [lo, hi) by the Conductor window's hands."""
    acts = unr = 0
    for e in events:
        t = _t(e)
        if not e.get("id") or t is None or not (lo <= t < hi):
            continue
        w = window_act(e)
        if w is None:
            unr += 1
        elif w:
            acts += 1
    return {"acts": acts, "unreadable": unr}


def closed_items(events, lo, hi, world):
    """-> [{"id", "closed": True, "window_acts", "closed_by"}] for each item now closed whose closing event lies in
    [lo, hi). window_acts counts the window's events after the item's first file event up to that close; None when
    one of them names no seat."""
    out = []
    for iid, evs in _by_item(events).items():
        it = world.items.get(iid)
        if it is None or it.state not in CLOSED_STATES:
            continue
        ends = [e for e in evs if e.get("event") in CLOSING]
        if not ends:
            continue
        end = ends[-1]
        te = _t(end)
        if te is None or not (lo <= te < hi):
            continue
        files = [i for i, e in enumerate(evs) if e.get("event") == "file"]
        start = files[0] + 1 if files else 0
        upto = evs.index(end) + 1
        kinds = [window_act(e) for e in evs[start:upto]]
        acts = None if any(k is None for k in kinds) else sum(1 for k in kinds if k)
        out.append({"id": iid, "closed": True, "window_acts": acts,
                    "closed_by": end.get("role_unit") or end.get("ranBy") or end.get("seat")})
    return sorted(out, key=lambda r: r["id"])


def debts(world, now):
    """-> {"count", "rows"} | {"unmeasured"}: the Conductor's open owed items ripe over a day (owed.split's actionable
    ones; ripe at the later of the filing and a passed wait's date)."""
    try:
        from rimflow import model, owed
        act, _ = owed.split(world, SEAT, now)
    except Exception as e:                                   # noqa: BLE001 - said, never 0
        return {"unmeasured": "owed.split failed (%s: %s)" % (type(e).__name__, e)}
    rows = []
    for it in act:
        t0 = model.iso_epoch(it.created_at) if it.created_at else None
        tw = model.iso_epoch(it.wait_until) if it.wait_until else None
        if t0 is None:
            rows.append({"id": it.id, "age": "unknown", "title": it.title or ""})
            continue
        ripe = max(t0, tw) if (tw is not None and tw <= now) else t0
        if now - ripe > RIPE_S:
            rows.append({"id": it.id, "age": "%.1fd" % ((now - ripe) / 86400.0), "title": it.title or ""})
    return {"count": len(rows), "rows": rows}


def waits_past(world, events, now):
    """-> {"count", "of", "rows"}: of the open items with a dated wait, those whose date passed with no event on the
    item since. An event with no readable time on such an item counts as a look (the count never grows on a blind
    read); `untimed` says how many items had one."""
    try:
        from rimflow import model
    except Exception as e:                                   # noqa: BLE001
        return {"unmeasured": "model cannot be imported (%s)" % e}
    by = _by_item(events)
    waited = [it for it in world.items.values() if it.open and it.wait_until]
    rows, untimed = [], 0
    for it in sorted(waited, key=lambda i: i.id):
        tw = model.iso_epoch(it.wait_until)
        if tw is None or tw > now:
            continue
        evs = by.get(it.id, [])
        if any(_t(e) is None for e in evs):
            untimed += 1
            continue
        if not any(_t(e) > tw for e in evs):
            rows.append({"id": it.id, "until": str(it.wait_until)[:10], "reason": it.wait_reason or ""})
    return {"count": len(rows), "of": len(waited), "rows": rows, "untimed": untimed}


def homeless(events, now, cfg=None, now_paths=None):
    """-> {"count", "of", "rows"} | {"unmeasured"}: his typed messages of the last HOMELESS_S with no home, by the
    wake's rule (wake_words.home_of: QUOTED is a home; ECHOED is not)."""
    import wake_words as WW
    lo = now - HOMELESS_S
    msgs, cause, notes = talk_needs(lo, now + 1, cfg, now_paths)
    if msgs is None:
        return {"unmeasured": cause}
    rows = []
    win = [e for e in events if _after(e, lo - WW.MATCH_BEFORE_S)]
    for m in msgs:
        t = m["ts"] - WW.MATCH_BEFORE_S
        said = [(e, WW.norm(e["ownerSaid"])) for e in win if e.get("ownerSaid") and _after(e, t)]
        echoes = [(e, WW.norm(" ".join(str(e.get(k) or "") for k in WW.ECHO_FIELDS))) for e in win if _after(e, t)]
        kind, _ = WW.home_of(WW.norm(m["text"]), said, echoes)
        if kind != "QUOTED":
            rows.append({"when": m["when"], "window": m["window"], "echoed": kind == "ECHOED", "text": m["text"]})
    return {"count": len(rows), "of": len(msgs), "rows": rows, "notes": notes}


def planted_id(date):
    return "RIMMANDRAKE_PLANT_WEEKLY_NEED_%s_WATCHED_FROM_OUTSIDE" % date.replace("-", "")


def reader_id(date):
    return "RIMMANDRAKE_READ_FOLLOW_THROUGH_SAMPLE_%s_FRESH_EYES" % date.replace("-", "")


def planted_path(date):
    return os.path.join(AUDIT_DIR, "planted", "%s.md" % date)


def planted_token(date):
    return "planted need %s answered" % date


def planted_reading(world, events, iid, runs=None):
    """-> what happened to one planted need, read from outside: state, closed when and by whom, window acts after its
    filing, runs launched on it. {"unmeasured": "not filed"} when it is not on the ledger."""
    it = world.items.get(iid)
    if it is None:
        return {"id": iid, "unmeasured": "not filed"}
    evs = _by_item(events).get(iid, [])
    files = [e for e in evs if e.get("event") == "file"]
    t0 = _t(files[0]) if files else None
    after = evs[evs.index(files[0]) + 1:] if files else evs
    kinds = [window_act(e) for e in after]
    out = {"id": iid, "state": it.state, "filed": pac(t0), "window_acts":
           None if any(k is None for k in kinds) else sum(1 for k in kinds if k), "runs": runs}
    ends = [e for e in evs if e.get("event") in CLOSING]
    if it.state in CLOSED_STATES and ends:
        te = _t(ends[-1])
        out.update({"closed": pac(te), "closed_by": ends[-1].get("role_unit") or ends[-1].get("ranBy") or
                    ends[-1].get("seat"), "hours": None if (te is None or t0 is None) else round((te - t0) / 3600.0, 1)})
    return out


# ---- the record and the page ------------------------------------------------------------------------------------

def _root(root):
    return root or os.environ.get("RM_FOLLOW_THROUGH_ROOT") or REPO     # the override is the selftest's scratch tree


def record_path(date, root=None):
    return os.path.join(_root(root), AUDIT_DIR, "%s.json" % date)


def page_path(date, root=None):
    return os.path.join(_root(root), AUDIT_DIR, "%s.md" % date)


def seed_of(date):
    return "follow-through:%s" % date


def _world_and_events(root=None):
    import wake_words as WW
    led = WW.Ledger(root or REPO)
    from rimflow import model as M
    return M.replay(), led.events, led.bad


def _runs_on(iid):
    try:
        import detached_helper as DH
        recs = [r for r in DH.all_records() if r.get("item") == iid]
        return {"n": len(recs), "live": [r["unit"] for r in recs if DH.live_status(r) in ("launching", "running")]}
    except Exception as e:                                   # noqa: BLE001
        return {"n": None, "live": None, "why": "%s: %s" % (type(e).__name__, e)}


def draw(date, root=None, now=None, cfg=None, now_paths=None, world=None, events=None):
    """-> the week's record: the sample of each stream and every reading beside it, with no verdict yet."""
    now = time.time() if now is None else now
    lo, hi = week(date)
    if world is None or events is None:
        world, events, bad = _world_and_events(root)
    else:
        bad = []
    talk, tcause, tnotes = talk_needs(lo, hi, cfg, now_paths)
    pipe = pipe_needs(events, lo, hi)
    streams = {"talk": talk, "pipe": pipe}
    drawn = sample(streams, N, seed_of(date))
    closed = closed_items(events, lo, hi, world)
    return {
        "week_ending": date, "week": [pac(lo), pac(hi)], "read_at": pac(now), "seed": seed_of(date), "n": N,
        "streams": {s: (None if drawn[s] is None else [dict(x, verdict=None, evidence="") for x in drawn[s]])
                    for s in STREAMS},
        "sizes": {s: (None if streams[s] is None else len(streams[s])) for s in STREAMS},
        "unreadable": {s: c for s, c in (("talk", tcause),) if c},
        "notes": {"talk": tnotes, "ledger": bad},
        "load": window_load(events, lo, hi),
        "hands_off": hands_off(closed), "closed_items": closed,
        "debts": debts(world, now), "waits": waits_past(world, events, now),
        "homeless": homeless(events, now, cfg, now_paths),
        "planted": planted_reading(world, events, planted_id(date), _runs_on(planted_id(date))["n"]),
        "rates": None,
    }


def judged_lists(rec):
    return {s: (None if rec["streams"].get(s) is None else [x.get("verdict") for x in rec["streams"][s]])
            for s in STREAMS}


def _pct(x):
    return "UNMEASURED (not judged yet)" if x is None else "%.0f%%" % (100 * x)


def render(rec):
    """-> the page text. A stream that could not be read says UNMEASURED with its cause; a rate not judged says so."""
    r = rec.get("rates")
    L = ["# Follow-through audit, week ending %s" % rec["week_ending"], "",
         "The week: %s to %s. Drawn at %s with seed `%s`, %d needs per stream. Page: "
         "`design/specs/2026-11-23-follow-through-audit/boundary.md`." % (rec["week"][0], rec["week"][1], rec["read_at"],
                                                                         rec["seed"], rec["n"]), "",
         "## Headline: follow-through without the owner", ""]
    for s, label in (("talk", "his talk (typed words in the Conductor window)"),
                     ("pipe", "the pipeline (run ends with a `LEFT OPEN:` next act)")):
        size = rec["sizes"].get(s)
        if size is None:
            L.append("- **%s**: UNMEASURED: %s" % (label, rec["unreadable"].get(s, "could not be read")))
            continue
        rate = r["by_stream"].get(s) if r else None
        shown = ("UNMEASURED (no drawn need was a need)" if r and s in r.get("unmeasured", []) else _pct(rate))
        L.append("- **%s**: %s of %d drawn (from %d needs in the week)" % (label, shown, len(rec["streams"][s]), size))
    L.append("- **Headline (the lower rate)**: %s" % (_pct(r["headline"]) if r else "UNMEASURED (not judged yet)"))
    if r and r.get("unmeasured"):
        L.append("- Unmeasured streams: %s" % ", ".join(r["unmeasured"]))
    ho, ld = rec["hands_off"], rec["load"]
    L += ["", "## The Conductor's load", "",
          "- The Conductor window's acts on items in the week: %d (%d events name no seat)." % (ld["acts"],
                                                                                              ld["unreadable"]),
          "- Items closed in the week with no act by the window: %s (%d of %d closed)." % (
              "UNMEASURED (an act could not be read)" if ho["share"] is None and ho["closed"] else
              ("none closed" if not ho["closed"] else "%.0f%%" % (100 * ho["share"])), ho["hands_off"], ho["closed"])]
    L += ["", "## Beside it, the same evening", ""]
    for key, label in (("debts", "Conductor debts ripe over a day and still open"),
                       ("waits", "Waits past their date with no event since"),
                       ("homeless", "His typed messages of the last 3 days with no home")):
        b = rec[key]
        if "unmeasured" in b:
            L.append("- %s: UNMEASURED: %s" % (label, b["unmeasured"]))
        else:
            L.append("- %s: %d%s" % (label, b["count"], (" of %d" % b["of"]) if "of" in b else ""))
    p = rec["planted"]
    L.append("- The week's planted need (`%s`, filed a week before): %s" % (p["id"], "UNMEASURED: " + p["unmeasured"]
             if "unmeasured" in p else "%s; %s window acts; %s runs%s" % (
                 p["state"], p["window_acts"], p["runs"], ("; closed %s by %s after %s h" % (
                     p["closed"], p["closed_by"], p["hours"])) if p.get("closed") else "")))
    for s in STREAMS:
        rows = rec["streams"].get(s)
        L += ["", "## The %s sample" % s, ""]
        if rows is None:
            L.append("UNMEASURED: %s" % rec["unreadable"].get(s, "could not be read"))
            continue
        if not rows:
            L.append("Looked: no need started in this stream in the week.")
        for x in rows:
            L.append("- `%s` %s: **%s** %s" % (x["id"], x["when"], x.get("verdict") or "not judged",
                                              ("(%s)" % x["evidence"]) if x.get("evidence") else ""))
            L.append("")
            L += ["    > " + ln for ln in str(x["text"]).splitlines() or [""]]
            L.append("")
    for key, label in (("debts", "Debts ripe over a day"), ("waits", "Waits past their date"),
                       ("homeless", "Typed messages with no home")):
        b = rec[key]
        if b.get("rows"):
            L += ["", "## %s" % label, ""]
            cls = rec.get("debt_classes") or {} if key == "debts" else {}
            for row in b["rows"]:
                L.append("- " + "; ".join("%s: %s" % (k, str(v).replace("\n", " ")) for k, v in row.items()) +
                         ("  **%s**" % cls[row["id"]] if row.get("id") in cls else ""))
    if rec.get("findings"):
        L += ["", "## The reader's findings (each with its filed item)", ""] + ["- %s" % f for f in rec["findings"]]
    return "\n".join(L) + "\n"


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def _read_record(date, root=None):
    with open(record_path(date, root), encoding="utf-8") as f:
        return json.load(f)


def has_verdict(rec):
    return any(x.get("verdict") for s in STREAMS for x in (rec.get("streams", {}).get(s) or []))


def judged(date, root=None):
    """-> (rc, text): 0 every drawn need has a verdict and evidence and the page states the rates computed now; 1 one
    of these fails (named); 2 the record cannot be read."""
    p = record_path(date, root)
    if not os.path.exists(p):
        return 1, "no record at %s: run follow_through.py sample --week-ending %s --write" % (p, date)
    try:
        rec = _read_record(date, root)
    except (OSError, ValueError) as e:
        return 2, "the record %s cannot be read (%s: %s)" % (p, type(e).__name__, e)
    missing = ["%s %s" % (s, x.get("id")) for s in STREAMS for x in (rec["streams"].get(s) or [])
               if x.get("verdict") not in VERDICTS or not str(x.get("evidence") or "").strip()]
    if missing:
        return 1, "%d drawn needs lack a verdict of %s or an evidence line: %s" % (len(missing), "/".join(VERDICTS),
                                                                                ", ".join(missing))
    try:
        now = rates(judged_lists(rec))
    except ValueError as e:
        return 1, str(e)
    if rec.get("rates") != now:
        return 1, "the record's rates are not the rates of its verdicts: run follow_through.py rates --week-ending %s " \
                  "--write" % date
    try:
        with open(page_path(date, root), encoding="utf-8") as f:
            page = f.read()
    except OSError as e:
        return 1, "no page at %s (%s)" % (page_path(date, root), type(e).__name__)
    if page != render(rec):
        return 1, "the page is not the record's: run follow_through.py rates --week-ending %s --write" % date
    return 0, "judged: headline %s" % _pct(now["headline"])


# ---- the tick: file the reader item and the planted need, launch the reader -----------------------------------------

def _cli(args, apply):
    argv = [sys.executable, os.path.join(RIMFLOW, "cli.py")] + args + ["--seat", SEAT, "--publish"]
    if not apply:
        return 0, "would run: " + " ".join(argv[1:])
    env = dict(os.environ, RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT, RIMFLOW_SEAT=SEAT,
               RM_FILING_PROGRAM="follow_through._cli")     # filing_gate.py: the program files its plant and reader
    for k in ("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID"):     # never a window's session
        env.pop(k, None)
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, timeout=CLI_TIMEOUT_S,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def _gates(iid, now):
    try:
        import pipeline_pause as PP
        if PP.blocks(None, now):
            return "the pipeline is paused"
        import control as C
        b = C.blocked({"family": FAMILY, "item": iid})
        if b:
            return "pipe off: %s" % (b,)
        import maturation_dispatch as MD
        go, why = MD.account_gate()
        if not go:
            return why
    except Exception as e:                                   # noqa: BLE001 - a gate that cannot look holds
        return "a gate could not be read (%s: %s)" % (type(e).__name__, e)
    return None


def plan_tick(date, world, runs, gate):
    """-> [(action, detail)]: what one tick does for the week ending `date`. Pure. runs: {"n", "live"} on the reader."""
    if date < FIRST_WEEK:
        return [("not_yet", "the first audit is the week ending %s" % FIRST_WEEK)]
    acts = []
    nxt = next_week(date)
    if planted_id(nxt) not in world.items:
        acts.append(("plant", nxt))
    rid = reader_id(date)
    if rid not in world.items:
        acts.append(("file_reader", rid))
        state = "ready"
    else:
        state = world.items[rid].state
    if state in CLOSED_STATES:
        acts.append(("reader_done", rid))
    elif runs.get("n") is None:
        acts.append(("blind", "the run records cannot be read"))
    elif runs["live"]:
        acts.append(("reader_live", ", ".join(runs["live"])))
    elif runs["n"]:
        acts.append(("reader_ran", "%d run(s) ended with the item open: the Workshop Pipeline works it now" % runs["n"]))
    elif gate:
        acts.append(("held", gate))
    else:
        acts.append(("launch", rid))
    return acts


def next_week(date):
    return (dt.date.fromisoformat(date) + dt.timedelta(days=7)).isoformat()


def plant(date, apply, cli=None):
    """File the planted need that the audit of the week ending `date` reads: a harmless item with an outcome check,
    worked by the Workshop Pipeline like any other. -> (rc, text)."""
    return (cli or _cli)(["file", planted_id(date), "--for", SEAT, "--kind", "task", "--title",
                          "Planted need of the follow-through audit, week ending %s: write %s holding the line '%s', "
                          "land it with ./publish, close this item with its sha" % (date, planted_path(date),
                                                                                     planted_token(date)),
                          "--effect", "path-has:%s::%s" % (planted_path(date), planted_token(date)),
                          "--caused-by", ITEM, "--why", "the weekly planted need, watched from outside by the audit "
                          "of %s (plan.md §Where I push back)" % date], apply)


def _brief(date, rid):
    with open(BRIEF, encoding="utf-8") as f:
        return f.read().format(date=date, item=rid, page=os.path.join(AUDIT_DIR, "%s.md" % date),
                               record=os.path.join(AUDIT_DIR, "%s.json" % date), verdicts=", ".join(VERDICTS))


def tick(apply=False, date=None, now=None, fx=None):
    """One beat. Without apply: prints what it would do and writes nothing but its reading."""
    now = time.time() if now is None else now
    fx = fx or {}
    date = date or latest_sunday(now)
    world = fx["world"] if "world" in fx else _world_and_events()[0]
    rid = reader_id(date)
    runs = fx["runs"] if "runs" in fx else _runs_on(rid)
    gate = fx["gate"] if "gate" in fx else _gates(rid, now)
    cli = fx.get("cli", _cli)
    out = []
    for act, detail in plan_tick(date, world, runs, gate):
        rc, text = 0, detail
        if act == "plant":
            rc, text = plant(detail, apply, cli)
        elif act == "file_reader":
            rc, text = cli(["file", rid, "--for", SEAT, "--kind", "task", "--title",
                            "Read the follow-through sample of the week ending %s with fresh eyes: one verdict per "
                            "drawn need, then the two rates" % date,
                            "--effect", "cmd:python3 src/RimMandrake/Utils/follow_through.py judged --week-ending %s"
                            % date, "--caused-by", ITEM, "--why", "the weekly follow-through audit (plan.md step 5)"],
                           apply)
        elif act == "launch":
            rc, text = (fx.get("launch") or launch)(date, rid, apply)
        out.append({"action": act, "detail": detail, "rc": rc, "out": text})
    reading = {"ts": now, "at": pac(now), "week_ending": date, "apply": apply, "actions": out}
    if fx.get("reading_path") is not False:
        _write(fx.get("reading_path") or reading_path(), json.dumps(reading, indent=1))
    return reading


def reading_path():
    d = os.environ.get("RM_FOLLOW_THROUGH_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), FAMILY)
    return os.path.join(d, "reading.json")


def launch(date, rid, apply):
    import tempfile
    brief = _brief(date, rid)
    if not apply:
        return 0, "would launch one opus reader on %s" % rid
    d = os.path.join(os.path.dirname(reading_path()), "briefs")
    os.makedirs(d, exist_ok=True)
    fd, path = tempfile.mkstemp(prefix="%s-" % rid, suffix=".md", dir=d)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(brief)
    argv = [sys.executable, os.path.join(RIMFLOW, "detached_helper.py"), "launch", "--by-program", "follow_through", "--seat", SEAT, "--item", rid,
            "--brief-file", path, "--model", "opus", "--budget-usd", "%g" % READER_CAP_USD]
    try:
        r = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=LAUNCH_TIMEOUT_S,
                           stdin=subprocess.DEVNULL, errors="replace")
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


# ---- the command line -------------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("sample", "rates", "judged", "tick", "plant"):
        p = sub.add_parser(name)
        p.add_argument("--week-ending", default=None)
        if name != "judged":
            p.add_argument("--apply" if name in ("tick", "plant") else "--write", action="store_true")
    a = ap.parse_args(argv)
    date = a.week_ending or latest_sunday()
    try:
        week(date)
    except ValueError as e:
        print("REFUSED: %s" % e)
        return 2
    if a.cmd == "tick":
        r = tick(apply=a.apply, date=a.week_ending)
        for x in r["actions"]:
            print("%s  %s  rc=%s  %s" % ("APPLY" if a.apply else "DRY", x["action"], x["rc"], x["detail"]))
        return 0 if all(x["rc"] == 0 for x in r["actions"]) else 1
    if a.cmd == "plant":
        rc, text = plant(date, a.apply)
        print(text)
        return 0 if rc == 0 else 1
    if a.cmd == "judged":
        rc, text = judged(date)
        print(("HOLDS " if rc == 0 else "FAILS " if rc == 1 else "UNMEASURED ") + text)
        return rc
    if a.cmd == "sample":
        p = record_path(date)
        if a.write and os.path.exists(p):
            try:
                old = _read_record(date)
            except (OSError, ValueError) as e:
                print("UNMEASURED: the record %s exists and cannot be read (%s); move it aside by hand" % (p, e))
                return 2
            if has_verdict(old):
                print("REFUSED: %s already holds verdicts; a new draw would destroy them. Judge on it, or move it "
                      "aside by hand and draw again" % p)
                return 3
        try:
            rec = draw(date)
        except Exception as e:                               # noqa: BLE001 - could not look, said by name
            print("UNMEASURED: the draw failed (%s: %s)" % (type(e).__name__, e))
            return 2
        text = render(rec)
        if a.write:
            _write(p, json.dumps(rec, indent=1, ensure_ascii=False))
            _write(page_path(date), text)
            print("WROTE %s and %s" % (p, page_path(date)))
        else:
            print(text)
        return 0
    # rates
    try:
        rec = _read_record(date)
    except (OSError, ValueError) as e:
        print("UNMEASURED: the record %s cannot be read (%s)" % (record_path(date), e))
        return 2
    try:
        rec["rates"] = rates(judged_lists(rec))
    except ValueError as e:
        print("FAILS: %s" % e)
        return 1
    text = render(rec)
    if a.write:
        _write(record_path(date), json.dumps(rec, indent=1, ensure_ascii=False))
        _write(page_path(date), text)
        print("WROTE rates: headline %s" % _pct(rec["rates"]["headline"]))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
