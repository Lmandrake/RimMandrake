#!/usr/bin/env python3
"""proof_cost.py -- the proof cost ledger and the live-throughput report (PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES,
fast-testing #8: the instrument that proves the rest; design/RimMandrake/fast_testing_2026-11-05/scored.md).

    python3 src/RimMandrake/rimflow/proof_cost.py throughput [--hours 24 | --since ISO --until ISO] [--json]
    python3 src/RimMandrake/rimflow/proof_cost.py throughput --source runs --since ... --until ...   # legacy cross-check

THE LEDGER: <RELENTLESS_ROOT>/live/proof_cost.jsonl, append-only, one row per live proof run, written by the code that
ran it at the moment it ended, never reconstructed later:
  - relentless_live.run (every Relentless game_prove round and every broker clause: the broker runs the same round);
  - relentless_game.steve_sync (each clause a testq job on SteveDesktop answered or failed to answer).
A row: at (start), ended, source (round | broker | testq), item, clause, sha, tier, verdict (PASS | FAIL | UNMEASURED;
REFUSED and NOT_ADMITTED read UNMEASURED with their outcome kept), and the wall clock split
  queue_s    waiting before the bridge was taken: from the broker queue entry when there is one, else from the run's start
  staging_s  bridge held, before the proof started: the health check and the clause's live-site
  proving_s  bridge held, the proof command running (both runs when a WSL traceback reran it)
  idle_s     bridge held and neither: taking, release, the checks between
  held_s     taken -> released (= staging + proving + idle)
and tokens: LLM tokens the item's staging worker spent for this run (staging_tokens): every
`rm-relentless-stage-<short>-g<gen>-s<n>` unit booked in <root>/store/spend-*.json for the item and not yet carried by an
earlier row of the same item, so each staging run is charged once, to the first proof row after it (a later clause of the
same batch reads a measured 0). `tokens_units` names them; `tokens_estimated` is the part booked at the run reserve, not
read from usage. None (UNMEASURED) when no spend record can be read. A scripted proof's own `claude -p` calls are not seen. Every seconds field is None when the run never reached that part (a
NOT_ADMITTED row holds no bridge: held_s 0.0, not None, because it measured that it held nothing).

THE REPORT (`throughput`, and one line of `relentless.py reading`) over a window [since, until):
  measured rows/hour = (PASS + FAIL rows ended in the window) / window hours; a window with NO rows reads UNMEASURED, never
  0 (a lane that ran nothing measured nothing about its own rate; a lane that ran 5 rows all UNMEASURED reads 0.0);
  bridge driven share = bridge_utilization.py's |ACTIVE n HELD| / |HELD| over the same window (ledger bridge events vs
  session logs), and next to it the proof-busy share of our own holds, (staging + proving) / held;
  staging minutes p50 / p95 (nearest rank) over rows that staged;
  tokens per measured row = tokens over the rows that carry them / measured rows; UNMEASURED when no row carries tokens.
`--source runs` reads live/runs.jsonl instead (outcome and `at` only, no split): the cross-check that the report's
arithmetic reproduces the 2.7 rows/hour baseline of runs.jsonl's own history (scored.md: 230 PASS+FAIL in 84.6 h).
"""
import argparse
import calendar
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LEDGER = os.path.join("live", "proof_cost.jsonl")
UNMEASURED = "UNMEASURED"
MEASURED = ("PASS", "FAIL")
SOURCES = ("round", "broker", "testq")
SPLIT = ("queue_s", "staging_s", "proving_s", "idle_s", "held_s")


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def epoch(s):
    """ISO UTC stamp (Z, optional fraction) -> epoch seconds; None for anything unreadable."""
    if not s or not isinstance(s, str):
        return None
    try:
        return float(calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")))
    except ValueError:
        return None


def verdict_of(outcome):
    return outcome if outcome in MEASURED else UNMEASURED


def _secs(a, b):
    return None if a is None or b is None else round(max(0.0, b - a), 3)


def split(marks):
    """Timing marks (epoch seconds) -> the split. marks: start, queued (broker entry, optional), taken, proof_start,
    proof_s (summed proof command wall time), released, ended. A run that never took the bridge holds 0.0, unless
    held_unknown (a testq job: SteveDesktop's bridge time is not seen from here, so None)."""
    start, taken, released = marks.get("start"), marks.get("taken"), marks.get("released")
    queued = marks.get("queued")
    origin = queued if queued is not None and start is not None and queued <= start else start
    if taken is None:
        return {"queue_s": _secs(origin, marks.get("ended")), "staging_s": None, "proving_s": None, "idle_s": None,
                "held_s": None if marks.get("held_unknown") else 0.0}
    held = _secs(taken, released)
    staging = _secs(taken, marks.get("proof_start") if marks.get("proof_start") is not None else released)
    proving = round(marks["proof_s"], 3) if marks.get("proof_s") is not None else None
    idle = None
    if held is not None and staging is not None:
        idle = round(max(0.0, held - staging - (proving or 0.0)), 3)
    return {"queue_s": _secs(origin, taken), "staging_s": staging, "proving_s": proving, "idle_s": idle, "held_s": held}


STAGE_UNIT = "rm-relentless-stage-%s-g"


def _short(item):
    import hashlib
    return hashlib.sha1(item.encode()).hexdigest()[:10]       # relentless.short: the hash in a unit name


def staging_tokens(root, item, rows=None):
    """-> {"tokens", "tokens_units", "tokens_estimated"}: the item's staging-worker spend not yet carried by an earlier row
    (rows: the ledger as read; None reads it). tokens None when no spend-*.json under <root>/store reads, or the item is
    unnamed: an unreadable record is never a zero."""
    import glob
    if not item:
        return {"tokens": None}
    files = sorted(glob.glob(os.path.join(root, "store", "spend-*.json")))
    if not files:
        return {"tokens": None}
    pre = STAGE_UNIT % _short(item)
    runs, basis = {}, {}
    try:
        for p in files:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            for u, v in (d.get("runs") or {}).items():
                if u.startswith(pre) and isinstance(v, (int, float)) and not isinstance(v, bool):
                    runs[u] = runs.get(u, 0) + v
            basis.update(d.get("basis") or {})
    except (OSError, ValueError, AttributeError, TypeError):
        return {"tokens": None}
    if rows is None:
        rows = read(os.path.join(root, LEDGER))
    seen = {u for r in rows if r.get("item") == item for u in (r.get("tokens_units") or [])}
    new = sorted(u for u in runs if u not in seen)
    return {"tokens": int(sum(runs[u] for u in new)), "tokens_units": new,
            "tokens_estimated": int(sum(runs[u] for u in new if basis.get(u) == "estimated"))}


def make_row(source, item, clause, sha, tier, outcome, marks, tokens=None, why=None, **extra):
    if source not in SOURCES:
        raise ValueError("proof_cost source %r is not one of %s" % (source, ", ".join(SOURCES)))
    row = {"at": iso(marks["start"]) if marks.get("start") is not None else None,
           "ended": iso(marks["ended"]) if marks.get("ended") is not None else None,
           "source": source, "item": item, "clause": clause, "sha": sha, "tier": tier,
           "outcome": outcome, "verdict": verdict_of(outcome), "tokens": tokens}
    row.update(split(marks))
    if why:
        row["why"] = str(why)[:200]
    row.update(extra)
    return row


def append(root, row):
    """Append one row to <root>/live/proof_cost.jsonl. A cost row must never cost the run its verdict: callers wrap it."""
    p = os.path.join(root, LEDGER)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return p


def record(root, *a, **kw):
    """make_row + append; -> the row. Never raises: a failure is returned as {"unwritten": why} for the caller's row."""
    try:
        row = make_row(*a, **kw)
        append(root, row)
        return row
    except Exception as e:      # noqa: BLE001  the instrument failing is a note, never the proof's failure
        return {"unwritten": "%s: %s" % (type(e).__name__, str(e)[:200])}


def read(path):
    rows = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict):
                    rows.append(r)
    return rows


def from_runs(rows):
    """live/runs.jsonl rows -> cost-shaped rows with no split (the legacy cross-check). A void row is not a run."""
    out = []
    for r in rows:
        if r.get("void") or not r.get("at"):
            continue
        out.append({"at": r["at"], "ended": r["at"], "source": r.get("source") or "round", "item": r.get("item"),
                    "clause": r.get("criterion"), "sha": r.get("sha"), "outcome": r.get("outcome"),
                    "verdict": verdict_of(r.get("outcome")), "tokens": None,
                    "queue_s": None, "staging_s": None, "proving_s": None, "idle_s": None, "held_s": None})
    return out


def pct(vals, q):
    """Nearest-rank percentile of a non-empty list."""
    s = sorted(vals)
    k = max(1, int(-(-q * len(s) // 100)))      # ceil(q/100 * n), at least the first
    return s[min(k, len(s)) - 1]


def throughput(rows, since, until, driven=None, min_hours=0.0):
    """rows in [since, until) by their end stamp -> the report dict. driven: bridge_utilization's report dict for the
    same window (or {"unread": why}), carried through as the bridge-driven share. A window shorter than min_hours reads
    its rate UNMEASURED: two quick rows over a few minutes are no hourly rate."""
    if until <= since:
        raise ValueError("the window ends before it starts")
    win = [r for r in rows if since <= (epoch(r.get("ended")) or epoch(r.get("at")) or -1) < until]
    hours = (until - since) / 3600.0
    n = len(win)
    meas = [r for r in win if r.get("verdict") in MEASURED]
    by = {v: sum(1 for r in win if r.get("verdict") == v) for v in ("PASS", "FAIL", UNMEASURED)}
    held = [r["held_s"] for r in win if isinstance(r.get("held_s"), (int, float))]
    busy = [(r.get("staging_s") or 0.0) + (r.get("proving_s") or 0.0) for r in win
            if isinstance(r.get("held_s"), (int, float)) and r["held_s"] > 0]
    stg = [r["staging_s"] / 60.0 for r in win if isinstance(r.get("staging_s"), (int, float))]
    tok = [r["tokens"] for r in win if isinstance(r.get("tokens"), (int, float))]
    held_total = sum(held)
    rep = {"since": iso(since), "until": iso(until), "hours": round(hours, 3), "rows": n, "by_verdict": by,
           "by_source": {s: sum(1 for r in win if r.get("source") == s) for s in sorted({r.get("source") for r in win})},
           "measured": len(meas),
           "rows_per_hour": round(len(meas) / hours, 3) if n and hours >= min_hours else UNMEASURED,
           "held_min": round(held_total / 60.0, 2) if held else UNMEASURED,
           "proof_busy_share": round(sum(busy) / held_total, 4) if held_total > 0 else UNMEASURED,
           "staging_min_p50": round(pct(stg, 50), 2) if stg else UNMEASURED,
           "staging_min_p95": round(pct(stg, 95), 2) if stg else UNMEASURED,
           "tokens_per_measured_row": (round(sum(tok) / len(meas), 1) if tok and meas else UNMEASURED),
           "tokens_rows": len(tok)}
    if driven is None or "unread" in (driven or {}):
        rep["bridge_driven_share"] = UNMEASURED
        if driven:
            rep["bridge_driven_unread"] = driven["unread"]
    else:
        u = driven.get("utilization")
        rep["bridge_driven_share"] = UNMEASURED if u is None else u
        rep["bridge_held_min"] = driven.get("held_min")
    return rep


def driven_share(since, until, repo=REPO):
    """bridge_utilization.report over [since, until) -> its dict, or {"unread": why}. Its inputs are the ones its own CLI
    defaults to (the ledger's bridge events, Transient modcheck/northstar rows, the bridge session log)."""
    try:
        import datetime as dt
        from zoneinfo import ZoneInfo
        sys.path.insert(0, os.path.join(repo, "src", "RimMandrake", "Utils", "northstar_driver"))
        import bridge_utilization as BU
        from rmpaths import rm_str
        evs = BU.read_events(os.path.join(repo, "infrastructure", "state", "ledger", "events"))
        now = dt.datetime.now(BU.UTC)
        held = BU.held_intervals(evs, now)
        active = BU.active_intervals([os.path.join(repo, "Transient", "modcheck", "*.jsonl")],
                                     os.path.join(repo, "Transient", "northstar", "*.json"),
                                     ZoneInfo("America/Los_Angeles"), rm_str("scratch", "bridge_sessions.jsonl"))
        lo = dt.datetime.fromtimestamp(since, BU.UTC)
        hi = dt.datetime.fromtimestamp(until, BU.UTC)
        held = [(max(a, lo), min(b, hi), w, p) for a, b, w, p in held if b > lo and a < hi]
        r = BU.report(held, active, [e for e in evs if e["event"] == "game"], None, 5.0)
        r.pop("gaps", None)
        return r
    except Exception as e:      # noqa: BLE001  an unread share is UNMEASURED, never 0
        return {"unread": "%s: %s" % (type(e).__name__, str(e)[:200])}


def line(rep):
    """The report -> the one line `relentless.py reading` prints."""
    def f(v, fmt):
        return v if v == UNMEASURED else fmt % v
    return ("proof cost %s..%s: %s measured rows/h (%d rows: %d PASS %d FAIL %d UNMEASURED), bridge driven %s, "
            "proof-busy %s of our %s held min, staging p50 %s / p95 %s min, tokens/measured row %s"
            % (rep["since"][5:16], rep["until"][5:16], f(rep["rows_per_hour"], "%.2f"), rep["rows"],
               rep["by_verdict"]["PASS"], rep["by_verdict"]["FAIL"], rep["by_verdict"][UNMEASURED],
               f(rep["bridge_driven_share"], "%.3f"), f(rep["proof_busy_share"], "%.3f"),
               f(rep["held_min"], "%.1f"), f(rep["staging_min_p50"], "%.1f"), f(rep["staging_min_p95"], "%.1f"),
               f(rep["tokens_per_measured_row"], "%.0f")))


def first(rows):
    """The ledger's first end stamp (epoch; a testq row's `at` is its job's submission, before the ledger), or None: a window reaching before it would divide by hours nobody measured."""
    ts = [t for t in (epoch(r.get("ended")) or epoch(r.get("at")) for r in rows) if t is not None]
    return min(ts) if ts else None


def reading_line(root, now, hours=24.0, repo=REPO):
    """`relentless.py reading`'s line: the last `hours` of the ledger, never reaching back before its first row (the
    ledger's first day would else read a rate diluted by hours before it existed). Never raises."""
    try:
        rows = read(os.path.join(root, LEDGER))
        since = max([now - hours * 3600.0] + [first(rows) or 0.0])
        if since >= now:
            since = now - hours * 3600.0
        return line(throughput(rows, since, now, driven_share(since, now, repo), min_hours=1.0))
    except Exception as e:      # noqa: BLE001
        return "proof cost: COULD NOT READ (%s: %s)" % (type(e).__name__, str(e)[:200])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("throughput", help="the report over a window")
    t.add_argument("--hours", type=float, default=24.0, help="the window ends now (default 24 h)")
    t.add_argument("--since", help="ISO UTC start (overrides --hours)")
    t.add_argument("--until", help="ISO UTC end (default now)")
    t.add_argument("--source", choices=("ledger", "runs"), default="ledger",
                   help="runs: live/runs.jsonl, outcome only (the legacy cross-check)")
    t.add_argument("--root", default=os.environ.get("RELENTLESS_ROOT") or "/home/mandrake/rm/relentless")
    t.add_argument("--no-bridge", action="store_true", help="skip the bridge_utilization read (UNMEASURED)")
    t.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    until = epoch(a.until) if a.until else time.time()
    since = epoch(a.since) if a.since else until - a.hours * 3600.0
    if since is None or until is None:
        print("UNMEASURED: unreadable --since/--until", file=sys.stderr)
        return 2
    rows = (read(os.path.join(a.root, LEDGER)) if a.source == "ledger"
            else from_runs(read(os.path.join(a.root, "live", "runs.jsonl"))))
    rep = throughput(rows, since, until, None if a.no_bridge else driven_share(since, until))
    rep["source"] = a.source
    print(json.dumps(rep, indent=1, sort_keys=True) if a.json else line(rep))
    return 0


if __name__ == "__main__":
    sys.exit(main())
