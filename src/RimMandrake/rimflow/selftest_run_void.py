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
        "last_run": {"unit": UL, "refused_before": 6, "refused_after": 6},
        "releases_used": {"rel-a": {"at": T0 + 1200, "stage": "blind_challenge", "usd": 90.0, "unit": U2}}}
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
             "result": "success (exited 0)", "cost_usd": 3.53, "out": "OUT_NONE"},    # its out reads no JSON: it counts
        U2: {"unit": U2, "item": "RIMMANDRAKE_ROUTE_FAKE_CYCLE_TWO_FAILURES_BACK", "at": T0 + 1219, "ended": T0 + 1381,
             "status": "finished", "result": "killed: success (killed TERM)", "cost_usd": "UNMEASURED", "out": "OUT_NONE"},
        U3: {"unit": U3, "item": "RIMMANDRAKE_SETTLE_FAKE", "at": T0 + 1567, "ended": T0 + 1593, "status": "finished",
             "result": "killed: success (killed TERM)", "cost_usd": "UNMEASURED", "out": "OUT_NONE"}}


def judge_rounds(CJ):
    """RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS: a coverage-judge round whose call died is
    void_system: no run, look, spend or malformed verdict for the caps, counted apart, and a judge that only dies still
    stops, as a system fault, at JUDGE_FAULT_LIMIT. A judge's own failure still counts."""
    def rnd(n, **kw):
        r = {"judge": "rm-coverage-judge-%d" % n, "verdict": None, "at": "2026-11-18T00:%02d:00Z" % n, "tokens": 0}
        r.update(kw)
        return r
    dead = {"coverage_rounds": [rnd(n, error="TimeoutExpired: judge call timed out") for n in range(4)]}
    ok(CJ.stop_reason(dead) is None and CJ.rounds(dead) == [],
       "four timed-out judge rounds (no error_kind: written before it) spend no judge run (%s)" % CJ.stop_reason(dead))
    ok(len(CJ.rounds(dead, voids=True)) == 4 and all(r.get("void_system") for r in CJ.rounds(dead, voids=True)),
       "rounds(voids=True) keeps them, each marked void_system with its cause")
    big = {"coverage_rounds": [rnd(n, error="x", error_kind="system", tokens=CJ.JUDGE_SPEND_MAX) for n in range(2)]}
    ok(CJ.stop_reason(big) is None, "a dead round's spend is not judge spend (shown apart): %s" % CJ.stop_reason(big))
    own = {"coverage_rounds": [rnd(n, error="no well-formed verdict (exit 0)", error_kind="judge") for n in range(4)]}
    ok(str(CJ.stop_reason(own)).startswith("4 judge runs"),
       "a judge that answered with no well-formed verdict is its own failure: it counts (%s)" % CJ.stop_reason(own))
    mal = {"coverage_rounds": [rnd(n, verdict="malformed", void_system="a re-ask of its refusal records died")
                               for n in range(CJ.MALFORMED_LIMIT)]}
    ok(CJ.stop_reason(mal) is None, "a malformed verdict left by a dead re-ask counts toward no malformed cap")
    mal2 = {"coverage_rounds": [rnd(n, verdict="malformed") for n in range(CJ.MALFORMED_LIMIT)]}
    ok("malformed" in str(CJ.stop_reason(mal2)), "a judge's own malformed verdicts still stop judging")
    loop = {"coverage_rounds": [rnd(n, error="the judge did not answer: x", error_kind="system")
                                for n in range(CJ.JUDGE_FAULT_LIMIT)]}
    why = str(CJ.stop_reason(loop))
    ok("system cause" in why and "no look, run or spend was counted" in why,
       "a judge that only dies stops at JUDGE_FAULT_LIMIT, as a system fault, never a spent look (%s)" % why[:90])
    rel = dict(loop, coverage_releases=[{"at": "2026-11-18T01:00:00Z", "why": "x",
                                         "judges_at": [r["judge"] for r in loop["coverage_rounds"]]}])
    ok(CJ.stop_reason(rel) is None, "a release resets the system-fault count of the judge rounds")


def release_back(RV, MD, record):
    """The Conductor's decision of 2026-11-18 1:05 PM PST on RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS:
    a ceiling release spent by a void_system run is given back; a hand void leaves it spent; a run that heals spends it
    again."""
    def fresh():
        return {"mods": {"Fake": {"steward": {"k2": {"item": "X2", "unit": U2, "at": T0 + 1200, "failed": None,
                                                     "tries": 1}},
                                  "releases_used": {"rel-s": {"at": T0 + 1200, "stage": "blind_challenge", "usd": 90.0,
                                                              "unit": U2},
                                                    "rel-o": {"at": T0 + 50, "stage": "blind_challenge", "usd": 80.0,
                                                              "unit": U1}}}}}
    st = fresh()
    RV.sync_system(st, record, now=T0 + 1400)
    s = st["mods"]["Fake"]
    ok("rel-s" not in s.get("releases_used", {}) and "rel-o" in s.get("releases_used", {}),
       "a ceiling release spent by a void_system run is given back; one spent by a run that counts stays spent")
    m = [x for x in s.get("voided") or [] if x["book"] == "releases_used"]
    ok(len(m) == 1 and m[0]["class"] == "void_system" and m[0]["unit"] == U2 and m[0].get("faults") == 0
       and RV.faults(s) == 1,
       "the release sits in voided (void_system, its run's unit) and adds no system fault of its own (%s)" % RV.faults(s))
    rel = [{"id": "rel-s", "mod": "Fake", "stage": "blind_challenge", "read_tokens": 23_750_000,
            "release_tokens": 5_000_000}]
    why, rid = MD.ceiling_gate({"stage_ceiling_tokens": 25_000_000}, s, "Fake", "blind_challenge", 23_750_000, 2_500_000,
                               "x", (rel, 0))
    ok(rid == "rel-s", "the ceiling gate reads the given-back release as fresh again (%s, %s)" % (why, rid))
    once = copy.deepcopy(st)
    RV.sync_system(st, record, now=T0 + 1500)
    ok(st == once, "sync_system with a given-back release is idempotent")
    healed = dict(RECS, **{U2: dict(RECS[U2], result="success (exited 0)")})
    RV.sync_system(st, healed.get, now=T0 + 1600)
    ok("rel-s" in st["mods"]["Fake"].get("releases_used", {}),
       "a void_system run that heals (its record now counts) spends its release again")
    st = fresh()
    RV.sync_system(st, record, now=T0 + 1400)
    st["mods"]["Fake"]["releases_used"]["rel-s"] = {"at": T0 + 1450, "unit": UB, "usd": 90.0}   # B reuses it
    RV.sync_system(st, healed.get, now=T0 + 1600)
    s = st["mods"]["Fake"]
    ok(s["releases_used"]["rel-s"]["unit"] == UB and any(m["book"] == "releases_used" for m in s.get("voided") or []),
       "a healed run whose release another run holds now: the newer one stands, the healed one's stays saved")
    s["releases_used"].pop("rel-s")         # B's own run is voided later and gives it back
    RV.sync_system(st, healed.get, now=T0 + 1700)
    ok((s.get("releases_used") or {}).get("rel-s", {}).get("unit") == U2,
       "the saved release is retried on its own: once free, the healed run (it counts) spends it again (Codex r1-1)")
    st = fresh()
    RV.sync_system(st, record, now=T0 + 1400)
    RV.sync_dispatch(st, {U2: {"id": "v-9", "unit": U2, "why": "his stop", "item": "X2"}})
    ok("rel-s" in st["mods"]["Fake"].get("releases_used", {}),
       "a hand void of a run already void_system leaves its release spent (the Conductor's line: void_system only)")


def designer_void(tmp):
    """A Designer run's no-result rejection marked void_system (designer_stage.void_rejection): no retry in the
    packet's count, no rejection for rejection_parked (two in a row would park it); a judged rejection is never marked."""
    import designer_stage as DS
    d = os.path.join(tmp, "dv", "design", "concepts", "Fake")
    os.makedirs(d)
    NR = "no result.json (a closing message is not a result)"
    st = {"stage": 3, "status": "ready", "item": "FAKE_ITEM", "budget": {"cap": 4000000, "spent": 0, "charges": []},
          "results": [{"stage": 3, "outcome": "rejected", "run": "rm-role-designer-%d" % n, "at": "2026-11-18T0%d:00:00Z"
                       % n, "why": [NR]} for n in (1, 2)],
          "history": [{"at": "2026-11-18T0%d:00:00Z" % n, "stage": 3, "what": "retry",
                       "why": "run rm-role-designer-%d result rejected: %s" % (n, NR)} for n in (1, 2)]}
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump(st, f)
    ok(DS.rejection_parked(DS.load_state(d)) and DS.stage_retries(DS.load_state(d)) == 2,
       "before: two identical no-result rejections park the concept and count two retries")
    ok(DS.void_rejection(d, "rm-role-designer-2", "killed at run_max_s") is True,
       "void_rejection marks the killed run's no-result rejection")
    ok(DS.void_rejection(d, "rm-role-designer-2", "again") is False, "a second mark is refused (nothing to mark)")
    s2 = DS.load_state(d)
    ok(DS.rejection_parked(s2) is None and DS.stage_retries(s2) == 1,
       "after: the void rejection is no rejection for parking and no retry (retries %d)" % DS.stage_retries(s2))
    ok(any(h.get("what") == "void_system" for h in s2["history"]), "the void is said in the stage history")
    st["results"].append({"stage": 3, "outcome": "rejected", "run": "rm-role-designer-3", "at": "2026-11-18T03:00:00Z",
                          "why": ["lint: leaf x has no root"]})
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump(st, f)
    ok(DS.void_rejection(d, "rm-role-designer-3", "x") is False, "a rejection judged on a written result is never void")


def pilot_void(RV, tmp):
    """A Test Pilot verify recorded fail because of a harness fault: a hand void by its run name
    (`maturation_dispatch.py void "<ID>/run-N@<config>" --why ...`) takes it out of the 3-in-a-row streak."""
    import model
    import testpilot_route as TP
    name = "FAKE_ITEM/run-3@full-578"

    class It(object):
        id, state, blocked, needs, history = "FAKE_ITEM", "ready", False, "bridge", []
        runs = [model.Run("FAKE_ITEM", n, "full-578", "fail", None, "abc", "2026-11-18T0%d:00:00Z" % n, n)
                for n in (1, 2, 3)]
    ok(TP.judge(It, [], void={}) and TP.judge(It, [], void={})["kind"] == "streak",
       "three fails in a row route the item to a Test Pilot")
    ok(TP.judge(It, [], void={name: {"id": "v", "why": "harness fault"}}) is None,
       "the third fail hand-voided as a harness fault: two in a row, no streak")
    real = RV.active
    RV.active = lambda *a, **k: (_ for _ in ()).throw(PermissionError("denied"))
    try:
        v = TP.judge(It, [])
    finally:
        RV.active = real
    ok(v and "UNMEASURED" in v["why"] and "denied" in v["why"],
       "an unreadable void ledger is said as UNMEASURED on the verdict, never read as 'no voids' (Codex r1-7): %s"
       % (v or {}).get("why"))
    got, bad = RV.resolve(tmp, {}, [name], verify_run=lambda n: n == name)
    ok(bad is None and [g[0] for g in got] == [name] and got[0][2] == "FAKE_ITEM",
       "void resolves a verify run by its name, the item from the name (%s)" % (bad or got))
    got, bad = RV.resolve(tmp, {}, ["FAKE_ITEM/run-9@full-578"], verify_run=lambda n: n == name)
    ok(bad and "unknown run" in bad, "a verify run the ledger does not hold is refused by name")
    rel = {"stage": 5, "coverage_releases": [{"at": "2026-11-18T18:02:53Z", "granted_at": "2026-11-17T18:45:12Z",
                                              "why": "locked-change chain FAKE_ITEM applies the grant"}]}
    RV.sync_stage(rel, {name: {"id": "v-1", "unit": name, "item": "FAKE_ITEM", "why": "harness fault"}})
    ok(len(rel.get("coverage_releases") or []) == 1,
       "a voided verify run un-applies no coverage look its item's name happens to appear in (Codex r1-4)")


def parent_children(RV, tmp):
    """A void's children are the Designer runs and judges its run launched (their recorded `parent`), never another
    run's that overlapped it on the same concept; an entry with no parent recorded (written before) goes by time."""
    root = os.path.join(tmp, "pc")
    d = os.path.join(root, "design", "concepts", "Fake")
    os.makedirs(d)
    P1, P2 = "rm-detached-bench-a-1", "rm-detached-bench-b-2"
    st = {"stage": 5, "coverage_rounds": [
        {"judge": "rm-coverage-judge-1", "at": "2026-11-18T18:05:00Z", "verdict": "covered", "parent": P1},
        {"judge": "rm-coverage-judge-2", "at": "2026-11-18T18:06:00Z", "verdict": "covered", "parent": P2},
        {"judge": "rm-coverage-judge-3", "at": "2026-11-18T18:07:00Z", "verdict": "covered"},
        {"judge": "rm-coverage-judge-4", "at": "2026-11-18T20:00:00Z", "verdict": "covered", "parent": P1}],
        "history": [{"at": "2026-11-18T18:04:00Z", "stage": 5, "what": "open", "parent": P2,
                     "why": "run rm-role-designer-9, stage 5, budget 10"}],
        "budget": {"charges": [{"at": "2026-11-18T18:06:30Z", "kind": "review", "tokens": 5,
                                "ref": "rm-coverage-judge-2-reader"}]}}
    with open(os.path.join(d, "stage.json"), "w") as f:
        json.dump(st, f)
    t0 = RV.parse_time("2026-11-18T18:00:00Z")
    kids = RV.children(root, "Fake", {"unit": P1, "at": t0, "ended": t0 + 1800})
    ok(kids == ["rm-coverage-judge-1", "rm-coverage-judge-3", "rm-coverage-judge-4"],
       "children by parent: its own judges (one queued past its end too), an old parentless one by time, never the "
       "overlapping run's (%s)" % kids)
    kids2 = RV.children(root, "Fake", {"unit": P2, "at": t0, "ended": t0 + 1800})
    ok(kids2 == ["rm-coverage-judge-2", "rm-coverage-judge-2-reader", "rm-coverage-judge-3", "rm-role-designer-9"],
       "the other run's children are its own (%s)" % kids2)


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
        cfg = {"launch_tries": 3, "steward_max_per_version": 2, "steward_cap_tokens": 2_000_000, "max_live": 4}
        row = {"aut": "steward", "mod": "Fake", "steward_key": "0.1.0|chain|2026-11-18T17:58:16Z"}
        go, why = AUT._gate(cfg, s, row, 0, "0.1.0")
        ok(go, "steward once-per-key: the void chain run's key is free again (%s)" % (why,))
        row2 = {"aut": "steward", "mod": "Fake", "steward_key": "0.1.0|blind_challenge|exit_not_met|2|6115bec2"}
        go2, why2 = AUT._gate(cfg, s, row2, 0, "0.1.0")
        ok(go2, "steward_max_per_version (2): one counted run left on 0.1.0, so the route steward may run (%s)" % (why2,))
        rowf = {"aut": "fixer", "mod": "Fake", "fix_item": "RIMMANDRAKE_SETTLE_FAKE"}
        gof, whyf = AUT._gate(dict(cfg, fix_cap_tokens=2_500_000), s, rowf, 0, "0.1.0")
        ok(gof, "fixer once-per-item: the void fixer's item is free again (%s)" % (whyf,))
        # the fixer count is the mod's, over every version (only stewards are version-filtered): its refusal says so,
        # never "at this version" (RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED: Pyrelands' 12/12)
        sx = {"fixers": {"OLD_0_0_9_FIX": {"item": "OLD_0_0_9_FIX", "unit": "u-old"},
                         "NEW_FIX": {"item": "NEW_FIX", "unit": "u-new"}}}
        gox, whyx = AUT._gate(dict(cfg, fix_cap_tokens=2_500_000), sx, {"aut": "fixer", "mod": "Fake", "fix_item": "THIRD"},
                              0, "0.1.0")
        ok(not gox and "at this version" not in whyx[1] and "every version" in whyx[1],
           "the fixer cap counts the mod's fixer runs over every version and says so (%s)" % (whyx,))
        gos, whys = AUT._gate(cfg, {"steward": {"0.1.0|a": {"item": "A", "unit": "ua"}, "0.1.0|b": {"item": "B",
                              "unit": "ub"}}}, {"aut": "steward", "mod": "Fake", "steward_key": "0.1.0|c"}, 0, "0.1.0")
        ok(not gos and "at this version" in whys[1], "the steward cap still says at this version (%s)" % (whys,))
        ok(not s.get("road_back"), "the road back the void route steward opened goes with it")
        ok(MD.holder_spent(dict(s, road_back={"at": T0}), ["RB_1"]) is None,
           "holder one-run-per-set: the void holder run on RB_1 is no try at it")
        ok(list(s.get("releases_used") or {}) == ["rel-a"],
           "a ceiling release the void run spent stays spent: un-spending it would release spend past the ceiling")
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
        DS.write_json(DS.state_path(d), dst)    # the void verb writes it so: the unvoid below must restore from disk
        raw = json.load(open(DS.state_path(d)))
        ok(not any(r.get("judge") == UJ for r in raw["coverage_rounds"]) and raw["voided"]["moved"],
           "the written stage.json carries the void (its moved entries saved under voided)")

        # ---- the verdict file: kept as evidence, the earlier one back ---------------------------------------------
        subprocess.run(["git", "init", "-q", root], check=True)
        vf = os.path.join(d, "coverage_verdict.json")
        for j, v, at in (("rm-coverage-judge-3", "not_covered", "2026-11-17T10:00:00Z"),
                         (UJ, "covered", "2026-11-18T18:03:47Z")):
            with open(vf, "w") as f:
                json.dump({"judge": j, "verdict": v, "at": at}, f)
            subprocess.run(["git", "-C", root, "add", vf], check=True)
            subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", j],
                           check=True)
        # RIMMANDRAKE_SKIP_VOID_LANDING_WHEN_STAGE_FILE_UNCHANGED: a void whose rewritten stage.json equals HEAD has
        # nothing to land; it is not a failed landing (./publish refuses "nothing to publish", exit 1 read as NOT LANDED)
        ok(callable(getattr(RV, "landable", None)), "run_void.landable exists (the paths a void verb must land)")
        if callable(getattr(RV, "landable", None)):
            rel_vf = os.path.relpath(vf, root)
            ok(RV.landable(root, [rel_vf]) == [], "a committed file unchanged since HEAD is not landable (nothing to land)")
            with open(vf, "a") as f:
                f.write("\n")
            ok(RV.landable(root, [rel_vf]) == [rel_vf], "a committed file changed since HEAD is landable")
            subprocess.run(["git", "-C", root, "checkout", "-q", "--", vf], check=True)
            new = os.path.join(d, "stage.json")
            ok(RV.landable(root, [os.path.relpath(new, root)]) == [os.path.relpath(new, root)],
               "an untracked file is landable")
            ok(RV.landable(os.path.join(tmp, "not_a_repo"), [rel_vf]) == [rel_vf],
               "where git cannot look, every path stays landable (could not look is not unchanged)")
        paths = RV.swap_verdict(root, "Fake", UJ)
        arch = os.path.join(d, "coverage_verdict.void.%s.json" % UJ)
        ok(json.load(open(vf))["judge"] == "rm-coverage-judge-3" and json.load(open(arch))["judge"] == UJ
           and len(paths) == 3,
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
        for k in ("steward", "fixers", "blind_auto", "ingame_auto", "holder_road_back", "launches", "last_run", "road_back",
                  "releases_used"):
            ok(st["mods"]["Fake"].get(k) == st0["mods"]["Fake"][k], "unvoid: the %s book is back as it was" % k)
        ok(not st["mods"]["Fake"].get("voided"), "unvoid: the voided list is empty")
        back_st = DS.load_state(d)
        ok({k: v for k, v in back_st.items() if k != "voided"} == applied(before_stage) and not back_st.get("voided"),
           "unvoid: stage.json, read from the voided file on disk, reads exactly as the run left it")
        ok(RV.unvoid([U1], "again")[1], "a second unvoid is refused")

        # ---- a hand void of a run the tick already classed void_system (Graffiti's two killed runs) -----------------
        st5 = state()
        RV.sync_system(st5, record, keep_failed=lambda b, x: False, kills_left=lambda b, x, w: False, now=T0 + 2000)
        s5 = st5["mods"]["Fake"]
        f_before = RV.faults(s5)
        got5 = RV.resolve(root, st5, [U2], record=lambda u: None)[0]
        ok(got5 and got5[0][1] == "Fake", "a run the tick already moved out (void_system) resolves to its mod (%s)"
           % (got5[0][1] if got5 else None))
        RV._append({"act": "void", "ts": "t", "unit": U2, "mod": "Fake", "why": "the Conductor's stop", "by": "B"})
        RV.sync_dispatch(st5)
        ok(f_before == 2 and RV.faults(s5) == 1 and [m["class"] for m in s5["voided"] if m.get("unit") == U2
                                                     or m["book"] == "road_back"] == ["void_hand", "void_hand"],
           "a hand void of a void_system run makes it (and its road back) a hand void and drops its system fault "
           "(faults %d -> %d)" % (f_before, RV.faults(s5)))
        RV._append({"act": "unvoid", "ts": "t", "unit": U2, "why": "t", "by": "B"})
        RV.sync_dispatch(st5)
        ok("0.1.0|blind_challenge|exit_not_met|2|6115bec2" in s5["steward"] and s5.get("road_back"),
           "its unvoid puts it back in its book (the next tick may class it void_system again: it was killed)")

        # ---- review cases (Codex, 2026-11-18): a newer grant survives an unvoid; partial unvoids keep time order ----
        RV._append({"act": "void", "ts": "t", "unit": U1, "mod": "Fake", "item": ITEM1, "why": "again", "by": "B"})
        RV._append({"act": "void", "ts": "t", "unit": UD, "mod": "Fake", "item": ITEM1, "why": "again", "by": "B",
                    "parent": U1})
        x = RV.sync_stage(applied(before_stage))
        x["coverage_release_granted"] = {"at": "2026-11-19T00:00:00Z", "why": "a newer grant", "after": []}
        RV._append({"act": "unvoid", "ts": "t", "unit": UD, "why": "partial", "by": "B"})
        x = RV.sync_stage(x)
        ok([h.get("at") for h in x["history"]] == sorted(h.get("at") for h in x["history"]),
           "a partial unvoid (the child first) puts its rows back in time order")
        RV._append({"act": "unvoid", "ts": "t", "unit": U1, "why": "partial", "by": "B"})
        x = RV.sync_stage(x)
        ok(x["coverage_release_granted"]["why"] == "a newer grant" and len(x["coverage_releases"]) == 1,
           "unvoid re-applies the release but leaves a grant made since the void standing (%s)"
           % x["coverage_release_granted"]["why"])
        ok([h.get("at") for h in x["history"]] == sorted(h.get("at") for h in x["history"]),
           "after both unvoids every history row is in time order")
        # a newer verdict survives an unvoid; the predecessor skips every void judge
        for j, v, at in (("rm-coverage-judge-4", "covered", "2026-11-18T12:00:00Z"),
                         (UJ, "covered", "2026-11-18T18:03:47Z")):
            with open(vf, "w") as f:
                json.dump({"judge": j, "verdict": v, "at": at}, f)
            subprocess.run(["git", "-C", root, "add", vf], check=True)
            subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", j],
                           check=True)
        RV._append({"act": "void", "ts": "t", "unit": "rm-coverage-judge-4", "mod": "Fake", "why": "t", "by": "B"})
        RV.swap_verdict(root, "Fake", UJ)
        ok(json.load(open(vf))["judge"] == "rm-coverage-judge-3",
           "the verdict put back skips every void judge (4 is void too): judge 3's")
        with open(vf, "w") as f:
            json.dump({"judge": "rm-coverage-judge-5", "verdict": "covered", "at": "2026-11-18T20:00:00Z"}, f)
        RV.swap_verdict(root, "Fake", UJ, back=True)
        ok(json.load(open(vf))["judge"] == "rm-coverage-judge-5" and os.path.exists(arch),
           "an unvoid never puts the void verdict over a newer one: judge 5's stands, the archive stays")
        # an older fallback is no newer work: void judge 4 as well, then unvoid UJ with judge 4 still void
        with open(vf, "w") as f:
            json.dump({"judge": "rm-coverage-judge-3", "verdict": "not_covered", "at": "2026-11-17T10:00:00Z"}, f)
        RV.swap_verdict(root, "Fake", UJ, back=True)
        ok(json.load(open(vf))["judge"] == UJ and not os.path.exists(arch),
           "unvoid over an older fallback (judge 3, while 4 is void) puts the void verdict back")
        RV._append({"act": "unvoid", "ts": "t", "unit": "rm-coverage-judge-4", "why": "t", "by": "B"})
        # ties in time keep their order through a partial unvoid; stop, status and block restore as a group
        tie = {"results": [{"run": r, "at": "2026-11-18T18:00:00Z"} for r in ("rA", "rB", "rC")]}
        RV._append({"act": "void", "ts": "t", "unit": "rA", "why": "t", "by": "B"})
        RV._append({"act": "void", "ts": "t", "unit": "rB", "why": "t", "by": "B"})
        tie = RV.sync_stage(tie)
        RV._append({"act": "unvoid", "ts": "t", "unit": "rB", "why": "t", "by": "B"})
        tie = RV.sync_stage(tie)
        RV._append({"act": "unvoid", "ts": "t", "unit": "rA", "why": "t", "by": "B"})
        tie = RV.sync_stage(tie)
        ok([r["run"] for r in tie["results"]] == ["rA", "rB", "rC"],
           "rows tied in time come back in their own order after a partial unvoid (%s)" % [r["run"] for r in tie["results"]])
        RV._append({"act": "void", "ts": "t", "unit": U1, "mod": "Fake", "item": ITEM1, "why": "g", "by": "B"})
        y = RV.sync_stage(applied(before_stage))
        y["coverage_stop"] = {"at": "2026-11-19T00:00:00Z", "why": "a newer stop"}
        y["blocked_on"] = "a newer block"
        RV._append({"act": "unvoid", "ts": "t", "unit": U1, "why": "g", "by": "B"})
        y = RV.sync_stage(y)
        ok(y["status"] == "blocked" and y["coverage_stop"]["why"] == "a newer stop" and y["blocked_on"] == "a newer block",
           "a newer stop and block stand through an unvoid, with the status they go with (%s)" % y["status"])

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
        st4 = {"mods": {"Fake": {"steward": {"k": {"item": "X", "unit": "rm-no-record-1", "at": T0}}}}}
        RV.sync_system(st4, record, now=T0)
        ok("k" in st4["mods"]["Fake"]["steward"] and st4["mods"]["Fake"]["void_unmeasured"] == ["rm-no-record-1"]
           and any("UNMEASURED run record" in x for x in RV.status_lines(st4, record)),
           "a run whose record cannot be read keeps its count and is NAMED UNMEASURED in status")
        ok(RV.void_spend({"voided": [{"book": "steward", "unit": U1}, {"book": "releases_used", "unit": U1}]},
                         record)[0] == 882500, "void spend counts a run once, however many books held it (weighted "
                                               "tokens: a legacy cost_usd 3.53 at 250,000 per list dollar)")
        ok(RV.system_cause(dict(RECS[U1], result="timeout (- -)")).startswith("it timed out")
           and RV.system_cause(dict(RECS[U1], result="exit-code (1 -)")).startswith("the CLI exited")
           and RV.system_cause(dict(RECS[U1], result="exit-code/claude-error (1 -)")) == ""
           and RV.system_cause(dict(RECS[U1], result="unknown (- -)")) == "",
           "a timeout and a CLI exit with no result are system causes; claude's own error and 'unknown' are not")
        # a real launch_failed record (2026-11-20, run ...1794834319): `state` is the state folder PATH, the failure word
        # is in `status`; read as void_system, never charged. Foils: a finished run with spend, and a running one.
        lf = {"unit": "u-lf", "status": "launch_failed", "state": "/mnt/d/ClaudeWork/rimmandrake/dispatcher",
              "why": "systemd-run did not answer (OSError); systemd reads the unit inactive"}
        ok(RV.system_cause(lf).startswith("its launch never started") and "systemd-run did not answer" in RV.system_cause(lf)
           and RV.system_cause(dict(lf, status="finished", result="success (exited 0)")) == ""
           and RV.system_cause({"unit": "u", "status": "finished", "state": "/x", "result": "success (exited 0)"}) == "",
           "a launch_failed record (status word, state is a path) is void_system; a finished run stays charged")
        # the instrument trap of 2026-11-18 ~11:10 AM PST: a success run classed void_system goes back, its fault dropped
        st3 = {"mods": {"Fake": {"steward": {}, "voided": [
            {"book": "steward", "key": "k1", "entry": {"item": "I1", "unit": U1, "at": T0}, "class": "void_system",
             "void": None, "why": "it ended with no result JSON (success (exited 0))", "unit": U1, "faults": 1}],
            "system_faults": [{"at": T0, "book": "steward", "key": "k1", "unit": U1, "cause": "x", "n": 1}]}}}
        st3["mods"]["Fake"]["voided"].append({"book": "releases_used", "key": "rel-b", "entry": {"unit": U2, "usd": 9.0},
                                              "class": "void_hand", "void": "v-1", "why": "x", "unit": U2})
        RV.sync_system(st3, record, now=T0 + 10)
        ok(st3["mods"]["Fake"].get("releases_used", {}).get("rel-b"),
           "heal: a ceiling release an earlier build moved out under a hand void goes back: it stays spent")
        s3 = st3["mods"]["Fake"]
        ok(s3["steward"].get("k1", {}).get("unit") == U1 and not s3["voided"] and RV.faults(s3) == 0,
           "heal: a void_system entry whose record reads success is back in its book, its fault dropped")
        st2 = {"mods": {"Fake": {"steward": {"k": {"item": "X", "unit": None, "failed": "LAUNCH FAILED pool full",
                                                   "tries": 3}}}}}
        RV.sync_system(st2, record, keep_failed=lambda b, x: False, now=T0)
        # a launch that never started is a fault of form (form_fault, 2026-11-21): out of its book, no fault, one
        # repair owed. Before, it was void_system and its three tries three faults.
        f2 = st2["mods"]["Fake"]
        ok(not f2["steward"] and RV.faults(f2) == 0 and [r.get("state") for r in f2.get("form_repairs") or []] == ["owed"],
           "a launch that never started is void_form: no fault, one repair owed")
        # a never-started launch booked as a system fault BEFORE the form rule (2026-11-21) is not counted: two such
        # holder_road_back faults of 2026-11-18 ("its launch never started: no unit") plus one timeout tripped the
        # fault loop on ExplosiveKnockback, 2026-11-23 (RIMMANDRAKE_REPAIR_EXPLOSIVEKNOCKBACK_FAULT_LOOP_AT_THE_GATE)
        old = [{"at": T0, "book": "holder_road_back", "key": None, "unit": None,
                "cause": "its launch never started: no unit", "n": 1} for _ in range(2)]
        timed = {"at": T0, "book": "blind_auto", "key": None, "unit": "u-timed", "cause": "it timed out (x)", "n": 1}
        held = {"at": T0, "book": "launch", "key": "I", "unit": None,
                "cause": "the repair of X did not hold (repair run u ended; the same refusal came back): X", "n": 1}
        sf = {"system_faults": old + [timed]}
        ok(RV.faults(sf) == 1, "a pre-form-rule 'its launch never started' fault is not counted (read %d, want 1)"
           % RV.faults(sf))
        ok(RV.faults({"system_faults": old + [timed, held]}) == 2,
           "a 'repair did not hold' fault and a dead run still count (want 2)")
        rows = [{"mod": "Fake", "decision": "launch"}]
        ok(MD.system_fault_stop({"system_fault_limit": 3}, {"mods": {"Fake": sf}}, rows, ["Fake"]) == ["Fake"],
           "two stale never-started faults and one timeout do not trip the fault loop (%s)" % rows[0]["decision"])
        f2["system_faults"] = [{"at": T0, "book": "steward", "unit": "u-dead-%d" % i, "cause": "it timed out", "n": 1}
                               for i in range(3)]
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
        judge_rounds(CJ)
        release_back(RV, MD, record)
        designer_void(tmp)
        pilot_void(RV, tmp)
        parent_children(RV, tmp)
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
