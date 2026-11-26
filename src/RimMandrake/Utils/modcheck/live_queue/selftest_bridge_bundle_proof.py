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
      "facingWrong": [], "returnedHome": 3, "save": "RM_pyre_review_x", "pinBefore": ["a", "b", "c"], "pinAfter": [],
      "moved600": ["a"], "lateTicks": 9000}
check("PEN2 released, moved, stayed, re-pinned", "PEN2", pn, 0)
check("PEN2 nobody moved (statues)", "PEN2", dict(pn, moved=[]), 1)
check("PEN2 one walked out of its pen", "PEN2", dict(pn, outside=["b"]), 1)
check("PEN2 a facing not restored", "PEN2", dict(pn, facingWrong=["c: South -> North"]), 1)
check("PEN2 one stayed pinned", "PEN2", dict(pn, released=2, notReleased=1), 1)
check("PEN2 the layout selects nobody", "PEN2", dict(pn, selected=0, ids=[]), 2)
check("PEN2 one left on the pin after release", "PEN2", dict(pn, pinAfter=["c"]), 1)
check("PEN2 the pin reading blind on the pinned state: UNMEASURED", "PEN2", dict(pn, pinBefore=[]), 2)
for _job, _want in (({"def": "Wait", "giver": None, "expiryInterval": 60000}, "pin"),
                    ({"def": "Wait", "giver": "RM_JobGiver_ShadeHop", "expiryInterval": 900}, "rest"),
                    ({"def": "Wait", "giver": "JobGiver_IdleError", "expiryInterval": 100}, "rest"),
                    ({"def": "GotoWander", "giver": "JobGiver_WanderAnywhere", "expiryInterval": -1}, "other"),
                    (None, "none")):
    _got = B.pen_job_class(_job)
    print("%s pen_job_class %-60s -> %s" % ("ok  " if _got == _want else "FAIL", _job, _got))
    if _got != _want:
        FAILS.append("pen_job_class %s" % _job)
check("ORIGIN a wild animal that arrived after mapgen is not a FAIL", "ORIGIN",
      dict(og, wild=["Thing_A1", "Thing_A3"], chains={"Thing_A1": "mapgen > wild-spawner", "Thing_A3": "wild-spawner"}), 0)
check("ORIGIN only late arrivals: no mapgen wildlife read", "ORIGIN",
      dict(og, wild=["Thing_A3"], chains={"Thing_A3": "wild-spawner"}), 1)
check("PEN2 a home cell held by another pen animal is the tool's rule, not a FAIL", "PEN2",
      dict(pn, returnedHome=2, homeOccupied=["c"]), 0)
# ---- TPSC3: a green fixture of the whole matrix, then one planted fault per rule
import copy as _copy


def _c3_inc(b):
    gap = round(b["blockedS"] + 0.02, 3)
    return {"gapS": gap, "kind": "incident", "type": "stall", "quietPhase": "Update@%.1fs" % b["blockedS"], "game": 1,
            "rendered": "2026-11-25 12:00:00 -08:00 PST stall %.3fs blocked in Update@x game 1" % gap,
            "mono": 1000.0, "gapStartMono": round(1000.0 - gap, 3)}


def _c3_green():
    bl = []
    for lab, x in ([("run", x) for x in B.C3_RUN_BLOCKS] + [("edge", x) for x in B.C3_EDGE_BLOCKS] +
                   [("fast", B.C3_FAST_BLOCK), ("paused", B.C3_PAUSED_BLOCK)] + [("long", x) for x in B.C3_LONG_BLOCKS]):
        b = {"label": "%s %.2f #%d" % (lab, x, len(bl)), "requestedS": x, "blockedS": x, "utcStart": "a", "utcEnd": "b",
             "game": 1}
        b["incidents"] = [_c3_inc(b)]
        b["contain"] = {"slack": 0.4, "simShare": 0.3, "monoStart": 990.0 - x, "monoEnd": 1001.0}
        bl.append(b)
    hb3 = [{"hbSeq": k, "scene": "menu"} for k in (1, 2, 3)]
    f = lambda n, by, torn=False: {"name": n, "bytes": by, "lines": 10, "bad": 0, "torn": torn}
    return {
        "platform": "nt", "recordDir": "X",
        "item1": [{"label": l, "pid": 1, "segment": "tps_s.jsonl", "startedBy": "bridge-registration",
                   "sampler": "complete", "hbs": list(hb3)} for l in ("cold A", "cold E")],
        "games": [{"label": l, "wantSeq": q, "wantSave": v, "row": {"game": q, "save": v}, "windows": 3}
                  for l, q, v in zip(B.C3_GAMES, (1, 1, 2, 3), ("", "L", "L", ""))],
        "blocks": bl,
        "strict": {"files": 6, "lines": 900, "bad": 0, "badSample": None},
        "saves": [{"label": "s1", "saveS": 0.4, "incidents": []},
                  {"label": "s2", "saveS": 3.2, "incidents": [{"type": "longevent", "gapS": 3.3, "explainedS": 3.2}]}],
        "hang": {"session": "h", "hbs": [{"watchdogMono": 10.0 * k, "watchdogEp": 100.0 + 10 * k, "mainBeatMono": 5.0,
                                          "mainBeatEp": 95.0 + 0.01 * k, "silentS": 10.0 * k} for k in (1, 2, 3, 4)],
                 "silenceRows": 3, "killed": True, "killWhy": "k", "observerErr": None, "observerRows": 1,
                 "findings": [], "observerRowsAfter": 1,
                 "retention": {"patterns": ["tps_*.jsonl", "hb_*.json"], "sane": True, "hits": []}},
        "kills": [{"label": l, "killed": True, "why": "w",
                   "files": [f("a", 2097000)] + ([f("b", 300, True)] if l == "K4-after-rotation" else [])}
                  for l in B.C3_KILLS],
        "readback": {"replayed": 0, "conflicts": 0, "malformed": 1, "torn": 1, "files": 5, "seqMissing": "[]"},
    }


def _c3(mut):
    d = _c3_green()
    mut(d)
    return d


check("TPSC3 the whole matrix green", "TPSC3", _c3_green(), 0)
_red = [
    ("two incidents over one block", lambda d: d["blocks"][0]["incidents"].append(dict(d["blocks"][0]["incidents"][0]))),
    ("no incident over a block", lambda d: d["blocks"][3].update(incidents=[])),
    ("gapS short of blockedS", lambda d: d["blocks"][1]["incidents"][0].update(gapS=1.9)),
    ("gapS far over blockedS", lambda d: d["blocks"][1]["incidents"][0].update(gapS=3.2)),
    ("kind not incident", lambda d: d["blocks"][2]["incidents"][0].update(kind="stall")),
    ("an edge hitch with no phase", lambda d: d["blocks"][6]["incidents"][0].update(quietPhase="")),
    ("a phase but no 'blocked in'", lambda d: d["blocks"][6]["incidents"][0].update(rendered="2026 12:00:00 -08:00 PST stall")),
    ("no offset in local time", lambda d: d["blocks"][0]["incidents"][0].update(rendered="12:00:00 stall blocked in X")),
    ("game id mismatch", lambda d: d["blocks"][0]["incidents"][0].update(game=2)),
    ("no containing window", lambda d: d["blocks"][0].update(contain=None)),
    ("window misses the gap", lambda d: d["blocks"][0]["contain"].update(slack=-0.2)),
    ("simShare over 1", lambda d: d["blocks"][0]["contain"].update(simShare=1.3)),
    ("a bad strict line", lambda d: d["strict"].update(bad=1, badSample='{"a":1,"a":2}')),
    ("a long save with no incident", lambda d: d["saves"][1].update(incidents=[])),
    ("a save that is a stall", lambda d: d["saves"][1]["incidents"][0].update(type="stall")),
    ("a save under-explained", lambda d: d["saves"][1]["incidents"][0].update(explainedS=1.0)),
    ("a save with no save row", lambda d: d["saves"][0].update(saveS=None)),
    ("the main beat moved in the hang", lambda d: d["hang"]["hbs"][3].update(mainBeatMono=40.0)),
    ("the watchdog stopped in the hang", lambda d: d["hang"]["hbs"][3].update(watchdogMono=20.0)),
    ("one silence row", lambda d: d["hang"].update(silenceRows=1)),
    ("two observer rows", lambda d: d["hang"].update(observerRows=2)),
    ("no observer row", lambda d: d["hang"].update(observerRows=0)),
    ("the observer row gone next launch", lambda d: d["hang"].update(observerRowsAfter=0)),
    ("a retention pattern deletes observer.jsonl", lambda d: d["hang"]["retention"].update(hits=["*.jsonl"])),
    ("a glued line in a killed file", lambda d: d["kills"][0]["files"][0].update(bad=1)),
    ("a torn line mid-session", lambda d: d["kills"][3]["files"][0].update(torn=True)),
    ("a segment over 2 MiB", lambda d: d["kills"][2]["files"][0].update(bytes=B.C3_SEGMENT_BYTES + 1)),
    ("a replayed row", lambda d: d["readback"].update(replayed=1)),
    ("a conflicting row", lambda d: d["readback"].update(conflicts=1)),
    ("malformed beyond the torn tails", lambda d: d["readback"].update(malformed=2)),
    ("item 1 startedBy a client", lambda d: d["item1"][0].update(startedBy="tps_report")),
    ("item 1 sampler partial", lambda d: d["item1"][1].update(sampler="partial")),
    ("item 1 heartbeat stuck", lambda d: d["item1"][0].update(hbs=[{"hbSeq": 1, "scene": "menu"}] * 3)),
    ("item 1 heartbeat not at the menu", lambda d: d["item1"][0]["hbs"][0].update(scene="map")),
    ("item 1 no segment", lambda d: d["item1"][0].update(segment=None)),
    ("a load with the wrong save label", lambda d: d["games"][2]["row"].update(save="")),
    ("a reused game seq", lambda d: d["games"][2]["row"].update(game=1)),
    ("a game with no window", lambda d: d["games"][0].update(windows=0)),
]
for _n, _m in _red:
    check("TPSC3 planted: %s" % _n, "TPSC3", _c3(_m), 1)
_gap = [
    ("posix python", lambda d: d.update(platform="posix")),
    ("aborted", lambda d: d.update(aborted="_C3Stop: E: launch_ready FAILED")),
    ("the block tool refused", lambda d: d["blocks"][0].update(refused="FTestOnly off", incidents=None)),
    ("blocks missing", lambda d: d.update(blocks=d["blocks"][:5])),
    ("no long save reached", lambda d: d.update(saves=d["saves"][:1], rampWhy="map 250x250, 0.9 s")),
    ("a kill not run", lambda d: d.update(kills=d["kills"][:3])),
    ("no rotation", lambda d: d["kills"][3].update(files=d["kills"][3]["files"][:1])),
    ("K3 short of the boundary", lambda d: d["kills"][2]["files"][0].update(bytes=1000)),
    ("observer not reread", lambda d: d["hang"].update(observerRowsAfter=None)),
    ("one cold launch", lambda d: d.update(item1=d["item1"][:1])),
    ("a game not reached", lambda d: d.update(games=d["games"][:3])),
    ("no read-back", lambda d: d.update(readback=None)),
]
for _n, _m in _gap:
    check("TPSC3 gap: %s" % _n, "TPSC3", _c3(_m), 2)
print("RESULT: %s" % ("FAIL (%d failing)" % len(FAILS) if FAILS else "PASS (0 failing)"))
sys.exit(1 if FAILS else 0)
