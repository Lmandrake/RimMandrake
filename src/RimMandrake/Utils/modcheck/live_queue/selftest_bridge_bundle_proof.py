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

good = {"noFileProfile": "campaign", "spawnRan": True, "staticRefused": True, "backProfile": "test", "flipS": 0.4,
        "listedProfile": "campaign"}
check("PROFILE both halves", "PROFILE", good, 0)
check("PROFILE static_call allowed in campaign", "PROFILE", dict(good, staticRefused=False), 1)
check("PROFILE a listed campaign save reads test", "PROFILE", dict(good, listedProfile="test"), 1)
check("PROFILE slow flip", "PROFILE", dict(good, flipS=5.0), 1)

pen = {"ids": [1, 2], "waitBefore": 2, "release": {"released": 2, "notReleased": 0}, "waitAfter": 0,
       "pin": {"pinned": 2, "returnedHome": 2}}
check("PEN release and pin", "PEN", pen, 0)
check("PEN one still waits", "PEN", dict(pen, waitAfter=1), 1)

amb = {"resolved": False, "ambiguous": [1, 2]}
check("EXPLAIN ambiguous + vanished refused", "EXPLAIN", {"name": amb, "cell": amb, "gone": {"success": False}}, 0)
check("EXPLAIN vanished id resolved (2026-11-25)", "EXPLAIN",
      {"name": amb, "cell": amb, "gone": {"success": True, "resolved": True}}, 1)
check("EXPLAIN killed pawn refused like a vanished one (review 2026-11-25)", "EXPLAIN",
      {"name": amb, "cell": amb, "gone": {"success": False}, "dead": {"success": False}}, 1)
check("EXPLAIN killed pawn still explains", "EXPLAIN",
      {"name": amb, "cell": amb, "gone": {"success": False}, "dead": {"success": True, "resolved": True}}, 0)
check("TPS report gives no min/median/max", "TPS", {"windows": win, "summary": {}, "grew": 3000}, 1)
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
      "oldEpochMsg": "REFUSED: stale expectGameEpoch", "absentMapMsg": "REFUSED: no such map",
      "releaseAfterLoad": "new-game", "releaseAfterTtl": "expired"}
check("EPOCH all refusals", "EPOCH", ep, 0)
check("EPOCH old epoch passes", "EPOCH", dict(ep, oldEpoch=True), 1)
check("EPOCH a client error read as a refusal (2026-11-25)", "EPOCH",
      dict(ep, oldEpochMsg="jawa/map_info does not declare expectGameEpoch"), 1)
check("EPOCH reload kept the epoch", "EPOCH", dict(ep, epochAfter=1), 1)
check("EPOCH block survives the load", "EPOCH", dict(ep, releaseAfterLoad=None), 1)
fr = {"sessionParses": True, "mergedParses": True, "n0": 3, "n1": 300}
check("FRAME parses, fresh, no late frames", "FRAME", fr, 0)
check("FRAME malformed session string", "FRAME", dict(fr, sessionParses=False), 1)
check("FRAME arm does not reset", "FRAME", dict(fr, n0=2400, n1=2700), 1)
check("FRAME load frames merged late", "FRAME", dict(fr, n1=2100), 1)
check("PROFILE no save loaded", "PROFILE", {"why": "precondition"}, 2)
kp = {"keepers": 4, "unstored": [], "save": {"verified": True, "problems": [], "changed": ["bundle_keeper_x.rws"]},
      "target": "bundle_keeper_x", "slot": "none"}
check("KEEPER every keeper stored, a new save verified", "KEEPER", kp, 0)
check("KEEPER a keeper with no store copy", "KEEPER", dict(kp, unstored=["Colony.rws"]), 1)
check("KEEPER a keeper changed by the save", "KEEPER",
      dict(kp, save={"verified": False, "problems": ["keeper Colony.rws CHANGED (5 -> 6 bytes)"], "changed": []}), 1)
check("KEEPER the save went to another slot", "KEEPER",
      dict(kp, save={"verified": False, "problems": ["no bundle_keeper_x.rws appeared"], "changed": []}), 1)
check("KEEPER no keeper to guard", "KEEPER", dict(kp, keepers=0), 2)
check("KEEPER the guard could not back up", "KEEPER", {"why": "cannot back up keepers"}, 2)

og = {"launchRc": 0, "startedBy": "bridge-registration", "genHook": "installed early (install.generation-early) by bridge-registration",
      "wild": ["Thing_A1", "Thing_A2"], "chains": {"Thing_A1": "mapgen > wild-spawner", "Thing_A2": "mapgen > wild-spawner"},
      "restored": True}
check("ORIGIN cold launch, mapgen wildlife chain", "ORIGIN", og, 0)
check("ORIGIN started by a tool call", "ORIGIN", dict(og, startedBy="tool-call"), 1)
check("ORIGIN a wild animal with origin unknown", "ORIGIN", dict(og, chains={"Thing_A1": "mapgen > wild-spawner", "Thing_A2": None}), 1)
check("ORIGIN chain without the spawner", "ORIGIN", dict(og, chains={"Thing_A1": "mapgen", "Thing_A2": "mapgen"}), 1)
check("ORIGIN the hook was not installed early", "ORIGIN", dict(og, genHook="not installed (lazy)"), 2)
check("ORIGIN no wildlife on the first map", "ORIGIN", dict(og, wild=[], chains={}), 2)
check("ORIGIN the launch failed", "ORIGIN", dict(og, launchRc=1), 2)
check("ORIGIN the settings file was not restored", "ORIGIN", dict(og, restored=False), 1)
check("AWARE a game launched with generation-early is a precondition, not a FAIL", "AWARE",
      {"early": True, "genBefore": True, "genAfter": False}, 2)
wb = {"blocked": True, "ticks": 1300, "skipped": 1300, "releasedBlocked": False, "lastRelease": "released",
      "afterTicks": 120, "skippedAfter": 0}
check("WILDBLOCK blocks, skips each tick, release restores", "WILDBLOCK", wb, 0)
check("WILDBLOCK skips nothing over 1300 ticks", "WILDBLOCK", dict(wb, skipped=0), 1)
check("WILDBLOCK still skipping after the release", "WILDBLOCK", dict(wb, skippedAfter=120), 1)
check("WILDBLOCK block not read back", "WILDBLOCK", dict(wb, blocked=False), 1)
check("WILDBLOCK the clock moved too little", "WILDBLOCK", dict(wb, ticks=400, skipped=400), 2)
pt = {"gssStarted": True, "fwRefusal": "A GSS playtest run is active: g1. Collect or abort it", "fwRefused": True,
      "fwStarted": True, "fwRunningAtCall": True, "gssRefusal": "A FlowWorks playtest run is active: p1.", "gssRefused": True}
# measured 2026-11-25 (lane job J20261125T214629Z-889e6f): the FlowWorks 'fluids' run completed in 4 frames, so the
# GSS start came after it and ran: the scene was wrong, not the guard
check("PLAYTEST the FlowWorks run ended before the cross-call", "PLAYTEST",
      dict(pt, fwRunningAtCall=False, gssRefused=False, gssRefusal="{\"success\": true, \"runId\": \"gsspt_1\"}"), 2)
check("PLAYTEST GSS started beside a running FlowWorks run", "PLAYTEST",
      dict(pt, gssRefused=False, gssRefusal="{\"success\": true}"), 1)
check("PLAYTEST each runner refuses while the other runs", "PLAYTEST", pt, 0)
check("PLAYTEST FlowWorks started beside a GSS run", "PLAYTEST", dict(pt, fwRefused=False, fwRefusal=""), 1)
# the real shape of that fault: the stray FlowWorks run still holds the slot, so the second playtest_start is refused
check("PLAYTEST FlowWorks started beside a GSS run, its own second start then refused", "PLAYTEST",
      dict(pt, fwRefused=False, fwRefusal="", fwStarted=False,
           startMsg="A playtest run is active: p0. Pass force=true to abort it."), 1)
check("PLAYTEST GSS refused for another reason", "PLAYTEST", dict(pt, gssRefusal="No current map."), 1)
check("PLAYTEST the first run never started", "PLAYTEST", dict(pt, gssStarted=False), 2)
cp = {"profile": "campaign", "artRefused": True, "artMsg": "REFUSED under the CAMPAIGN profile: killHostiles destroys",
      "setRefused": True, "setMsg": "REFUSED: set is off under the CAMPAIGN profile (x)", "restored": "test"}
check("CAMPAIGN both writes refused", "CAMPAIGN", cp, 0)
check("CAMPAIGN killHostiles ran", "CAMPAIGN", dict(cp, artRefused=False, artMsg=""), 1)
check("CAMPAIGN set refused for the type, not the profile", "CAMPAIGN", dict(cp, setMsg="REFUSED: 'x' is neither"), 1)
check("CAMPAIGN the profile never read campaign", "CAMPAIGN", dict(cp, profile="test"), 2)
check("CAMPAIGN the profile file not restored", "CAMPAIGN", dict(cp, restored="campaign"), 1)
st = {"refused": True, "msg": "REFUSING before clearing: 1 row(s) land on a tile", "before": 40, "after": 40}
check("SETTLE refused before clearing, nothing removed", "SETTLE", st, 0)
check("SETTLE cleared the roster", "SETTLE", dict(st, refused=False, msg="", after=1), 1)
check("SETTLE refused but removed some", "SETTLE", dict(st, after=39), 1)
check("SETTLE the import refused a row instead", "SETTLE", dict(st, msg="REFUSING the whole import: 1 of 1"), 2)
pn = {"selected": 3, "released": 3, "notReleased": 0, "ids": ["a", "b", "c"], "moved": ["a", "b"], "outside": [],
      "facingWrong": [], "returnedHome": 3, "save": "RM_pyre_review_x"}
check("PEN2 released, moved, stayed, re-pinned", "PEN2", pn, 0)
check("PEN2 nobody moved (statues)", "PEN2", dict(pn, moved=[]), 1)
check("PEN2 one walked out of its pen", "PEN2", dict(pn, outside=["b"]), 1)
check("PEN2 a facing not restored", "PEN2", dict(pn, facingWrong=["c: South -> North"]), 1)
check("PEN2 one stayed pinned", "PEN2", dict(pn, released=2, notReleased=1), 1)
check("PEN2 the layout selects nobody", "PEN2", dict(pn, selected=0, ids=[]), 2)
check("ORIGIN a wild animal that arrived after mapgen is not a FAIL", "ORIGIN",
      dict(og, wild=["Thing_A1", "Thing_A3"], chains={"Thing_A1": "mapgen > wild-spawner", "Thing_A3": "wild-spawner"}), 0)
check("ORIGIN only late arrivals: no mapgen wildlife read", "ORIGIN",
      dict(og, wild=["Thing_A3"], chains={"Thing_A3": "wild-spawner"}), 1)
check("PEN2 a home cell held by another pen animal is the tool's rule, not a FAIL", "PEN2",
      dict(pn, returnedHome=2, homeOccupied=["c"]), 0)
print("RESULT: %s" % ("FAIL (%d failing)" % len(FAILS) if FAILS else "PASS (0 failing)"))
sys.exit(1 if FAILS else 0)
