"""Selftest for obs_summary on synthetic event streams. Each rule has a control that must not trigger it.
Run: python3 selftest_obs_summary.py"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import obs_summary as S  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


def mk(calls, t0=1000.0, end=True, drops=0, run_end_t=None):
    """calls: [(tool, start_offset_s, dur_s, outcome|None)] ; None outcome = never ended"""
    ev = [{"ev": "run_start", "run_id": "r", "producer": "p", "t": t0, "seq": 1}]
    seq = 2
    for i, (tool, off, dur, out) in enumerate(calls):
        ev.append({"ev": "call_start", "run_id": "r", "producer": "p", "req": "r%d" % i, "attempt": 1,
                   "tool": tool, "t": t0 + off, "seq": seq}); seq += 1
        if out is not None:
            ev.append({"ev": "call_end", "run_id": "r", "producer": "p", "req": "r%d" % i, "attempt": 1,
                       "tool": tool, "t_start": t0 + off, "t_end": t0 + off + dur, "latency_ms": dur * 1000.0,
                       "outcome": out, "timeout": out == "timeout", "t": t0 + off + dur, "seq": seq}); seq += 1
    if end:
        ev.append({"ev": "run_end", "run_id": "r", "producer": "p", "t": run_end_t or t0 + 100, "emitted": seq,
                   "dropped": drops, "written": seq, "write_errors": 0, "seq": seq})
    return ev


ev = mk([("jawa/a", 10, 1, "ok"), ("jawa/a", 12, 3, "ok"), ("jawa/step_game_ticks", 20, 30, "ok"),
         ("jawa/b", 60, 2, "reconnected")])
s = S.summarize(ev)
check("4 calls counted, telemetry complete", s["n_calls"] == 4 and s["telemetry"] == "complete", s["telemetry"])
check("retries = reconnect outcomes", s["retries"] == 1)
check("p50/p95 of jawa/a over [1000,3000] ms", S.pct(s["by_tool"]["jawa/a"]["ms"], .5) == 2000.0 and S.pct(s["by_tool"]["jawa/a"]["ms"], .95) == 2900.0)
tl = s["timeline"]
check("setup = run_start to first call (10 s)", abs(tl["setup"] - 10) < 1e-6, tl)
check("waiting_ticks = the 30 s tick wait", abs(tl["waiting_ticks"] - 30) < 1e-6, tl)
check("tool = 1+3+2 s", abs(tl["tool"] - 6) < 1e-6, tl)
check("four categories partition run_start..run_end (100 s) exactly, trailing idle included", abs(sum(tl.values()) - 100) < 1e-6, tl)

# hung call is visible and flagged
h = S.summarize(mk([("jawa/ok", 5, 1, "ok"), ("jawa/hangs", 10, 0, None)], end=False))
check("hung call reported UNFINISHED", h["unfinished"] == ["jawa/hangs"], h["unfinished"])
check("no run_end => telemetry INCOMPLETE (control: complete above)", h["telemetry"].startswith("INCOMPLETE"))
check("render names the hung tool", "jawa/hangs" in S.render(h))

# drops mark incomplete; zero drops do not
d = S.summarize(mk([("a", 1, 1, "ok")], drops=7))
check("dropped events => INCOMPLETE", "7 events dropped" in d["telemetry"])

# empty stream is UNMEASURED, never zero
e = S.summarize([])
check("empty stream renders UNMEASURED", "UNMEASURED" in S.render(e))

# overlapping calls are unioned, not double counted
o = S.summarize(mk([("a", 10, 10, "ok"), ("b", 12, 4, "ok")]))
check("overlap unioned: tool time 10 s not 14", abs(o["timeline"]["tool"] - 10) < 1e-6, o["timeline"])

# torn trailing line after a kill is tolerated
tmp = tempfile.mkdtemp()
p = os.path.join(tmp, "x.jsonl")
with open(p, "w") as f:
    for r in mk([("a", 1, 1, "ok")], end=False):
        f.write(json.dumps(r) + "\n")
    f.write('{"ev": "call_st')
evs, bad = S.load(p)
check("torn last line counted, rest readable", bad == 1 and len(evs) == 3, (bad, len(evs)))
check("main() on a file prints a report", S.main([p]) == 0)

if FAILS:
    print("\nFAILED: %s" % FAILS)
    sys.exit(1)
print("\nOK: selftest_obs_summary")
