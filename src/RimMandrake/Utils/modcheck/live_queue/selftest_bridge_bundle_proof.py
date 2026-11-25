#!/usr/bin/env python3
"""selftest_bridge_bundle_proof.py - the pure verdicts of bridge_bundle_proof.py: each clause PASSes its good reading,
FAILs a planted bad one, and reads a missing precondition UNMEASURED. The bad readings are the ones measured live on
2026-11-25 (Steve1) where they exist: a vanished id that thing_explain still resolved, an end row without a pid."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bridge_bundle_proof as B  # noqa: E402

FAILS = []


def check(name, clause, d, want):
    rc, msg = B.verdict(clause, d)
    print("%s %-52s -> %d %s" % ("ok  " if rc == want else "FAIL", name, rc, msg[:120]))
    if rc != want:
        FAILS.append(name)


rows = [{"ev": "start", "cid": "a", "pid": 1}, {"ev": "end", "cid": "a"}]
check("EVIDENCE start and end", "EVIDENCE", {"rows": rows, "cids": ["a"], "inflight": []}, 0)
check("EVIDENCE end missing", "EVIDENCE", {"rows": rows[:1], "cids": ["a"], "inflight": []}, 1)
check("EVIDENCE marker left", "EVIDENCE", {"rows": rows, "cids": ["a"], "inflight": ["a.1.json"]}, 1)
check("EVIDENCE no calls", "EVIDENCE", {"rows": [], "cids": []}, 2)

win = [{"state": "run", "ratio": 1.0}] * 11
summ = {"min": 0.9, "median": 1.0, "max": 1.1}
check("TPS steady", "TPS", {"windows": win, "summary": summ, "grew": 3000}, 0)
check("TPS slow", "TPS", {"windows": [{"state": "run", "ratio": 0.4}] * 11, "summary": summ, "grew": 3000}, 1)
check("TPS segment flat", "TPS", {"windows": win, "summary": summ, "grew": 0}, 1)
check("TPS no segment", "TPS", {"why": "no segment"}, 2)

check("NORTHSTAR clean", "NORTHSTAR", {"faults": {}, "note": "x"}, 0)
check("NORTHSTAR a tool wrong", "NORTHSTAR", {"faults": {"damage_log": "0 events"}}, 1)
check("STATICCALL both resolve", "STATICCALL", {"calls": {"a": {"ok": True}, "b": {"ok": True}}, "note": "x"}, 0)
check("STATICCALL whole id lost", "STATICCALL", {"calls": {"a": {"ok": False, "message": "No thing"}}}, 1)
check("TILECACHE cycle", "TILECACHE", {"staleBefore": True, "verifiedNull": True, "staleAfter": False, "tile": 1}, 0)
check("TILECACHE reset left stale", "TILECACHE", {"staleBefore": True, "verifiedNull": True, "staleAfter": True}, 1)

good = {"noFileProfile": "campaign", "spawnRan": True, "staticRefused": True, "backProfile": "test", "flipS": 0.4}
check("PROFILE both halves", "PROFILE", good, 0)
check("PROFILE static_call allowed in campaign", "PROFILE", dict(good, staticRefused=False), 1)
check("PROFILE slow flip", "PROFILE", dict(good, flipS=5.0), 1)

pen = {"ids": [1, 2], "waitBefore": 2, "release": {"released": 2, "notReleased": 0}, "waitAfter": 0,
       "pin": {"pinned": 2, "returnedHome": 2}}
check("PEN release and pin", "PEN", pen, 0)
check("PEN one still waits", "PEN", dict(pen, waitAfter=1), 1)

amb = {"resolved": False, "ambiguous": [1, 2]}
check("EXPLAIN ambiguous + vanished refused", "EXPLAIN", {"name": amb, "cell": amb, "gone": {"success": False}}, 0)
check("EXPLAIN vanished id resolved (2026-11-25)", "EXPLAIN",
      {"name": amb, "cell": amb, "gone": {"success": True, "resolved": True}}, 1)
check("EXPLAIN tool picked one", "EXPLAIN", {"name": {"resolved": True}, "cell": amb, "gone": {"success": False}}, 1)

check("HOOKS all ok", "HOOKS", {"coverage": {"tps.Root.Update": "ok"}, "faults": 0, "minutes": 10}, 0)
check("HOOKS a hook dark", "HOOKS", {"coverage": {"tps.Root.Update": "never-entered"}, "faults": 0}, 1)
check("HOOKS a fault", "HOOKS", {"coverage": {"tps.Root.Update": "ok"}, "faults": 2}, 1)

check("AWARE lazy by arm, campaign off", "AWARE", {"early": False, "genBefore": False, "genAfter": True, "detailAfter": "x",
                                                   "campaignMeasured": True, "campaign": "refused in campaign"}, 0)
check("AWARE campaign arm installed it", "AWARE", {"genAfter": True, "campaignMeasured": True,
                                                   "campaign": "installed lazily by jawa/awareness arm"}, 1)
check("AWARE campaign half not measured", "AWARE", {"genAfter": True, "campaignMeasured": False}, 2)
check("AWARE installed at startup", "AWARE", {"early": False, "genBefore": True, "genAfter": True}, 1)
check("AWARE early set", "AWARE", {"early": True}, 2)

ep = {"epochBefore": 1, "epochAfter": 2, "oldEpoch": False, "absentMap": False, "currentBoth": True,
      "releaseAfterLoad": "new-game", "releaseAfterTtl": "expired"}
check("EPOCH all refusals", "EPOCH", ep, 0)
check("EPOCH old epoch passes", "EPOCH", dict(ep, oldEpoch=True), 1)
check("EPOCH reload kept the epoch", "EPOCH", dict(ep, epochAfter=1), 1)
check("EPOCH block survives the load", "EPOCH", dict(ep, releaseAfterLoad=None), 1)
fr = {"sessionParses": True, "mergedParses": True, "n0": 3, "n1": 300}
check("FRAME parses, fresh, no late frames", "FRAME", fr, 0)
check("FRAME malformed session string", "FRAME", dict(fr, sessionParses=False), 1)
check("FRAME arm does not reset", "FRAME", dict(fr, n0=2400, n1=2700), 1)
check("FRAME load frames merged late", "FRAME", dict(fr, n1=2100), 1)
check("PROFILE no save loaded", "PROFILE", {"why": "precondition"}, 2)

print("RESULT: %s" % ("FAIL (%d failing)" % len(FAILS) if FAILS else "PASS (0 failing)"))
sys.exit(1 if FAILS else 0)
