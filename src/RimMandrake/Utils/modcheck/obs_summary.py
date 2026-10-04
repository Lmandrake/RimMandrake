"""modcheck.obs_summary -- offline reader for the bridge call telemetry (observatory S2). DIAGNOSTICS ONLY:
per owner ruling 2026-10-03 the required-checks-proven headline leads; nothing here is a target or a verdict.

    python3 obs_summary.py [run.jsonl ...]      default: every file in <obs dir>/runs (newest last)
    python3 obs_summary.py --dir D:\\Luke\\dev\\_obs

Prints per run: completeness, calls/min by tool and by outcome, p50/p95 latency, retries (reconnects),
UNFINISHED calls (a call_start with no call_end: a hang, or a kill) and a timeline of where the bridge
time went. Read-only; never touches the game or the bridge.

Timeline categories (seconds, partition of run_start..last event; ticks beat tool beats idle where
intervals overlap):
  setup         run_start -> first call_start (session open, focus, preflight)
  waiting_ticks calls to tick-advancing tools (name contains step_game_ticks / wait_ticks / game_ticks)
  tool          every other call in flight
  idle          the gaps between calls (client-side work, sleeps, screenshots decoding, judge time)
An unfinished call is counted to the last event seen in its file (right-censored) and flagged.
"""
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
TICK_MARKS = ("step_game_ticks", "wait_ticks", "game_ticks")


def default_dir():
    env = os.environ.get("OBS_DIR")
    return env or (r"D:\Luke\dev\_obs" if os.name == "nt" else "/mnt/d/Luke/dev/_obs")


def load(path):
    out, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                bad += 1            # a torn last line after a kill; counted, not fatal
    return out, bad


def pct(vals, q):
    if not vals:
        return None
    v = sorted(vals)
    k = (len(v) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def _union(ivs):
    ivs = sorted(ivs)
    out = []
    for a, b in ivs:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def _len(ivs):
    return sum(b - a for a, b in ivs)


def _minus(ivs, cut):
    out = []
    for a, b in ivs:
        cur = a
        for c, d in cut:
            if d <= cur or c >= b:
                continue
            if c > cur:
                out.append([cur, c])
            cur = max(cur, d)
        if cur < b:
            out.append([cur, b])
    return out


def summarize(events, bad_lines=0):
    starts = {}
    ends = {}
    run_start = run_end = None
    t_last = None
    for e in events:
        t = e.get("t")
        if t is not None and (t_last is None or t > t_last):
            t_last = t
        ev = e.get("ev")
        if ev == "run_start" and run_start is None:
            run_start = e
        elif ev == "run_end":
            run_end = e
        elif ev == "call_start":
            starts[(e.get("producer"), e.get("req"), e.get("attempt"))] = e
        elif ev == "call_end":
            ends[(e.get("producer"), e.get("req"), e.get("attempt"))] = e
    calls = []
    for k, st in starts.items():
        en = ends.get(k)
        calls.append({"tool": st.get("tool"), "t0": st["t"], "t1": en["t_end"] if en else None,
                      "ms": en["latency_ms"] if en else None, "outcome": en["outcome"] if en else "UNFINISHED",
                      "timeout": bool(en and en.get("timeout"))})
    for k, en in ends.items():         # an end with no start in the file (dropped start): still counted
        if k not in starts:
            calls.append({"tool": en.get("tool"), "t0": en.get("t_start"), "t1": en.get("t_end"),
                          "ms": en.get("latency_ms"), "outcome": en["outcome"], "timeout": bool(en.get("timeout"))})
    t0 = run_start["t"] if run_start else (min(c["t0"] for c in calls) if calls else None)
    t1 = max([c["t1"] for c in calls if c["t1"]] + [t_last or 0]) if calls else t_last
    span = (t1 - t0) if (t0 is not None and t1 is not None) else 0.0
    drops = (run_end or {}).get("dropped")
    telemetry = "complete"
    if run_end is None:
        telemetry = "INCOMPLETE (no run_end: killed run or sink stalled)"
    elif drops:
        telemetry = "INCOMPLETE (%d events dropped)" % drops
    elif (run_end or {}).get("write_errors"):
        telemetry = "INCOMPLETE (%d write errors)" % run_end["write_errors"]
    by_tool = {}
    for c in calls:
        d = by_tool.setdefault(c["tool"], {"n": 0, "ms": [], "outcomes": {}})
        d["n"] += 1
        if c["ms"] is not None:
            d["ms"].append(c["ms"])
        d["outcomes"][c["outcome"]] = d["outcomes"].get(c["outcome"], 0) + 1
    outcomes = {}
    for c in calls:
        outcomes[c["outcome"]] = outcomes.get(c["outcome"], 0) + 1
    # timeline
    tl = {"setup": 0.0, "waiting_ticks": 0.0, "tool": 0.0, "idle": 0.0}
    if calls and t0 is not None:
        first = min(c["t0"] for c in calls)
        tl["setup"] = max(0.0, first - t0)
        tick_iv, tool_iv = [], []
        for c in calls:
            end = c["t1"] if c["t1"] else t1
            (tick_iv if any(m in (c["tool"] or "") for m in TICK_MARKS) else tool_iv).append([c["t0"], max(end, c["t0"])])
        tick_u = _union(tick_iv)
        tool_u = _minus(_union(tool_iv), tick_u)
        tl["waiting_ticks"], tl["tool"] = _len(tick_u), _len(tool_u)
        tl["idle"] = max(0.0, (t1 - first) - tl["waiting_ticks"] - tl["tool"])
    return {"run_id": (run_start or run_end or {}).get("run_id") or (events[0].get("run_id") if events else None),
            "n_calls": len(calls), "unfinished": [c["tool"] for c in calls if c["outcome"] == "UNFINISHED"],
            "span_s": span, "calls_per_min": (len(calls) / (span / 60.0)) if span > 0 else None,
            "by_tool": by_tool, "outcomes": outcomes, "retries": outcomes.get("reconnected", 0),
            "timeouts": sum(1 for c in calls if c["timeout"]), "timeline": tl, "telemetry": telemetry,
            "bad_lines": bad_lines}


def render(s):
    L = ["run %s  --  telemetry %s" % (s["run_id"], s["telemetry"])]
    if s["span_s"] <= 0 and not s["n_calls"]:
        L.append("  no calls recorded (UNMEASURED, not zero)")
        return "\n".join(L)
    L.append("  %d calls over %.0fs = %s/min   outcomes %s   retries(reconnects) %d   timeouts %d%s" % (
        s["n_calls"], s["span_s"], "%.1f" % s["calls_per_min"] if s["calls_per_min"] else "?",
        s["outcomes"], s["retries"], s["timeouts"],
        "   torn lines %d" % s["bad_lines"] if s["bad_lines"] else ""))
    if s["unfinished"]:
        L.append("  UNFINISHED (call_start, no call_end): %s" % ", ".join(sorted(set(s["unfinished"]))))
    tl, tot = s["timeline"], (sum(s["timeline"].values()) or 1.0)
    L.append("  where the time went: " + "  ".join("%s %.0fs (%.0f%%)" % (k, tl[k], 100 * tl[k] / tot)
                                                    for k in ("setup", "tool", "waiting_ticks", "idle")))
    L.append("  %-34s %5s %7s %9s %9s  %s" % ("tool", "n", "per_min", "p50 ms", "p95 ms", "outcomes"))
    for tool, d in sorted(s["by_tool"].items(), key=lambda kv: -kv[1]["n"])[:15]:
        per = d["n"] / (s["span_s"] / 60.0) if s["span_s"] > 0 else 0
        p50, p95 = pct(d["ms"], .5), pct(d["ms"], .95)
        L.append("  %-34s %5d %7.1f %9s %9s  %s" % ((tool or "?")[:34], d["n"], per,
                 "%.0f" % p50 if p50 is not None else "-", "%.0f" % p95 if p95 is not None else "-", d["outcomes"]))
    L.append("  (diagnostics only: required checks proven leads; see required_checks_report.py)")
    return "\n".join(L)


def main(argv):
    files = [a for a in argv if not a.startswith("--")]
    if "--dir" in argv:
        d = argv[argv.index("--dir") + 1]
        files = [f for f in files if f != d]
    else:
        d = default_dir()
    if not files:
        files = sorted(glob.glob(os.path.join(d, "runs", "*.jsonl")), key=os.path.getmtime)
    if not files:
        print("no telemetry files under %s -- UNMEASURED (the S2 hook has not run live yet)" % d)
        return 0
    for f in files:
        ev, bad = load(f)
        print(render(summarize(ev, bad)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
