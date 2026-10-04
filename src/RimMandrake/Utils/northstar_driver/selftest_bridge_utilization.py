#!/usr/bin/env python3
"""Selftest for bridge_utilization.py: fixture ledger + two fake results files."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge_utilization as U  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print("%s  %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


with tempfile.TemporaryDirectory() as d:
    led = os.path.join(d, "ledger")
    os.makedirs(led)
    evs = [
        {"seat": "FOUNDRY", "event": "bridge", "state": "taken", "purpose": "run A", "ts": "2026-10-01T10:00:00Z"},
        {"seat": "FOUNDRY", "event": "game", "state": "LOADING", "ts": "2026-10-01T10:05:00Z"},
        {"seat": "FOUNDRY", "event": "bridge", "state": "released", "ts": "2026-10-01T11:00:00Z"},
        {"seat": "FOUNDRY", "event": "note", "id": "X", "ts": "2026-10-01T10:30:00Z"},
    ]
    with open(os.path.join(led, "FOUNDRY.jsonl"), "w") as fh:
        fh.write("\n".join(json.dumps(e) for e in evs) + "\n")
    mc = os.path.join(d, "mc.jsonl")
    # naive local (America/Los_Angeles, PDT = UTC-7): 03:20-03:40 local = 10:20-10:40Z
    with open(mc, "w") as fh:
        fh.write(json.dumps({"job": "j", "started": "2026-10-01T03:20:00", "finished": "2026-10-01T03:40:00"}) + "\n")
        fh.write(json.dumps({"job": "dry", "dry_run": True, "started": "2026-10-01T03:00:00",
                             "finished": "2026-10-01T03:59:00"}) + "\n")
    ns = os.path.join(d, "ns")
    os.makedirs(ns)
    json.dump({"mod": "M", "mode": "live", "started_utc": "2026-10-01T10:45:00Z", "timing": {"total_ms": 300000}},
              open(os.path.join(ns, "M_1.json"), "w"))
    json.dump({"mod": "Mock", "mode": "mock", "started_utc": "2026-10-01T10:00:00Z", "timing": {"total_ms": 3600000}},
              open(os.path.join(ns, "Mock_1.json"), "w"))
    sess = os.path.join(d, "sessions.jsonl")
    with open(sess, "w") as fh:   # 10:55-10:58Z, overlaps nothing else; plus one junk line
        fh.write(json.dumps({"started": "2026-10-01T10:55:00Z", "finished": "2026-10-01T10:58:00Z", "script": "s.py"}) + "\nnot json\n")
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Los_Angeles")
    e = U.read_events(led)
    held = U.held_intervals(e, U._utc("2026-10-02T00:00:00Z"))
    act = U.active_intervals([mc], os.path.join(ns, "*.json"), tz)
    check("one hold read", len(held) == 1 and held[0][2] == "FOUNDRY", str(held))
    check("dry run and mock skipped", len(act) == 2, str(act))
    act3 = U.active_intervals([mc], os.path.join(ns, "*.json"), tz, sess)
    r3 = U.report(held, act3, [], U.dt.date(2026, 10, 1), 5)
    check("session log adds 3 active min", r3["active_min"] == 28.0, str(r3["active_min"]))
    r = U.report(held, act, [x for x in e if x["event"] == "game"], U.dt.date(2026, 10, 1), 5)
    check("held 60 min", r["held_min"] == 60.0, str(r["held_min"]))
    check("active 25 min (20 modcheck + 5 northstar)", r["active_min"] == 25.0, str(r["active_min"]))
    check("utilization 25/60", abs(r["utilization"] - 25 / 60) < 1e-3, str(r["utilization"]))
    g = r["gaps"]
    check("two gaps > 5 min (10:00-10:20, 10:50-11:00)", [x["minutes"] for x in g] == [20.0, 10.0], str(g))
    check("first gap attributed to the LOADING event", g and g[0]["cause"].startswith("cold load"), str(g[:1]))
    r2 = U.report(held, act, [], U.dt.date(2026, 10, 2), 5)
    check("other day is empty", r2["held_min"] == 0 and r2["utilization"] is None, str(r2))

print("%d/%d" % (9 - len(fails), 9))
sys.exit(1 if fails else 0)
