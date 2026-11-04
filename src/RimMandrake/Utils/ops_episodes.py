#!/usr/bin/env python3
"""ops_episodes: the episodes list and the judge's graded notes, step 7 of
design/RimMandrake/operations_metronome_strategy_2026-11-02.md (§3, OPS_JUDGE_NOTES_MEASURE_VS_NO_CHANGE).

Both are written by ops_memory.py publish, into the same generation as memory.md (two sections on the page), and
gather nothing new: reading episodes come from the generations ops_memory builds, incident episodes from told.jsonl.

EPISODES (14 d). What happened, not samples:
  outside / blind   a reading left its band (or went blind) and, maybe, came back; kept across generations in
                    episodes.json, because one generation sees only "now"
  step              a reading moved to a new level and stayed (ops_memory keeps the step); it closes when the step
                    leaves the 7-day window
  incident          an incident of one cause opened, relapsed or reopened, and closed (told.jsonl, read whole)
  Repeats fold: one line per (subject, kind) with a count, so a reading that flaps every minute takes one line. An
  OPEN episode is never evicted and never cut from the page; a closed one is evicted 14 d after it closed. The page
  says how many lines it cut. Deaths and lives have no source yet (the register of lives is step 3): the page says so.
  A blind store generation does not move a reading episode: open ones stay open, marked unread; a reading going blind
  is not a recovery either. Reading episodes are sampled at each generation, and ops_memory builds one after every
  ops_watch pass, so the generation IS the reading's sample (a pass skipped is an excursion unseen, never a fake one).

JUDGE NOTES. At the end of a run Operations may leave up to 10 typed notes (one run tag):
  reading  a key memory.json holds (never a guessed one); its value now is recorded as v0
  cmp      < <= > >= == !=      value  a number (a flag: 0 or 1; a counter: its rate per hour, as the page shows it)
  deadline an ISO time or +Nh / +Nm from now      mode  at (the reading at the deadline) | before (at any point until)
  Graded once, after the deadline (a `before` note holds early the moment a measured sample satisfies it):
    held | missed | ungradable (no fresh measured reading: within the reading's staleness either side of the deadline
    for `at`, none at all in the window for `before`)
  The score is shown beside ASSUMING NO CHANGE: that forecaster says a note holds iff its condition is already true
  of v0; it scores a point where that agrees with what happened. Ten notes that only restate today score the same as
  no change. "Foresaw" counts notes that held while no change said they would not. Each run's line also counts the
  incidents open when the notes were written that no note names (by one of its metrics, or --incident from a note on
  the same family: naming an incident from an unrelated reading covers nothing), so ten easy notes cannot look like
  understanding. v0 must come from a memory generation under 30 min old; a deadline is at most 14 d ahead.

Files, in ops_watch's dir: episodes.json (state, ops_memory only), judge_notes.jsonl (append-only, the judge),
judge_grades.json (ops_memory only; a grade is final once written).

Usage:
  python3 ops_episodes.py note --run TAG --reading KEY --cmp '<' --value 5 --deadline +6h [--mode at|before]
                               [--incident ID] [--why TEXT]
  python3 ops_episodes.py notes            # the graded section as the page shows it
"""
import argparse
import calendar
import fcntl
import json
import math
import operator
import os
import re
import sys
import time
from pathlib import Path

H = 3600.0
WINDOW_D = 14
NOTES_PER_RUN = 10
PENDING_MAX = 30            # unbounded writers are a leak; 3 runs' worth waiting is plenty
MEMORY_MAX_AGE_S = 1800.0   # v0 comes from a generation no older than ops_memory check accepts
GRACE_S = 1800.0            # an `at` note waits this long past its deadline for a reading taken just after it
STALE_FLOOR_S = 1800.0
EPISODE_LINES = 40
GRADE_LINES = 12
CMPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq,
        "!=": operator.ne}
NO_SOURCE = ("death", "relapse of a life")      # step 3 (register of lives) is not built


def ops_dir():
    return Path(os.environ.get("RM_OPS_WATCH_DIR") or "/mnt/d/ClaudeWork/rimmandrake/ops_watch")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def short(t):
    return time.strftime("%m-%d %H:%M", time.localtime(t))


def atomic_json(p, obj):
    p = Path(p)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)


def read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


# ======================================================================================================== episodes
def _open(eps, subject, kind, t, detail):
    e = eps.get("%s|%s" % (subject, kind))
    if e is None:
        eps["%s|%s" % (subject, kind)] = {"subject": subject, "kind": kind, "first_t": t, "opened_t": t,
                                          "closed_t": None, "count": 1, "detail": detail}
    elif e["closed_t"] is not None:          # a repeat folds into the same line
        e.update(opened_t=t, closed_t=None, count=e["count"] + 1, detail=detail)
    else:
        e["detail"] = detail


def _close(eps, subject, kind, t):
    e = eps.get("%s|%s" % (subject, kind))
    if e is not None and e["closed_t"] is None:
        e["closed_t"] = t


def reading_episodes(prev, mem, now):
    """prev: the reading episodes kept so far {key: ep}; mem: this generation (ops_memory.build). -> (eps, unread).
    A store that did not answer moves nothing; every open episode is unread this generation."""
    eps = {k: dict(v) for k, v in (prev or {}).items()}
    if mem.get("store_error"):
        return eps, True
    rds = mem.get("readings") or {}
    for key, rd in rds.items():
        st = rd.get("state")
        for kind in ("outside", "blind"):
            if st == kind:
                _open(eps, key, kind, now, rd.get("why") if kind == "blind" else
                      "%s (normal %s to %s)" % (_n(rd.get("v")), _n((rd.get("band") or {}).get("lo")),
                                                 _n((rd.get("band") or {}).get("hi"))))
            elif st != "blind":     # only a fresh measured reading resolves an episode; going blind is not recovery
                _close(eps, key, kind, now)
        if st == "blind":
            continue
        step = rd.get("step")
        if step:
            sid = "%s|step" % key
            e = eps.get(sid)
            if e is None or e["closed_t"] is not None or e.get("at") != step.get("at"):
                if e is not None and e["closed_t"] is None:     # a NEW step while one is open: a repeat, counted
                    e["closed_t"] = step.get("at") or now
                _open(eps, key, "step", step.get("at") or now, "stepped from %s to %s" % (
                    _n(step.get("from")), _n(step.get("to"))))
                eps[sid]["at"] = step.get("at")
        else:
            _close(eps, key, "step", now)
    for e in eps.values():      # a reading gone from this generation is not resolved: its episode stays open, said
        if e["closed_t"] is None:
            e["absent"] = e["subject"] not in rds
    return eps, False


def incident_episodes(rows):
    """told.jsonl rows -> {cause|incident: ep}, one line per cause: opened, relapsed and reopened fold into it."""
    eps, cause_of, live_ids = {}, {}, {}
    for r in rows or []:
        if "ev" not in r or "id" not in r:
            continue
        t = r.get("t")
        if t is None:
            try:
                t = calendar.timegm(time.strptime(r.get("at", ""), "%Y-%m-%dT%H:%M:%SZ"))
            except ValueError:
                continue
        iid = r["id"]
        if r.get("cause"):
            cause_of[iid] = r["cause"]
        cause = cause_of.get(iid) or iid.rsplit("-", 1)[0]
        ev = r["ev"]
        live = live_ids.setdefault(cause, set())
        if ev in ("opened", "reopened", "relapsing"):
            e = eps.get("%s|incident" % cause)
            if e is not None and e["closed_t"] is None and (ev != "opened" or iid not in live):
                e["count"] += 1     # a relapse, or a second incident of the cause, while its episode is open
            _open(eps, cause, "incident", t, "%s %s" % (iid, ev))
            eps["%s|incident" % cause]["ids"] = sorted(set(eps["%s|incident" % cause].get("ids", [])) | {iid})
            live.add(iid)
        elif ev == "closed":
            live.discard(iid)
            if not live:            # one cause's episode closes when its last open incident does
                _close(eps, cause, "incident", t)
    return eps


def read_told(d):
    """told.jsonl rows, or None when a line does not parse (a torn ledger is said, as incident.read_rows does)."""
    try:
        with open(Path(d) / "told.jsonl", encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None


def evict(eps, now, days=WINDOW_D):
    """-> (kept, evicted count). Open episodes are never evicted."""
    keep, n = {}, 0
    for k, e in eps.items():
        if e["closed_t"] is not None and e["closed_t"] < now - days * 24 * H:
            n += 1
        else:
            keep[k] = e
    return keep, n


def update(state, mem, told_rows, now):
    """Pure. state: episodes.json as last written. -> new state: {readings, incidents, evicted, unread, written_at}."""
    state = state or {}
    rd, unread = reading_episodes(state.get("readings"), mem, now)
    rd, n1 = evict(rd, now)
    if told_rows == [] and state.get("incidents"):
        told_rows = None        # a told.jsonl gone missing is unread, never "no incidents ever": keep what was known
    inc = incident_episodes(told_rows) if told_rows is not None else (state.get("incidents") or {})
    inc, n2 = evict(inc, now)
    return {"readings": rd, "incidents": inc, "evicted": int(state.get("evicted", 0)) + n1,
            "evicted_incidents": n2, "unread": unread, "told_unread": told_rows is None, "written_at": now}


def _n(x):
    if x is None:
        return "?"
    a = abs(x)
    return "%.0f" % x if a >= 100 else "%.1f" % x if a >= 10 else "%.2f" % x if a >= 1 else "%.3g" % x


def ep_line(e, unread=False):
    if e["closed_t"] is None:
        s = "OPEN %s %s since %s" % (e["subject"], e["kind"], short(e["opened_t"]))
        if unread and e["kind"] != "incident":
            s += " (store unread this generation)"
        elif e.get("absent"):
            s += " (absent from this generation)"
    else:
        s = "%s %s %s to %s" % (e["subject"], e["kind"], short(e["opened_t"]), short(e["closed_t"]))
    if e["count"] > 1:
        s += ", %d times since %s" % (e["count"], short(e["first_t"]))
    if e.get("detail"):
        s += ": %s" % e["detail"]
    return s


def render_episodes(state, max_lines=EPISODE_LINES):
    eps = list((state.get("readings") or {}).values()) + list((state.get("incidents") or {}).values())
    opn = sorted((e for e in eps if e["closed_t"] is None), key=lambda e: e["opened_t"])
    shut = sorted((e for e in eps if e["closed_t"] is not None), key=lambda e: -e["closed_t"])
    room = max(0, max_lines - len(opn))
    cut = max(0, len(shut) - room)
    out = ["## Episodes, %d d (%d open, %d closed)" % (WINDOW_D, len(opn), len(shut))]
    if state.get("told_unread"):
        out.append("- told.jsonl did not read: incident episodes are the last ones read")
    out += ["- " + ep_line(e, state.get("unread")) for e in opn]
    out += ["- " + ep_line(e) for e in shut[:room]]
    tail = []
    if cut:
        tail.append("%d older closed lines cut (all in episodes.json)" % cut)
    if state.get("evicted"):
        tail.append("%d reading episodes evicted 14 d after closing, all time" % state["evicted"])
    tail.append("no source yet for %s (register of lives, step 3)" % " or ".join(NO_SOURCE))
    out.append("- (" + "; ".join(tail) + ")")
    return out


# ====================================================================================================== judge notes
def parse_deadline(s, now):
    m = re.fullmatch(r"\+(\d+(?:\.\d+)?)([hm])", s.strip())
    if m:
        return now + float(m.group(1)) * (H if m.group(2) == "h" else 60.0)
    for f in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%MZ"):
        try:
            return float(calendar.timegm(time.strptime(s.strip(), f)))
        except ValueError:
            pass
    raise ValueError("--deadline: an ISO UTC time (2026-11-05T12:00Z) or +Nh / +Nm, not %r" % s)


def read_notes(path=None):
    p = Path(path) if path else ops_dir() / "judge_notes.jsonl"
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    out = []
    for x in lines:
        if x.strip():
            try:
                out.append(json.loads(x))
            except ValueError:
                continue        # a torn last line from a writer killed mid-append: the rest stand
    return out


def add_note(run, reading, cmp, value, deadline, mode="at", incident=None, why=None, by="Operations",
             memory=None, incidents=None, now=None, d=None):
    """Validate against the current memory generation and append one note. -> the note. Raises ValueError."""
    now = time.time() if now is None else now
    d = Path(d) if d else ops_dir()
    if cmp not in CMPS:
        raise ValueError("--cmp: one of %s" % " ".join(CMPS))
    if mode not in ("at", "before"):
        raise ValueError("--mode: at | before")
    if not (run or "").strip():
        raise ValueError("--run: the run's tag (the same for every note of one run)")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("--value must be finite")
    dl = parse_deadline(deadline, now) if isinstance(deadline, str) else float(deadline)
    if dl <= now:
        raise ValueError("--deadline is not in the future")
    if dl > now + WINDOW_D * 24 * H:
        raise ValueError("--deadline more than %d d ahead would leave the scoreboard before it is graded" % WINDOW_D)
    mem = memory if memory is not None else read_json(d / "memory.json", {})
    age = now - float(mem.get("written_at") or 0)
    if age > MEMORY_MAX_AGE_S:
        raise ValueError("memory.json generation %s is %.0f min old: v0 would be a stale baseline (run ops_memory.py "
                         "build)" % (mem.get("generation"), age / 60.0))
    rd = (mem.get("readings") or {}).get(reading)
    if rd is None:
        raise ValueError("%s: not a reading in memory.json generation %s (never guess a key)" % (
            reading, mem.get("generation")))
    v0 = rd.get("v", rd.get("last"))
    if rd.get("state") == "blind" or v0 is None:
        raise ValueError("%s is blind now (%s): a note against it could only be ungradable" % (reading, rd.get("why")))
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "judge_notes.lock", "w") as lk:     # check, number and append under one lock: no shared id
        fcntl.flock(lk, fcntl.LOCK_EX)
        return _append_note(d, run, by, now, reading, rd, cmp, value, dl, mode, v0, incident, why, incidents)


def _append_note(d, run, by, now, reading, rd, cmp, value, dl, mode, v0, incident, why, incidents):
    notes = read_notes(d / "judge_notes.jsonl")
    graded = read_json(d / "judge_grades.json", {})
    if sum(1 for n in notes if n.get("run") == run) >= NOTES_PER_RUN:
        raise ValueError("run %s already left %d notes, the most one run may" % (run, NOTES_PER_RUN))
    if sum(1 for n in notes if n.get("id") not in graded) >= PENDING_MAX:
        raise ValueError("%d notes are still waiting for their deadlines" % PENDING_MAX)
    snap = incidents if incidents is not None else read_json(d / "incidents.json", {})
    open_inc = [{"id": i.get("id"), "metrics": sorted(set([i.get("metric")] + list(i.get("metrics") or {})) - {None})}
                for i in (snap.get("open") or []) if isinstance(i, dict)]
    note = {"id": "%s#%d" % (run, sum(1 for n in notes if n.get("run") == run) + 1), "run": run, "by": by,
            "written_t": now, "written": iso(now), "reading": reading, "kind": rd.get("kind"), "cmp": cmp,
            "value": value, "deadline_t": dl, "deadline": iso(dl), "mode": mode, "v0": v0,
            "incident": incident, "why": why, "open_incidents": open_inc, "v0_t": rd.get("t")}
    p = d / "judge_notes.jsonl"
    torn = p.exists() and p.stat().st_size > 0 and not p.read_bytes().endswith(b"\n")
    with open(p, "a", encoding="utf-8") as f:
        if torn:            # end a torn tail first, or it swallows this note; the torn line stays unparsed and skipped
            f.write("\n")
        f.write(json.dumps(note, sort_keys=True) + "\n")
    return note


def series_for(note, samples, rate_fn=None):
    """samples [(t, mark, v, b)] -> [(t, v)] measured, as the note means it (a counter: rates per hour)."""
    meas = [(t, v) for t, m, v, _b in samples or [] if m == "MEASURED" and v is not None]
    if note.get("kind") == "counter" and rate_fn:
        meas = rate_fn(meas)[0]
    return meas


def grade_one(note, pts, now, stale_s=STALE_FLOOR_S):
    """-> (grade or None if not yet, the value it was graded on, its time)."""
    f = CMPS[note["cmp"]]
    w0, dl = note["written_t"], note["deadline_t"]
    if note["mode"] == "before":
        inside = [(t, v) for t, v in pts if w0 <= t <= dl]
        hit = next(((t, v) for t, v in inside if f(v, note["value"])), None)
        if hit:
            return "held", hit[1], hit[0]
        if now < dl:
            return None, None, None
        if not inside:
            return "ungradable", None, None
        return "missed", inside[-1][1], inside[-1][0]
    win = max(GRACE_S, stale_s)         # the reading's own staleness, either side of the deadline
    if now < dl + win:
        return None, None, None
    near = [(abs(t - dl), t, v) for t, v in pts if dl - win <= t <= dl + win]
    if not near:
        return "ungradable", None, None
    _d, t, v = min(near)
    return ("held" if f(v, note["value"]) else "missed"), v, t


def grade(notes, grades, samples_of, now, stale_of=None, rate_fn=None):
    """Pure. notes: judge_notes.jsonl; grades: judge_grades.json {id: grade}; samples_of(key) -> samples or None
    (None: the store did not answer, so nothing is graded this generation). -> new grades (final ones kept)."""
    out = dict(grades or {})
    for n in notes:
        if n.get("id") in out or n.get("cmp") not in CMPS:
            continue
        s = samples_of(n["reading"])
        if s is None:
            continue
        g, v, t = grade_one(n, series_for(n, s, rate_fn), now, (stale_of or (lambda k: STALE_FLOOR_S))(n["reading"]))
        if g is None:
            continue
        nc = bool(CMPS[n["cmp"]](n["v0"], n["value"]))
        out[n["id"]] = {"grade": g, "v": v, "t": t, "graded_t": now, "no_change_says": "held" if nc else "missed"}
    return out


def score(notes, grades, now, days=WINDOW_D):
    """-> per run [{run, n, held, missed, ungradable, pending, no_change, foresaw, left_out}] newest first."""
    runs = {}
    for n in notes:
        if n.get("deadline_t", 0) < now - days * 24 * H:     # windowed by deadline: a pending note is always shown
            continue
        r = runs.setdefault(n["run"], {"run": n["run"], "t": n["written_t"], "n": 0, "held": 0, "missed": 0,
                                       "ungradable": 0, "pending": 0, "no_change": 0, "foresaw": 0, "notes": [],
                                       "open": {}})
        r["n"] += 1
        r["notes"].append(n)
        for i in n.get("open_incidents") or []:
            r["open"][i["id"]] = i["metrics"]
        g = (grades or {}).get(n["id"])
        if not g:
            r["pending"] += 1
            continue
        r[g["grade"]] += 1
        if g["grade"] != "ungradable":
            if g["no_change_says"] == g["grade"]:
                r["no_change"] += 1
            if g["grade"] == "held" and g["no_change_says"] == "missed":
                r["foresaw"] += 1
    out = []
    for r in runs.values():
        # covered: a note on one of its metrics, or --incident naming it from a note in the same family (a note on an
        # unrelated reading cannot cover an incident by naming it)
        reads = {n["reading"] for n in r["notes"]}
        fam = lambda k: (k or "").split(".", 1)[0]     # noqa: E731
        named = {n.get("incident") for n in r["notes"] if n.get("incident") and
                 any(fam(m) == fam(n["reading"]) for m in r["open"].get(n["incident"], []))}
        r["left_out"] = sorted(i for i, ms in r["open"].items() if i not in named and not (set(ms) & reads))
        del r["open"]
        out.append(r)
    return sorted(out, key=lambda r: -r["t"])


def note_line(n, g):
    s = "%s: %s %s %s %s %s (was %s)" % (n["id"], n["reading"], n["cmp"], _n(n["value"]),
                                          "at" if n["mode"] == "at" else "by", short(n["deadline_t"]), _n(n["v0"]))
    if not g:
        return s + ", pending"
    s += ", %s" % g["grade"].upper()
    if g.get("v") is not None:
        s += " on %s at %s" % (_n(g["v"]), short(g["t"]))
    if g["grade"] != "ungradable":
        s += "; no change said %s" % g["no_change_says"]
    return s


def render_notes(notes, grades, now, max_lines=GRADE_LINES):
    runs = score(notes, grades, now)
    out = ["## Your notes, graded against assuming no change (%d runs in %d d)" % (len(runs), WINDOW_D)]
    if not runs:
        out.append("- none left: end a run with up to %d notes (`ops_episodes.py note`, your instructions)" %
                   NOTES_PER_RUN)
        return out
    tot = {k: sum(r[k] for r in runs) for k in ("held", "missed", "ungradable", "pending", "no_change", "foresaw")}
    gradable = tot["held"] + tot["missed"]
    out.append("- %d d: you %d of %d gradable, assuming no change %d of %d; foresaw a change %d; ungradable %d; "
               "pending %d" % (WINDOW_D, tot["held"], gradable, tot["no_change"], gradable, tot["foresaw"],
                               tot["ungradable"], tot["pending"]))
    used = 0
    for r in runs:
        if used >= max_lines:
            out.append("- (%d older runs cut; all in judge_grades.json)" % (len(runs) - runs.index(r)))
            break
        gr = r["held"] + r["missed"]
        out.append("- run %s (%s): you %d of %d, no change %d of %d, foresaw %d; open incidents the notes left out: %s" % (
            r["run"], short(r["t"]), r["held"], gr, r["no_change"], gr, r["foresaw"],
            "%d (%s)" % (len(r["left_out"]), ", ".join(r["left_out"])) if r["left_out"] else "none"))
        used += 1
        for n in r["notes"]:
            if used >= max_lines:
                break
            out.append("  - " + note_line(n, (grades or {}).get(n["id"])))
            used += 1
    return out


def pending_readings(notes, grades):
    return sorted({n["reading"] for n in notes if n.get("id") not in (grades or {})})


# ========================================================================================================== publish
def publish_extra(mem, samples, d, now, read_told, stale_of=None, rate_fn=None):
    """Called by ops_memory.publish before it renders. Updates episodes.json and judge_grades.json, puts their
    summaries in mem, and returns the page lines. Each part fails alone, said on the page."""
    lines = []
    try:
        rows = read_told()
        st = update(read_json(d / "episodes.json", {}), mem, rows, now)
        atomic_json(d / "episodes.json", st)
        mem["episodes"] = {"open": sum(1 for x in list(st["readings"].values()) + list(st["incidents"].values())
                                       if x["closed_t"] is None), "unread": st["unread"]}
        lines += render_episodes(st) + [""]
    except Exception as e:      # noqa: BLE001 - the memory page is still worth having
        mem["episodes_error"] = "%s: %s" % (type(e).__name__, e)
        lines += ["## Episodes: NOT BUILT (%s)" % mem["episodes_error"], ""]
    try:
        notes = read_notes(d / "judge_notes.jsonl")
        old = read_json(d / "judge_grades.json", {})
        new = grade(notes, old, (lambda k: None) if mem.get("store_error") else (lambda k: samples.get(k, [])),
                    now, stale_of, rate_fn)
        if new != old:
            atomic_json(d / "judge_grades.json", new)
        mem["notes"] = {"total": len(notes), "graded": len(new), "pending_readings": pending_readings(notes, new)}
        lines += render_notes(notes, new, now) + [""]
    except Exception as e:      # noqa: BLE001
        mem["notes_error"] = "%s: %s" % (type(e).__name__, e)
        lines += ["## Your notes: NOT GRADED (%s)" % mem["notes_error"], ""]
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("note", help="leave one typed note (up to %d per run)" % NOTES_PER_RUN)
    n.add_argument("--run", required=True)
    n.add_argument("--reading", required=True)
    n.add_argument("--cmp", required=True, choices=list(CMPS))
    n.add_argument("--value", required=True, type=float)
    n.add_argument("--deadline", required=True)
    n.add_argument("--mode", default="at", choices=("at", "before"))
    n.add_argument("--incident")
    n.add_argument("--why")
    sub.add_parser("notes", help="the graded section as the page shows it")
    a = ap.parse_args(argv)
    if a.cmd == "note":
        try:
            nt = add_note(a.run, a.reading, a.cmp, a.value, a.deadline, a.mode, a.incident, a.why)
        except ValueError as e:
            print("REFUSED: %s" % e)
            return 2
        print("noted %s: %s %s %s %s %s (now %s)" % (nt["id"], nt["reading"], nt["cmp"], _n(nt["value"]), nt["mode"],
                                                     nt["deadline"], _n(nt["v0"])))
        return 0
    d = ops_dir()
    print("\n".join(render_notes(read_notes(d / "judge_notes.jsonl"), read_json(d / "judge_grades.json", {}),
                                 time.time())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
