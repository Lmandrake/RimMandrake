#!/usr/bin/env python3
"""selftest_run_void.py: no trial, turn, look or cycle is spent by a system failure or a stopped run (run_void.py, item
RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT). Offline, in temp dirs; written before run_void.py and watched
failing on the base (the import fails), then passing.

    python3 src/RimMandrake/rimflow/selftest_run_void.py      exit 0 when every check prints PASS

What it proves, one counter of the census (design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md) at a time,
through the readers the pipeline itself uses: a hand void takes a run out of the blind cycles and in-game runs of a
visit, the steward's once-per-key and per-version counts, a fixer's key, the holder's one run per set, the builder's
last run and its road back; it restores a coverage look the run applied (the grant stands again, grant_waits empty,
stop_reason and the round caps as before), drops its judge's round and the legacy round its charge would rebuild, and its
Designer results and retries; it keeps the advisory verdict on file as evidence and puts the earlier one back. Unvoid
puts every one back. An unknown run, a void with no why, a double void and an unvoid of a run not void are refused; a run
that genuinely failed may be voided (his call) and is recorded as a hand void with its result. The automatic class:
a killed or result-less run in a book is void_system, counted on system_faults, never on a trial; a run that wrote its
result counts; a record that cannot be read is left as the books had it; at the fault limit the mod launches nothing
(system_fault, OPS_MATURATION_SYSTEM_FAULT_LOOP); a clear resets the count.
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS, COUNT = [], [0]


def ok(cond, what):
    COUNT[0] += 1
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


U1 = "rm-detached-bench-rimmandrake-retake-graffiti-exam-after-l-1795024763"     # the chain run (steward)
U2 = "rm-detached-bench-rimmandrake-route-graffiti-cycle-two-fai-1795025961"     # the route steward, killed
U3 = "rm-detached-bench-rimmandrake-settle-tribute-rival-band-ne-1795026309"     # its fixer, killed
UB = "rm-detached-bench-judge-fake-blind-cycle-two-1"
UI = "rm-detached-bench-drive-fake-in-game-visit-one-1"
UH = "rm-detached-bench-fix-fake-holder-1"
UL = "rm-detached-bench-autobuild-fake-1"
UD = "rm-steward-fake-chain-1795024973"
UJ = "rm-coverage-judge-1795025027"
T0 = 1795024742.0       # 2026-11-18 9:59 AM PST
ITEM1 = "RIMMANDRAKE_RETAKE_FAKE_EXAM_AFTER_LOCKED_CHANGE_RUN_TWO"


def state():
    s = {"steward": {
        "0.1.0|chain|2026-11-17T17:26:00Z": {"item": "RIMMANDRAKE_RETAKE_FAKE_EXAM_AFTER_LOCKED_CHANGE", "unit": "rm-old-1",
                                             "at": T0 - 90000, "failed": None, "tries": 1},
        "0.1.0|chain|2026-11-18T17:58:16Z": {"item": ITEM1, "unit": U1, "at": T0, "failed": None, "tries": 1},
        "0.1.0|blind_challenge|exit_not_met|2|6115bec2": {"item": "RIMMANDRAKE_ROUTE_FAKE_CYCLE_TWO_FAILURES_BACK",
                                                          "unit": U2, "at": T0 + 1200, "failed": None, "tries": 1}},
        "road_back": {"caused_by": "RIMMANDRAKE_ROUTE_FAKE_CYCLE_TWO_FAILURES_BACK", "at": T0 + 1200,
                      "from": "blind_challenge"},
        "fixers": {"RIMMANDRAKE_SETTLE_FAKE": {"item": "RIMMANDRAKE_SETTLE_FAKE", "unit": U3, "at": T0 + 1560,
                                               "failed": None, "tries": 1}},
        "blind_auto": [{"visit_id": "0.1.0#1", "cycle": 1, "unit": "rm-old-blind-1", "at": T0 - 99999},
                       {"visit_id": "0.1.0#1", "cycle": 2, "unit": UB, "at": T0 + 100}],
        "ingame_auto": [{"visit_id": "0.1.0#1", "visit": 1, "unit": UI, "at": T0 + 200}],
        "holder_road_back": [{"at": T0 + 1300, "ids": ["RB_1"], "item": "RB_1", "unit": UH}],
        "launches": [{"unit": UL, "item": "RIMMANDRAKE_AUTOBUILD_FAKE", "at": T0 + 50, "refused": 6, "ids": ["a"]}],
        "last_run": {"unit": UL, "refused_before": 6, "refused_after": 6}}
    return {"mods": {"Fake": s}}


def stage():
    return {"status": "blocked", "stage": 5,
            "blocked_on": "REFUSAL_NOTHING_COULD_EVER_PASS: 3 not_covered verdicts (limit 3); judging stopped on Fake "
                          "(coverage_judge.py release <dir> --why ... grants one more look)",
            "coverage_stop": {"at": "2026-11-17T18:29:13Z", "why": "3 not_covered verdicts (limit 3)"},
            "coverage_release_granted": {"at": "2026-11-17T18:45:12Z", "why": "one more look", "after": ["RB_FIX"]},
            "coverage_rounds": [{"judge": "rm-coverage-judge-%d" % n, "verdict": "not_covered", "at": "2026-11-1%dT08:00:00Z"
                                 % (5 + n % 3), "tokens": 100} for n in (1, 2, 3)],
            "results": [{"stage": 4, "outcome": "done", "run": "rm-role-designer-1", "at": "2026-11-17T18:00:00Z"}],
            "history": [{"at": "2026-11-17T18:29:13Z", "stage": 5, "what": "coverage_stop",
                         "why": "REFUSAL_NOTHING_COULD_EVER_PASS: 3 not_covered verdicts (limit 3); judging stopped on "
                                "Fake (coverage_judge.py release <dir> --why ... grants one more look)"},
                        {"at": "2026-11-17T18:45:12Z", "stage": 5, "what": "coverage_release_granted", "why": "one more"},
                        {"at": "2026-11-18T17:58:16Z", "stage": 5, "what": "locked_change", "why": "re-pin"}],
            "budget": {"cap": 4000000, "charges": [{"at": "2026-11-17T08:00:00Z", "kind": "review",
                                                    "ref": "rm-coverage-judge-1", "tokens": 100}]}}


def applied(st):
    """What the chain run U1 did to stage.json (as Graffiti's did, 2026-11-18 10:02-10:05 AM PST)."""
    st = copy.deepcopy(st)
    g = st.pop("coverage_release_granted")
    st.pop("coverage_stop")
    st["status"], st["blocked_on"] = "ready", None
    st["coverage_releases"] = [{"at": "2026-11-18T18:02:53Z", "final": True, "granted_at": g["at"], "granted_why": g["why"],
                                "after": g["after"], "rounds_at": 3,
                                "why": "locked-change chain %s applies the grant of %s" % (ITEM1, g["at"])}]
    st["history"] += [
        {"at": "2026-11-18T18:02:55Z", "stage": 5, "what": "coverage_release", "why": "locked-change chain %s applies "
         "the grant" % ITEM1},
        {"at": "2026-11-18T18:02:55Z", "stage": 5, "what": "open", "why": "run %s, stage 5, budget 3940000" % UD},
        {"at": "2026-11-18T18:05:48Z", "stage": 5, "what": "retry", "why": "run %s result rejected: no result.json" % UD}]
    st["coverage_rounds"].append({"judge": UJ, "verdict": "covered", "at": "2026-11-18T18:03:47Z", "tokens": 167016})
    st["results"].append({"stage": 5, "outcome": "rejected", "run": UD, "at": "2026-11-18T18:05:48Z"})
    st["budget"]["charges"] += [{"at": "2026-11-18T18:04:18Z", "kind": "review", "ref": UJ, "tokens": 167016},
                                {"at": "2026-11-18T18:05:48Z", "kind": "stage", "ref": "run " + UD, "tokens": 0}]
    return st


RECS = {U1: {"unit": U1, "item": ITEM1, "at": T0 + 21, "ended": T0 + 1008, "status": "finished",
             "result": "success (exited 0)", "cost_usd": 3.53, "out": "OUT_OK"},
        U2: {"unit": U2, "item": "RIMMANDRAKE_ROUTE_FAKE_CYCLE_TWO_FAILURES_BACK", "at": T0 + 1219, "ended": T0 + 1381,
             "status": "finished", "result": "killed: success (killed TERM)", "cost_usd": "UNMEASURED", "out": "OUT_NONE"},
        U3: {"unit": U3, "item": "RIMMANDRAKE_SETTLE_FAKE", "at": T0 + 1567, "ended": T0 + 1593, "status": "finished",
             "result": "killed: success (killed TERM)", "cost_usd": "UNMEASURED", "out": "OUT_NONE"}}


def main():
    try:
        import run_void as RV
    except ImportError as e:
        ok(False, "run_void.py exists and imports (%s)" % e)
        print("\n%d check(s), %d FAIL" % (COUNT[0], len(FAILS)))
        return 1
    import role_launch as RL
    import detached_helper as DH
    import coverage_judge as CJ
    import maturation_autonomy as AUT
    import maturation_dispatch as MD
    tmp = tempfile.mkdtemp(prefix="run_void_")
    keep = {k: os.environ.get(k) for k in ("RM_RUN_VOIDS_FILE", "RM_MATURATION_DISPATCH_DIR")}
    real_read, real_killed = RL.read_result, DH.killed
    try:
        os.environ["RM_RUN_VOIDS_FILE"] = vp = os.path.join(tmp, "voids.jsonl")
        os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
        os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
        # a fake result reader: OUT_OK holds a result JSON, anything else none (role_launch.read_result's contract)
        RL.read_result = lambda run: {"result": "ok"} if run.get("out") == "OUT_OK" else None
        record = RECS.get
        root = os.path.join(tmp, "repo")
        d = os.path.join(root, "design", "concepts", "Fake")
        os.makedirs(d)
        before_stage = stage()
        with open(os.path.join(d, "stage.json"), "w") as f:
            json.dump(applied(before_stage), f)
        st = state()

        # ---- the verbs: refusals ---------------------------------------------------------------------------------
        got, bad = RV.void(root, st, ["rm-detached-bench-nobody-1"], why="test", record=record)
        ok(not got and bad and "unknown run rm-detached-bench-nobody-1" in bad and not os.path.exists(vp),
           "an unknown run is refused by name and nothing is written (%s)" % bad)
        got, bad = RV.void(root, st, [U1], why="  ", record=record)
        ok(not got and "says why" in str(bad), "a void with no why is refused (%s)" % bad)
        got, bad = RV.void(root, st, item="RIMMANDRAKE_NO_SUCH_ITEM", why="t", record=record)
        ok(not got and "no run is known for item" in str(bad), "an item with no run is refused (%s)" % bad)

        # ---- a hand void of the three Graffiti-shaped runs, by --mod --since -------------------------------------
        got, bad = RV.void(root, st, mod="Fake", since=T0 - 60, why="launched without his authorization",
                           by="BENCH", owner_said="Ensure it didn't use up it's turns", record=record)
        units = sorted(x["unit"] for x in got)
        ok(not bad and {U1, U2, U3, UB, UI, UH, UL} <= set(units) and UD in units and UJ in units
           and "rm-old-1" not in units and "rm-old-blind-1" not in units,
           "--mod --since voids every run on the mod since then, with the Designer run and judge the chain started "
           "(%s; %s)" % (bad, units))
        ok(all(x["kind"] == "hand" and x["owner_said"] and x["why"] for x in got)
           and next(x for x in got if x["unit"] == UD).get("parent") == U1,
           "every line is a hand void with his words and the why; a child names its parent run")
        u1 = next(x for x in got if x["unit"] == U1)
        ok(u1["result"] == "success (exited 0)" and u1["cost_usd"] == 3.53,
           "a run that ended with a result (U1, success) may be voided: his call, recorded as a hand void with its "
           "result and its true spend")
        got2, bad2 = RV.void(root, st, [U1], why="again", record=record)
        ok(not got2 and "already VOID" in str(bad2) and U1 in str(bad2), "a double void is refused (%s)" % bad2)

        # ---- the dispatch books, through their own readers --------------------------------------------------------
        cur = RV.active()
        RV.sync_dispatch(st, cur)
        s = st["mods"]["Fake"]
        ok([x["cycle"] for x in s["blind_auto"]] == [1],
           "blind cycles of the visit: the void cycle-2 judge is out; the visit counts 1 (read %s)"
           % [x["cycle"] for x in s["blind_auto"]])
        ok(s.get("ingame_auto") == [], "in-game runs of the visit: the void driver is out (0 counted)")
        cfg = {"launch_tries": 3, "steward_max_per_version": 2, "steward_cap_usd": 8, "max_live": 4}
        row = {"aut": "steward", "mod": "Fake", "steward_key": "0.1.0|chain|2026-11-18T17:58:16Z"}
        go, why = AUT._gate(cfg, s, row, 0, "0.1.0")
        ok(go, "steward once-per-key: the void chain run's key is free again (%s)" % (why,))
        row2 = {"aut": "steward", "mod": "Fake", "steward_key": "0.1.0|blind_challenge|exit_not_met|2|6115bec2"}
        go2, why2 = AUT._gate(cfg, s, row2, 0, "0.1.0")
        ok(go2, "steward_max_per_version (2): one counted run left on 0.1.0, so the route steward may run (%s)" % (why2,))
        rowf = {"aut": "fixer", "mod": "Fake", "fix_item": "RIMMANDRAKE_SETTLE_FAKE"}
        gof, whyf = AUT._gate(dict(cfg, fix_cap_usd=10), s, rowf, 0, "0.1.0")
        ok(gof, "fixer once-per-item: the void fixer's item is free again (%s)" % (whyf,))
        ok(not s.get("road_back"), "the road back the void route steward opened goes with it")
        ok(MD.holder_spent(dict(s, road_back={"at": T0}), ["RB_1"]) is None,
           "holder one-run-per-set: the void holder run on RB_1 is no try at it")
        ok("last_run" not in s and s.get("launches") == [],
           "builder progress: the void builder run is neither the last run judged nor a launch")
        ok(len(s["voided"]) >= 8 and all(m["class"] == "void_hand" and m["why"] for m in s["voided"]),
           "every moved entry sits in the mod's voided list with class void_hand and its why (%d)" % len(s["voided"]))
        lines = RV.status_lines(st, record)
        ok(any("VOID hand %s" % U2 in x for x in lines) and any("void spend" in x and "UNMEASURED" in x for x in lines),
           "status names each VOID run and its why, and the void spend apart, UNMEASURED where a run has none (%s)"
           % lines[-1])
        once = copy.deepcopy(st)
        RV.sync_dispatch(st, cur)
        ok(st == once, "sync_dispatch is idempotent: a second reader changes nothing")

        # ---- a Designer stage.json: the look, the rounds, the retries ---------------------------------------------
        import designer_stage as DS
        dst = DS.load_state(d)
        g = dst.get("coverage_release_granted")
        ok(isinstance(g, dict) and g.get("at") == "2026-11-17T18:45:12Z" and not dst.get("coverage_releases"),
           "the granted look: the release the void run applied is un-applied, the grant stands again (%s)" % g)
        ok(CJ.grant_waits(dst, item_state=lambda ids: {i: "done" for i in ids}) == [],
           "grant_waits reads [] (due): the one granted look is available again")
        ok([r["judge"] for r in CJ.rounds(dst)] == ["rm-coverage-judge-%d" % n for n in (1, 2, 3)],
           "coverage rounds: the void judge's round is out, and its charge builds no legacy round (%s)"
           % [r["judge"] for r in CJ.rounds(dst)])
        ok(dst.get("coverage_stop", {}).get("why") == "3 not_covered verdicts (limit 3)" and dst["status"] == "blocked"
           and dst["blocked_on"] == before_stage["blocked_on"],
           "the stop and block the release lifted are back, word for word")
        ok(not any(r.get("run") == UD for r in dst["results"])
           and not any(h["what"] == "retry" for h in dst["history"]),
           "Designer results and retries: the void run's rejected result and retry row are out (retries 0)")
        ok(sum(int(c["tokens"]) for c in dst["budget"]["charges"]) == 100 + 167016
           and UJ in RV.stage_spend_refs(dst),
           "the void judge's spend stays measured in the budget (true), listed apart in voided.spend_refs")
        for k in ("coverage_release_granted", "coverage_stop", "status", "blocked_on", "coverage_rounds", "results"):
            ok(dst.get(k) == before_stage.get(k), "stage.json %s reads as before the void run" % k)

        # ---- the verdict file: kept as evidence, the earlier one back ---------------------------------------------
        subprocess.run(["git", "init", "-q", root], check=True)
        vf = os.path.join(d, "coverage_verdict.json")
        for j, v in (("rm-coverage-judge-3", "not_covered"), (UJ, "covered")):
            with open(vf, "w") as f:
                json.dump({"judge": j, "verdict": v}, f)
            subprocess.run(["git", "-C", root, "add", vf], check=True)
            subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", j],
                           check=True)
        paths = RV.swap_verdict(root, "Fake", UJ)
        arch = os.path.join(d, "coverage_verdict.void.%s.json" % UJ)
        ok(json.load(open(vf))["judge"] == "rm-coverage-judge-3" and json.load(open(arch))["judge"] == UJ
           and len(paths) == 2,
           "the void judge's verdict is kept as evidence (%s) and the earlier verdict is back" % os.path.basename(arch))
        ok(CJ.prior_verdict(d)["judge"] == "rm-coverage-judge-3",
           "the next look checks the look before the void one (prior_verdict)")
        RV.swap_verdict(root, "Fake", UJ, back=True)
        ok(json.load(open(vf))["judge"] == UJ and not os.path.exists(arch), "unvoid puts the void verdict back")
        ok(CJ.prior_verdict(d) is None, "a void judge's verdict in the file is never the prior look (none read)")

        # ---- unvoid: everything back --------------------------------------------------------------------------------
        bad_u = RV.unvoid(["rm-not-void-1"], "t")[1]
        ok("not VOID" in str(bad_u), "an unvoid of a run not void is refused (%s)" % bad_u)
        back, bad = RV.unvoid([U1, U2, U3, UB, UI, UH, UL], "test reversal", by="BENCH")
        ok(not bad and {UD, UJ} <= {x["unit"] for x in back}, "unvoid of a parent reverses its children too")
        RV.sync_dispatch(st)
        st0 = state()
        for k in ("steward", "fixers", "blind_auto", "ingame_auto", "holder_road_back", "launches", "last_run", "road_back"):
            ok(st["mods"]["Fake"].get(k) == st0["mods"]["Fake"][k], "unvoid: the %s book is back as it was" % k)
        ok(not st["mods"]["Fake"].get("voided"), "unvoid: the voided list is empty")
        ok(DS.load_state(d) == applied(before_stage), "unvoid: stage.json reads exactly as the run left it")
        ok(RV.unvoid([U1], "again")[1], "a second unvoid is refused")

        # ---- the automatic class: void_system ----------------------------------------------------------------------
        st = state()
        moved = RV.sync_system(st, record, keep_failed=lambda b, x: False, kills_left=lambda b, x, w: False, now=T0 + 2000)
        s = st["mods"]["Fake"]
        ok(set(s["fixers"]) == set() and "0.1.0|blind_challenge|exit_not_met|2|6115bec2" not in s["steward"]
           and not s.get("road_back"),
           "a killed steward and a killed fixer (no result JSON) are void_system: out of their books, the road back too")
        ok("0.1.0|chain|2026-11-18T17:58:16Z" in s["steward"],
           "a run that wrote its result (U1) counts: no system cause, it stays in the book")
        ok(s["blind_auto"][-1]["unit"] == UB and s.get("ingame_auto"),
           "a run whose record cannot be read (UNMEASURED) is left as the books had it")
        ok(RV.faults(s) == 2 and all(m["class"] == "void_system" for m in s["voided"]),
           "each is a system fault on the mod's own count (2), never a trial (read %d)" % RV.faults(s))
        ok(s["void_seen"].get(U1) == "counted",
           "a run judged counted is remembered (its record is not read again)")
        st2 = {"mods": {"Fake": {"steward": {"k": {"item": "X", "unit": None, "failed": "LAUNCH FAILED pool full",
                                                   "tries": 3}}}}}
        RV.sync_system(st2, record, keep_failed=lambda b, x: False, now=T0)
        ok(not st2["mods"]["Fake"]["steward"] and RV.faults(st2["mods"]["Fake"]) == 3,
           "a launch that never started is void_system, its three tries three faults")
        rows = [{"mod": "Fake", "decision": "launch"}]
        la = MD.system_fault_stop({"system_fault_limit": 3}, st2, rows, ["Fake"])
        ok(la == [] and rows[0]["decision"] == "system_fault" and RV.ALARM_ID in rows[0]["why"]
           and "no trial is spent" in rows[0]["why"],
           "at the limit the mod launches nothing: system_fault with its alarm, no trial spent (%s)" % rows[0]["why"][:80])
        st2["mods"]["Fake"]["cleared"] = [{"at": T0 + 1}]
        rows = [{"mod": "Fake", "decision": "launch"}]
        ok(MD.system_fault_stop({}, st2, rows, ["Fake"]) == ["Fake"], "a clear resets the system-fault count")
        ok(RV.system_cause({"unit": "u", "status": "finished", "out": "OUT_OK", "result": "success"}) == ""
           and RV.system_cause(None) == "",
           "a run that wrote its result, or no record, has no system cause (could not look is not void)")
    finally:
        RL.read_result, DH.killed = real_read, real_killed
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d check(s), %d FAIL" % (COUNT[0], len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
