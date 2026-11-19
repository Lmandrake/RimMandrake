#!/usr/bin/env python3
"""obs_report.py - the bridge validation observatory's first slice: ONE run, folded after the fact
(RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST; design/RimMandrake/bridge_validation_observatory.md).

    python3 src/RimMandrake/Utils/modcheck/obs_report.py <run-id> [--log PATH ...] [--mod Mod] [--results GLOB]
                                                         [--out report.md] [--json]

The run stream already exists: rimbridge_client.py appends a start and an end event per call (cid, run, script, tool,
mutating, t, ms) to <agent storage>/rimmandrake/scratch/bridge_calls.jsonl, rotated to .1 (measured 2026-11-18: 38k calls
over 2026-11-12..17). This tool adds nothing to the run; it reads that stream and the run's own verdict.

Line 1 is the owner's ruling (by card 2026-10-03): REQUIRED CHECKS PROVEN, from required_checks_report.py (the normative
rules, design section 2.4), for the mod whose checkout script made the run. It is the count of THIS run only when the
mod's newest live result started inside the run's window; otherwise it reads UNMEASURED for this run and names the
result it could see. Below it: findings (new / recurring / resolved, this run's result against the previous live one)
and where the bridge time went (tick calls, reads, writes, waits between calls). No LLM, no quota, and the report never
gates a run: it exits 0 whatever the checks say.

Exit codes: 0 report written · 2 the log holds no call of that run (could not look) · 3 no bridge call log could be read.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
MANIFEST = os.path.join(HERE, "required_checks.json")
TICK_RE = re.compile(r"step_game_ticks|safe_advance|advance|_ticks$")
WINDOW_SLACK_S = 10           # a result's start may lead the run's first logged call by this much, and never into another run


def default_logs():
    import rmpaths
    p = str(rmpaths.rm_path("scratch", "bridge_calls.jsonl"))
    return [p + ".1", p]


def _utc(s):
    """An ISO time -> aware UTC, or None when absent or unreadable. A naive time is LOCAL (proof_all.py writes `started`
    with time.strftime)."""
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return t.astimezone(dt.timezone.utc) if t.tzinfo else t.astimezone().astimezone(dt.timezone.utc)


def fold(run_id, logs):
    """-> (calls, skipped, readable, others). calls: one dict per call of the run (start fields + ms/outcome when it
    ended); skipped: unreadable lines (bad JSON or time); readable: logs read to the end; others: {run: [t0, t1, script]}
    of every OTHER run, so a result inside another run's window is never taken for this one."""
    starts, ends, skipped, readable, others, other_cid = {}, {}, 0, [], {}, {}
    for p in logs:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        e = json.loads(line)
                    except ValueError:
                        skipped += 1
                        continue
                    if not isinstance(e, dict) or _utc(e.get("t")) is None:
                        skipped += 1
                        continue
                    if e.get("ev") == "start":
                        if e.get("run") == run_id:
                            starts[e.get("cid")] = e
                        else:
                            o = others.setdefault(e.get("run"), [e["t"], e["t"], e.get("script")])
                            o[0], o[1] = min(o[0], e["t"]), max(o[1], e["t"])
                            other_cid[e.get("cid")] = e.get("run")
                    elif e.get("ev") == "end":
                        ends[e.get("cid")] = e
                        r = other_cid.get(e.get("cid"))
                        if r in others:              # another run's window runs to its last END, not its last start
                            others[r][1] = max(others[r][1], e["t"])
            readable.append(p)
        except OSError:
            continue                              # not readable (or not to the end): not counted as read
    calls = []
    for cid, st in starts.items():
        c = dict(st)
        en = ends.get(cid)
        c["ms"] = en.get("ms") if en else None
        c["outcome"] = en.get("outcome") if en else None
        c["t_end"] = en.get("t") if en else None
        calls.append(c)
    calls.sort(key=lambda c: c.get("t") or "")
    return calls, skipped, readable, others


def split(calls):
    sp = {"calls": len(calls), "unanswered": 0, "ticks_ms": 0, "reads_ms": 0, "writes_ms": 0, "tick_calls": 0}
    by_tool = {}
    for c in calls:
        if c["ms"] is None:
            sp["unanswered"] += 1
            continue
        by_tool[c.get("tool")] = by_tool.get(c.get("tool"), 0) + c["ms"]
        if TICK_RE.search(str(c.get("tool") or "")):
            sp["ticks_ms"] += c["ms"]
            sp["tick_calls"] += 1
        elif c.get("mutating"):
            sp["writes_ms"] += c["ms"]
        else:
            sp["reads_ms"] += c["ms"]
    times = [_utc(c.get("t")) for c in calls] + [_utc(c.get("t_end")) for c in calls if c.get("t_end")]
    times = [t for t in times if t]
    sp["wall_ms"] = int((max(times) - min(times)).total_seconds() * 1000) if times else None
    # waits: wall minus in-call time. The log's times have 1-second resolution, so an interval union would merge every
    # short call ending in the same second (measured 2026-11-18: busy 80 s against 241 s of call time on run
    # 4d0e9a2ae543); the client is serial, so the sum of call ms is the busy time. Calls that overlap (the sum exceeds
    # the wall) or a call that went unanswered make waits unknown, with the cause, never a negative or guessed number.
    sp["busy_ms"] = sp["ticks_ms"] + sp["reads_ms"] + sp["writes_ms"]
    sp["waits_cause"] = None
    if sp["wall_ms"] is None:
        sp["waits_ms"], sp["waits_cause"] = None, "no readable times"
    elif sp["unanswered"]:
        sp["waits_ms"], sp["waits_cause"] = None, "%d call(s) went unanswered, so their span is unknown" % sp["unanswered"]
    elif sp["busy_ms"] > sp["wall_ms"] + 1000:
        sp["waits_ms"], sp["waits_cause"] = None, "calls overlapped (%s of call time in %s of wall)" % (_s(sp["busy_ms"]), _s(sp["wall_ms"]))
    else:
        sp["waits_ms"] = max(0, sp["wall_ms"] - sp["busy_ms"])
    sp["top_tools"] = sorted(by_tool.items(), key=lambda kv: -kv[1])[:5]
    sp["t0"] = min(times).isoformat() if times else None
    sp["t1"] = max(times).isoformat() if times else None
    return sp


def owns(run_id, script, started, bridge_run, t0, t1, others):
    """-> (yes, how). A result is THIS run's when it carries our bridge_run; never when it carries another; without one,
    when it started inside our window (WINDOW_SLACK_S before the first call at most) and inside no other run of the
    same script."""
    if bridge_run:
        return (bridge_run == run_id), "bridge_run %s" % bridge_run
    if started is None:
        return False, "no readable start time"
    if not (t0 - dt.timedelta(seconds=WINDOW_SLACK_S) <= started <= t1):
        return False, "started outside the run window"
    for r, (a, b, scr) in others.items():
        if scr == script and _utc(a) - dt.timedelta(seconds=WINDOW_SLACK_S) <= started <= _utc(b):
            return False, "started inside run %s of the same script" % r
    return True, "joined by time window"


def mod_for_script(script, manifest_path=MANIFEST):
    """-> (mod, cause): the one mod whose checkout script is `script`; (None, why) otherwise."""
    try:
        mods = json.load(open(manifest_path, encoding="utf-8")).get("mods") or {}
    except (OSError, ValueError) as ex:
        return None, "the required-check manifest could not be read: %s" % ex
    hit = [m for m, v in mods.items() if os.path.basename(((v or {}).get("checkout") or {}).get("script") or "") == script]
    if len(hit) == 1:
        return hit[0], None
    if not hit:
        return None, "the run's script %s is no mod's checkout script in the required-check manifest" % script
    return None, "the run's script %s is the checkout of several mods: %s" % (script, ", ".join(hit))


def real_required(mod):
    import required_checks_report as R
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    report, _ = R.build_report(manifest, R.RECORDS, R.AMEND, None, mod)
    return report[0] if report else None


def _rows(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d, {r.get("id"): r.get("status") for r in (d.get("rows") or []) if isinstance(r, dict) and r.get("id")}


def findings(result_glob, run_id, script, t0, t1, others):
    """New / recurring / resolved non-PASS rows: this run's live result against the live one before it. A finding is
    resolved only when the current result records that check PASS; a check now absent is `absent`, never resolved."""
    live, unreadable = [], []
    for p in sorted(glob.glob(result_glob)) if result_glob else []:
        try:
            d, rows = _rows(p)
        except (OSError, ValueError) as ex:
            unreadable.append("%s (%s)" % (p, type(ex).__name__))
            continue
        if d.get("mode") != "live":
            continue
        st = _utc(d.get("started"))
        if st is None:
            unreadable.append("%s (no readable start time)" % p)
            continue
        live.append((st, p, rows, d.get("bridge_run")))
    live.sort(key=lambda x: x[0])
    mine = [x for x in live if owns(run_id, script, x[0], x[3], t0, t1, others)[0]]
    if unreadable:
        return {"status": "UNMEASURED: result file(s) could not be read, so no comparison is trustworthy: " + "; ".join(unreadable)}
    if not mine:
        return {"status": "UNMEASURED for this run: no live result of it"
                          + ((" (newest live result: %s)" % live[-1][1]) if live else " (no live result found)")}
    cur = mine[-1]
    if not cur[2]:
        return {"status": "UNMEASURED: this run's result %s records no rows" % cur[1]}
    prev = [x for x in live if x[0] < cur[0]]
    now = {k for k, v in cur[2].items() if v != "PASS"}
    if not prev:
        return {"status": "ran", "result": cur[1], "previous": None, "new": sorted(now), "recurring": [], "resolved": [], "absent": []}
    before = {k for k, v in prev[-1][2].items() if v != "PASS"}
    return {"status": "ran", "result": cur[1], "previous": prev[-1][1], "new": sorted(now - before),
            "recurring": sorted(now & before), "resolved": sorted(k for k in before if cur[2].get(k) == "PASS"),
            "absent": sorted(k for k in before if k not in cur[2])}


def build(run_id, logs, mod=None, required=real_required, result_glob=None):
    calls, skipped, readable, others = fold(run_id, logs)
    rep = {"run": run_id, "logs": logs, "logs_readable": len(readable), "logs_unread": [p for p in logs if p not in readable],
           "skipped_lines": skipped, "calls": len(calls)}
    if not calls:
        return rep
    scripts = sorted({c.get("script") for c in calls if c.get("script")})
    rep["script"] = scripts[0] if len(scripts) == 1 else ",".join(scripts)
    rep["split"] = sp = split(calls)
    if mod:
        rep["mod"], cause = mod, None
    else:
        rep["mod"], cause = mod_for_script(rep["script"])
    t0, t1 = _utc(sp["t0"]), _utc(sp["t1"])
    if rep["mod"] is None:
        rep["required"] = {"status": "UNMEASURED", "cause": cause}
    else:
        try:
            e = required(rep["mod"])
        except Exception as ex:                       # noqa: BLE001 - the report could not be built: say so, never a count
            e, cause = None, "required_checks_report failed: %s: %s" % (type(ex).__name__, ex)
        ck = (e or {}).get("checkout") or {}
        started = _utc((ck.get("ident") or {}).get("started"))
        head = (e or {}).get("head") or {}
        br = None
        if ck.get("path"):
            try:
                with open(os.path.join(REPO, ck["path"]) if not os.path.isabs(ck["path"]) else ck["path"], encoding="utf-8") as f:
                    br = json.load(f).get("bridge_run")
            except (OSError, ValueError):
                br = None
        mine, how = owns(run_id, rep["script"], started, br, t0, t1, others)
        if e is None:
            rep["required"] = {"status": "UNMEASURED", "cause": cause or "required_checks_report has no entry for %s" % rep["mod"]}
        elif not mine:
            rep["required"] = {"status": "UNMEASURED", "cause": "no result of this run (%s); the newest live result is %s (started %s): %s of %s there"
                               % (how, ck.get("path"), started.isoformat() if started else "unknown", head.get("proven"), head.get("required"))}
        else:
            rep["required"] = {"status": "ran", "proven": head.get("proven"), "required": head.get("required"), "joined": how,
                               "proven_pass": head.get("proven_pass"), "proven_fail": head.get("proven_fail"), "result": ck.get("path")}
        if result_glob is None and ck.get("path"):
            result_glob = os.path.join(REPO, os.path.dirname(ck["path"]), os.path.basename(ck["path"]).split("_2")[0] + "_*.json")
    rep["findings"] = findings(result_glob, run_id, rep["script"], t0, t1, others)
    return rep


def _s(ms):
    return "unknown" if ms is None else "%.1f s" % (ms / 1000.0)


def render(rep):
    rq = rep.get("required") or {}
    if rq.get("status") == "ran":
        first = "required checks proven: %s of %s (%s PASS, %s FAIL; result %s)" % (
            rq["proven"], rq["required"], rq.get("proven_pass"), rq.get("proven_fail"), rq.get("result"))
    else:
        first = "required checks proven: UNMEASURED for this run (%s)" % rq.get("cause", "no required-check reading")
    L = [first, "", "run %s, script %s, mod %s, %d calls" % (rep["run"], rep.get("script"), rep.get("mod"), rep["calls"])]
    fi = rep.get("findings") or {}
    if fi.get("status") == "ran":
        L.append("findings vs %s: new %s; recurring %s; resolved %s; absent now %s" % (
            fi.get("previous") or "(no earlier live result)", fi["new"] or "[]", fi["recurring"] or "[]", fi["resolved"] or "[]",
            fi.get("absent") or "[]"))
    else:
        L.append("findings: %s" % fi.get("status", "UNMEASURED"))
    sp = rep.get("split") or {}
    w = sp.get("wall_ms")
    pct = lambda ms: "" if not w or ms is None else " (%d%%)" % round(100.0 * ms / w)  # noqa: E731
    L.append("bridge time (diagnostic, never a target): wall %s; ticks %s%s in %d call(s); reads %s%s; writes %s%s; "
             "waits between calls %s%s; unanswered calls %d" % (
                 _s(w), _s(sp.get("ticks_ms")), pct(sp.get("ticks_ms")), sp.get("tick_calls", 0), _s(sp.get("reads_ms")),
                 pct(sp.get("reads_ms")), _s(sp.get("writes_ms")), pct(sp.get("writes_ms")), _s(sp.get("waits_ms")),
                 pct(sp.get("waits_ms")), sp.get("unanswered", 0)))
    if sp.get("top_tools"):
        L.append("most in-call time: " + "; ".join("%s %s%s" % (t, _s(ms), pct(ms)) for t, ms in sp["top_tools"]))
    if sp.get("waits_cause"):
        L.append("waits are unknown: %s" % sp["waits_cause"])
    if rep.get("skipped_lines"):
        L.append("log lines skipped as unreadable: %d" % rep["skipped_lines"])
    if rep.get("logs_unread"):
        L.append("logs not read: %s" % ", ".join(rep["logs_unread"]))
    return "\n".join(L)


def main(argv=None, required=real_required):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run")
    ap.add_argument("--log", action="append", help="a bridge call log (repeatable; default the live log and its .1)")
    ap.add_argument("--mod")
    ap.add_argument("--results", help="glob of the mod's result files (default: beside its checkout result)")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    logs = a.log or default_logs()
    rep = build(a.run, logs, a.mod, required, a.results)
    if not rep["logs_readable"]:
        print("could not report: no bridge call log could be read (%s)" % ", ".join(logs))
        return 3
    if not rep["calls"]:
        print("could not look: the bridge call log holds no call of run %s (%s)" % (a.run, ", ".join(logs)))
        return 2
    text = json.dumps(rep, indent=1, default=str) if a.json else render(rep)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
