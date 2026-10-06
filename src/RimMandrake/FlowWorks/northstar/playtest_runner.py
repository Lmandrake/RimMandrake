#!/usr/bin/env python3
"""playtest_runner.py - thin launcher for the FlowWorks in-game scenario runner (Approach A pilot).

    python.exe D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\FlowWorks\\northstar\\playtest_runner.py [--recipe pilot]
        [--seed 1] [--tick-mode batch|speed] [--budget-ms 50] [--poll 2] [--timeout 1500] [--force]

Three bridge tools do all the work (JawaBench companion, JawaBenchFlowWorksPlaytest.cs):
jawa/playtest_start returns a run id at once; the run advances inside the game across frames;
this script polls jawa/playtest_status, then jawa/playtest_collect, reads the JSONL journal the game
wrote, re-derives the verdict from it, prints a timing table, and copies the journal to
Transient/flowworks_playtest/. Design: design/RimMandrake/flowworks_playtest_runner_A.md.

Needs python.exe (the bridge binds Windows loopback), a running game with a map, and the companion
DLL that carries the three tools. The run MODIFIES THE MAP - scratch maps only.

Verdict rule (same as the C# collect, re-derived here from the file): INCOMPLETE unless the last
record is run_end with completed=true; then FAIL if any scenario FAILed, INVALID if any was
INVALID, else PASS. An ERROR scenario always comes with completed=false, so it reads INCOMPLETE.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")


# ── pure logic (selftest_playtest_runner.py) ─────────────────────────────

def parse_journal(text):
    """JSONL text -> list of dicts. A torn last line (game killed mid-write) is dropped and reported."""
    recs, torn = [], 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except ValueError:
            torn += 1
    return recs, torn


def verdict(recs):
    if not recs or recs[-1].get("type") != "run_end" or recs[-1].get("completed") is not True:
        return "INCOMPLETE"
    statuses = [r.get("status") for r in recs if r.get("type") == "scenario"]
    if any(s not in ("PASS", "FAIL", "INVALID") for s in statuses):
        return "INCOMPLETE"
    if len(statuses) != recs[-1].get("scenariosPlanned", len(statuses)):
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if "INVALID" in statuses:
        return "INVALID"
    return "PASS"


def _ph(t, name, key):
    return ((t.get("phases") or {}).get(name) or {}).get(key, 0)


def timing_table(recs, launcher=None):
    """Plain-text table: one row per scenario + run total; setup/exec/observe split; ticks/s."""
    rows = [("scenario", "status", "wall s", "ticks", "frames", "setup s", "exec s", "observe s", "ticks/s")]
    for r in recs:
        if r.get("type") != "scenario":
            continue
        t = r.get("timing") or {}
        rows.append((r.get("name", "?"), r.get("status", "?"), "%.2f" % t.get("wallSec", 0), str(t.get("ticks", 0)),
                     str(t.get("frames", 0)), "%.2f" % _ph(t, "setup", "wallSec"), "%.2f" % _ph(t, "exec", "wallSec"),
                     "%.2f" % _ph(t, "observe", "wallSec"), "%.0f" % t.get("ticksPerSecDuringWaits", 0)))
    end = recs[-1] if recs and recs[-1].get("type") == "run_end" else None
    if end:
        t = end.get("timing") or {}
        rows.append(("RUN TOTAL", "done" if end.get("completed") else "ABORTED", "%.2f" % t.get("wallSec", 0),
                     str(t.get("ticks", 0)), str(t.get("frames", 0)), "%.2f" % _ph(t, "setup", "wallSec"),
                     "%.2f" % _ph(t, "exec", "wallSec"), "%.2f" % _ph(t, "observe", "wallSec"),
                     "%.0f" % t.get("ticksPerSecDuringWaits", 0)))
    else:
        rows.append(("RUN TOTAL", "NO run_end", "-", "-", "-", "-", "-", "-", "-"))
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    out = ["  ".join(c.ljust(widths[i]) for i, c in enumerate(row)) for row in rows]
    out.insert(1, "  ".join("-" * w for w in widths))
    if end:
        t = end.get("timing") or {}
        out.append("tick mode %s (%s), frame budget %s ms, runner overhead %.2f s, Ultrafast multiplier %s"
                   % (t.get("tickMode"), t.get("timeSpeedDuringRun"), t.get("frameBudgetMs"),
                      _ph(t, "runner", "wallSec"), t.get("tickRateMultiplierUltrafast")))
    if launcher:
        out.append("launcher: %.2f s wall start->collect, %d bridge calls" % (launcher["wall"], launcher["calls"]))
    return "\n".join(out)


# ── bridge ───────────────────────────────────────────────────────────────

def _connect():
    sys.path.insert(0, UTILS)
    import rimbridge_client as rb  # noqa: E402
    host, port, token = rb.resolve_endpoint()
    s = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
    s.connect()
    return s


def _call(s, counter, tool, **p):
    counter[0] += 1
    r = s.call(tool, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except (ValueError, KeyError, IndexError, TypeError):
            pass
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recipe", default="pilot")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tick-mode", default="batch", choices=("batch", "speed"))
    ap.add_argument("--budget-ms", type=int, default=50)
    ap.add_argument("--poll", type=float, default=2.0)
    ap.add_argument("--timeout", type=float, default=1500.0, help="launcher-side wall limit, seconds")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--out-dir", default=os.path.join(REPO, "Transient", "flowworks_playtest"))
    a = ap.parse_args(argv)

    calls = [0]
    s = _connect()
    t0 = time.time()
    st = _call(s, calls, "jawa/playtest_start", recipe=a.recipe, seed=a.seed, tickMode=a.tick_mode,
               frameBudgetMs=a.budget_ms, force=a.force)
    if not st.get("success"):
        print("START REFUSED: %s" % st.get("message", st))
        return 2
    run_id = st["runId"]
    print("run %s  scenarios=%s  mode=%s  driver=%s" % (run_id, ",".join(st["scenarios"]), st["tickMode"], st["driver"]))
    seen = 0
    while True:
        time.sleep(a.poll)
        stat = _call(s, calls, "jawa/playtest_status", runId=run_id)
        recs = stat.get("records") or []
        for r in recs[seen:]:
            print("  %-8s %-8s %6.2fs %6d ticks  %s" % (r["name"], r["status"], r["wallSec"], r["ticks"], r.get("reason") or ""))
        seen = len(recs)
        if stat.get("state") != "running":
            break
        if time.time() - t0 > a.timeout:
            print("LAUNCHER TIMEOUT after %.0f s; the run is still going in game (state %s)" % (time.time() - t0, stat.get("state")))
            break
    col = _call(s, calls, "jawa/playtest_collect", runId=run_id)
    wall = time.time() - t0
    path = col.get("reportPath")
    if not path or not os.path.exists(path):
        print("COLLECT: no readable journal (%s); C# verdict %s" % (path, col.get("verdict")))
        return 3
    with open(path, encoding="utf-8") as f:
        text = f.read()
    recs, torn = parse_journal(text)
    v = verdict(recs)
    os.makedirs(a.out_dir, exist_ok=True)
    copy = os.path.join(a.out_dir, os.path.basename(path))
    shutil.copyfile(path, copy)
    print()
    print(timing_table(recs, {"wall": wall, "calls": calls[0]}))
    print()
    if v != col.get("verdict"):
        print("VERDICT DISAGREEMENT: file says %s, C# collect says %s" % (v, col.get("verdict")))
    print("VERDICT %s  (%d records%s)  journal %s  copy %s" % (v, len(recs), ", %d torn" % torn if torn else "", path, copy))
    return 0 if v == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
