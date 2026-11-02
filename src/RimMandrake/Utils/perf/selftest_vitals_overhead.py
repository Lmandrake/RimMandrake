#!/usr/bin/env python3
"""Offline selftest of vitals_overhead.verdict (VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL). No bridge, no game."""
import copy, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vitals_overhead as V

FAILS = []


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r want %r" % (name, got, want))


def meters(calls=10, ms=1.0, on=True, skip=()):
    return {c: (None if c in skip else {"calls": calls, "totalMs": ms, "on": on}) for c in V.CHANNELS}


def run(mods=13, off_ms=1000.0, armed_ms=1020.0, m=None):
    wls = {}
    for name, (reps, ticks) in V.WORKLOADS.items():
        rows = []
        for _ in range(reps):
            pz = {} if ticks else {"paused_ok": True}
            rows.append(dict({"arm": "off", "ticks_req": ticks, "ticks_run": ticks, "wall_ms": off_ms, "meters": None,
                              "armed_state": [False, False]}, **pz))
            rows.append(dict({"arm": "armed", "ticks_req": ticks, "ticks_run": ticks, "wall_ms": armed_ms, "armed_state": [True, True],
                              "meters": copy.deepcopy(m) if m is not None else meters()}, **pz))
        wls[name] = rows
    return {"mods": mods, "workloads": wls,
            "setup": {"busy": {"asked": 60, "wild_pawns": 60}, "arrivals_fired": 2, "hurt_ok": 30}}


# a clean minimal run: MEASURED, within budget; A/B delta and meter share computed
code, word, text, s = V.verdict(run(), "minimal")
check("clean exit", (code, word), (0, "MEASURED"))
check("clean budget", "WITHIN 10%" in text, True)
check("long A/B", s["long"]["ab_delta_pct"], 2.0)
check("long meter share", s["long"]["meter_share_pct"], round(100.0 * 6 * 2 / 2040.0, 3))
check("paused has no tick rate", "off_ms_per_tick" in s["paused"], False)
check("paused meter share", s["paused"]["meter_share_pct"], round(100.0 * 6 * 2 / 2040.0, 3))

# tier guard: the full tier refuses a minimal list, and a missing count
check("wrong list", V.verdict(run(mods=13), "full")[:2], (1, "WRONG_LIST"))
check("no count", V.verdict(run(mods=None), "minimal")[:2], (1, "WRONG_LIST"))
check("full ok", V.verdict(run(mods=540), "full")[:2], (0, "MEASURED"))

# a channel that never ran while armed (subjects without specimens) is UNMEASURED, never free
mm = meters()
mm["subjects"] = {"calls": 0, "totalMs": 0.0, "on": True}
code, word, text, _ = V.verdict(run(m=mm), "minimal")
check("subjects unmeasured", (code, word), (1, "UNMEASURED"))
check("subjects named", "channel subjects never ran" in text, True)

# a switched-off channel is UNMEASURED and says so
code, word, text, _ = V.verdict(run(m=meters(on=False)), "minimal")
check("switched off", (code, word, "switched off" in text), (1, "UNMEASURED", True))

# a rep that did not run its ticks is BLIND
r = run()
r["workloads"]["busy"][1]["ticks_run"] = 0
check("short rep", V.verdict(r, "minimal")[:2], (1, "BLIND"))

# an armed rep with no status is BLIND (not a free monitor)
r = run()
r["workloads"]["health"][1]["meters"] = None
check("no status", V.verdict(r, "minimal")[:2], (1, "BLIND"))

# a channel missing from status is BLIND
check("channel missing", V.verdict(run(m=meters(skip=("ui",))), "minimal")[:2], (1, "BLIND"))

# GPT review 2026-11-02: missing tick fields, zero ticks, an empty meters dict, a dropped channel key, failed setup
r = run()
del r["workloads"]["busy"][0]["ticks_run"], r["workloads"]["busy"][0]["ticks_req"]
check("tick fields absent", V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
for row in r["workloads"]["long"]:
    row["ticks_req"] = row["ticks_run"] = 0
check("zero ticks", V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
r["workloads"]["busy"][1]["meters"] = {}
check("empty meters", V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
del r["workloads"]["busy"][1]["meters"]["clock"]
check("channel key dropped", V.verdict(r, "minimal")[:2], (1, "BLIND"))
for k, v in (("busy", {"asked": 60, "wild_pawns": 3}), ("arrivals_fired", 0), ("hurt_ok", 0)):
    r = run()
    r["setup"][k] = v
    check("setup " + k, V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
del r["setup"]
check("setup absent", V.verdict(r, "minimal")[:2], (1, "BLIND"))

# GPT review pass 2: a paused rep whose pause/window did not take, zero wall times (no crash), ABBA balance
r = run()
r["workloads"]["paused"][1]["paused_ok"] = False
check("paused not taken", V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
for row in r["workloads"]["long"]:
    if row["arm"] == "off":
        row["wall_ms"] = 0
check("zero wall is BLIND, no crash", V.verdict(r, "minimal")[:2], (1, "BLIND"))
for name, (reps, _t) in V.WORKLOADS.items():
    check("even reps " + name, reps % 2, 0)
    order = V.abba(reps)
    check("abba count " + name, (order.count(False), order.count(True)), (reps, reps))
    walls = [100.0 + 10 * i for i in range(len(order))]       # linear drift, zero overhead
    import statistics as _st
    off = _st.median(w for w, arm in zip(walls, order) if not arm)
    arm = _st.median(w for w, arm in zip(walls, order) if arm)
    check("abba unbiased " + name, off, arm)
# span_ms (status read to status read) is the meter-share denominator when present
r = run()
for row in r["workloads"]["long"]:
    if row["arm"] == "armed":
        row["span_ms"] = 2 * row["wall_ms"]
check("share over span", V.verdict(r, "minimal")[3]["long"]["meter_share_pct"], round(100.0 * 6 * 2 / 4080.0, 3))

# GPT review pass 3: an off rep whose disarm failed (monitor still armed), an armed rep that lapsed, no state read
for idx, st in ((0, [True, True]), (1, [True, False]), (0, None)):
    r = run()
    r["workloads"]["busy"][idx]["armed_state"] = st
    check("armed state %d %r" % (idx, st), V.verdict(r, "minimal")[:2], (1, "BLIND"))

# a missing workload and too few reps are BLIND
r = run()
del r["workloads"]["arrivals"]
check("workload absent", V.verdict(r, "minimal")[:2], (1, "BLIND"))
r = run()
r["workloads"]["long"] = r["workloads"]["long"][:2]
check("too few reps", V.verdict(r, "minimal")[:2], (1, "BLIND"))

# over budget is still MEASURED (a measurement item), but says OVER
code, word, text, _ = V.verdict(run(armed_ms=1200.0), "minimal")
check("over budget measured", (code, word, "OVER 10%" in text), (0, "MEASURED", True))
code, word, text, _ = V.verdict(run(m=meters(ms=200.0)), "minimal")
check("meter share over", "OVER 10%" in text, True)

# _delta subtracts and keeps the switch
d = V._delta({"pawns": {"calls": 30, "totalMs": 5.5, "on": True}}, {"pawns": {"calls": 10, "totalMs": 1.5, "on": True}})
check("delta pawns", d["pawns"], {"calls": 20, "totalMs": 4.0, "on": True})
check("delta absent", d["ui"], None)

# the CLI --judge path agrees with verdict and exits with its code
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "r.json")
    with open(p, "w") as f:
        json.dump(run(), f)
    cp = subprocess.run([sys.executable, os.path.join(HERE, "vitals_overhead.py"), "--tier", "minimal", "--judge", p],
                        capture_output=True, text=True, timeout=60)
    check("cli exit", cp.returncode, 0)
    check("cli word", "MEASURED" in cp.stdout, True)
    with open(p, "w") as f:
        json.dump(run(m=meters(calls=0)), f)
    cp = subprocess.run([sys.executable, os.path.join(HERE, "vitals_overhead.py"), "--tier", "minimal", "--judge", p],
                        capture_output=True, text=True, timeout=60)
    check("cli unmeasured exit", cp.returncode, 1)

if FAILS:
    print("FAIL selftest_vitals_overhead: %d" % len(FAILS))
    for f in FAILS:
        print("  " + f)
    sys.exit(1)
print("PASS selftest_vitals_overhead")
