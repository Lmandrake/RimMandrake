#!/usr/bin/env python3
"""Selftest for the testing-rig efficiency collector (TESTING_RIG_MONITOR_EFFICIENCY_IN_PULSE).

Every metric is driven from fixtures with a hand-computed answer, and every source is probed both ways: a sane
source with no work reads a MEASURED 0, a source the reader cannot parse reads UNMEASURED (a zero must mean zero).
Also: the RimPulse red rule for the Testing panel (red only when the owner has a verb and work waits) and the
phone-brief judge re-deriving the testing line from the history file. Fixtures only; touches no live state.
"""
import atexit
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_testing_metrics_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="tm_state_")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import testing_metrics as T  # noqa: E402

FAILS = []
D0 = 1_792_000_000.0       # a day start (fixtures pass explicit day bounds; no time zone involved)
D1 = D0 + 86400


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def iso(t):
    return T.iso(t)


def v(m, *path):
    for p in path:
        m = m[p]
    return m


# ---------------------------------------------------------------- intervals
u = T.union([(0, 10), (5, 20), (30, 40), (41, 50)], gap=0)
check("union merges overlaps only", u == [(0, 20), (30, 40), (41, 50)], u)
u = T.union([(0, 10), (5, 20), (30, 40), (41, 50)], gap=2)
check("union merges gaps <= gap", u == [(0, 20), (30, 50)], u)
check("overlap length", T.overlap([(0, 20), (30, 50)], [(10, 35)]) == 15, T.overlap([(0, 20), (30, 50)], [(10, 35)]))
check("clip", T.clip([(0, 20), (30, 50)], 10, 40) == [(10, 20), (30, 40)])


# ---------------------------------------------------------------- testq fixture
def mkq(root, attempts, pending=(), garbage=0):
    for d in ("done", "pending", "running", "cancelled", "orphans"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    for a in attempts:
        jid = a["job"]
        job = {"schema": "testq.job/1", "id": jid, "mod": a.get("mod", "FlowWorks"),
               "selector": a.get("selector", {"chains": ["c1"]}), "purpose": a.get("purpose", "fix"),
               "submitted": iso(a["submitted"]), "lane": "stevedesktop", "deploy": []}
        rows = [{"chain": "c1", "row": r, "verdict": vd} for r, vd in a.get("rows", [])]
        res = {"schema": "testq.result/1", "job": jid, "attempt": jid + ".a1", "host": "stevedesktop",
               "outcome": a.get("outcome", "DONE"), "cause": a.get("cause"), "rows": rows,
               "phase_s": a.get("phase_s", {}), "started": iso(a["started"]), "finished": iso(a["finished"]),
               "deployed": {"mods": {job["mod"]: {"dll_sha256": a.get("dll", "d1"), "defs_sha256": "x"}}}}
        json.dump({"job": job, "result": res, "attempts": [jid + ".a1"], "finished": iso(a["finished"])},
                  open(os.path.join(root, "done", jid + ".json"), "w"))
    for jid, sub in pending:
        json.dump({"schema": "testq.job/1", "id": jid, "mod": "FlowWorks", "selector": {"chains": ["c1"]},
                   "purpose": "fix", "submitted": iso(sub), "lane": "stevedesktop"},
                  open(os.path.join(root, "pending", jid + ".json"), "w"))
    for i in range(garbage):
        open(os.path.join(root, "done", "Jbad%d.json" % i), "w").write("{not json")


H = 3600.0
q1 = tempfile.mkdtemp(prefix="q1_")
A = [
    # commissioned at D0+10h (first submit). Busy 10:00-11:00 and 12:00-12:30; 11:00-12:00 idle with job 3 waiting
    {"job": "J20260101T000000Z-aaaaa1", "submitted": D0 + 10 * H, "started": D0 + 10 * H, "finished": D0 + 11 * H,
     "phase_s": {"attest": 60, "deploy": 240, "load": 300, "run": 3000},
     "rows": [("r1", "PASS"), ("r2", "PASS"), ("r3", "UNMEASURED"), ("r4", "NOT_RUN")]},
    {"job": "J20260101T000001Z-aaaaa2", "submitted": D0 + 10.5 * H, "started": D0 + 12 * H,
     "finished": D0 + 12.5 * H, "phase_s": {"deploy": 600, "load": 1200, "run": 0},
     "outcome": "INVALID", "cause": "HARNESS", "rows": []},
    {"job": "J20260101T000002Z-aaaaa3", "submitted": D0 + 11 * H, "started": D0 + 13 * H,
     "finished": D0 + 13.5 * H, "phase_s": {"run": 1800}, "rows": [("r1", "FAIL"), ("r2", "PASS")], "dll": "d2"},
    # unchanged rerun of job 3 (same mod/selector/deployed identity, purpose fix): waste
    {"job": "J20260101T000003Z-aaaaa4", "submitted": D0 + 13.5 * H, "started": D0 + 14 * H,
     "finished": D0 + 14.5 * H, "phase_s": {"run": 1800}, "rows": [("r1", "FAIL"), ("r2", "PASS")], "dll": "d2"},
    # a sweep rerun of the same identity is budgeted, not waste; all-UNMEASURED is waste
    {"job": "J20260101T000004Z-aaaaa5", "submitted": D0 + 15 * H, "started": D0 + 15 * H,
     "finished": D0 + 15.25 * H, "phase_s": {"run": 900}, "purpose": "sweep",
     "rows": [("r1", "UNMEASURED"), ("r2", "UNMEASURED")]},
]
mkq(q1, A)
src = T.load_testq(q1)
check("testq probe sees 5 attempts, 0 unreadable", src["probe"]["records"] == 5 and src["probe"]["bad"] == 0,
      src["probe"])
LEDGER = [
    {"seat": "RUNNER", "event": "finding", "id": "ITEM_A", "type": "UNTRIAGED", "ts": iso(D0 + 13.6 * H),
     "from": "ITEM_A/run-1@steve-targeted"},
    {"seat": "RUNNER", "event": "finding", "id": "ITEM_A", "type": "HARNESS", "ts": iso(D0 + 12.6 * H),
     "from": "ITEM_A/run-2@steve-targeted"},
    {"seat": "RUNNER", "event": "verify", "id": "ITEM_B", "result": "pass", "config": "steve-targeted",
     "ts": iso(D0 + 11 * H)},
    {"seat": "BENCH", "event": "close", "id": "ITEM_B", "ts": iso(D0 + 16 * H)},
    {"seat": "RUNNER", "event": "verify", "id": "ITEM_C", "result": "pass", "config": "steve-targeted",
     "ts": iso(D0 + 17 * H)},
    {"seat": "BENCH", "event": "close", "id": "ITEM_C", "ts": iso(D0 + 16.5 * H)},   # closed BEFORE the pass
    {"seat": "FOUNDRY", "event": "verify", "id": "ITEM_D", "result": "pass", "config": "min-14",
     "ts": iso(D0 + 9 * H)},
    {"seat": "FOUNDRY", "event": "verify", "id": "ITEM_E", "result": "pass", "config": "offline-defs",
     "ts": iso(D0 + 9 * H)},
    {"seat": "FOUNDRY", "event": "close", "id": "ITEM_D", "ts": iso(D0 + 18 * H)},
    {"seat": "FOUNDRY", "event": "close", "id": "ITEM_E", "ts": iso(D0 + 18 * H)},
    {"seat": "FOUNDRY", "event": "finding", "id": "ITEM_D", "type": "modcheck-failure", "ts": iso(D0 + 9 * H)},
]
NOW = D0 + 20 * H
s = T.steve_day(src, LEDGER, D0, D1, NOW)
win = 10 * H        # commissioned 10:00 -> now 20:00
busy = 1 * H + 0.5 * H + 0.5 * H + 0.5 * H + 0.25 * H
check("steve window starts at commissioning", v(s, "window_h", "v") == 10.0, s["window_h"])
check("steve busy %", abs(v(s, "busy_pct", "v") - round(100 * busy / win, 1)) < 0.05, (s["busy_pct"], busy / win))
load_s = 60 + 240 + 300 + 600 + 1200
check("steve load/deploy % from phase_s", abs(v(s, "load_pct", "v") - round(100 * load_s / win, 1)) < 0.05,
      s["load_pct"])
check("steve run %", abs(v(s, "run_pct", "v") - round(100 * (3000 + 0 + 1800 * 2 + 900) / win, 1)) < 0.05,
      s["run_pct"])
check("steve idle while work waited: 11:00-12:00 + 12:30-13:00 + 13:30-14:00", abs(v(s, "idle_waiting_min", "v")
      - 120.0) < 0.05, s["idle_waiting_min"])
check("steve longest idle gap = 15:15 -> now 20:00", abs(v(s, "max_idle_gap_min", "v") - 285.0) < 0.05,
      s["max_idle_gap_min"])
check("steve jobs", v(s, "jobs", "v") == 5, s["jobs"])
# rows executed: PASS/FAIL/UNMEASURED (NOT_RUN and SKIP did not run): 3 + 0 + 2 + 2 + 2 = 9
check("steve rows run", v(s, "rows_run", "v") == 9, s["rows_run"])
check("steve rows/busy hour", abs(v(s, "rows_per_hour", "v") - round(9 / (busy / H), 1)) < 0.05, s["rows_per_hour"])
sh = s["verdict_counts"]
check("verdict counts over 10 rows + 1 INVALID attempt", sh["PASS"]["v"] == 4 and sh["FAIL"]["v"] == 2
      and sh["UNMEASURED"]["v"] == 3 and sh["NOT_RUN"]["v"] == 1 and sh["INVALID"]["v"] == 1, sh)
check("verdict shares: PASS 40% of rows, INVALID 20% of attempts", v(s, "verdicts", "PASS", "v") == 40.0
      and v(s, "verdicts", "INVALID", "v") == 20.0, s["verdicts"])
check("failures split: 1 harness (INVALID HARNESS), 2 mod rows", v(s, "fail_split", "harness", "v") == 1
      and v(s, "fail_split", "mod", "v") == 2, s["fail_split"])
check("regression PASS->FAIL caught once (r1, job 3), not again at job 4", v(s, "regressions", "v") == 1,
      s["regressions"])
check("findings filed from runs", v(s, "findings", "v") == 2, s["findings"])
check("findings by type", s["findings_by_type"] == {"UNTRIAGED": 1, "HARNESS": 1}, s["findings_by_type"])
check("closed after a passing run (B yes, C closed before its pass)", v(s, "closed_after_pass", "v") == 1,
      s["closed_after_pass"])
check("wasted: INVALID + unchanged rerun + all-UNMEASURED = 3 of 5", v(s, "wasted", "v") == 3
      and abs(v(s, "waste_pct", "v") - 60.0) < 0.05, (s["wasted"], s["waste_pct"], s.get("waste_why")))
check("waste reasons named", sorted(s["waste_why"]) == ["all_unmeasured", "invalid", "unchanged_rerun"],
      s["waste_why"])
check("every steve value carries MEASURED/UNMEASURED", all(isinstance(x, dict) and x.get("m") in T.MARKS
                                                            for x in T.leaves(s)), [x for x in T.leaves(s)][:3])

# zero means zero: a sane, empty queue on a commissioned day is a MEASURED 0; before commissioning UNMEASURED
q0 = tempfile.mkdtemp(prefix="q0_")
mkq(q0, [])
s0 = T.steve_day(T.load_testq(q0), [], D0, D1, NOW)
check("empty queue, never commissioned -> busy UNMEASURED", v(s0, "busy_pct", "m") == "UNMEASURED", s0["busy_pct"])
s_next = T.steve_day(src, LEDGER, D1, D1 + 86400, D1 + 2 * H)
check("day after, no jobs: busy is a MEASURED 0", v(s_next, "busy_pct", "m") == "MEASURED"
      and v(s_next, "busy_pct", "v") == 0.0, s_next["busy_pct"])
check("day after, no jobs: jobs MEASURED 0", v(s_next, "jobs", "v") == 0 and v(s_next, "jobs", "m") == "MEASURED")
check("day after, no rows: verdict shares UNMEASURED (no denominator)", v(s_next, "verdicts", "PASS", "m")
      == "UNMEASURED")
qb = tempfile.mkdtemp(prefix="qb_")
mkq(qb, [], garbage=3)
sb = T.steve_day(T.load_testq(qb), [], D0, D1, NOW)
check("unreadable records -> blind -> UNMEASURED, never 0", v(sb, "jobs", "m") == "UNMEASURED"
      and "unreadable" in v(sb, "jobs", "why"), sb["jobs"])
check("missing testq root -> UNMEASURED", v(T.steve_day(T.load_testq("/nonexistent/q"), [], D0, D1, NOW), "jobs",
                                            "m") == "UNMEASURED")

# pending job during the day counts as waiting
q2 = tempfile.mkdtemp(prefix="q2_")
mkq(q2, A[:1], pending=[("J20260101T000009Z-bbbbb1", D0 + 18 * H)])
s2 = T.steve_day(T.load_testq(q2), [], D0, D1, NOW)
check("a pending job's wait counts as idle-while-waiting", abs(v(s2, "idle_waiting_min", "v") - 120.0) < 0.05,
      s2["idle_waiting_min"])

# ---------------------------------------------------------------- Archmagi
bl = os.path.join(tempfile.mkdtemp(prefix="bl_"), "bridge_calls.jsonl")
with open(bl + ".1", "w") as f:
    f.write(json.dumps({"cid": "a", "ev": "start", "t": iso(D0 + 8 * H)}) + "\n")
    f.write(json.dumps({"cid": "a", "ev": "end", "t": iso(D0 + 8 * H + 30)}) + "\n")
with open(bl, "w") as f:
    for i in range(0, 30 * 60, 60):        # a call a minute for 30 min from 09:00: one merged busy span
        f.write(json.dumps({"cid": "b%d" % i, "ev": "start", "t": iso(D0 + 9 * H + i)}) + "\n")
        f.write(json.dumps({"cid": "b%d" % i, "ev": "end", "t": iso(D0 + 9 * H + i + 5)}) + "\n")
    f.write("{torn\n")
br = T.load_bridge(bl)
check("bridge probe reads both files, counts the torn line", br["probe"]["records"] == 62 and br["probe"]["bad"] == 1,
      br["probe"])
sd = tempfile.mkdtemp(prefix="sheets_")


def sheet(mod, t, comps):
    stamp = T.stamp(t)
    json.dump({"mod": mod, "stamp": stamp, "summary": {"chains": [{"name": "c1", "components": [
        {"name": r, "verdict": vd} for r, vd in comps]}], "refused": ""}},
        open(os.path.join(sd, "%s_%s.json" % (mod, stamp)), "w"))


sheet("FlowWorks", D0 - 2 * H, [("r1", "PASS"), ("r2", "PASS")])
sheet("FlowWorks", D0 + 9.5 * H, [("r1", "FAIL"), ("r2", "PASS")])
sheet("FlowWorks", D0 + 10 * H, [("r1", "UNMEASURED"), ("r2", "UNMEASURED")])
runs = T.load_sheets([sd])
a = T.archmagi_day(runs, br, LEDGER, D0, D1, NOW)
cov0 = D0 + 8 * H
check("archmagi window = bridge-log coverage -> now (12 h)", abs(v(a, "window_h", "v") - 12.0) < 0.01, a["window_h"])
busy_a = 30 + (30 * 60 - 60 + 5)          # call a (30 s) + the merged 09:00 span
check("archmagi bridge-busy %", abs(v(a, "busy_pct", "v") - round(100 * busy_a / (12 * H), 1)) < 0.05,
      (a["busy_pct"], busy_a))
check("archmagi load % UNMEASURED (no phase timings)", v(a, "load_pct", "m") == "UNMEASURED")
check("archmagi jobs = 2 sheets today", v(a, "jobs", "v") == 2, a["jobs"])
check("archmagi regression from the sheet before the day", v(a, "regressions", "v") == 1, a["regressions"])
check("archmagi findings = finding events by BENCH/FOUNDRY", v(a, "findings", "v") == 1, a["findings"])
check("archmagi closed after a live pass (D yes, E offline no)", v(a, "closed_after_pass", "v") == 1,
      a["closed_after_pass"])
check("archmagi waste = 1 all-UNMEASURED of 2", v(a, "wasted", "v") == 1 and abs(v(a, "waste_pct", "v") - 50) < .05,
      a["waste_pct"])
check("archmagi unchanged-rerun is UNMEASURED (no source identity in local sheets)",
      "unchanged_rerun" in v(a, "waste_pct", "note"), a["waste_pct"])
a_old = T.archmagi_day(runs, br, LEDGER, D0 - 86400, D0, NOW)
check("a day before the bridge log covers -> busy UNMEASURED", v(a_old, "busy_pct", "m") == "UNMEASURED",
      a_old["busy_pct"])

# ---------------------------------------------------------------- history
hp = os.path.join(tempfile.mkdtemp(prefix="hist_"), "history.jsonl")
r1 = {"schema": T.SCHEMA, "day": "2026-01-01", "generated": iso(NOW), "coverage": 0.5, "machines": {"x": 1}}
check("append writes a new record", T.append_if_changed(hp, r1) is True)
check("append skips an unchanged record", T.append_if_changed(hp, dict(r1, generated=iso(NOW + 60))) is False)
r2 = dict(r1, generated=iso(NOW + 120), coverage=0.4, machines={"x": 2})
T.append_if_changed(hp, r2)
best = T.best_per_day(T.read_history(hp))
check("best per day keeps the higher-coverage record", best["2026-01-01"]["machines"] == {"x": 1}, best)
r3 = dict(r1, generated=iso(NOW + 180), coverage=0.5, machines={"x": 3})
T.append_if_changed(hp, r3)
check("equal coverage: the latest wins", T.best_per_day(T.read_history(hp))["2026-01-01"]["machines"] == {"x": 3})
with open(hp, "a") as f:
    f.write("{torn\n")
check("a torn history line is skipped, not fatal", len(T.read_history(hp)) == 3)

# ---------------------------------------------------------------- RimPulse panel + red rule
import pulse_core as pc  # noqa: E402


def snapd(steve, arch, live=None):
    return {"days": [{"day": "2026-01-0%d" % i, "machines": {"steve": steve, "archmagi": arch}} for i in range(1, 8)],
            "live": live or {}}


M, U = T.M, T.U
st = {"busy_pct": M(40.0), "rows_per_hour": M(12.0), "findings": M(2), "waste_pct": M(10.0)}
ar = {"busy_pct": M(5.0), "rows_per_hour": U("no rows"), "findings": M(0), "waste_pct": U("no runs")}
panel = pc.testing_panel(snapd(st, ar), NOW)
check("panel has both machines side by side", [m["key"] for m in panel["machines"]] == ["steve", "archmagi"], panel)
check("panel carries a 7-day series per metric", len(panel["machines"][0]["metrics"]["busy_pct"]["series"]) == 7)
check("panel keeps UNMEASURED as null, never 0", panel["machines"][1]["metrics"]["rows_per_hour"]["series"][-1] is None)
idle_empty = {"steve": {"idle_since": NOW - 2 * H, "pending": 0, "ssh_down_since": None, "paused": None}}
rows = pc.classify_testing(idle_empty, {}, NOW)
check("Steve idle 2 h with an empty queue: a warn for agents, not red", rows and rows[0]["kind"] == "warn"
      and not any(r["kind"] == "red" for r in pc.owner_view(rows, NOW) if not r.get("agent")), rows)
down_wait = {"steve": {"idle_since": NOW - 2 * H, "pending": 3, "ssh_down_since": NOW - 2 * H, "paused": None}}
rows = pc.classify_testing(down_wait, {}, NOW)
ov = [r for r in pc.owner_view(rows, NOW) if not r.get("agent")]
check("Steve unreachable 2 h with 3 jobs waiting: red (his verb: wake SteveDesktop)", ov and ov[0]["kind"] == "red",
      ov)
rows = pc.classify_testing({"steve": dict(down_wait["steve"], ssh_down_since=NOW - 600)}, {}, NOW)
check("unreachable 10 min: not red yet", not any(r["kind"] == "red" for r in rows), rows)
rows = pc.classify_testing({"steve": {"idle_since": NOW - 600, "pending": 0, "ssh_down_since": None,
                                      "paused": None}}, {}, NOW)
check("idle 10 min: no row", rows == [], rows)
rows = pc.classify_testing({"steve": {"idle_since": NOW - 2 * H, "pending": 2, "ssh_down_since": None,
                                      "paused": {"since": iso(NOW - 2 * H), "cause": "CANARY"}}}, {}, NOW)
check("paused lane with work waiting: warn for agents (testq resume is an agent verb)",
      rows and rows[0]["kind"] == "warn" and "paused" in rows[0]["text"], rows)

# ---------------------------------------------------------------- phone brief line + judge
import brief  # noqa: E402
hp2 = os.path.join(tempfile.mkdtemp(prefix="hist2_"), "history.jsonl")
today = {"schema": T.SCHEMA, "day": "2026-01-07", "generated": iso(NOW), "coverage": 1.0,
         "machines": {"steve": st, "archmagi": ar}}
T.append_if_changed(hp2, today)
os.environ["RM_TESTING_HISTORY"] = hp2
snap = {"charts": {"testing": pc.testing_panel({"days": [today], "live": {}}, NOW)},
        "sources": {"testing": {"ok": True}}}
ln = brief.testing_line(snap)
check("brief testing line names both machines", ln and "Steve" in ln["text"] and "Archmagi" in ln["text"], ln)
check("brief line shows UNMEASURED words, not 0", ln and "unmeasured" in ln["text"].lower(), ln)
check("judge passes the true line", brief.check_testing(ln["claim"]) == "pass", brief.check_testing(ln["claim"]))
bad = dict(ln["claim"], values={**ln["claim"]["values"], "steve.busy_pct": 99.0})
check("judge withholds a tampered number", brief.check_testing(bad).startswith("fail"), brief.check_testing(bad))

print("\nselftest_testing_metrics: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
