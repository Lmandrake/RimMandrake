#!/usr/bin/env python3
"""Cost and yield per GPT review round (GPT_CONSULT_MEASURE_COST_UNLOGGED; testing_policy_2026-10-28.md §2.5).

    python3 src/RimMandrake/Utils/gpt_consult.py "review this" -f x.py --round XPARSER_R1     # meter a call
    python3 src/RimMandrake/Utils/gpt_consult_rounds.py yield --round XPARSER_R1 --findings 4 --strong 1 --repeated 2
    python3 src/RimMandrake/Utils/gpt_consult_rounds.py report [--days 14] [--round NAME] [--json]

COST comes from the per-call log gpt_consult already writes (gpt_call_log): calls, answered, timeouts (rc 124), real
codex tokens and wall seconds. A call with no real token figure is counted as `tok?`, never filled from the chars/4
estimate; a call from before rounds were tagged (no `secs`) leaves the seconds UNMEASURED.
YIELD is two things: the findings the round's runner recorded with `yield` (UNMEASURED until one is recorded; the
last record for a round wins), and the code-review records whose reviewer names one of the round's jobs
(`code_review_status mark-clean --gpt-job`). Untagged calls are summed in one `(untagged)` row.

The yield log is <agent storage>/rimmandrake/consult/rounds.jsonl ($RM_CONSULT_ROUNDS overrides), one appending writer
per record, like the receipts beside it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROUNDS_ENV = "RM_CONSULT_ROUNDS"
UNTAGGED = "(untagged)"


def rounds_path() -> Path:
    v = os.environ.get(ROUNDS_ENV, "").strip()
    if v:
        return Path(v)
    from rmpaths import rm_path
    return rm_path("consult", "rounds.jsonl")


def write_yield(round_name, findings, strong=None, weak=None, repeated=None, note=None, path=None):
    """Append one yield record for a round. Counts are non-negative ints; strong/weak/repeated are optional parts of
    findings and may not exceed it."""
    import gpt_consult
    if not gpt_consult.ROUND_RE.match(round_name or ""):
        raise ValueError("bad round name %r" % round_name)
    parts = {"strong": strong, "weak": weak, "repeated": repeated}
    for k, v in [("findings", findings)] + list(parts.items()):
        if v is not None and (not isinstance(v, int) or v < 0):
            raise ValueError("%s must be a non-negative integer, got %r" % (k, v))
    for k, v in parts.items():
        if v is not None and v > findings:
            raise ValueError("%s (%d) exceeds findings (%d)" % (k, v, findings))
    rec = {"t": time.time(), "round": round_name, "findings": findings, **{k: v for k, v in parts.items()
                                                                            if v is not None}}
    if note:
        rec["note"] = str(note)
    p = Path(path) if path else rounds_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(p), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
    finally:
        os.close(fd)
    return rec


def read_yields(path=None):
    """{round: last yield record}, and the count of unreadable lines."""
    p = Path(path) if path else rounds_path()
    out, bad = {}, 0
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return out, 0
    for ln in lines:
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
            if not isinstance(r, dict) or not isinstance(r.get("round"), str):
                raise ValueError
        except ValueError:
            bad += 1
            continue
        out[r["round"]] = r
    return out, bad


def review_jobs(records):
    """{consult job id: number of code-review records whose reviewer names it}."""
    n = {}
    for r in records:
        rv = r.get("reviewer")
        if isinstance(rv, dict) and rv.get("tool") == "gpt_consult" and rv.get("job"):
            n[rv["job"]] = n.get(rv["job"], 0) + 1
    return n


def _code_review_records():
    import code_review_status
    return code_review_status.read_records()


def build_report(calls, yields, reviews, since=None, only=None):
    """Rows, one per round (plus one `(untagged)` row), oldest first. calls: gpt_call_log records; yields: read_yields()
    map; reviews: review_jobs() map."""
    rows = {}
    for c in calls:
        t = c.get("t")
        if since is not None and not (isinstance(t, (int, float)) and t >= since):
            continue
        name = c.get("round") or UNTAGGED
        if only and name != only:
            continue
        r = rows.setdefault(name, {"round": name, "calls": 0, "answered": 0, "timeouts": 0, "tokens": 0,
                                   "tok_unmeasured": 0, "secs": 0.0, "secs_unmeasured": 0, "reviews": 0,
                                   "first": t, "last": t, "jobs": []})
        r["calls"] += 1
        ans = c.get("answered")
        if ans is None:                                 # legacy record: an answer leaves out_tok_est > 0
            ans = (c.get("out_tok_est") or 0) > 0
        r["answered"] += bool(ans)
        r["timeouts"] += c.get("rc") == 124
        if isinstance(c.get("tokens_used"), int):
            r["tokens"] += c["tokens_used"]
        else:
            r["tok_unmeasured"] += 1
        if isinstance(c.get("secs"), (int, float)):
            r["secs"] += c["secs"]
        else:
            r["secs_unmeasured"] += 1
        if c.get("job") not in r["jobs"]:              # a job id logged twice (retry, same pid+second) counts once
            r["reviews"] += reviews.get(c.get("job"), 0)
            r["jobs"].append(c.get("job"))
        if isinstance(t, (int, float)):
            r["first"] = t if r["first"] is None else min(r["first"], t)
            r["last"] = t if r["last"] is None else max(r["last"], t)
    for name, y in yields.items():
        if only and name != only:
            continue
        if name not in rows:                            # a yield for a round with no metered call in the window
            continue
        rows[name]["yield"] = {k: y[k] for k in ("findings", "strong", "weak", "repeated", "note") if k in y}
    return sorted(rows.values(), key=lambda r: (r["round"] == UNTAGGED, r["first"] or 0))


def _fmt(rows):
    out = ["%-28s %5s %4s %4s %11s %5s %9s %7s %s" % ("round", "calls", "ans", "t/o", "tokens", "tok?", "secs",
                                                    "reviews", "findings (strong/weak/repeated)")]
    for r in rows:
        secs = "UNMEASURED" if r["secs_unmeasured"] == r["calls"] else "%.0f%s" % (
            r["secs"], "+?" if r["secs_unmeasured"] else "")
        y = r.get("yield")
        if r["round"] == UNTAGGED:
            yt = "-"
        elif y is None:
            yt = "UNMEASURED"
        else:
            yt = "%d (%s/%s/%s)" % (y["findings"], *(str(y.get(k, "?")) for k in ("strong", "weak", "repeated")))
        out.append("%-28s %5d %4d %4d %11d %5d %9s %7d %s" % (r["round"][:28], r["calls"], r["answered"],
                                                            r["timeouts"], r["tokens"], r["tok_unmeasured"], secs,
                                                            r["reviews"], yt))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    y = sub.add_parser("yield", help="record what a round found")
    y.add_argument("--round", required=True)
    y.add_argument("--findings", type=int, required=True, help="findings the round raised")
    y.add_argument("--strong", type=int, help="of which acted on / real")
    y.add_argument("--weak", type=int, help="of which weak or partial")
    y.add_argument("--repeated", type=int, help="of which repeat an earlier round's")
    y.add_argument("--note")
    rp = sub.add_parser("report", help="cost and yield per round")
    rp.add_argument("--days", type=float, help="only calls in the last N days")
    rp.add_argument("--round", help="only this round")
    rp.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "yield":
        try:
            rec = write_yield(a.round, a.findings, a.strong, a.weak, a.repeated, a.note)
        except ValueError as e:
            print("FAIL: %s" % e, file=sys.stderr)
            return 2
        print("recorded yield for %s: %s -> %s" % (a.round, rec["findings"], rounds_path()))
        return 0
    import gpt_call_log
    calls, bad_calls = gpt_call_log.read_records()
    yields, bad_y = read_yields()
    since = time.time() - a.days * 86400 if a.days else None
    rows = build_report(calls, yields, review_jobs(_code_review_records()), since=since, only=a.round)
    if a.json:
        print(json.dumps({"rows": rows, "unreadable_call_lines": bad_calls, "unreadable_yield_lines": bad_y},
                         indent=1))
    else:
        print(_fmt(rows) if rows else "no metered calls%s" % (" for round %s" % a.round if a.round else ""))
        print("(%d call records, %d unreadable; %d yield records, %d unreadable)" % (
            len(calls), bad_calls, len(yields), bad_y), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
