#!/usr/bin/env python3
"""arena_spend.py - per-(arm, task) RAW token spend for arena_analysis.py (harness side, read-only on the logs).

    python3 src/RimMandrake/Utils/arena/arena_spend.py --out SPEND.json [--raw-dir DIR] [--allow-untrusted]
            [--projects ~/.claude/projects] [--clones-root /home/mandrake/rm/arena] [--gpt-log PATH]
            [--since ISO] [--until ISO]

WHAT IT DOES. The meter (sim/spend_census.py) knows each Claude API call (from the transcripts, attributed to an
arm by the clone path the session ran in) and each GPT call (gpt_call_log, tagged by RM_ARM), with a time. The
arm's signed event log knows when the arm worked on which task. This script joins the two:
  - a task SPAN is [first, last] event time of one (run_id, task) in the arm's log, over every event that carries a
    task EXCEPT `gate` and `judge` (harness events written after the arm's pass; a gate running while the arm
    starts its next task would otherwise make every task ambiguous). A task run twice has two spans.
  - a call whose time lies inside spans of exactly one task is that task's; inside spans of two or more different
    tasks it is AMBIGUOUS (counted on each such task as `ambiguous_calls`, its tokens on none; arena_analysis.py
    refuses such a task); inside no span it is the arm's `overhead` (reported, never in the efficiency).
  - meter buckets that are not an arm with a usable log (HARNESS, UNATTRIBUTED, UNTAGGED, UNREADABLE, an arm whose
    log is UNMEASURED) go to `overhead` whole, and are flagged.

OUTPUT, schema arena_task_spend/1 (arena_analysis.SPEND_SCHEMA):
  {"schema", "window": {since, until}, "arms": {arm: {task: row}}, "overhead": {bucket: row}, "flags": [str]}
  row = {"claude": {model: {input, cache_read, cache_write_5m, cache_write_1h, output}},     RAW counts per model
         "claude_ite": float,          DERIVED (spend_census weighting) for humans; arena_analysis.py ignores it
         "gpt": {tokens, in_est, out_est, calls, est_calls},   RAW: real codex tokens (a total; codex gives no
                                        in/out split) or, for calls with no usage line, the chars/4 in/out estimates
         "calls": int, "ambiguous_calls": int}
No conversion between models or between Claude and GPT happens here: arena_analysis.py does all weighting.

LIMITS: attribution is by TIME inside one arm. An arm that works on two tasks at once (ralph_c members in parallel)
makes the overlapping calls ambiguous, so those tasks read UNMEASURED until calls carry a per-member key. Calls
before an arm's first event or between tasks are overhead. A wrong clock on either side misattributes silently.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE.parent))
import arena_eventlog as L  # noqa: E402
import spend_census as S  # noqa: E402

SCHEMA = "arena_task_spend/1"
SPAN_EXCLUDED_EVENTS = ("gate", "judge")
CLAUDE_RAW = (("input", "in"), ("cache_read", "cr"), ("cache_write_5m", "c5"), ("cache_write_1h", "c1"),
              ("output", "out"))


def new_row():
    return {"claude": {}, "claude_ite": 0.0,
            "gpt": {"tokens": 0.0, "in_est": 0.0, "out_est": 0.0, "calls": 0, "est_calls": 0},
            "calls": 0, "ambiguous_calls": 0}


def spans_of(recs):
    """[(start, end, task)] from an arm's accepted records, one per (run_id, task). Raises ValueError on a bad ts
    (the caller makes that arm's spend overhead, flagged)."""
    by = {}
    for r in recs:
        t = r.get("task")
        if not isinstance(t, str) or not t or r.get("event") in SPAN_EXCLUDED_EVENTS:
            continue
        e = L.ts_epoch(r.get("ts"))
        k = (r.get("run_id"), t)
        lo, hi = by.get(k, (e, e))
        by[k] = (min(lo, e), max(hi, e))
    return sorted((lo, hi, t) for (_rid, t), (lo, hi) in by.items())


def tasks_at(spans, t):
    return {task for lo, hi, task in spans if lo <= t <= hi}


def add_claude(row, c):
    m = row["claude"].setdefault(str(c.get("model") or "?"), {k: 0 for k, _ in CLAUDE_RAW})
    for k, ck in CLAUDE_RAW:
        m[k] += c.get(ck) or 0
    row["claude_ite"] += c.get("ite") or 0.0
    row["calls"] += 1


def add_gpt(row, d):
    _ite, est = S.gpt_ite_of(d)
    g = row["gpt"]
    if est:
        g["in_est"] += d.get("in_tok_est") or 0
        g["out_est"] += d.get("out_tok_est") or 0
        g["est_calls"] += 1
    else:
        g["tokens"] += d.get("tokens_used")
    g["calls"] += 1
    row["calls"] += 1


def call_time(kind, item):
    t = item.get("t")
    if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t):
        return None
    return float(t)


def attribute(arm_logs, claude_calls, gpt_calls):
    """arm_logs {arm: {"recs"} | {"unmeasured"}}; claude_calls / gpt_calls: [(bucket, call)] from the meter's sinks.
    -> the schema dict without the window."""
    arms, overhead, flags = defaultdict(lambda: defaultdict(new_row)), defaultdict(new_row), []
    spans = {}
    for arm, lg in (arm_logs or {}).items():
        if "recs" not in lg:
            flags.append("arm %s: event log UNMEASURED (%s); its spend is overhead" % (arm, lg.get("unmeasured")))
            continue
        try:
            spans[arm] = spans_of(lg["recs"])
        except ValueError as e:
            flags.append("arm %s: unusable event ts (%s); its spend is overhead" % (arm, e))
    ambiguous = 0
    for kind, items, add in (("claude", claude_calls, add_claude), ("gpt", gpt_calls, add_gpt)):
        for bucket, c in items:
            t = call_time(kind, c)
            sp = spans.get(bucket)
            hit = tasks_at(sp, t) if (sp is not None and t is not None) else set()
            if len(hit) == 1:
                add(arms[bucket][next(iter(hit))], c)
            elif len(hit) > 1:
                ambiguous += 1
                for task in hit:
                    arms[bucket][task]["ambiguous_calls"] += 1
            else:
                add(overhead[bucket], c)
    if ambiguous:
        flags.append("%d call(s) fell inside spans of two or more tasks of one arm: those tasks are refused by "
                     "arena_analysis.py (ambiguous_calls)" % ambiguous)
    for b in overhead:
        if b not in spans:
            flags.append("meter bucket %s has no usable event log: all its spend is overhead" % b)
    return {"schema": SCHEMA, "arms": {a: dict(r) for a, r in arms.items()}, "overhead": dict(overhead),
            "flags": flags}


def meter(arm_logs, *, projects=None, clones_root=None, gpt_log=None, since=None, until=None):
    """Run the meter over the window with sinks. Window defaults to the logs' first..last event (inclusive)."""
    if since is None or until is None:
        ts = [L.ts_epoch(r["ts"]) for lg in arm_logs.values() for r in lg.get("recs", ())
              if isinstance(r.get("ts"), str)]
        since = min(ts) if since is None and ts else since
        until = (max(ts) + 1e-3) if until is None and ts else until
    if since is None or until is None:
        raise ValueError("no event times to derive a window from: pass --since and --until")
    cl, gp, diag = [], [], {}
    S.claude_spend_by_arm(projects=projects, arms=sorted(arm_logs), arena_root=clones_root, since=since,
                          until=until, diag=diag, sink=lambda arm, c: cl.append((arm, c)))
    S.gpt_spend_by_arm(gpt_log, since=since, until=until, diag=diag, sink=lambda arm, d: gp.append((arm, d)))
    doc = attribute(arm_logs, cl, gp)
    doc["window"] = {"since": since, "until": until}
    for k in ("unreadable_files", "cwd_mismatch", "gpt_unreadable"):
        if diag.get(k):
            doc["flags"].append("meter %s: %s" % (k, diag[k] if not isinstance(diag[k], list) else len(diag[k])))
    if diag.get("id_conflicts"):
        doc["flags"].append("meter id_conflicts: %d message id(s) under two arm folders" % len(diag["id_conflicts"]))
    return doc


def main(argv=None):
    import arena_analysis as AA
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw-dir", help="read unsigned <arm>.jsonl from this dir instead of the signed log")
    ap.add_argument("--allow-untrusted", action="store_true")
    ap.add_argument("--projects", help="Claude transcripts root (default ~/.claude/projects)")
    ap.add_argument("--clones-root", help="arm clones root (default $RM_ARENA_ROOT or %s)" % S.ARENA_ROOT)
    ap.add_argument("--gpt-log", help="gpt call log file/dir (default gpt_call_log's)")
    ap.add_argument("--since", help="ISO-8601 with zone (default: first event)")
    ap.add_argument("--until", help="ISO-8601 with zone (default: last event)")
    a = ap.parse_args(argv)
    logs = AA.load_raw(a.raw_dir) if a.raw_dir else AA.load_verified(allow_untrusted=a.allow_untrusted)
    try:
        doc = meter(logs, projects=a.projects, clones_root=a.clones_root, gpt_log=a.gpt_log,
                    since=L.ts_epoch(a.since) if a.since else None, until=L.ts_epoch(a.until) if a.until else None)
    except ValueError as e:
        print("arena_spend: %s" % e, file=sys.stderr)
        return 2
    tmp = a.out + ".tmp"
    Path(tmp).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, a.out)
    print(json.dumps({"arms": {k: len(v) for k, v in doc["arms"].items()}, "overhead": sorted(doc["overhead"]),
                      "flags": doc["flags"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
