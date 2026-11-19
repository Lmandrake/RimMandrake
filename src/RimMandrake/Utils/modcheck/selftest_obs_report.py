#!/usr/bin/env python3
"""Selftest: obs_report.py, the observatory's first slice (RIMMANDRAKE_BUILD_OBSERVATORY_SMALL_PROVEN_FIRST).

A synthetic bridge call log (the shape rimbridge_client.py writes) and synthetic result files; no game, no bridge. Proves:
  R1  a run id the log does not hold is "could not look" (exit 2), and no report file is written
  R2  the time split: tick calls, reads, writes and waits (wall minus in-call time) in ms; a call with no end is counted
      as unanswered, never as 0 ms
  R3  line 1 is "required checks proven: P of R" when a result of THIS run exists (it carries this run's bridge_run);
      a result that only STARTED inside the window, with no bridge_run, is UNMEASURED for this run
  R4  a newest result from another run makes line 1 UNMEASURED for this run, naming that result; never its count as ours
  R5  a script that names no mod with a required-check manifest is UNMEASURED with that cause
  R6  findings: new / recurring / resolved, this run's result against the previous live one
  R7  an unreadable log line is skipped and counted; a missing log is exit 3, a cause of its own
  R8  the report never gates: a run with proven FAILs still exits 0
  R9  (Codex review 2026-11-18) a result started just before the run, inside a predecessor run of the same script, is
      never ours; a result carrying our bridge_run is ours, one carrying another run's never; overlapping calls make
      waits unknown with the cause (never negative); a check absent from the current result is "absent", never resolved; an
      unreadable result file makes the comparison UNMEASURED; a log that cannot be read to the end is not "read"
All of it runs under TZ=America/Los_Angeles, so reading a naive local start as UTC would fail.
Run: python3 src/RimMandrake/Utils/modcheck/selftest_obs_report.py
"""
import io
import json
import os
import sys
import tempfile
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import obs_report as O  # noqa: E402

FAILS = []
os.environ["TZ"] = "America/Los_Angeles"
time_mod = __import__("time")
time_mod.tzset()


def local(utc):
    """A naive LOCAL time string, as proof_all.py writes `started`, for a UTC instant."""
    import datetime as dt
    return dt.datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).astimezone().replace(tzinfo=None).isoformat()


def check(name, ok, detail=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else detail))
    if not ok:
        FAILS.append(name)


def ev(cid, e, t, **kw):
    d = {"cid": cid, "ev": e, "t": t}
    d.update(kw)
    return d


def make_log(path):
    run, scr = "aaaaaaaaaaaa", "proof_all.py"
    lines = [
        ev("c1", "start", "2026-11-17T10:00:00Z", run=run, script=scr, tool="rimworld/step_game_ticks", mutating=True),
        ev("c1", "end", "2026-11-17T10:00:10Z", ms=10000, outcome="ok"),
        ev("c2", "start", "2026-11-17T10:00:20Z", run=run, script=scr, tool="jawa/list_things", mutating=False),
        ev("c2", "end", "2026-11-17T10:00:22Z", ms=2000, outcome="ok"),
        ev("c3", "start", "2026-11-17T10:00:30Z", run=run, script=scr, tool="jawa/spawn_batch", mutating=True),
        ev("c3", "end", "2026-11-17T10:00:35Z", ms=5000, outcome="ok"),
        ev("c4", "start", "2026-11-17T10:00:40Z", run=run, script=scr, tool="jawa/safe_advance", mutating=True),
        ev("c4", "end", "2026-11-17T10:00:50Z", ms=10000, outcome="ok"),
        ev("c5", "start", "2026-11-17T10:00:55Z", run=run, script=scr, tool="jawa/map_info", mutating=False),
        ev("x1", "start", "2026-11-17T10:00:01Z", run="bbbbbbbbbbbb", script="other.py", tool="jawa/map_info", mutating=False),
        ev("x1", "end", "2026-11-17T10:00:02Z", ms=1000, outcome="ok"),
    ]
    with open(path, "w") as f:
        for d in lines:
            f.write(json.dumps(d) + "\n")
        f.write("{not json\n")
    return run


def rcr(started, proven=3, required=5, path="proof_all_X.json"):
    """A fake required_checks_report entry for GimmeSomeSlack."""
    return lambda mod: {"mod": mod, "head": {"required": required, "proven": proven, "proven_pass": proven - 1, "proven_fail": 1},
                        "checkout": {"path": path, "ident": {"started": started}}}


def results(d):
    a = {"mod": "GimmeSomeSlack", "mode": "live", "started": local("2026-11-16T09:00:00Z"),
         "rows": [{"id": "A", "status": "FAIL"}, {"id": "B", "status": "UNMEASURED"}, {"id": "C", "status": "PASS"}]}
    b = {"mod": "GimmeSomeSlack", "mode": "live", "started": local("2026-11-17T10:00:00Z"), "bridge_run": "aaaaaaaaaaaa",
         "rows": [{"id": "A", "status": "FAIL"}, {"id": "B", "status": "PASS"}, {"id": "C", "status": "PASS"}, {"id": "D", "status": "FAIL"}]}
    pa, pb = os.path.join(d, "proof_all_20261116T090000.json"), os.path.join(d, "proof_all_20261117T100000.json")
    json.dump(a, open(pa, "w"))
    json.dump(b, open(pb, "w"))
    return pa, pb


def run(argv, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = O.main(argv, **kw)
    return code, buf.getvalue()


def main():
    d = tempfile.mkdtemp()
    log = os.path.join(d, "bridge_calls.jsonl")
    rid = make_log(log)
    pa, pb = results(d)
    out = os.path.join(d, "rep.md")

    code, txt = run(["zzzzzzzzzzzz", "--log", log, "--out", out], required=rcr(local("2026-11-17T10:00:00Z")))
    check("R1 an unknown run is could-not-look, exit 2, nothing written", code == 2 and "could not look" in txt and not os.path.exists(out), (code, txt))

    rep = O.build(rid, [log], required=rcr(local("2026-11-17T10:00:00Z"), path=pb), result_glob=os.path.join(d, "proof_all_*.json"))
    sp = rep["split"]
    check("R2 tick, read and write ms", sp["ticks_ms"] == 20000 and sp["reads_ms"] == 2000 and sp["writes_ms"] == 5000, sp)
    check("R2 wall, and waits unknown while a call went unanswered", sp["wall_ms"] == 55000 and sp["waits_ms"] is None and sp["busy_ms"] == 27000, sp)
    folded = O.fold(rid, [log])[0]
    check("R2 an unanswered call is counted, its ms None (never 0)", sp["unanswered"] == 1 and sp["calls"] == 5
          and [c["ms"] for c in folded if c["cid"] == "c5"] == [None], sp)
    check("R2 a naive start is LOCAL (America/Los_Angeles here)", O._utc("2026-11-17T02:00:00").isoformat() == "2026-11-17T10:00:00+00:00",
          O._utc("2026-11-17T02:00:00"))
    check("R2 another run's calls are not ours", rep["script"] == "proof_all.py" and rep["mod"] == "GimmeSomeSlack", rep.get("script"))
    first = O.render(rep).splitlines()[0]
    check("R3 line 1 is required checks proven, P of R", first.startswith("required checks proven: 3 of 5") and pb in first, first)

    pw = os.path.join(d, "window_only.json")
    json.dump({"mode": "live", "started": local("2026-11-17T10:00:00Z"), "rows": []}, open(pw, "w"))
    f3 = O.render(O.build(rid, [log], required=rcr(local("2026-11-17T10:00:00Z"), path=pw), result_glob=os.path.join(d, "none_*.json"))).splitlines()[0]
    check("R3 a window-only result (no bridge_run) is UNMEASURED for this run", f3.startswith("required checks proven: UNMEASURED")
          and "names no bridge_run" in f3, f3)
    rep4 = O.build(rid, [log], required=rcr("2026-11-07T03:10:35", path="proof_all_20261107T031035.json"), result_glob=os.path.join(d, "none_*.json"))
    f4 = O.render(rep4).splitlines()[0]
    check("R4 another run's result: UNMEASURED for this run, never its count", f4.startswith("required checks proven: UNMEASURED")
          and "proof_all_20261107T031035.json" in f4 and "3 of 5" not in f4.split("(")[0], f4)

    log5 = os.path.join(d, "l5.jsonl")
    with open(log5, "w") as f:
        f.write(json.dumps(ev("c1", "start", "2026-11-17T10:00:00Z", run="cccccccccccc", script="random_probe.py", tool="jawa/map_info", mutating=False)) + "\n")
        f.write(json.dumps(ev("c1", "end", "2026-11-17T10:00:01Z", ms=1000)) + "\n")
    f5 = O.render(O.build("cccccccccccc", [log5], required=rcr(local("2026-11-17T10:00:00Z")))).splitlines()[0]
    check("R5 no mod for the script is UNMEASURED with its cause", f5.startswith("required checks proven: UNMEASURED") and "random_probe.py" in f5, f5)

    fi = rep["findings"]
    check("R6 new / recurring / resolved", fi.get("new") == ["D"] and fi.get("recurring") == ["A"] and fi.get("resolved") == ["B"], fi)
    check("R6 findings are UNMEASURED for a run without its own result", rep4["findings"].get("status", "").startswith("UNMEASURED"), rep4["findings"])

    check("R7 an unreadable line is skipped and counted", rep["skipped_lines"] == 1, rep.get("skipped_lines"))
    code7, txt7 = run([rid, "--log", os.path.join(d, "nope.jsonl"), "--out", out], required=rcr(local("2026-11-17T10:00:00Z")))
    check("R7 a missing log is exit 3 with its cause", code7 == 3 and "no bridge call log" in txt7 and not os.path.exists(out), (code7, txt7))

    code8, txt8 = run([rid, "--log", log, "--out", out, "--results", os.path.join(d, "proof_all_*.json")],
                      required=rcr(local("2026-11-17T10:00:00Z"), path=pb))
    check("R8 never gates: exit 0 with a proven FAIL, report written", code8 == 0 and os.path.exists(out)
          and open(out).read().splitlines()[0].startswith("required checks proven:"), (code8, txt8[:200]))
    # R9 predecessor, bridge_run, overlap, absent, unreadable result, unreadable log
    log9 = os.path.join(d, "l9.jsonl")
    with open(log9, "w") as f:
        for e in [ev("p1", "start", "2026-11-17T09:50:00Z", run="pppppppppppp", script="proof_all.py", tool="jawa/map_info", mutating=False),
                  ev("p1", "end", "2026-11-17T09:59:55Z", ms=1000),
                  ev("o1", "start", "2026-11-17T10:00:00Z", run=rid, script="proof_all.py", tool="jawa/a", mutating=False),
                  ev("o2", "start", "2026-11-17T10:00:05Z", run=rid, script="proof_all.py", tool="jawa/b", mutating=False),
                  ev("o1", "end", "2026-11-17T10:00:10Z", ms=10000), ev("o2", "end", "2026-11-17T10:00:15Z", ms=10000)]:
            f.write(json.dumps(e) + "\n")
    r9 = O.build(rid, [log9], required=rcr(local("2026-11-17T09:59:52Z")), result_glob=os.path.join(d, "none_*.json"))
    check("R9 a result inside a predecessor's window is never ours", r9["required"]["status"] == "UNMEASURED"
          and "pppppppppppp" in r9["required"]["cause"], r9["required"])
    check("R9 overlapping calls make waits unknown with the cause, never negative", r9["split"]["waits_ms"] is None
          and "overlapped" in (r9["split"]["waits_cause"] or ""), r9["split"])
    d9 = tempfile.mkdtemp()
    mine = {"mod": "GimmeSomeSlack", "mode": "live", "started": "2026-01-01T00:00:00", "bridge_run": rid, "rows": [{"id": "A", "status": "PASS"}]}
    other = {"mod": "GimmeSomeSlack", "mode": "live", "started": local("2026-11-17T10:00:03Z"), "bridge_run": "qqqqqqqqqqqq",
             "rows": [{"id": "A", "status": "FAIL"}]}
    json.dump(mine, open(os.path.join(d9, "proof_all_1.json"), "w"))
    json.dump(other, open(os.path.join(d9, "proof_all_2.json"), "w"))
    f9 = O.findings(os.path.join(d9, "proof_all_*.json"), rid, "proof_all.py", O._utc("2026-11-17T10:00:00Z"), O._utc("2026-11-17T10:00:15Z"), {})
    check("R9 bridge_run links a result whatever its start; another run's bridge_run never", f9.get("result", "").endswith("proof_all_1.json"), f9)
    d10 = tempfile.mkdtemp()
    json.dump({"mode": "live", "started": local("2026-11-16T09:00:00Z"), "rows": [{"id": "A", "status": "FAIL"}, {"id": "B", "status": "FAIL"}]},
              open(os.path.join(d10, "proof_all_a.json"), "w"))
    json.dump({"mode": "live", "started": local("2026-11-17T10:00:00Z"), "bridge_run": rid, "rows": [{"id": "A", "status": "PASS"}]},
              open(os.path.join(d10, "proof_all_b.json"), "w"))
    f10 = O.findings(os.path.join(d10, "proof_all_*.json"), rid, "proof_all.py", O._utc("2026-11-17T10:00:00Z"), O._utc("2026-11-17T10:00:55Z"), {})
    check("R9 a check absent now is absent, never resolved", f10.get("resolved") == ["A"] and f10.get("absent") == ["B"], f10)
    open(os.path.join(d10, "proof_all_c.json"), "w").write("{broken")
    f11 = O.findings(os.path.join(d10, "proof_all_*.json"), rid, "proof_all.py", O._utc("2026-11-17T10:00:00Z"), O._utc("2026-11-17T10:00:55Z"), {})
    check("R9 an unreadable result makes the comparison UNMEASURED, naming it", f11.get("status", "").startswith("UNMEASURED") and "proof_all_c.json" in f11["status"], f11)
    r12 = O.build(rid, [d10, log], required=rcr(local("2026-11-17T10:00:00Z")))
    check("R9 a log that cannot be read (a directory) is not counted as read", r12["logs_readable"] == 1 and r12["logs_unread"] == [d10], r12.get("logs_unread"))
    log13 = os.path.join(d, "l13.jsonl")
    with open(log13, "w") as f:
        for e in [ev("u1", "start", "2026-11-17T10:00:00Z", run=rid, script="proof_all.py", tool="jawa/a", mutating=False),
                  ev("u2", "start", "2026-11-17T10:00:02Z", run=rid, script="proof_all.py", tool="jawa/b", mutating=False),
                  ev("u2", "end", "2026-11-17T10:00:03Z", ms=1000),
                  ev("u3", "start", "2026-11-17T10:00:20Z", run=rid, script="proof_all.py", tool="jawa/c", mutating=False),
                  ev("u3", "end", "2026-11-17T10:00:21Z", ms=1000)]:
            f.write(json.dumps(e) + "\n")
    s13 = O.split(O.fold(rid, [log13])[0])
    check("R9 an unanswered call spanning later calls makes waits unknown, never known", s13["waits_ms"] is None
          and "unanswered" in (s13["waits_cause"] or ""), s13)
    log14 = os.path.join(d, "l14.jsonl")
    with open(log14, "w") as f:
        for e in [ev("v1", "start", "2026-11-17T10:00:00Z", run=rid, script="proof_all.py", tool="jawa/a", mutating=False),
                  ev("v1", "end", "2026-11-17T10:00:00Z", ms=900)]:
            f.write(json.dumps(e) + "\n")
    s14 = O.split(O.fold(rid, [log14])[0])
    check("R9 call time above the logged wall (even by under a second) makes waits unknown", s14["waits_ms"] is None and s14["waits_cause"], s14)
    check("R9 an out-of-range time is unreadable, never a crash", O._utc("9999-12-31T23:59:59-01:00") is None)
    print("obs report: %d failed" % len(FAILS) if FAILS else "obs report: all passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
