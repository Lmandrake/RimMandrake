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


# ---- the void hold ends by itself when the fault is gone ------------------------------------------------------------
# RIMMANDRAKE_REARM_BREAKER_BY_PROBE_KNOCKBACK_SAT_105_MIN: three Explosive Knockback Designer runs were void in 13 min
# (the stage-5 judge step exited 3 on a signed tree); the limit stopped the chain; the cause was fixed at 9:10 PM PST
# 2026-11-26 (f84a3bc6e2), and nothing chained the concept until a hand run-now at 10:55 PM PST.

NO_CLAUDE = "the unit ended with no claude result of its own"


def held_rs(now, probe=True, n=None):
    import role_launch as RL
    import run_void as RV
    n = RV.SYSTEM_FAULT_LIMIT if n is None else n
    return {"void_faults": [dict({"day": RL.day_of(now), "concept": C1, "unit": "v%d" % i, "cause": NO_CLAUDE,
                                  "at": now - 600 + i}, **({"probe": RL.void_probe_argv(C1, NO_CLAUDE)} if probe
                                                          else {})) for i in range(n)]}


def drive_sweep(rs, now, reader):
    """One real decide tick over a chain_stages role whose one concept is ready at stage 5 (pending 2 h), with the void
    dry check read by `reader(argv) -> (rc, line)`. -> (asks, role state, reader calls)."""
    import role_launch as RL
    import selftest_dispatcher as SD
    calls = []
    keep = RL.VOID_PROBE_READ
    RL.VOID_PROBE_READ = lambda argv: (calls.append(list(argv)), reader(argv))[1]
    try:
        rows = [(C1, {"status": "ready", "stage": 5, "results": [], "history": [{"what": "open"}]}, now - 7200)]
        o = SD.robs(SD.ops_status(now))
        o["stage_concepts"] = lambda: rows
        acts, st = [], {"roles": {"Operations": rs}}
        role = SD.operations(chain_stages=True, runs_local=[], economy_pass_local=None)
        RL.decide_roles({"roles": [role]}, st, o, now, lambda **k: acts.append(k), set(), None)
    finally:
        RL.VOID_PROBE_READ = keep
    asks = [a for a in acts if a.get("do") == "role_hold" and "next stage chained" in str(a.get("why"))]
    return asks, st["roles"]["Operations"], calls


def t_a_dry_check_that_passes_lifts_the_void_hold(tmp):
    import role_launch as RL
    import selftest_dispatcher as SD
    now = SD.at_local("10:15")
    # the void route writes the dry check on the fault of a unit that ended with no claude result, none on a timeout
    rs = {}
    RL.void_route("Operations", rs, {}, {"concept": C1, "unit": "u1"}, NO_CLAUDE, now, lambda **k: None, {})
    RL.void_route("Operations", rs, {}, {"concept": C1, "unit": "u2"}, "stopped at run_max_s after 1 stop(s), before "
                  "it wrote result.json", now, lambda **k: None, {})
    f1, f2 = rs["void_faults"]
    ok(f1.get("probe") == ["python3", "src/RimMandrake/rimflow/role_launch.py", "prelaunch-dry", C1]
       and "probe" not in f2, "the void fault of a unit that ended with no claude result carries its dry check, a "
       "timeout none (%r / %r)" % (f1.get("probe"), f2.get("probe")))
    # the step now exits 0: the next tick lifts the hold and chains the held concept
    asks, rs, calls = drive_sweep(held_rs(now), now, lambda argv: (0, "stage5-judge: already signed"))
    lift = (rs.get("void_lifts") or [{}])[-1]
    req = rs.get("run_now") or rs.get("run_now_last") or {}     # the same decide takes the asked run-now
    ok(calls and len(asks) == 1 and req.get("concept") == C1 and req.get("chained_from") == "orphan-sweep",
       "a tripped void limit whose dry check now exits 0: the next tick chains the held concept (%d ask, %d read)"
       % (len(asks), len(calls)))
    ok(lift.get("how") == "probe" and lift.get("concept") == C1 and "already signed" in str(lift.get("reading")),
       "the lift is recorded with its reading: %r" % lift)
    # the step still fails: nothing is chained
    asks, rs, calls = drive_sweep(held_rs(now), now, lambda argv: (1, "stage5-judge: the judge would end the unit"))
    ok(calls and not asks and not rs.get("run_now") and not rs.get("run_now_last") and not rs.get("void_lifts"),
       "a dry check that still exits 1 chains nothing (%d ask, %r)" % (len(asks), rs.get("void_lifts")))
    # a probe that cannot look decides nothing by itself: the trial rule's wait still stands
    asks, rs, calls = drive_sweep(held_rs(now), now, lambda argv: (2, "no pre-launch step at stage 3"))
    ok(calls and not asks and not rs.get("void_lifts"),
       "a dry check that could not look (exit 2) lifts nothing inside the trial wait (%d ask)" % len(asks))


def t_a_held_concept_with_no_dry_check_gets_one_trial_after_a_growing_wait(tmp):
    import role_launch as RL
    import selftest_dispatcher as SD
    now = SD.at_local("10:15")
    W = RL.VOID_TRIAL_WAIT_S
    no_read = lambda argv: (_ for _ in ()).throw(AssertionError("no dry check to read"))   # noqa: E731
    rs = held_rs(now, probe=False)
    last = max(f["at"] for f in rs["void_faults"])
    asks, rs, calls = drive_sweep(rs, last + W - 60, no_read)
    ok(not asks and not rs.get("void_lifts"), "inside the wait nothing is chained (%d ask)" % len(asks))
    asks, rs, calls = drive_sweep(rs, last + W + 60, no_read)
    ok(len(asks) == 1 and [x.get("how") for x in rs.get("void_lifts") or []] == ["trial"],
       "after the wait one trial run is chained (%d ask, lifts %r)" % (len(asks), rs.get("void_lifts")))
    # the trial voids: held at once, and the next wait is twice as long
    rs.pop("run_now", None), rs.pop("run_now_last", None)
    t4 = last + W + 300
    rs["void_faults"].append({"day": RL.day_of(t4), "concept": C1, "unit": "trial1", "cause": NO_CLAUDE, "at": t4})
    ok(RL.void_held(rs, C1, t4 + 60), "a void after the trial's lift holds the concept again at once")
    asks, rs, calls = drive_sweep(rs, t4 + W + 60, no_read)
    ok(not asks, "one wait after the failed trial nothing is chained: the wait grew (%d ask)" % len(asks))
    asks, rs, calls = drive_sweep(rs, t4 + 2 * W + 60, no_read)
    ok(len(asks) == 1 and len(rs.get("void_lifts") or []) == 2,
       "two waits after the failed trial the second trial is chained (%d ask)" % len(asks))
    # a dry check whose lift a void followed is not read again that day: the trial rule decides
    rs = held_rs(now)
    asks, rs, calls = drive_sweep(rs, now, lambda argv: (0, "fine"))
    rs.pop("run_now", None)
    t5 = now + 120
    rs["void_faults"].append(dict(rs["void_faults"][0], unit="after-probe", at=t5))
    asks, rs, calls = drive_sweep(rs, t5 + 60, lambda argv: (0, "fine"))
    ok(not calls and not asks, "a dry check that lifted and was followed by a void is not read again (%d read, %d ask)"
       % (len(calls), len(asks)))


def t_the_dry_check_reads_the_stage_5_judge_step_without_a_judge(tmp):
    import role_launch as RL
    import designer_stage as DS
    import coverage_judge as CJ
    d = os.path.join(tmp, "dry_concept")
    DS.init(d, "DryMod")
    st = DS.load_state(d)
    st.update(stage=5, status="ready")
    DS.write_json(DS.state_path(d), st)
    keep = CJ.plan, CJ.prior_verdict
    ran = []
    runner = lambda *a, **k: ran.append(a)      # noqa: E731
    advisory = {"verdict": "not_covered", "advisory": "an uncalibrated brief"}
    try:
        # (plan, prior verdict, the dry exit): as coverage_judge.main/run answer each plan without a look
        for what, why, prior, want in (("skip", "already signed at tree abc", advisory, 0),
                                       ("judge", "the tree changed", None, 0),
                                       ("skip", "the exam does not pass: x", None, 0),
                                       ("skip", "the exam does not pass: x", advisory, 1),
                                       ("skip", "the exam does not pass: x", dict(advisory, stale_inputs=["t"]), 0),
                                       ("stopped", "the loop limit", None, 1), ("parked", "for him", None, 1),
                                       ("error", "unreadable concept: x", None, 1)):
            CJ.plan = lambda c, repo=None, w=what, y=why: (w, y)
            CJ.prior_verdict = lambda c, p=prior: p
            rc = RL.stage5_judge(d, runner=runner, dry=True)
            ok(rc == want and not ran, "dry stage5-judge on a plan of %s (%s, prior %s) exits %d, no judge started "
               "(got %r, %d judge calls)" % (what, why, "advisory" if prior else "none", want, rc, len(ran)))
    finally:
        CJ.plan, CJ.prior_verdict = keep
    rc, line = RL.prelaunch_dry(os.path.join(tmp, "no_such_concept"))
    ok(rc == 2, "prelaunch-dry on a concept with no readable stage exits 2, could not look: %r" % line)
    st.update(stage=3)
    DS.write_json(DS.state_path(d), st)
    rc, line = RL.prelaunch_dry(d)
    ok(rc == 2 and "no pre-launch step" in line, "prelaunch-dry where the stage has no pre-launch step exits 2: %r"
       % line)


# ---- a stage-5 unit that ended at its coverage judge ----------------------------------------------------------------

NO_RESULT_WHY = "no result.json (a closing message is not a result)"


def judge_harvest(verdict, prior_voids=0, run_at=T0, transcript=None):
    """One finished stage-5 Designer run on C1 that left no result.json and no claude result (the unit ended at its
    stage5-judge step), with `verdict` on the concept's coverage_verdict.json. -> (rs, acts, seam calls)."""
    import role_launch as RL
    import selftest_designer_chain as SC
    import run_void as RV
    now = run_at + 900
    day = RL.day_of(now)
    rs = {"runs": [{"state": "running", "unit": "rm-role-designer-look", "at": run_at, "day": day, "budget": 400000,
                    "mode": "run", "item": "X_ITEM", "concept": C1, "scope": "S.scope", "marker": "M"}],
          "void_faults": [{"day": day, "concept": C1, "unit": "v%d" % i, "cause": "launch fault", "at": run_at - 900 + i}
                          for i in range(min(prior_voids, RV.SYSTEM_FAULT_LIMIT - 1))]}
    calls = {"close": [], "void": [], "look": []}
    acts = []
    obs = {"unit_state": lambda u: "inactive", "result": lambda r: None, "procs": lambda *a, **k: [],
           "transcript": lambda r: transcript, "program_closed": lambda c, u: None,
           "stage_close": lambda c, u, t: (calls["close"].append((u, t)), (False, [NO_RESULT_WHY]))[1],
           "stage_void": lambda c, u, why: (calls["void"].append(why), True)[1],
           "stage_judge_look": lambda c, u, look: (calls["look"].append(look), True)[1],
           "coverage_verdict": lambda c: verdict, "stage_land": lambda c, u: None, "stage_turn": lambda c: None,
           "stage_status": lambda c: {"stage": 5, "status": "ready"}}
    RL._supervise_one("Designer", rs, dict(RL.ROLE_DEFAULTS, **SC.designer_row()), obs, now,
                      lambda **kw: acts.append(kw), set())
    return rs, acts, calls


def look_verdict(at, fixed=True):
    """A not_covered verdict as coverage_judge.run writes it: with the judge's own fix (advisory, stale_inputs: the
    unit then exits STOP_EXIT) or a plain refusal."""
    import role_launch as RL
    v = {"verdict": "not_covered", "signed": False, "judge": "rm-coverage-judge-%d" % int(at), "at": RL.iso(at),
         "gaps": [{"gid": "g1", "ids": ["c1"]}], "error": None}
    if fixed:
        v.update(judge_fixed={"files": ["scenes.json"], "what": ["added a scene"], "by": v["judge"]},
                 stale_inputs=["scenes.json"], advisory="the judge fixed scenes.json itself: the next look, a fresh "
                 "judge that did not make it, checks it as a repair")
    return v


def t_an_unsigned_judge_look_is_the_judges_result(tmp):
    """Wrecked Machines 2026-11-27 (RIMMANDRAKE_CLASS_UNSIGNED_JUDGE_LOOK_AS_VERDICT_FOURTH_VOID): the stage-5 judge
    answered not_covered and fixed scenes.json itself, its step exited STOP_EXIT, and the unit was classed void_system
    as "the unit ended with no claude result of its own"; with three earlier voids that day the limit stopped the
    chain. The look is the judge's result: no void fault, charged 0 (the judge's own look is charged by its rules), the
    rejection marked judge_look, and the stage chained again for the act the verdict names."""
    import designer_stage as DS
    for fixed, nxt in ((True, "a fresh judge look"), (False, "the Designer's mend")):
        rs, acts, calls = judge_harvest(look_verdict(T0 + 90, fixed), prior_voids=2)
        run = rs["runs"][0]
        what = "a judge's own fix" if fixed else "a plain refusal"
        ok(not calls["void"] and len(rs["void_faults"]) == 2
           and not any(a.get("kind") == "role:Designer:system_fault" for a in acts),
           "%s: the unit is not void_system and adds no void fault (void marks %r, faults %d)" % (
               what, calls["void"], len(rs["void_faults"])))
        ok(run.get("by") == "judge_look" and run.get("state") == "done" and run.get("tokens") == 0
           and calls["close"] == [("rm-role-designer-look", 0)],
           "%s: the run is the judge's look, done, charged 0 and closed at 0 (by %r, state %r, tokens %r, closes %r)" % (
               what, run.get("by"), run.get("state"), run.get("tokens"), calls["close"]))
        look = (calls["look"] or [{}])[0]
        ok(look.get("judge") == "rm-coverage-judge-%d" % int(T0 + 90) and str(look.get("next")).startswith(nxt),
           "%s: the stage record names the judge and the next act, %r: %r" % (what, nxt, look))
        req = rs.get("run_now") or {}
        ok(req.get("concept") == C1 and req.get("chain_stage") == "5" and nxt in str(req.get("why")),
           "%s: stage 5 is chained again for %s: %r" % (what, nxt, req))
    # the stage file: the judge look's rejection spends no Designer retry, parks nothing, and its run spends no loop
    d = os.path.join(tmp, "look_concept")
    DS.init(d, "LookMod")
    st = DS.load_state(d)
    st.update(stage=5, status="ready")
    st["results"].append({"stage": 5, "outcome": "rejected", "run": "U1", "at": "2026-11-18T18:00:00Z",
                          "why": [NO_RESULT_WHY]})
    st["results"].append({"stage": 5, "outcome": "rejected", "run": "U2", "at": "2026-11-18T18:30:00Z",
                          "why": [NO_RESULT_WHY]})
    for u in ("U1", "U2"):
        DS.hist(st, "retry", "run %s result rejected: %s" % (u, NO_RESULT_WHY))
    DS.write_json(DS.state_path(d), st)
    look = {"judge": "rm-coverage-judge-1", "verdict": "not_covered", "next": "a fresh judge look"}
    for u in ("U1", "U2"):
        ok(DS.judge_look_rejection(d, u, look), "the judge look marks run %s's no-result rejection" % u)
    st = DS.load_state(d)
    ok(DS.stage_retries(st) == 0 and DS.rejection_parked(st) is None and {"run U1", "run U2"} <= DS.loop_void_refs(st),
       "a judge look's rejection spends no retry, parks nothing, and its run's charge is no loop spend (retries %d, "
       "parked %r)" % (DS.stage_retries(st), DS.rejection_parked(st)))
    ok(not DS.judge_look_rejection(d, "U1", look), "a run already marked is not marked twice")


def t_a_unit_with_no_look_of_its_own_stays_void(tmp):
    """The two must-stay cases of the judge look: a unit killed before any verdict, and a unit that left only an
    EARLIER unit's verdict on file, are void_system as before; so is a verdict whose own judge call died."""
    void_round = {"verdict": None, "signed": False, "judge": "rm-coverage-judge-x", "at": None,
                  "error": "the judge did not answer", "error_kind": "system"}
    void_round["at"] = __import__("role_launch").iso(T0 + 90)
    for verdict, what in ((None, "no verdict on file (killed before the judge answered)"),
                          (look_verdict(T0 - 3600), "an earlier unit's verdict"),
                          (void_round, "a verdict whose judge call died")):
        rs, acts, calls = judge_harvest(verdict)
        run = rs["runs"][0]
        ok(calls["void"] and not calls["look"] and run.get("by") != "judge_look" and len(rs["void_faults"]) == 1,
           "%s: still void_system (void marks %r, looks %r, faults %d)" % (what, calls["void"], calls["look"],
                                                                         len(rs["void_faults"])))
    rs, acts, calls = judge_harvest(look_verdict(T0 + 90), transcript={"usage": {}})
    ok(not calls["look"] and rs["runs"][0].get("by") != "judge_look",
       "a unit whose model started (a transcript) is not a judge look: harvested as before")


def t_a_void_judge_look_is_reclassed_by_its_verb(tmp):
    """The record an earlier harvest wrote (Wrecked Machines, rm-role-designer-1795777997) is corrected by the
    program's own verb: role_launch.reclass_judge_look takes the void fault off and re-marks the stage file; a unit
    with no look of its own is refused and nothing is written."""
    import designer_stage as DS
    import role_launch as RL
    rs, _acts, _calls = judge_harvest(None)        # classed void_system on the base rule: no verdict was read
    unit = rs["runs"][0]["unit"]
    d = os.path.join(tmp, "reclass_concept")
    DS.init(d, "ReclassMod")
    st = DS.load_state(d)
    st.update(stage=5, status="ready")
    st["results"].append({"stage": 5, "outcome": "rejected", "run": unit, "at": "2026-11-18T18:15:00Z",
                          "why": [NO_RESULT_WHY], "void_system": "the unit ended with no claude result of its own"})
    DS.hist(st, "retry", "run %s result rejected: %s" % (unit, NO_RESULT_WHY))
    st["history"][-1]["void_system"] = "the unit ended with no claude result of its own"
    DS.write_json(DS.state_path(d), st)
    rs["runs"][0]["concept"] = d
    for f in rs["void_faults"]:
        f["concept"] = d
    landed = []
    obs = {"coverage_verdict": lambda c: look_verdict(T0 + 90), "stage_land": lambda c, u: landed.append(u)}
    look, refused = RL.reclass_judge_look(rs, unit, "selftest", T0 + 2000, obs)
    st = DS.load_state(d)
    res = [r for r in st["results"] if r.get("run") == unit][-1]
    ok(look and not refused and not rs["void_faults"] and rs["runs"][0].get("by") == "judge_look"
       and rs["runs"][0].get("tokens") == 0 and landed == [unit],
       "the verb takes the void fault off and the run reads the judge's look at 0 tokens (refused %r, faults %r)" % (
           refused, rs["void_faults"]))
    ok(res.get("judge_look") and not res.get("void_system") and DS.stage_retries(st) == 0
       and "run %s" % unit in DS.loop_void_refs(st),
       "the stage file's rejection is re-marked judge_look, spends no retry and no loop spend: %r" % res)
    look2, refused2 = RL.reclass_judge_look(rs, unit, "again", T0 + 2100, obs)
    ok(look2 is None and "not classed void_system" in str(refused2), "a second reclass is refused: %r" % refused2)
    rs3, _a, _c = judge_harvest(None)
    before = json.dumps(rs3, sort_keys=True)
    look3, refused3 = RL.reclass_judge_look(rs3, rs3["runs"][0]["unit"], "x", T0 + 2000,
                                            {"coverage_verdict": lambda c: look_verdict(T0 - 3600)})
    ok(look3 is None and "stays void_system" in str(refused3) and json.dumps(rs3, sort_keys=True) == before,
       "a unit whose only verdict is an earlier unit's is refused and nothing is written: %r" % refused3)


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
        t_a_dry_check_that_passes_lifts_the_void_hold(tmp)
        t_a_held_concept_with_no_dry_check_gets_one_trial_after_a_growing_wait(tmp)
        t_the_dry_check_reads_the_stage_5_judge_step_without_a_judge(tmp)
        t_an_unsigned_judge_look_is_the_judges_result(tmp)
        t_a_unit_with_no_look_of_its_own_stays_void(tmp)
        t_a_void_judge_look_is_reclassed_by_its_verb(tmp)
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
