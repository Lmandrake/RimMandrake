#!/usr/bin/env python3
"""selftest_void_counters.py: the promises of design/specs/2026-11-19-void-counters/boundary.md, one test of each
promise's name (boundary_check.py). Item RIMMANDRAKE_CLOSE_VOID_GAPS_REVIEW_FOUND_SIX_MORE: a review named six places a
system failure might still spend a counter; each test was written from its claim and run on the base first (the claims
that held on base are recorded as not real, the test kept). Offline: temp dirs, a throwaway control store, fake run
records; no systemd, no git, no live store.

    python3 src/RimMandrake/rimflow/selftest_void_counters.py      exit 0 when every check prints PASS
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS, COUNT = [], [0]
T0 = 1795024742.0       # 2026-11-18 9:59 AM PST
MOD = "Fake"


def ok(cond, what):
    COUNT[0] += 1
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def records(**by_unit):
    return lambda u: by_unit.get(u)


def fin(result, unit="u"):
    return {"unit": unit, "status": "finished", "result": result, "at": T0, "ended": T0 + 60}


# ---- run_void ---------------------------------------------------------------------------------------------------------

def t_unknown_result_with_its_own_answer_counts(tmp):
    import detached_helper as DH
    import run_void as RV
    out, err = os.path.join(tmp, "u.out"), os.path.join(tmp, "u.err")
    with open(out, "w") as f:
        json.dump({"type": "result", "subtype": "success", "is_error": False, "result": "done"}, f)
    open(err, "w").close()
    with_json = DH.outcome({"out": out, "err": err, "model": "opus"}, {})[0]
    open(out, "w").close()
    without = DH.outcome({"out": out, "err": err, "model": "opus"}, {})[0]
    ok(with_json.startswith("unknown (") and without.startswith("killed: unknown"),
       "a finish with no systemd variables writes 'unknown' only beside the agent's own result JSON (%r / %r)"
       % (with_json, without))
    U = "rm-detached-bench-fake-unknown-1"
    st = {"mods": {MOD: {"launches": [{"unit": U, "item": "I", "at": T0}]}}}
    RV.sync_system(st, records(**{U: fin(with_json, U)}))
    s = st["mods"][MOD]
    ok([x["unit"] for x in s["launches"]] == [U] and s["void_seen"].get(U) == "counted" and not s.get("voided"),
       "an 'unknown' run with its own answer counts and is final: %r" % s.get("void_seen"))
    st = {"mods": {MOD: {"launches": [], "voided": [
        {"book": "launches", "key": None, "entry": {"unit": U, "item": "I", "at": T0}, "class": "void_system",
         "void": None, "why": "its unit died", "unit": U, "faults": 1}],
        "system_faults": [{"at": T0, "unit": U, "n": 1}]}}}
    RV.sync_system(st, records(**{U: fin(with_json, U)}))
    s = st["mods"][MOD]
    ok([x["unit"] for x in s["launches"]] == [U] and not s.get("system_faults") and not s.get("voided"),
       "an earlier void_system class heals once the record reads 'unknown' with its own answer")
    st = {"mods": {MOD: {"launches": [{"unit": U, "item": "I", "at": T0}]}}}
    RV.sync_system(st, records(**{U: fin(without, U)}))
    s = st["mods"][MOD]
    ok(not s["launches"] and s["voided"][0]["class"] == "void_system",
       "'killed: unknown' (no answer of its own) is void_system")


def t_mod_since_finds_moved_system_voids(tmp):
    import run_void as RV
    US, UH = "rm-detached-bench-fake-sys-1", "rm-detached-bench-fake-hand-1"
    p = os.path.join(tmp, "voids_since.jsonl")
    RV._append({"act": "void", "ts": RV._iso(T0), "unit": UH, "mod": MOD, "item": "H", "why": "his stop", "by": "T",
                "kind": "hand"}, p)
    st = {"mods": {MOD: {"launches": [], "voided": [
        {"book": "launches", "key": None, "entry": {"unit": US, "item": "S", "at": T0 + 100}, "class": "void_system",
         "void": None, "why": "it timed out", "unit": US, "faults": 1},
        {"book": "launches", "key": None, "entry": {"unit": UH, "item": "H", "at": T0 + 200}, "class": "void_hand",
         "void": "void-x", "why": "his stop", "unit": UH}],
        "system_faults": [{"at": T0 + 150, "unit": US, "n": 1}]}}}
    got, bad = RV.resolve(tmp, st, mod=MOD, since=T0, record=lambda u: None)
    ok(bad is None and [g[0] for g in got] == [US],
       "--mod --since finds the run sync_system moved out, not the one already hand-voided: %r %r" % (got, bad))
    lines, bad = RV.void(tmp, st, mod=MOD, since=T0, why="the Conductor's stop", by="T", record=lambda u: None, p=p,
                         now=T0 + 300)
    RV.sync_dispatch(st, RV.active(p))
    s = st["mods"][MOD]
    ok(bad is None and [x["unit"] for x in lines] == [US]
       and next(m for m in s["voided"] if m["unit"] == US)["class"] == "void_hand" and not s.get("system_faults"),
       "it becomes a hand void and leaves the system-fault count (%r, %r)" % (bad, s.get("system_faults")))
    got, bad = RV.resolve(tmp, st, mod=MOD, since=T0 + 1000, record=lambda u: None)
    ok(got == [] and "no run on" in str(bad), "a window with no run is still refused by name: %r" % bad)


def t_a_killed_pilot_launch_spends_no_holder_try(tmp):
    import maturation_dispatch as MD
    import run_void as RV
    UP = "rm-detached-bench-fake-pilot-1"
    st = {"mods": {MOD: {"road_back": {"caused_by": "RB", "at": T0},
                         "pilot_launches": [{"at": T0 + 10, "item": "RB_ITEM", "unit": UP, "why": "hand",
                                             "stage": "offline_build"}]}}}
    s = st["mods"][MOD]
    ok(MD.holder_spent(s, ["RB_ITEM"]) is not None, "before the read, the hand run reads as a spent holder try")
    RV.sync_system(st, records(**{UP: fin("timeout (- -)", UP)}))
    ok(not s.get("pilot_launches") and MD.holder_spent(s, ["RB_ITEM"]) is None and RV.faults(s) == 1,
       "a timed-out hand pilot-launch is void_system: no holder try spent, one system fault (%r)"
       % MD.holder_spent(s, ["RB_ITEM"]))
    RV.sync_system(st, records(**{UP: fin("success (0 exited)", UP)}))
    ok([x["unit"] for x in s.get("pilot_launches") or []] == [UP] and RV.faults(s) == 0,
       "it goes back when its record heals")


def t_a_killed_red_decider_builder_spends_no_try(tmp):
    import run_void as RV
    UC = "rm-detached-bench-fake-green-red-1"
    cr = {"tests": ["T_A"], "items": {"T_A": "I"}, "unit": UC, "at": T0, "failed": None, "stage": "offline_build",
          "tries": 1}
    st = {"mods": {MOD: {"launches": [{"unit": UC, "item": "I", "at": T0, "cap": 5, "stage": "offline_build",
                                       "cert_reds": ["T_A"]}], "cert_red": dict(cr)}}}
    s = st["mods"][MOD]
    RV.sync_system(st, records(**{UC: fin("killed: signal (killed 9)", UC)}))
    ok(not s.get("launches") and "cert_red" not in s and RV.faults(s) == 1,
       "a killed red-decider builder takes its cert_red out with its launch: no 'ended and still red' stop")
    RV.sync_system(st, records(**{UC: fin("success (0 exited)", UC)}))
    ok(s.get("cert_red") == cr and [x["unit"] for x in s.get("launches") or []] == [UC],
       "both come back when its record heals")


def t_ledger_runs_stay_for_their_run_end(tmp):
    import run_void as RV
    UL = "rm-detached-bench-fake-ledger-1"
    st = {"mods": {MOD: {"launches": [{"unit": UL, "item": "I", "at": T0}],
                         "ledger_runs": [{"run": "r1", "unit": UL, "item": "I", "at": T0, "stage": "offline_build"}],
                         "releases_used": {"rel1": {"at": T0, "stage": "offline_build", "unit": UL}}}}}
    s = st["mods"][MOD]
    RV.sync_system(st, records(**{UL: fin("timeout (- -)", UL)}))
    ok(not s["launches"] and [r["unit"] for r in s["ledger_runs"]] == [UL] and not s.get("releases_used"),
       "a void_system run is classed from its other book; its ledger_runs entry stays for run.end and its release "
       "is given back")


# ---- the certificate rerun ------------------------------------------------------------------------------------------

def t_a_certificate_rerun_left_no_result_is_tried_again(tmp):
    import maturation_dispatch as MD
    cert = {"rows": [{"status": "REFUSED", "clause": "ran_on_this_build", "test": "T_A", "would_pass": "build abc"}]}
    key = MD.stale_key(cert)
    puts = []

    def put(decision, why, need=None):
        puts.append((decision, why, need))

    def decide(prior, res=None, now=T0 + MD.RERUN_MAX_S + 60):
        del puts[:]
        s, row = {"cert_rerun": dict(prior)}, {"mod": MOD}
        f = {"certificate": cert, "cert_rerun_result": res}
        return MD.cert_rerun_decide({"launch_tries": 3}, s, f, row, put, now), s, row
    U = "rm-cert-rerun-fake-1"
    got, s, row = decide({"key": key, "unit": U, "at": T0, "failed": None, "tries": 1})
    ok(got == "launch" and row.get("cert_rerun_key") == key,
       "a rerun that left no result by RERUN_MAX_S is started again (%r %r)" % (got, puts[-1:]))
    called = []
    st = {"mods": {MOD: s}}
    if got == "launch":
        MD.cert_rerun_launch({}, st, row, T0 + MD.RERUN_MAX_S + 60,
                             {"cert_rerun": lambda m, k: (called.append(k), (0, "STARTED", "rm-cert-rerun-fake-2"))[1]})
    ok(called == [key] and s["cert_rerun"]["tries"] == 2 and s["cert_rerun"]["unit"] == "rm-cert-rerun-fake-2",
       "the retry is counted on its build key's tries: %r" % s["cert_rerun"])
    # 2026-11-21 (form_fault): at launch_tries the tick never waits for a hand: it owes a repair run with the evidence
    def owed(s):
        return " ".join(x["text"] for x in s.get("form_repairs") or [] if x.get("state") == "owed")
    got, s, row = decide({"key": key, "unit": U, "at": T0, "failed": None, "tries": 3})
    ok(got == "decided" and "left no result" in owed(s) and not row.get("need"),
       "at launch_tries it owes a repair, saying so, no hand line (%r)" % owed(s)[:120])
    got, s, row = decide({"key": key, "unit": U, "at": T0, "failed": None, "tries": 1},
                         res={"unit": U, "ok": False, "key_after": None, "published": None, "error": None})
    ok(got == "decided" and "ended" in owed(s),
       "a rerun that wrote its own result counts: the same build never reruns (%r)" % owed(s)[:120])
    got, _, _ = decide({"key": key, "unit": U, "at": T0, "failed": None, "tries": 1}, now=T0 + 60)
    ok(got == "decided" and puts and puts[-1][0] == "live", "within its bound it still reads live: %r" % puts[-1:])


# ---- the Designer's chain count -------------------------------------------------------------------------------------

C1 = "/tmp/concepts/FakeConcept"


def chained(how):
    import role_launch as RL
    key = "%s %s" % (RL.day_of(T0), C1)
    req = {"at": T0, "by": "Dispatcher", "mode": "run", "concept": C1, "chain_key": key, "chain_stage": "4"}
    rs = {"chain_day": {key: 3}, "chain_stages_day": {key: ["3", "4", "4"]}, "run_now": req}
    RL.refuse_now(rs, how, T0, {"manual": req})
    return rs, key


def t_a_run_now_never_launched_gives_its_chain_back(tmp):
    for how in ("expired", "pipeline paused", "owner hold", "off switch"):
        rs, key = chained(how)
        ok(rs["chain_day"][key] == 2 and rs["chain_stages_day"][key] == ["3", "4"] and "run_now" not in rs
           and rs["run_now_last"]["outcome"] == "refused: " + how,
           "a run-now consumed unlaunched (%s) gives its chain back: %r" % (how, rs["chain_day"]))


def t_a_gate_refusal_keeps_its_chain(tmp):
    for how in ("stage machine: BLOCKED on x", "no cap", "daily cap", "ops reading UNMEASURED"):
        rs, key = chained(how)
        ok(rs["chain_day"][key] == 3 and rs["chain_stages_day"][key] == ["3", "4", "4"],
           "a gate refusal (%s) keeps its chain: the brake on an ask-and-refuse loop" % how)


def t_no_sweep_while_the_role_is_off(tmp):
    import role_launch as RL
    import selftest_dispatcher as SD
    now = SD.at_local("10:15")
    rows = [(C1, {"status": "ready", "stage": 4, "results": [], "history": []}, now - 7200)]

    def drive(off):
        o = SD.robs(SD.ops_status(now), off=off)
        o["stage_concepts"] = lambda: rows
        acts, st = [], {"roles": {}}
        role = SD.operations(chain_stages=True, runs_local=[], economy_pass_local=None)
        RL.decide_roles({"roles": [role]}, st, o, now, lambda **k: acts.append(k), set(), None)
        asks = [a for a in acts if a.get("do") == "role_hold" and "next stage chained" in str(a.get("why"))]
        return asks, (st["roles"].get("Operations") or {})
    asks, rs = drive(None)
    ok(len(asks) == 1, "with the role on, the sweep asks the ready concept (it can see: %d ask)" % len(asks))
    asks, rs = drive("off for the test")
    ok(asks == [] and not any((rs.get("chain_day") or {}).values()),
       "with the role's off switch set, the sweep asks nothing and spends no chain (%r)" % rs.get("chain_day"))


def t_a_concept_no_run_opened_is_not_swept(tmp):
    """The chain sweep, through the decide tick, and the Designer stall reader skip a concept no run has opened
    (fresh from designer_stage init); one whose first run opened and died is still swept and still counted."""
    import designer_stage as DS
    import role_launch as RL
    import selftest_dispatcher as SD
    sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
    import ops_watch as OW
    now = SD.at_local("10:15")
    root = os.path.join(tmp, "fresh_concepts")
    d = os.path.join(root, "FreshMod")
    DS.init(d, "FreshMod")
    fresh = DS.load_state(d)
    opened = dict(fresh, history=fresh["history"] + [{"at": "2026-11-18T17:00:00Z", "stage": 0, "what": "open",
                                                     "why": "run rm-role-designer-1, stage 0"}])

    def drive(st):
        o = SD.robs(SD.ops_status(now), off=None)
        o["stage_concepts"] = lambda: [(d, st, now - 7200)]
        acts, state = [], {"roles": {}}
        role = SD.operations(chain_stages=True, runs_local=[], economy_pass_local=None)
        RL.decide_roles({"roles": [role]}, state, o, now, lambda **k: acts.append(k), set(), None)
        return [a for a in acts if a.get("do") == "role_hold" and "next stage chained" in str(a.get("why"))]
    ok(RL.never_opened(fresh) and not RL.never_opened(opened), "never_opened reads init's state as never opened, and "
       "one with an `open` row as opened")
    ok(drive(fresh) == [], "the decide tick's sweep asks nothing for a concept no run has opened")
    ok(len(drive(opened)) == 1, "a concept whose first run opened and died is still swept (the sweep can see)")
    state_file = os.path.join(tmp, "dispatcher_state.json")
    with open(state_file, "w") as f:
        json.dump({"roles": {}}, f)
    q = {"root": root, "repo": tmp, "state_file": state_file, "runs_dir": os.path.join(tmp, "no_runs")}
    plist = OW._q_designer(q, now, {}, None)[0]
    ok(plist == [], "the stall reader counts a concept no run has opened as pending to nobody (%r)" % plist)
    DS.write_json(DS.state_path(d), opened)
    plist = OW._q_designer(q, now, {}, None)[0]
    ok(len(plist) == 1, "the stall reader still counts a ready concept a run has opened (%r)" % plist)


def claim_void_mark_that_raises():
    """DOES NOT SURVIVE a-void-mark-that-raises (not a promise): the claim's own test, run on the base and failing
    there (the rejection counts), was recorded real; rare by the owner's card of 2026-11-19, so no fix: this pins what
    the page says happens instead."""
    import selftest_role_launch_reject_routes as RR

    def boom(c, u, why):
        raise OSError("stage.json read failed")
    rs = {}
    acts, _, _ = RR.harvest(rs, ["no result.json (a closing message is not a result)"], res=None,
                            seams={"stage_void": boom})
    void_alarm = [a for a in acts if a.get("kind") == "role:Designer:stage_void"]
    ok(void_alarm and "the rejection counts" in void_alarm[0]["why"]
       and any(a.get("kind") == "role:Designer:stage_rejected" for a in acts),
       "not handled, as the page says: a void mark that raises leaves the rejection counted and says so once")


# ---- the Designer's loop ceiling ------------------------------------------------------------------------------------

def t_void_runs_spend_nothing_on_the_loop_ceiling(tmp):
    import designer_stage as DS

    def iso(t):
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))
    J1, J2 = DS.JUDGE_REF + "1", DS.JUDGE_REF + "2"
    t1, t2, t3, t4, t5 = (T0 + 60 * n for n in (1, 2, 3, 4, 5))
    # run U5 is hand-voided INSIDE the loop: counted, it would cross the ceiling at t5 + 30 (second look)
    charges = [(t1, 100, J1), (t1, 50, J1 + "-reader"), (t2, 1500, "run U9"), (t3, 1000, "run U8"),
               (t4, 100, J2), (t5, 300, "run U7"), (t5 + 30, 1700, "run U5")]
    st = {"budget": {"cap": 1000, "spent": sum(c[1] for c in charges),
                     "charges": [{"at": iso(a), "tokens": n, "kind": "stage", "ref": r} for a, n, r in charges]},
          "coverage_rounds": [{"judge": J1, "at": iso(t1), "verdict": None, "error": "timeout", "error_kind": "system"},
                              {"judge": J2, "at": iso(t4), "verdict": "not_covered"}],
          "results": [{"run": "U8", "outcome": "rejected", "at": iso(t3), "void_system": "killed",
                       "why": ["no result.json (a closing message is not a result)"]}],
          "voided": {"spend_refs": ["run U9", "run U5"]}}
    ok(DS.loop_start(st) == t4, "a void_system judge round starts no loop: it starts at the first real round (%s)"
       % DS.loop_start(st))
    ok(DS.loop_spend(st) == 400 and DS.loop_ceiling(st) is None,
       "void charges (a void judge and its reader, a hand-voided run, a void_system run, one inside the loop) do "
       "not count: %s"
       % DS.loop_spend(st))
    st["budget"]["charges"].append({"at": iso(t5 + 60), "tokens": 1700, "kind": "stage", "ref": "run U6"})
    ceil = DS.loop_ceiling(st)
    ok(DS.ceiling_crossed_at(st) == t5 + 60 and ceil and "void spend 4350" in ceil,
       "the crossing is the real charge that met the ceiling, the void spend shown apart: %r" % ceil)


def t_a_done_run_after_the_voids_lifts_the_void_hold(tmp):
    """queues-20261121133600: Pyrelands met the void limit (3 void_system runs), the cause was repaired, a hand
    run-now finished done, and still nothing chained it for 4.6 h: the hold lasted to the local midnight."""
    import role_launch as RL
    import run_void as RV
    day = RL.day_of(T0)
    rs = {"void_faults": [{"day": day, "concept": C1, "unit": "v%d" % i, "cause": "no claude result", "at": T0 + i}
                          for i in range(RV.SYSTEM_FAULT_LIMIT)]}
    last = T0 + RV.SYSTEM_FAULT_LIMIT - 1
    ok(RL.void_held(rs, C1, last + 120), "at the void limit the concept is held")
    rs["runs"] = [{"unit": "hand", "concept": C1, "state": "done", "at": last + 60}]
    ok(not RL.void_held(rs, C1, last + 120), "a run launched after the last void that finished done lifts the hold")
    for run, why in (({"state": "failed", "at": last + 60}, "a run that did not finish done"),
                     ({"state": "done", "at": last - 60}, "a done run launched before the last void"),
                     ({"state": "done", "at": last + 60, "concept": "/tmp/concepts/Other"}, "another concept's run"),
                     ({"state": "done", "at": last + 60, "unit": "v0"}, "a void unit itself")):
        rs["runs"] = [dict({"unit": "hand", "concept": C1}, **run)]
        ok(RL.void_held(rs, C1, last + 120), "%s lifts nothing" % why)


def main():
    import control as C
    tmp = tempfile.mkdtemp(prefix="selftest_void_counters_")
    keep = {k: os.environ.get(k) for k in ("RM_RUN_VOIDS_FILE", "RM_MATURATION_DISPATCH_DIR", "RM_CONTROL_DB",
                                           "RM_PIPELINE_PAUSE_FILE", "RM_OWNER_HOLD_FILE", "RM_UNDER_SELFTEST", "TZ")}
    try:
        os.environ["RM_RUN_VOIDS_FILE"] = os.path.join(tmp, "voids.jsonl")
        os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
        os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
        os.environ["RM_CONTROL_DB"] = os.path.join(tmp, "control.db")
        C.init(os.environ["RM_CONTROL_DB"])
        os.environ["RM_PIPELINE_PAUSE_FILE"] = os.path.join(tmp, "PIPELINE_PAUSE.json")
        os.environ["RM_OWNER_HOLD_FILE"] = os.path.join(tmp, "mod_owner_hold.json")
        with open(os.environ["RM_OWNER_HOLD_FILE"], "w") as f:
            json.dump({"holds": []}, f)
        os.environ["RM_UNDER_SELFTEST"] = "1"
        t_unknown_result_with_its_own_answer_counts(tmp)
        t_mod_since_finds_moved_system_voids(tmp)
        t_a_killed_pilot_launch_spends_no_holder_try(tmp)
        t_a_killed_red_decider_builder_spends_no_try(tmp)
        t_ledger_runs_stay_for_their_run_end(tmp)
        t_a_certificate_rerun_left_no_result_is_tried_again(tmp)
        t_a_run_now_never_launched_gives_its_chain_back(tmp)
        t_a_gate_refusal_keeps_its_chain(tmp)
        t_no_sweep_while_the_role_is_off(tmp)
        t_a_concept_no_run_opened_is_not_swept(tmp)
        t_void_runs_spend_nothing_on_the_loop_ceiling(tmp)
        t_a_done_run_after_the_voids_lifts_the_void_hold(tmp)
        claim_void_mark_that_raises()
    finally:
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
