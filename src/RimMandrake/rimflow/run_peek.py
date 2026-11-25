#!/usr/bin/env python3
"""run_peek.py: what each live mod run spends its time on, and the Conductor asked when one check takes over an hour.

Item RIMMANDRAKE_PEEK_AT_LIVE_MOD_RUNS_HE_SAID_IT_IS_THE_CONDUCTORS_JOB. The owner, 2026-11-24: "If they're spending a lot
of time on one or two tests, PLEASE let's ask if it's even sensible to try that, if it needs to be deferred, re-examined,
replaced with a simpler test, or needs to be raised with me". Page: design/specs/2026-11-25-run-peek/boundary.md; tests:
selftest_run_peek.py. No model, no tokens.

    run_peek.py show [--json]     every live mod run: its checks by time, its last PROGRESS note, its last message
    run_peek.py live              exit 0 the applied tick wrote a fresh peek; 1 it did not; 2 could not look

The applied tick (maturation_dispatch._tick) calls observe(): a run with LONG_S on one check gets ONE `LONG ON ONE
CHECK:` line in the Conductor log and one Needs Conductor line, once per run and check. It stops nothing, launches
nothing and writes no rimflow note.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ITEM = "RIMMANDRAKE_PEEK_AT_LIVE_MOD_RUNS_HE_SAID_IT_IS_THE_CONDUCTORS_JOB"
# The page's LIMITS name each number's reason and measurement.
LONG_S = 3600       # the item: "a program that names a run with over an hour on one check"; the point of asking, not a limit
LAPSE_CALLS = 10    # calls with no check named before the focus clears (the page: 79 min against 30 min, measured)
# budget: danger=a tick that no longer calls the peek still reads as live; ends no work: the age bound of a reading,
# budget: 15 ticks; longest=60s (rm-maturation-dispatch.timer OnUnitActiveSec)
FRESH_S = 900       # the tick runs each 60 s; an older peek block means the tick does not run it
CLAIM = re.compile(r"cli\.py\s+(claim|start)\s")
PROGRESS = re.compile(r"PROGRESS:(?:[^\"\\]|\\[^\"])*")   # in the call's JSON text: up to the note's closing quote
HEAD = "LONG ON ONE CHECK"


class CouldNotLook(Exception):
    """A fact could not be read; its text is the cause."""


def ep(s):
    """ISO time -> epoch. ValueError when it is not one."""
    d = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return (d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)).timestamp()


def pst(t):
    return time.strftime("%Y-%m-%d %-I:%M %p %Z", time.localtime(t))


# ---- the facts ---------------------------------------------------------------------------------------------------

def check_ids(clone, mod, repo=REPO):
    """-> the check ids of the mod's test table, from the run's clone, else this repo. CouldNotLook when neither reads."""
    why = []
    for root in [r for r in (clone, repo) if r]:
        p = os.path.join(root, "design", "concepts", mod, "version", "test_table.json")
        if not os.path.isfile(p):
            why.append("%s: absent" % p)
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                tests = json.load(fh).get("tests")
        except (OSError, ValueError, AttributeError) as e:
            why.append("%s: %s" % (p, e))
            continue
        if isinstance(tests, dict) and tests:
            return set(tests)
        why.append("%s: no tests" % p)
    raise CouldNotLook("no test table of %s: %s" % (mod, "; ".join(why) or "no clone"))


def calls(path):
    """-> ([(epoch, input text)] of the run's own tool calls, oldest first, the count of calls with no readable time).
    CouldNotLook when the file cannot be read."""
    out, undated = [], 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                if '"tool_use"' not in ln:
                    continue
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if not isinstance(r, dict) or r.get("type") != "assistant" or r.get("isSidechain"):
                    continue
                content = (r.get("message") or {}).get("content")
                uses = [c for c in (content if isinstance(content, list) else [])
                        if isinstance(c, dict) and c.get("type") == "tool_use"]
                try:
                    t = ep(r.get("timestamp"))
                except ValueError:
                    undated += len(uses)
                    continue
                out += [(t, json.dumps(c.get("input"), ensure_ascii=False)) for c in uses]
    except OSError as e:
        raise CouldNotLook("transcript: %s" % e)
    out.sort(key=lambda x: x[0])
    return out, undated


def dwell(evs, ids, end, lapse=LAPSE_CALLS):
    """-> ({check: seconds}, the focus at the end as a sorted list). The page's §How time is put on a check. Pure."""
    if not ids:
        return {}, []
    pat = re.compile(r"(?<![A-Za-z0-9_])(%s)(?![A-Za-z0-9_])" % "|".join(
        sorted(map(re.escape, ids), key=len, reverse=True)))
    tot, focus, quiet = {}, frozenset(), 0
    for i, (t, text) in enumerate(evs):
        hits = set(pat.findall(text))
        if CLAIM.search(text) or len(hits) > 2:
            focus, quiet = frozenset(), 0
        elif hits:
            focus, quiet = frozenset(hits), 0
        else:
            quiet += 1
            if quiet > lapse:
                focus = frozenset()
        nxt = evs[i + 1][0] if i + 1 < len(evs) else end
        for k in focus:
            tot[k] = tot.get(k, 0.0) + max(0.0, nxt - t)
    return tot, sorted(focus)


def last_progress(evs):
    """-> the text of the newest PROGRESS: note among the calls, or None."""
    for _, text in reversed(evs):
        m = list(PROGRESS.finditer(text))
        if m:
            try:
                return json.loads('"%s"' % m[-1].group(0))
            except ValueError:
                return m[-1].group(0)
    return None


# ---- one run -----------------------------------------------------------------------------------------------------

def peek_run(rec, now, projects=None, repo=REPO, mod=None):
    """-> one row: {unit, mod, item, at, checks: [[id, s], ...] longest first, long: [ids], focus, progress, message}, or
    {"blind": cause} in it."""
    import run_alive as RA
    import run_host
    import socket
    row = {"unit": rec.get("unit"), "mod": mod or RA.mod_of(rec), "item": rec.get("item"), "at": rec.get("at")}
    door = run_host.door(rec.get("host"))
    if door and run_host._norm(rec.get("host")) != socket.gethostname().strip().lower():
        row["blind"] = "could not look: it runs on %s; its transcript is there" % rec.get("host")
        return row
    try:
        ids = check_ids(rec.get("clone"), row["mod"], repo)
        path = RA.transcript(rec, projects)
        evs, undated = calls(path)
    except (CouldNotLook, RA.CouldNotLook) as e:
        row["blind"] = "could not look: %s" % e
        return row
    tot, focus = dwell(evs, ids, now)
    row["checks"] = [[k, round(v)] for k, v in sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))]
    row["long"] = [k for k, v in row["checks"] if v >= LONG_S]
    row["focus"] = focus
    row["calls"] = len(evs)
    if undated:
        row["undated_calls"] = undated      # counted in no check's time; said, never dropped
    row["progress"] = last_progress(evs)
    try:
        row["message"] = RA._flat(RA.last_message(path))
    except RA.CouldNotLook as e:
        row["message"] = None
        row["message_blind"] = str(e)
    return row


def live_mod_runs(root=None, records=None):
    import detached_helper as DH
    import run_alive as RA
    recs = (records or DH.all_records)(root)
    return [r for r in recs if r.get("status") in ("launching", "running") and RA.mod_of(r)]


def peek(now=None, root=None, records=None, projects=None, repo=REPO, units=None):
    """-> rows for every live mod run, or for `units` ({unit: mod}, the tick's own placement of its live runs). One run's
    surprise never stops the others."""
    import detached_helper as DH
    now = now or time.time()
    if units is None:
        recs = [(r, None) for r in live_mod_runs(root, records)]
    else:
        recs = []
        for u, mod in sorted(units.items()):
            try:
                rec = DH.read_record(u, root)
            except Exception as e:  # noqa: BLE001
                rec, why = None, "%s: %s" % (type(e).__name__, e)
            else:
                why = "no run record of it could be read"
            recs.append((rec, mod) if rec else ({"unit": u, "blind": "could not look: " + why}, mod))
    rows = []
    for rec, mod in recs:
        if rec.get("blind"):
            rows.append({"unit": rec["unit"], "mod": mod, "blind": rec["blind"]})
            continue
        try:
            rows.append(peek_run(rec, now, projects, repo, mod))
        except Exception as e:  # noqa: BLE001
            rows.append({"unit": rec.get("unit"), "mod": mod, "item": rec.get("item"),
                         "blind": "could not look: %s: %s" % (type(e).__name__, e)})
    return rows


def tick_units(facts):
    """-> {unit: mod} of the live runs that the tick placed on each mod (facts[mod]['live_units']; an UNMEASURED list
    places none)."""
    out = {}
    for mod, f in (facts or {}).items():
        lu = (f or {}).get("live_units") if isinstance(f, dict) else None
        for u in lu if isinstance(lu, list) else []:
            out.setdefault(u, mod)
    return out


# ---- the tick's pass ---------------------------------------------------------------------------------------------

def seen_path(tick_dir=None):
    """The (run, check) pairs already asked, beside the tick's own reading (a test tick's folder is its own)."""
    if tick_dir is None:
        import maturation_dispatch as MD
        tick_dir = MD.sdir()
    return os.path.join(tick_dir, "run_peek_seen.json")   # a flat file: the tick's folder holds files only


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=0)
    os.replace(tmp, path)


def ask_line(row, check, secs):
    return ("%s: %s (%s, item %s) has spent %d min on check %s. Its last PROGRESS: %s. Its last message: %s. Ask: is "
            "the test sensible? Defer it, re-examine it, replace it with a cheaper test (cheaper_why), or raise it with "
            "him. `python3 src/RimMandrake/rimflow/run_peek.py show`" % (
                HEAD, row["unit"], row.get("mod"), row.get("item"), secs // 60, check,
                row.get("progress") or "none (looked)",
                '"%s"' % row["message"] if row.get("message") else ("none (looked)" if row.get("message") == ""
                                                                    else "could not look")))


def observe(now, rd, fx=None, tick_dir=None, facts=None):
    """The applied tick's pass over the live runs it placed on its mods. -> rd with rd['peek']; each new (run, check)
    past LONG_S gets its Conductor line once."""
    import detached_helper as DH
    fx = fx or {}
    sp = fx.get("seen") or seen_path(tick_dir)
    units = tick_units(facts)
    rows = fx["peek"](now, units) if "peek" in fx else peek(now, units=units)
    try:
        with open(sp, encoding="utf-8") as fh:
            seen = set(json.load(fh))
    except FileNotFoundError:
        seen = set()
    told = []
    for row in rows:
        for check in row.get("long") or []:
            key = "%s|%s" % (row["unit"], check)
            if key in seen:
                continue
            secs = dict((k, v) for k, v in row["checks"]).get(check, 0)
            line = ask_line(row, check, secs)
            try:
                (fx.get("log") or (lambda text: DH.conductor_line(text[len(HEAD) + 2:], now, head=HEAD)))(line)
                said = "logged"
            except Exception as e:  # noqa: BLE001  an unwritten log line is tried again at the next tick
                said = "conductor log failed: %s" % e
            if said == "logged":
                seen.add(key)
            rd.setdefault("needs_conductor", []).append(line)
            told.append({"unit": row["unit"], "check": check, "min": secs // 60, "log": said})
    _write(sp, sorted(seen))
    rd["peek"] = {"at": now, "runs": len(rows), "told": told,
                  "checks": {r["unit"]: (r.get("checks") or [])[:3] for r in rows if not r.get("blind")},
                  "long": {r["unit"]: r["long"] for r in rows if r.get("long")},
                  "blind": {r["unit"]: r["blind"] for r in rows if r.get("blind")}}
    return rd


def live(now=None, reading=None):
    """-> (exit code, text): 0 the tick's reading holds a fresh peek with no peek_error; 1 it does not; 2 unreadable."""
    now = now or time.time()
    if reading is None:
        import maturation_dispatch as MD
        reading = os.path.join(MD.sdir(), "reading.json")
    try:
        with open(reading, encoding="utf-8") as fh:
            rd = json.load(fh)
    except (OSError, ValueError) as e:
        return 2, "COULD NOT LOOK: %s: %s" % (reading, e)
    if rd.get("peek_error"):
        return 1, "FAILS: the tick's peek raised: %s" % rd["peek_error"]
    pk = rd.get("peek")
    if not isinstance(pk, dict) or not isinstance(pk.get("at"), (int, float)):
        return 1, "FAILS: the tick's reading holds no peek block (%s)" % reading
    age = now - pk["at"]
    if age > FRESH_S:
        return 1, "FAILS: the tick's peek is %d s old (over %d s)" % (age, FRESH_S)
    return 0, "HOLDS: the tick peeked %d s ago at %d live mod runs; long: %s; blind: %d" % (
        age, pk.get("runs", 0), json.dumps(pk.get("long") or {}), len(pk.get("blind") or {}))


def show_text(rows, now):
    if not rows:
        return "no live mod run (looked at %s)" % pst(now)
    out = ["live mod runs at %s: %d" % (pst(now), len(rows))]
    for r in rows:
        age = int((now - (r.get("at") or now)) / 60)
        out.append("- %s  %s  item %s  (%d min old)" % (r.get("unit"), r.get("mod"), r.get("item"), age))
        if r.get("blind"):
            out.append("    %s" % r["blind"])
            continue
        top = ", ".join("%s %d min" % (k, v // 60) for k, v in (r.get("checks") or [])[:5]) or "none named (looked)"
        out.append("    checks by time: %s" % top)
        if r.get("long"):
            out.append("    LONG ON ONE CHECK: %s. Ask: is it sensible; defer, re-examine, replace with a cheaper test, "
                       "or raise with him." % ", ".join(r["long"]))
        out.append("    now on: %s" % (", ".join(r.get("focus") or []) or "no one check"))
        out.append("    last PROGRESS: %s" % (r.get("progress") or "none (looked)"))
        msg = r.get("message")
        out.append("    last message: %s" % ('"%s"' % msg if msg else "none (looked)" if msg == "" else
                                             "could not look: %s" % r.get("message_blind")))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("--json", action="store_true")
    sub.add_parser("live")
    a = ap.parse_args(argv)
    now = time.time()
    if a.cmd == "live":
        rc, text = live(now)
        print(text)
        return rc
    try:
        rows = peek(now)
    except OSError as e:
        print("COULD NOT LOOK: the run records could not be listed: %s" % e)
        return 2
    print(json.dumps(rows, indent=1) if a.json else show_text(rows, now))
    return 0


if __name__ == "__main__":
    sys.exit(main())
