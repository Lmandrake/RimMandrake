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
record is run_end with completed=true and every scenario is PASS/FAIL/INVALID (an ERROR always comes
with completed=false; PENDING is a save_reload awaiting its resume half); then FAIL if any scenario
FAILed without an expectedFailUntil item, INVALID if any was INVALID, XFAIL if the only FAILs are
expected ones (e.g. sluice until FLOWWORKS_SLUICE_TWO_DOORS_1), else PASS.

Recipes: pilot (fluids,dig,pit), full (every scene; save_reload last), or a comma list of scene names.
save_reload is two-phase: the in-game half saves the game mid-flow, records the uninterrupted branch to a
checkpoint file and writes PENDING. This launcher then loads that save (rimworld/load_game_ready) and starts
save_reload_b with resume=<first runId>, which continues the same ticks and compares. The combined verdict
replaces the PENDING record with the resume half's result. --no-resume stops after the first half.
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
    scen = [r for r in recs if r.get("type") == "scenario"]
    statuses = [r.get("status") for r in scen]
    if any(s not in ("PASS", "FAIL", "INVALID") for s in statuses):
        return "INCOMPLETE"
    if len(statuses) != recs[-1].get("scenariosPlanned", len(statuses)):
        return "INCOMPLETE"
    if any(r.get("status") == "FAIL" and not r.get("expectedFailUntil") for r in scen):
        return "FAIL"
    if "INVALID" in statuses:
        return "INVALID"
    if "FAIL" in statuses:
        return "XFAIL"
    return "PASS"


def pending_resume(recs):
    """The PENDING save_reload record that asks for a resume half, or None."""
    for r in recs:
        if r.get("type") == "scenario" and r.get("status") == "PENDING" and (r.get("evidence") or {}).get("resumeRecipe"):
            return r
    return None


def combine(first, second):
    """Verdict of a two-phase run: the first run's PENDING record takes the resume half's status; the
    resume run must itself be complete. A missing or incomplete second half leaves INCOMPLETE."""
    if not second or verdict(second) == "INCOMPLETE":
        return "INCOMPLETE"
    res = {r.get("name"): r for r in second if r.get("type") == "scenario"}
    merged = []
    for r in first:
        if r.get("type") == "scenario" and r.get("status") == "PENDING":
            want = (r.get("evidence") or {}).get("resumeRecipe")
            b = res.get(want)
            if b is None:
                return "INCOMPLETE"
            r = dict(r, status=b.get("status"), expectedFailUntil=b.get("expectedFailUntil"))
        merged.append(r)
    v1 = verdict(merged)
    v2 = verdict(second)
    order = ["INCOMPLETE", "FAIL", "INVALID", "XFAIL", "PASS"]
    return min(v1, v2, key=order.index)


def mark(r):
    """Status as printed: XFAIL / XPASS when the scene carries an expectedFailUntil item."""
    st, item = r.get("status"), r.get("expectedFailUntil")
    if item and st == "FAIL":
        return "XFAIL"
    if item and st == "PASS":
        return "XPASS"
    return st or "?"


def _ph(t, name, key):
    return ((t.get("phases") or {}).get(name) or {}).get(key, 0)


def timing_table(recs, launcher=None):
    """Plain-text table: one row per scenario + run total; setup/exec/observe split; ticks/s."""
    rows = [("scenario", "status", "wall s", "ticks", "frames", "setup s", "exec s", "observe s", "ticks/s")]
    for r in recs:
        if r.get("type") != "scenario":
            continue
        t = r.get("timing") or {}
        rows.append((r.get("name", "?"), mark(r), "%.2f" % t.get("wallSec", 0), str(t.get("ticks", 0)),
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


def run_once(s, calls, a, recipe, resume=None):
    """Start one run, poll it to the end, collect, copy the journal. Returns (recs, c_sharp_verdict, path, wall)."""
    t0 = time.time()
    p = dict(recipe=recipe, seed=a.seed, tickMode=a.tick_mode, frameBudgetMs=a.budget_ms, force=a.force)
    if resume:
        p["resume"] = resume
    st = _call(s, calls, "jawa/playtest_start", **p)
    if not st.get("success"):
        print("START REFUSED: %s" % st.get("message", st))
        return None, None, None, 0.0
    run_id = st["runId"]
    print("run %s  scenarios=%s  mode=%s  driver=%s%s" % (run_id, ",".join(st["scenarios"]), st["tickMode"], st["driver"],
                                                         "  resume=" + resume if resume else ""))
    seen = 0
    while True:
        time.sleep(a.poll)
        stat = _call(s, calls, "jawa/playtest_status", runId=run_id)
        recs = stat.get("records") or []
        for r in recs[seen:]:
            print("  %-14s %-8s %6.2fs %6d ticks  %s" % (r["name"], mark(r), r["wallSec"], r["ticks"], r.get("reason") or ""))
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
        return None, col.get("verdict"), path, wall
    with open(path, encoding="utf-8") as f:
        recs, torn = parse_journal(f.read())
    os.makedirs(a.out_dir, exist_ok=True)
    copy = os.path.join(a.out_dir, os.path.basename(path))
    shutil.copyfile(path, copy)
    v = verdict(recs)
    print()
    print(timing_table(recs, {"wall": wall, "calls": calls[0]}))
    print()
    if v != col.get("verdict"):
        print("VERDICT DISAGREEMENT: file says %s, C# collect says %s" % (v, col.get("verdict")))
    print("RUN VERDICT %s  (%d records%s)  journal %s  copy %s" % (v, len(recs), ", %d torn" % torn if torn else "", path, copy))
    return recs, col.get("verdict"), path, wall


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--recipe", default="pilot", help="pilot | full | comma list of scenes")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--tick-mode", default="batch", choices=("batch", "speed"))
    ap.add_argument("--budget-ms", type=int, default=50)
    ap.add_argument("--poll", type=float, default=2.0)
    ap.add_argument("--timeout", type=float, default=1500.0, help="launcher-side wall limit per run, seconds")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--resume", default=None, help="runId of a save_reload run (with --recipe save_reload_b)")
    ap.add_argument("--no-resume", action="store_true", help="do not load the save and run save_reload_b")
    ap.add_argument("--out-dir", default=os.path.join(REPO, "Transient", "flowworks_playtest"))
    a = ap.parse_args(argv)

    calls = [0]
    s = _connect()
    recs, _, _, _ = run_once(s, calls, a, a.recipe, a.resume)
    if recs is None:
        return 2
    final = verdict(recs)
    pend = pending_resume(recs)
    if pend and not a.no_resume:
        ev = pend.get("evidence") or {}
        print()
        print("RESUME: loading %s (tick %s) for %s" % (ev.get("saveName"), ev.get("ticksAtSave"), ev.get("resumeRecipe")))
        t = time.time()
        calls[0] += 1
        lr = s.call("rimworld/load_game_ready", {"saveName": ev.get("saveName")}) or {}
        if isinstance(lr, dict) and lr.get("content"):
            try:
                lr = json.loads(lr["content"][0]["text"])
            except (ValueError, KeyError, IndexError, TypeError):
                pass
        print("load_game_ready: success=%s  %.1f s  %s" % (lr.get("success"), time.time() - t, lr.get("message") or ""))
        # load_game_ready answers before the map exists (live 2026-10-06: mapCount 0 for ~3 s), so
        # playtest_start would refuse "No current map". Wait for the map, bounded.
        while lr.get("success") and time.time() - t < 180:
            gi = _call(s, calls, "rimworld/get_game_info")
            # the OLD game still answers for a moment (live: mapCount 2 at the pre-load tick), so the
            # map counts only once the clock is back at the save's tick
            tk = gi.get("ticksGame")
            if (gi.get("mapCount") or 0) >= 1 and isinstance(tk, int) and 0 < tk <= (ev.get("ticksAtSave") or 0) + 5:
                print("map ready after %.1f s at tick %s" % (time.time() - t, gi.get("ticksGame")))
                break
            time.sleep(1.0)
        second = None
        if lr.get("success"):
            second, _, _, _ = run_once(s, calls, a, ev.get("resumeRecipe"), pend.get("runId"))
        final = combine(recs, second)
    elif pend:
        print("save_reload armed and NOT resumed (--no-resume): verdict stays INCOMPLETE")
    print()
    print("VERDICT %s" % final)
    return 0 if final in ("PASS", "XFAIL") else 1


if __name__ == "__main__":
    sys.exit(main())
