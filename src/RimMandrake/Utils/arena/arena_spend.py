#!/usr/bin/env python3
"""arena_spend.py - per-(arm, task) RAW token spend for arena_analysis.py (harness side, read-only on the logs).

    python3 src/RimMandrake/Utils/arena/arena_spend.py --out SPEND.json [--raw-dir DIR] [--ledger EVENTS.jsonl] [--allow-untrusted]
            [--projects ~/.claude/projects] [--clones-root /home/mandrake/rm/arena] [--gpt-log PATH]
            [--helpers DIR] [--sandbox-root DIR] [--since ISO] [--until ISO]

WHAT IT DOES. The meter (sim/spend_census.py) knows each Claude API call (from the transcripts, attributed to an
arm by the clone path the session ran in) and each GPT call (gpt_call_log, tagged by RM_ARM), with a time. The
arm's signed event log knows when the arm worked on which task. This script joins the two:
  - a task SPAN is one EXECUTION of a (run_id, task) in the arm's log: from its first event to its `pass_end`
    (inclusive; with no pass_end, to its last event), over every event that carries a task EXCEPT `gate` and `judge`
    (harness events written after the arm's pass; a gate running while the arm starts its next task would otherwise
    make every task ambiguous). A later event of the same (run_id, task) after a pass_end opens a new span, so a
    reused run_id never claims the idle gap between two runs.
  - a call whose time lies inside spans of exactly one task is that task's; inside spans of two or more different
    tasks it is AMBIGUOUS (counted on each such task as `ambiguous_calls`, its tokens on none; arena_analysis.py
    refuses such a task); inside no span it is the arm's `overhead` (reported, never in the efficiency).
  - meter buckets that are not an arm with a usable log (HARNESS, UNATTRIBUTED, UNTAGGED, UNREADABLE, an arm whose
    log is UNMEASURED) go to `overhead` whole, and are flagged.
  - every per-call raw count is validated BEFORE it is summed; a call with a bool/negative/non-int count adds nothing
    and marks its task row `invalid_calls` (arena_analysis.py refuses that task).
  - BLOCKING (arena_analysis.py refuses the whole file): calls with no usable time, and the meter diagnostics that
    mean spend was lost or may sit on the wrong arm (BLOCKING_DIAG: unreadable transcripts, bad lines, cwd mismatch,
    unreadable gpt log lines, a message id under two arm folders), and UNATTRIBUTED Claude spend under the arena root
    that the meter could not put on one arm (BLOCKING_UNATTRIBUTED). GPT calls with no RM_ARM tag (UNTAGGED) stay
    overhead: the log cannot tell an untagged arm call from unrelated GPT use in the same window (residual).
  - TESTERS (helpers): every model tester an arm's log says ran (`test_start`) must have a helper_capture.py capture
    (its transcripts + GPT records, copied by the loop before the tester's private root is deleted); those calls are
    the ARM's. A missing capture, skipped files or a capture with no transcript is BLOCKING: an arm never wins on
    spend the meter cannot see. Builders' transcripts are read from their arm_sandbox private HOMEs (sandbox_homes).
  - a null count is invalid; for GPT, tokens_used null/0 means "no usage line" and both chars/4 estimates must be
    present counts.

OUTPUT, schema arena_task_spend/2 (arena_analysis.SPEND_SCHEMA):
  {"schema", "window": {since, until}, "logs": {arm: {n, digest}} (arena_analysis.spend_log_binding of the logs
   metered: the analysis refuses the file against any other log), "blocking": [str], "arms": {arm: {task: row}},
   "overhead": {bucket: row}, "flags": [str] (report only)}
  row = {"claude": {model: {input, cache_read, cache_write_5m, cache_write_1h, output}},     RAW counts per model
         "claude_ite": float,          DERIVED (spend_census weighting) for humans; arena_analysis.py ignores it
         "gpt": {tokens, in_est, out_est, calls, est_calls},   RAW: real codex tokens (a total; codex gives no
                                        in/out split) or, for calls with no usage line, the chars/4 in/out estimates
         "calls": int, "ambiguous_calls": int, "invalid_calls": int}
No conversion between models or between Claude and GPT happens here: arena_analysis.py does all weighting.

LIMITS: attribution is by TIME inside one arm. An arm that works on two tasks at once (ralph_c members in parallel)
makes the overlapping calls ambiguous, so those tasks read UNMEASURED until calls carry a per-member key. Calls
before an arm's first event or between tasks are overhead. A wrong clock on either side, or an execution whose events
stop before its calls do, misattributes silently (GPT review r1 #1): fixing that needs calls that carry their task.
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
import arena_analysis as AA  # noqa: E402
import helper_capture as HC  # noqa: E402

SCHEMA = "arena_task_spend/2"
# meter diagnostics that mean spend was LOST or may be on the wrong arm: blocking, the analysis reads UNMEASURED
# UNATTRIBUTED Claude spend that may be an arm's (under the arena root, arm not decidable); "outside" (a session
# outside the arena root) and cwd_mismatch (already in BLOCKING_DIAG) are not listed here
# tester_outside: an arm tester's session (cwd rt-*/tree) outside the capture; sandbox_foreign: a transcript in one
# clone's private sandbox HOME that ran in another clone (spend_census.claude_spend_by_arm)
PRE_WINDOW_S = 4 * 3600     # a tester started this long before the window is still metered (> 2x a pass timeout)
BLOCKING_UNATTRIBUTED = ("ambiguous", "unlisted", "tester_outside", "sandbox_foreign")
BLOCKING_DIAG = ("unreadable_files", "bad_lines", "cwd_mismatch", "gpt_unreadable", "id_conflicts")
SPAN_EXCLUDED_EVENTS = ("gate", "judge")
SPAN_END_EVENT = "pass_end"
CLAUDE_RAW = (("input", "in"), ("cache_read", "cr"), ("cache_write_5m", "c5"), ("cache_write_1h", "c1"),
              ("output", "out"))


def new_row():
    return {"claude": {}, "claude_ite": 0.0,
            "gpt": {"tokens": 0.0, "in_est": 0.0, "out_est": 0.0, "calls": 0, "est_calls": 0},
            "calls": 0, "ambiguous_calls": 0, "invalid_calls": 0}


def spans_of(recs):
    """[(start, end, task)] from an arm's accepted records: one span per EXECUTION of a (run_id, task). An execution
    runs from its first event to its `pass_end` (inclusive); a later event of the same (run_id, task) opens a new
    execution, so a reused run_id never stretches one span across the idle gap between two runs. An execution with
    no pass_end ends at its last event. Raises ValueError on a bad ts (the caller makes that arm's spend overhead,
    blocking)."""
    seq = []
    for i, r in enumerate(recs):
        t = r.get("task")
        if not isinstance(t, str) or not t or r.get("event") in SPAN_EXCLUDED_EVENTS:
            continue
        seq.append((L.ts_epoch(r.get("ts")), i, r.get("event") == SPAN_END_EVENT, r.get("run_id"), t))
    open_, out = {}, []
    for e, _i, is_end, rid, t in sorted(seq, key=lambda x: (x[0], x[1])):   # equal times keep signed (file) order
        k = (rid, t)
        lo = open_.get(k, (e,))[0]
        open_[k] = (lo, e)
        if is_end:
            out.append((lo, e, t))
            del open_[k]
    out.extend((lo, hi, t) for (_rid, t), (lo, hi) in open_.items())
    return sorted(out)


def tasks_at(spans, t):
    return {task for lo, hi, task in spans if lo <= t <= hi}


def _n(v):
    """A per-call raw count: a non-negative int (not a bool, not null). -> int, or None if invalid."""
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        return None
    return v


def _invalid(row):
    row["invalid_calls"] += 1
    row["calls"] += 1


def add_claude(row, c):
    """Each count is validated BEFORE it is summed (a bool or a negative would otherwise launder into a valid-looking
    total); a call with any invalid count adds nothing and marks the row `invalid_calls` (the analysis refuses it)."""
    vals = [(k, _n(c.get(ck))) for k, ck in CLAUDE_RAW]
    if any(v is None for _k, v in vals):
        return _invalid(row)
    m = row["claude"].setdefault(str(c.get("model") or "?"), {k: 0 for k, _ in CLAUDE_RAW})
    for k, v in vals:
        m[k] += v
    ite = c.get("ite")
    row["claude_ite"] += ite if isinstance(ite, (int, float)) and not isinstance(ite, bool) else 0.0
    row["calls"] += 1


def add_gpt(row, d):
    """Real codex tokens when tokens_used > 0, else the chars/4 in/out estimates (spend_census.gpt_ite_of's rule);
    every count is validated first, as in add_claude."""
    tu = d.get("tokens_used")
    tu = 0 if tu is None else _n(tu)            # null = codex reported no usage line: the estimates must stand in
    if tu is None:
        return _invalid(row)
    ie, oe = (_n(d.get("in_tok_est")), _n(d.get("out_tok_est"))) if tu == 0 else (0, 0)
    if ie is None or oe is None:
        return _invalid(row)
    g = row["gpt"]
    if tu > 0:
        g["tokens"] += tu
    else:
        g["in_est"] += ie
        g["out_est"] += oe
        g["est_calls"] += 1
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
    ambiguous, untimed = 0, defaultdict(int)
    for kind, items, add in (("claude", claude_calls, add_claude), ("gpt", gpt_calls, add_gpt)):
        for bucket, c in items:
            t = call_time(kind, c)
            if t is None:
                untimed[bucket] += 1
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
    blocking = ["%d metered call(s) of %s have no usable time: they cannot be placed in a task" % (n, b)
                for b, n in sorted(untimed.items())]
    return {"schema": SCHEMA, "arms": {a: dict(r) for a, r in arms.items()}, "overhead": dict(overhead),
            "flags": flags, "blocking": blocking}


def sandbox_homes(sandbox_root):
    """-> ([(projects dir, None, scratch name)], blocking) for every arm_sandbox private HOME under the scratch base
    (<base>/<clone>-<sha8>-<tag>/<role>/home/.claude/projects): builders' transcripts live there, not in ~/.claude.
    A symlinked or unreadable component on that path is BLOCKING (an arm could hide its home or point it at another's).
    A builder that deletes its own transcripts mid-session hides nothing: the harness's append-only copy
    <base>/<clone>/<role>.mirror/home (helper_capture.Mirror, never bound into the sandbox) is read here as one more
    home of the same scratch; message-id dedup makes the overlap with the live home harmless. A mirror that recorded a
    failure (its state's skipped list, or a `<role>.mirror.failed` marker: helper_capture.mirror_skipped) BLOCKS its
    scratch (ARENA_MIRROR_FAILURE_ENFORCE_SILENT_LOSS): the builder's erased spend may be missing from both homes."""
    out, blocking = [], []
    base = Path(sandbox_root)
    if not base.is_dir():
        return out, blocking
    try:
        scs = sorted(base.iterdir())
    except OSError as e:
        return out, ["sandbox scratch base %s unreadable (%s): builder spend UNMEASURED" % (base, e)]
    for sc in scs:
        if sc.is_symlink() or not sc.is_dir():
            blocking.append("sandbox scratch %s is a symlink or not a directory: UNMEASURED" % sc)
            continue
        try:
            roles = sorted(sc.iterdir())
        except OSError as e:
            blocking.append("sandbox scratch %s unreadable (%s): UNMEASURED" % (sc, e))
            continue
        for role in roles:
            if role.name.endswith(".mirror.failed") or (role.name.endswith(".mirror") and role.is_dir()
                                                        and not role.is_symlink()):
                failed = role.name.endswith(".failed")
                mdir = role.with_name(role.name[:-len(".failed")]) if failed else role
                bad = (HC.mirror_failures(mdir) if not mdir.is_dir() else []) if failed else HC.mirror_skipped(mdir)
                if bad:                         # (a marker beside its mirror dir is read with that dir)
                    blocking.append("sandbox spend mirror %s recorded %d failure(s) (%s): UNMEASURED"
                                    % (mdir, len(bad), "; ".join(bad)[:300]))
                if role.name.endswith(".failed"):
                    continue
            pj = role / "home" / ".claude" / "projects"
            chain = (role, role / "home", role / "home" / ".claude", pj)
            if any(x.is_symlink() for x in chain):
                blocking.append("sandbox home %s has a symlinked component: UNMEASURED" % pj)
            elif pj.is_dir():
                out.append((str(pj), None, sc.name))
    return out, blocking


def tester_captures(arm_logs, helpers, since, until):
    """For every MODEL tester the arms' logs say started in the window or up to PRE_WINDOW_S before it (test_start; a detail "model": false runner such as
    ralph_c's live-lane proof runner is exempt): its helper_capture manifest. -> (claude extra roots, gpt dirs
    [(dir, arm)], blocking). A missing/foreign manifest, skipped files or no Claude transcript at all is BLOCKING."""
    extra, gdirs, blocking = [], [], []
    for arm, lg in sorted((arm_logs or {}).items()):
        for r in lg.get("recs", ()):
            if r.get("event") != "test_start":
                continue
            det = r.get("detail") if isinstance(r.get("detail"), dict) else {}
            if det.get("model") is False:
                continue
            try:
                t = L.ts_epoch(r.get("ts"))
            except (ValueError, TypeError):
                t = None
            if t is not None and t >= until:
                continue
            if t is not None and since - t > PRE_WINDOW_S:
                continue                     # a start up to PRE_WINDOW_S before the window may spend inside it
            who = "arm %s tester %s (test_start %s, task %s)" % (arm, det.get("tester"), r.get("ts"), r.get("task"))
            man, d = HC.load(r, helpers)
            if man is None:
                blocking.append("%s ran but its spend is not captured (%s): UNMEASURED" % (who, d))
                continue
            if man.get("skipped"):
                blocking.append("%s: capture skipped %d file(s) (%s): UNMEASURED"
                                % (who, len(man["skipped"]), "; ".join(man["skipped"])[:300]))
            if not man.get("claude_files"):
                blocking.append("%s: capture holds no Claude transcript: UNMEASURED" % who)
            extra.append((str(d / "claude"), arm, None))
            if man.get("gpt_files"):
                gdirs.append((str(d / "gpt") + "/", arm))
    return extra, gdirs, blocking


def meter(arm_logs, *, projects=None, clones_root=None, gpt_log=None, since=None, until=None, helpers=None,
          sandbox_root=None):
    """Run the meter over the window with sinks. Window defaults to the logs' first..last event (inclusive).
    helpers: tester captures (default helper_capture.root()); sandbox_root: arm_sandbox scratch base (default
    $RM_ARM_SANDBOX_SCRATCH or <arena root>/sandbox)."""
    if since is None or until is None:
        ts = [L.ts_epoch(r["ts"]) for lg in arm_logs.values() for r in lg.get("recs", ())
              if isinstance(r.get("ts"), str)]
        since = min(ts) if since is None and ts else since
        until = (max(ts) + 1e-3) if until is None and ts else until
    if since is None or until is None:
        raise ValueError("no event times to derive a window from: pass --since and --until")
    if helpers is None:
        helpers = HC.root()
    if sandbox_root is None:
        import arena_replay as R
        sandbox_root = os.environ.get("RM_ARM_SANDBOX_SCRATCH") or (R.arena_root() / "sandbox")
    extra, gdirs, cap_blocking = tester_captures(arm_logs, helpers, since, until)
    homes, home_blocking = sandbox_homes(sandbox_root)
    cl, gp, diag = [], [], {}
    by_arm = S.claude_spend_by_arm(projects=projects, arms=sorted(arm_logs), arena_root=clones_root, since=since,
                                   until=until, diag=diag, sink=lambda arm, c: cl.append((arm, c)),
                                   extra=extra + homes)
    S.gpt_spend_by_arm(gpt_log, since=since, until=until, diag=diag, sink=lambda arm, d: gp.append((arm, d)))
    for gdir, arm in gdirs:
        gd = {}
        S.gpt_spend_by_arm(gdir, since=since, until=until, diag=gd, sink=lambda a, d: gp.append((a, d)),
                           forced_arm=arm)
        if gd.get("gpt_unreadable"):
            diag["gpt_unreadable"] = (diag.get("gpt_unreadable") or 0) + gd["gpt_unreadable"]
    doc = attribute(arm_logs, cl, gp)
    doc["blocking"].extend(cap_blocking + home_blocking)
    doc["window"] = {"since": since, "until": until}
    for k in BLOCKING_DIAG:
        v = diag.get(k)
        if v:
            doc["blocking"].append("meter %s: %s" % (k, len(v) if isinstance(v, (list, dict)) else v))
    for why, ite in sorted(((by_arm or {}).get(S.UNATTRIBUTED) or {}).get("reasons", {}).items()):
        if why in BLOCKING_UNATTRIBUTED and ite:
            doc["blocking"].append("meter UNATTRIBUTED %s: %s ITE of Claude spend under the arena root on no one arm"
                                   % (why, ite))
    doc["logs"] = AA.spend_log_binding(arm_logs)
    return doc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw-dir", help="read unsigned <arm>.jsonl from this dir instead of the signed log")
    ap.add_argument("--allow-untrusted", action="store_true", help="meter untrusted signed logs (drops the tamper "
                    "check; reported in the doc's log_trust)")
    ap.add_argument("--ledger", help="rimflow events.jsonl holding the ARENA_ANCHOR notes (default: the repo ledger; "
                    "arena_analysis.ledger_external)")
    ap.add_argument("--projects", help="Claude transcripts root (default ~/.claude/projects)")
    ap.add_argument("--clones-root", help="arm clones root (default $RM_ARENA_ROOT or %s)" % S.ARENA_ROOT)
    ap.add_argument("--gpt-log", help="gpt call log file/dir (default gpt_call_log's)")
    ap.add_argument("--helpers", help="tester spend captures (default $ARENA_METER_HELPERS or <arena root>/meter_helpers)")
    ap.add_argument("--sandbox-root", help="arm_sandbox scratch base (default $RM_ARM_SANDBOX_SCRATCH or <arena root>/sandbox)")
    ap.add_argument("--since", help="ISO-8601 with zone (default: first event)")
    ap.add_argument("--until", help="ISO-8601 with zone (default: last event)")
    a = ap.parse_args(argv)
    logs, log_trust = AA.verified_logs(a.raw_dir, a.ledger, a.allow_untrusted)
    try:
        doc = meter(logs, projects=a.projects, clones_root=a.clones_root, gpt_log=a.gpt_log, helpers=a.helpers,
                    sandbox_root=a.sandbox_root,
                    since=L.ts_epoch(a.since) if a.since else None, until=L.ts_epoch(a.until) if a.until else None)
    except ValueError as e:
        unm = {k: v["unmeasured"] for k, v in sorted(logs.items()) if "unmeasured" in v}
        print("arena_spend: %s%s" % (e, "; UNMEASURED arm log(s) %s (ledger %s)" % (unm, log_trust.get("status"))
                                     if unm else ""), file=sys.stderr)
        return 2
    doc["log_trust"] = log_trust
    tmp = a.out + ".tmp"
    Path(tmp).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, a.out)
    print(json.dumps({"arms": {k: len(v) for k, v in doc["arms"].items()}, "overhead": sorted(doc["overhead"]),
                      "flags": doc["flags"], "log_trust": log_trust}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
