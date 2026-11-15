#!/usr/bin/env python3
"""acceptance_game_health_growth_per_game.py - the oracle for RIMMANDRAKE_SCOPE_HEAP_GROWTH_TO_ONE_GAME_SIX_LOADS.

mem.managed_growth_mb_per_h is a leak rate: heap growth while ONE game runs. game_health_check.py measures it from the
first game load to the end, so a staged visit that loads six saves in 54 minutes and never unpauses reads the reload
ratchet's steps as 1036.6 MB/h and pages (session a46da9a1, 2026-11-15; heap_ratchet.py: reload_ratchet). The reload
ratchet has its own instrument (heap_ratchet.py) and item (HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE).

Synthetic sessions, offline. Passes when:
  staged:  7 game loads, heap flat inside each game, +180 MB per load, 63 min, never unpaused -> no growth breach
  leak:    one game, +1200 MB/h for 60 min -> still a measured growth breach (the limit is not simply deleted)
  late:    a short first game, then one 45-min game growing 1200 MB/h -> still a measured growth breach
Expected: 3 PASS, exit 0. On the base commit (d403120931) the staged case FAILS (exit 1).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_health_check as G  # noqa: E402

T0 = 1793000000.0
KEY = "mem.managed_growth_mb_per_h"
FAILS = []


def utc(t):
    import datetime as D
    return D.datetime.fromtimestamp(t, D.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def session(sid, games, state):
    """games: [(minutes, heap_start, heap_rate_h)]; one context + one sample row per minute."""
    rows, seq = [], [0]

    def add(t, kind, **kw):
        seq[0] += 1
        r = {"seq": seq[0], "v": 2, "utc": utc(t), "mono": round(t - T0, 3), "session": sid, "kind": kind}
        r.update(kw)
        rows.append(r)

    add(T0, "session", pid=4242, build="b", engine="1.6", mods=316, modDigest="d1")
    add(T0 + 10, "menu", programState="Entry")
    t = T0 + 60
    for n, (minutes, h0, rate) in enumerate(games, 1):
        add(t, "game", game=n, save="SAVE_%d" % n, ticksGame=1, maps=1)
        for i in range(minutes):
            ti = t + i * 60.0
            heap = h0 + rate * (i / 60.0)
            add(ti + 5, "sample", state=state, ratio=1.0, tps=60.0, mult=1, dReal=5.0, heapMB=heap)
            add(ti + 6, "context", heapMB=heap, workingSetMB=0, privateMB=heap * 2 + 1000, gfxMB=0,
                upS=round(900 + (ti + 6 - T0), 1), logErr=0, logWarn=0, logEnabled=True, logMsgs=0,
                logCapReached=False, logErrLowerBound=False)
        t += minutes * 60.0
    add(t + 1, "shutdown", phase="intent")
    return rows


def growth(name, rows):
    with tempfile.TemporaryDirectory() as tmp:
        rec = os.path.join(tmp, "tps")
        os.makedirs(rec)
        p = os.path.join(rec, "tps_20261115T000000Z_%s_4242_000.jsonl" % rows[0]["session"])
        with open(p, "w") as fh:
            import json
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        res = G.record(directory=rec, rules=G.load_rules(), path=os.path.join(tmp, "history.jsonl"),
                       now=T0 + 13 * 3600)
        row = res["recorded"][0]
        return row["metrics"].get(KEY), [b["key"] for b in row.get("breaches") or []]


def check(name, ok, detail):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  :: %r" % (detail,)))
    if not ok:
        FAILS.append(name)


g, br = growth("staged", session("e" * 32, [(9, 3200 + 180 * k, 0.0) for k in range(7)], "pause"))
check("staged: seven flat games stepping 180 MB per load, never unpaused, breach no growth key",
      not any(k.endswith("_growth_mb_per_h") for k in br), (g, br))
g, br = growth("leak", session("f" * 32, [(60, 3200, 1200.0)], "run"))
check("leak: one game growing 1200 MB/h for 60 min still breaches", KEY in br and G.is_m(g) and g > 1024, (g, br))
g, br = growth("late", session("0" * 32, [(5, 3000, 0.0), (45, 3300, 1200.0)], "run"))
check("late: a 45-min game growing 1200 MB/h after a short first game still breaches", KEY in br and G.is_m(g), (g, br))
print("%d FAIL" % len(FAILS) if FAILS else "3 PASS")
sys.exit(1 if FAILS else 0)
