#!/usr/bin/env python3
"""Kills the mutation survivors of role_launch.decide_roles.one / _supervise_one / after_ready / after_slots /
_signal_marked (ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS; mutmut run 20261027T214640).

Method: each scenario drives the real function with fake observations and returns what it did (every action it
emitted, minus the long launch message, and the role state it left). The expected value is the reviewed golden
snapshot in GOLDEN below. Exact equality is the point: a mutated string literal is "XX<text>XX", which still
CONTAINS the old text, so a substring check cannot see it. A few scenarios carry explicit semantic asserts beside
the snapshot (boundaries). Regenerate the snapshot with `--gen` after a REVIEWED behaviour change.
Pure: fake runners, no systemd, no clock. Imports selftest_dispatcher for its role fixtures (conductor(), daily()...).
"""
import copy
import json
import os
import pprint
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ["TZ"] = "UTC"        # the golden epochs and day keys must not depend on the machine's zone
import time  # noqa: E402
time.tzset()
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402


FAILS = []
SCEN = []


def scen(fn):
    SCEN.append(fn)
    return fn


def acted(acts):
    """Actions as plain data; the launch message (prompt text) is another test's subject."""
    return [{k: (v if k != "message" else "<message>") for k, v in a.items()} for a in acts]


def norm(x):
    j = json.dumps(x, sort_keys=True, default=str)
    j = j.replace(SD.TMP, "<TMP>")    # paths compare relative to the test's own tmp dir, whatever TMPDIR is
    return json.loads(j)


def collector():
    acts = []
    return acts, lambda **kw: acts.append(kw)


def decide(roles, st, ob, now, busy=None, gate=None, **sch):
    acts, act = collector()
    s = dict({"roles": roles}, **sch)
    RL.decide_roles(s, st, ob, now, act, busy, gate)
    return {"acts": acted(acts), "roles": copy.deepcopy(st.get("roles")),
            "ledger_blind": st.get("ledger_blind")}


def supervise(roles, st, ob, now):
    acts, act = collector()
    busy = RL.supervise_roles({"roles": roles}, st, ob, now, act)
    return {"acts": acted(acts), "busy": sorted(busy), "runs": copy.deepcopy(
        {n: r.get("runs") for n, r in st["roles"].items()})}


T = SD.at_local("08:00")


def run(unit, at, **kw):
    r = {"state": "running", "unit": unit, "at": at, "mode": "quick", "budget": 1000, "item": "ROLES_ITEM_X",
         "seat": "BENCH", "run_max_s": 1800, "day": RL.day_of(T), "scope": "sc-" + unit}
    r.update(kw)
    return r


def usage(n):
    return {"input_tokens": n, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0}


OPUS, SONNET = "claude-opus-5-5", "claude-sonnet-5-5"


def cli(n, model=OPUS, **extra):
    """A result as `claude -p` writes it: the main thread's usage and modelUsage (the whole process, per model), which
    run_tokens weighs (weighted_v2: n uncached Opus 5.5 input tokens weigh n, Sonnet 5.5 n/2)."""
    r = {"usage": usage(n), "modelUsage": {model: {"inputTokens": n, "outputTokens": 0, "cacheReadInputTokens": 0,
                                                   "cacheCreationInputTokens": 0}}}
    r.update(extra)
    return r


def sobs(states, results=None, **kw):
    def unit_state(u):
        v = states.get(u, "inactive")
        if isinstance(v, Exception):
            raise v
        return v
    o = {"unit_state": unit_state, "result": lambda r: (results or {}).get(r["unit"])}
    o.update(kw)
    return o


# ---------------------------------------------------------------- _supervise_one

@scen
def sup_skips_finished_runs_then_looks_at_the_next():
    # a non-running entry first: `continue`, not `break`, so the running one after it is still supervised
    st = {"roles": {"Conductor": {"runs": [run("old", T - 100, state="done"), run("u2", T - 10)]}}}
    return supervise([SD.conductor()], st, sobs({"u2": "active"}), T)


@scen
def sup_unit_ended_without_scope_keeps_busy_and_next_run_still_seen():
    # u1: unit gone, no scope resolved -> "unit ..." reason: scope alarm (noted), busy, overdue -> stop on the scope
    # alone; u2 after it must still be handled (continue, not break): finished done
    st = {"roles": {"Conductor": {"runs": [
        run("u1", T - 2000, marker="m1", seat=None, scope=None),
        run("u2", T - 50, budget=500)]}}}
    res = {"u2": cli(400, SONNET, subtype="success")}
    return supervise([SD.conductor()], st, sobs({"u1": "inactive", "u2": "inactive"}, res), T)


@scen
def sup_unit_state_unmeasured_and_stop_ladder():
    st = {"roles": {"Conductor": {"runs": [
        run("weird", T - 10),
        run("noscope", T - 10, scope=None),
        run("t0", T - 1900, scope="s0", marker="m0"),
        run("t1", T - 1900, scope="s1", stop_tries=1),
        run("t2", T - 1900, scope="s2", stop_tries=2),
        run("short", T - 1799, run_max_s=1800),
        run("exact", T - 1800, run_max_s=1800)]}}}
    states = {"noscope": "inactive", "weird": "unknown", "t0": "active", "t1": "active", "t2": "active", "short": "active", "exact": "active"}
    return supervise([SD.conductor()], st, sobs(states), T)


@scen
def sup_learns_the_scope_of_an_unscoped_active_run():
    st = {"roles": {"Conductor": {"runs": [run("u1", T - 10, scope=None)]}}}
    got = supervise([SD.conductor()], st, sobs({"u1": "active"}, scope=lambda u, seat: "scope-of-%s-%s" % (u, seat)), T)
    # a run with a scope already is not re-resolved
    st2 = {"roles": {"Conductor": {"runs": [run("u1", T - 10, scope="kept")]}}}
    got2 = supervise([SD.conductor()], st2, sobs({"u1": "active"}, scope=lambda u, seat: "other"), T)
    return [got, got2]


@scen
def sup_done_runs_and_budget_alarm():
    runs = [run("ok", T - 60, budget=1000), run("eq", T - 60, budget=1000), run("over", T - 60, budget=1000),
            run("nobud", T - 60, budget=None), run("stopped", T - 60, stop_tries=2, budget=1000)]
    two = cli(999, subtype="success")
    two["modelUsage"][SONNET] = {"inputTokens": 0, "outputTokens": 0}     # a second model that spent nothing
    res = {"ok": two,
           "eq": cli(1000, subtype="success"),
           "over": cli(1001),
           "nobud": cli(5, subtype="success"),
           "stopped": cli(1, subtype="error_max_turns")}
    st = {"roles": {"Conductor": {"runs": runs}}}
    return supervise([SD.conductor()], st, sobs({}, res), T)


@scen
def sup_failed_runs_say_why():
    runs = [run("nofile", T - 60), run("iserr", T - 60), run("nousage", T - 60), run("emptyres", T - 60, err_tail="TAIL"),
            run("both", T - 60, err_tail="TAIL"), run("long", T - 60),
            run("noprice", T - 60, model_id="claude-nonesuch-9-9")]
    # noprice: usage but no modelUsage, of a model not in MODEL_PRICES: UNMEASURED by name, never another model's weight
    res = {"iserr": cli(3, is_error=True, result="boom"),
           "noprice": {"usage": usage(7), "subtype": "success"},
           "nousage": {"result": "usage limit"},
           "emptyres": {},
           "both": cli(1, result="RES", is_error=True),
           "long": cli(1, result="x" * 200, is_error=True)}
    st = {"roles": {"Conductor": {"runs": runs}}}
    return supervise([SD.conductor()], st, sobs({}, res), T)


@scen
def sup_old_runs_pruned_after_two_days():
    st = {"roles": {"Conductor": {"runs": [run("fresh", T - 2 * 86400 + 5, state="done"),
                                           run("stale", T - 2 * 86400, state="done"),
                                           run("live", T - 5 * 86400)]}}}
    return supervise([SD.conductor()], st, sobs({"live": "active"}), T)


@scen
def sup_one_roles_exception_alarms_with_its_item_and_is_busy():
    boom = RuntimeError("x" * 300)
    st = {"roles": {"Conductor": {"runs": [run("u1", T - 10)]}, "Ghost": {"runs": [run("g1", T - 10)]}}}
    return supervise([SD.conductor()], st, sobs({"u1": boom, "g1": boom}), T)


# ---------------------------------------------------------------- after_ready / after_slots

def rs_runs(*runs, done=None):
    return {"runs": list(runs), "done": dict(done or {})}


@scen
def after_ready_every_reason():
    op = SD.operations()
    c = SD.conductor(after_role="Operations")
    job = {"slot": "08:00", "key": RL.slot_key(T, "08:00")}
    k = RL.slot_key(T, "07:30")
    kp = RL.slot_key(RL.prev_day(T), "19:30")
    out = {}
    r = lambda *a, **kw: RL.after_ready(c, kw.pop("rst"), kw.pop("busy", set()), job, T, kw.pop("acfg", op))
    out["no after_role"] = RL.after_ready(SD.conductor(), {}, set(), job, T, op)
    out["alarm job"] = RL.after_ready(c, {}, set(), dict(job, slot=None), T, op)
    out["disabled"] = r(rst={}, acfg=dict(op, enabled=False))
    out["busy"] = r(rst={}, busy={"Operations"})
    out["no slots"] = r(rst={}, acfg=dict(op, runs_local=[], economy_pass_local=None))
    out["not run yet"] = r(rst={"Operations": rs_runs(done={})})
    out["not run (how)"] = r(rst={"Operations": rs_runs(done={k: "missed"})})
    out["ended"] = r(rst={"Operations": rs_runs({"slot": k, "state": "failed", "mode": "quick"},
                                                {"slot": k, "state": "done", "mode": "alarm"})})
    out["ended last of two"] = r(rst={"Operations": rs_runs({"slot": k, "state": "failed", "mode": "quick"},
                                                           {"slot": k, "state": "running", "mode": "quick"})})
    out["done"] = r(rst={"Operations": rs_runs({"slot": k, "state": "done", "mode": "quick"})})
    out["band skipped both"] = r(rst={"Operations": rs_runs(done={k: "band RED", kp: "band RED"})})
    out["band skipped then ok"] = r(rst={"Operations": rs_runs({"slot": kp, "state": "done", "mode": "quick"},
                                                               done={k: "band RED"})})
    return out


@scen
def after_slots_window_is_a_24h_half_open_interval():
    # slots of the parent exactly 24 h before the job's slot are out; exactly at it are in
    par = {"runs_local": ["08:00", "12:00"]}
    out = {}
    for hhmm in ("08:00", "07:59", "12:00", "08:01"):
        out[hhmm] = RL.after_slots(par, {"slot": hhmm}, T)
    return out


# ---------------------------------------------------------------- _signal_marked

@scen
def signal_marked_every_line():
    killed = []
    kill = lambda pid, sig: killed.append((pid, int(sig)))
    out = {}
    out["raise"] = RL._signal_marked("m", False, lambda m, since=None: 1 / 0, kill)
    out["none"] = RL._signal_marked("m", False, lambda m, since=None: None, kill)
    out["empty"] = RL._signal_marked("m", False, lambda m, since=None: [], kill)
    out["term"] = RL._signal_marked("m", False, lambda m, since=None: [11, 12], kill)
    out["kill"] = RL._signal_marked("m", True, lambda m, since=None: [13], kill)

    def kill_some(pid, sig):
        if pid == 21:
            raise OSError("gone")
        killed.append((pid, int(sig)))
    out["partly"] = RL._signal_marked("m", False, lambda m, since=None: [21, 22], kill_some)
    saved = RL.scan_marked
    try:
        RL.scan_marked = lambda marker, since=None: ([], "proc unlistable")
        out["blind empty"] = RL._signal_marked("m", False, None, kill)
        RL.scan_marked = lambda marker, since=None: ([31], "environ unreadable")
        out["blind with pid"] = RL._signal_marked("m", False, None, kill, since=5)
        RL.scan_marked = lambda marker, since=None: ([], None)
        out["clear"] = RL._signal_marked("m", False, None, kill)
        RL.scan_marked = lambda marker, since=None: 1 / 0
        out["scan raised"] = RL._signal_marked("m", False, None, kill)
    finally:
        RL.scan_marked = saved
    out["killed"] = killed
    return out


# ---------------------------------------------------------------- decide_roles.one

GATE_OK = lambda what: (True, {"account": "acctA", "state": "ready"})
GATE_NO = lambda what: (False, {"why": "switching to acctB"})


def fresh_st(**roles):
    return {"roles": {n: dict(v) for n, v in roles.items()}}


def tick(roles, st, ob, now, n=1, step=120, **kw):
    """n successive ticks; the list of each tick's result (acts and the role state)."""
    out = []
    for i in range(n):
        out.append(decide(roles, st, ob, now + i * step, **kw))
    return out


@scen
def decide_launch_golden_with_and_without_account():
    c = SD.conductor()
    a = decide([c], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set(), gate=GATE_OK)
    st = fresh_st()
    b = decide([c], st, SD.robs(SD.ops_status(T, runway=1.2)), T, busy=set())
    return [a, b]


@scen
def decide_default_busy_is_the_supervised_set():
    # busy is not given: decide asks supervise_roles, so a role with a run in flight launches nothing
    c = SD.conductor()
    st = fresh_st(Conductor={"done": {}, "runs": [run("live", T - 30, scope="sc")]})
    return decide([c], st, SD.robs(SD.ops_status(T), unit="active"), T)


@scen
def decide_busy_role_waits_and_is_not_marked():
    c = SD.conductor()
    st = fresh_st()
    return decide([c], st, SD.robs(SD.ops_status(T)), T, busy={"Conductor"})


@scen
def decide_slot_timing_edges():
    c = SD.conductor(slot_late_s=600)
    t0 = RL.slot_epoch(T, "08:00")
    out = {}
    for lab, now in (("before", t0 - 1), ("exact", t0), ("late edge", t0 + 600), ("missed", t0 + 601)):
        st = fresh_st()
        out[lab] = decide([c], st, SD.robs(SD.ops_status(now)), now, busy=set())
    # a missed slot that waited on its parent says so
    cc = SD.conductor(after_role="Operations", slot_late_s=600)
    st = fresh_st(Conductor={"done": {}, "runs": [], "waiting": [RL.slot_key(t0, "08:00"), "the Operations x"]})
    out["missed after waiting"] = decide([cc, SD.operations()], st, SD.robs(SD.ops_status(t0 + 700)), t0 + 700, busy=set())
    st = fresh_st(Conductor={"done": {}, "runs": [], "waiting": ["other key", "the Operations x"]})
    out["missed, waiting for another slot"] = decide([cc, SD.operations()], st, SD.robs(SD.ops_status(t0 + 700)),
                                                     t0 + 700, busy=set())
    return out


@scen
def decide_role_entries_and_schedule_errors():
    out = {}
    out["non-mapping entries"] = decide(["junk", 7, SD.conductor(enabled=False)], fresh_st(), SD.robs(SD.ops_status(T)), T,
                                        busy=set())
    out["disabled role"] = decide([SD.conductor(enabled=False)], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    out["missing launch keys"] = decide([{"name": "Nobody", "enabled": True, "seat": "BENCH"}], fresh_st(),
                                        SD.robs(SD.ops_status(T)), T, busy=set())
    out["bad slot_late_s"] = decide([SD.conductor(slot_late_s=0)], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    cc = SD.conductor(after_role="Operations")
    out["parent disabled"] = decide([cc, SD.operations(enabled=False)], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    out["parent unknown"] = decide([cc], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    out["parent slots unreadable"] = decide([cc, SD.operations(runs_local=["Wdy 07:30"])], fresh_st(),
                                            SD.robs(SD.ops_status(T)), T, busy=set())
    return out


@scen
def decide_after_role_waits_once_and_follows():
    t0 = SD.at_local("08:00")
    cc, op = SD.conductor(after_role="Operations"), SD.operations()
    st = fresh_st()
    ticks = tick([cc, op], st, SD.robs(SD.ops_status(t0)), t0, n=2, busy=set())
    return ticks


@scen
def decide_alarm_runs():
    op = SD.operations(alarm_runs=True, runs_local=["07:30"], economy_pass_local=None, alarm_run_gap_s=1000)
    now = SD.at_local("12:00")
    al = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}, "a2": {"state": "OPEN", "for": "Operations"},
          "a3": {"state": "CLOSED", "item": "GONE"}}
    out = {}
    st = fresh_st(Operations={"done": {}, "runs": [], "alarms_seen": ["ITEM_ONE", "STALE_KEY"]})
    out["fresh one launches, stale pruned"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarms_seen": ["ITEM_ONE", "alarm:a2"]})
    out["all seen: nothing"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    # blind readings hold once; the flag is True
    st = fresh_st()
    out["alarms unreadable"] = tick([op], st, SD.robs(dict(SD.ops_status(now), alarms={"_alarm_state": "UNREADABLE"})), now,
                                    n=2, busy=set())
    st = fresh_st()
    out["status unmeasured"] = tick([op], st, SD.robs(None), now, n=2, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_blind": True})
    out["blind clears"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    # gap
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_last_run": now - 999})
    out["gap held"] = tick([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, n=2, step=0, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_last_run": now - 1000})
    out["gap exactly over launches"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_last_run": now - 5000})
    out["after gap launches"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    return out


@scen
def decide_alarm_daily_limits():
    now = SD.at_local("12:00")
    al = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}, "a2": {"state": "OPEN", "item": "ITEM_TWO"}}
    out = {}
    op = SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs_per_day=1)
    st = fresh_st()
    out["per_day unused: launches"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_day": {"day": RL.day_of(now), "n": 1, "keys": {}}})
    out["per_day used: held once"] = tick([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, n=2, busy=set())
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_day": {"day": "2000-01-01", "n": 9, "keys": {}}})
    out["yesterday's count does not carry"] = decide([op], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    op2 = SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs_per_alarm_per_day=1)
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_day": {"day": RL.day_of(now), "n": 1, "keys": {"ITEM_ONE": 1}}})
    out["per_key used for one key"] = tick([op2], st, SD.robs(SD.ops_status(now, alarms=al)), now, n=2, busy=set())
    op3 = SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs_per_alarm_per_day=2)
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_day": {"day": RL.day_of(now), "n": 1, "keys": {"ITEM_ONE": 1}}})
    out["per_key not yet used"] = decide([op3], st, SD.robs(SD.ops_status(now, alarms=al)), now, busy=set())
    return out


@scen
def decide_done_retention():
    # old done keys are dropped past two local days; two days back stays
    p = SD.daily(after_role=None)
    t = SD.at_local("13:00")
    d = lambda n: RL.day_of(t - n * 86400)
    st = fresh_st(Daily={"done": {d(3) + " 09:00": "launch", d(2) + " 09:00": "launch", d(1) + " 09:00": "launch"},
                         "runs": []})
    decide([p], st, SD.robs(SD.ops_status(t)), t, busy=set())
    return sorted(st["roles"]["Daily"]["done"])


@scen
def decide_off_switch_and_window():
    c = SD.conductor()
    out = {}
    seen = []
    ob = SD.robs(SD.ops_status(T), off="owner: stop")
    ob["off"] = lambda p: (seen.append(p), "owner: stop")[1]
    st = fresh_st()
    out["off reason"] = decide([c], st, ob, T, busy=set())
    out["off path"] = seen
    ob2 = SD.robs(SD.ops_status(T), off="")
    out["off, no reason"] = decide([SD.conductor()], fresh_st(), ob2, T, busy=set())
    out["off without an off_file"] = decide([SD.conductor(off_file=None)], fresh_st(), SD.robs(SD.ops_status(T), off=None),
                                            T, busy=set())
    seen2 = []
    ob3 = SD.robs(SD.ops_status(T))
    ob3["off"] = lambda p: (seen2.append(p), None)[1]
    decide([SD.conductor(off_file=None)], fresh_st(), ob3, T, busy=set())
    out["no off_file: asked with empty path"] = seen2
    # window of the role
    cw = SD.conductor(window_name="Conductor RC")
    for lab, val in (("live", (True, "window found")), ("unmeasured", (None, "enumeration failed")),
                     ("not live", (False, "no window"))):
        ob = SD.robs(SD.ops_status(T))
        asked = []
        ob["window_live"] = lambda name, val=val, asked=asked: (asked.append(name), val)[1]
        st = fresh_st()
        out["window " + lab] = tick([cw], st, ob, T, n=2, busy=set())
        out["window %s asked" % lab] = asked
    st = fresh_st(Conductor={"done": {}, "runs": [], "window_hold": "old"})
    ob = SD.robs(SD.ops_status(T))
    ob["window_live"] = lambda name: (False, "")
    out["window gone clears hold"] = decide([cw], st, ob, T, busy=set())
    return out


@scen
def decide_blocked_by_reading_band_and_caps():
    out = {}
    c = SD.conductor()
    out["ops unreadable"] = decide([c], fresh_st(), SD.robs(None), T, busy=set())
    out["band FLOOR blocks the slot"] = decide([c], fresh_st(), SD.robs(SD.ops_status(T, week_left=5.0)), T, busy=set())
    t20 = SD.at_local("20:00")
    st = fresh_st()
    out["AMBER: second slot held"] = tick([c], st, SD.robs(SD.ops_status(t20, runway=1.2)), t20, n=1, busy=set())
    out["no cap"] = decide([SD.conductor(quick_token_cap=0)], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    out["daily cap 0"] = decide([SD.conductor(daily_token_cap=0)], fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set())
    out["daily cap exactly fits"] = decide([SD.conductor(daily_token_cap=30000)], fresh_st(), SD.robs(SD.ops_status(T)), T,
                                           busy=set())
    out["daily cap one short"] = decide([SD.conductor(daily_token_cap=29999)], fresh_st(), SD.robs(SD.ops_status(T)), T,
                                        busy=set())
    st = fresh_st(Conductor={"done": {}, "runs": [run("r1", T - 7200, state="done", tokens=190000, day=RL.day_of(T),
                                                      budget=190000)]})
    out["daily cap used up by a run today"] = decide([c], st, SD.robs(SD.ops_status(T)), T, busy=set())
    out["gate holds, once"] = tick([c], fresh_st(), SD.robs(SD.ops_status(T)), T, n=2, busy=set(), gate=GATE_NO)
    return out


@scen
def decide_alarm_reserve_the_days_scheduled_runs():
    out = {}
    t = SD.at_local("07:00")
    op = SD.operations(runs_local=["06:00"], economy_pass_local=None, daily_token_cap=60000, run_token_cap=60000)
    al = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}}
    out["alarm fits exactly"] = decide([op], fresh_st(), SD.robs(SD.ops_status(t, alarms=al)), t, busy=set())
    op2 = dict(op, daily_token_cap=59999)
    out["alarm over the cap waits"] = tick([op2], fresh_st(), SD.robs(SD.ops_status(t, alarms=al)), t, n=2, busy=set())
    return out


@scen
def decide_failure_after_consuming_gives_it_back():
    c = SD.conductor()
    st = fresh_st()
    acts = []

    def act(**kw):
        if kw["do"] == "role_launch":
            raise RuntimeError("act failed")
        acts.append(kw)
    RL.decide_roles({"roles": [c]}, st, SD.robs(SD.ops_status(T)), T, act, set(), None)
    return {"acts": acted(acts), "roles": st["roles"]}


@scen
def decide_exception_without_a_launch_alarms_with_the_roles_item():
    c = SD.conductor()
    ob = SD.robs(SD.ops_status(T))
    ob["account"] = lambda: 1 / 0
    out = [decide([c], fresh_st(), ob, T, busy=set())]
    out.append(decide([{"name": "Bad", "enabled": True, "instructions": "x", "seat": "S", "clone": "c", "model": "m",
                        "ledger_item": "I", "quick_token_cap": "z", "runs_local": ["08:00"]}],
                      fresh_st(), SD.robs(SD.ops_status(T)), T, busy=set()))
    return out


@scen
def slot_blocked_table_and_slots_edges():
    c = SD.conductor(quick_checks_local=["09:00", "13:00", "19:30"], economy_pass_local="13:00", economy_token_cap=5000)
    t = SD.at_local("07:00")
    sl = RL.slots(c, t)
    out = {"slots": sl}
    jobs = []
    for i, (hh, m, _) in enumerate(sl):
        jobs.append({"slot": hh, "first": i == 0, "mode": m})
    jobs.append({"slot": None, "first": False, "mode": "alarm"})
    jobs.append({"slot": "", "first": False, "mode": "quick"})
    for allowed in RL.BAND_SLOTS + ("bogus",):
        out[allowed] = [RL.slot_blocked(allowed, j, c, t) for j in jobs]
    # quick_one with a schedule of nothing but an economy slot
    ce = SD.conductor(quick_checks_local=["13:00"], economy_pass_local="13:00", economy_token_cap=5000)
    out["quick_one, only economy"] = [RL.slot_blocked("quick_one", {"slot": "13:00", "first": True, "mode": "quick"}, ce, t)]
    # weekday filtering
    p = SD.daily(runs_local=["Wed 09:00", "Wed 15:00", "Thu 09:00"])
    out["Wed"] = RL.slots(p, SD.at_local("07:00"))
    out["Thu"] = RL.slots(p, SD.at_local("07:00") + 86400)
    out["no day"] = RL.slots(p, None)
    return out


@scen
def supervise_seat_passes_the_runs_seat_before_the_roles():
    out = []
    for rseat, cseat in (("RS", "CS"), (None, "CS"), ("RS", None)):
        seen = []
        c = SD.conductor(seat=cseat)
        r = run("u1", T - 3600, scope=None, seat=rseat, run_max_s=1800)
        st = {"roles": {"Conductor": {"done": {}, "runs": [r]}}}
        ob = sobs({"u1": "active"}, scope=lambda u, s: (seen.append([u, s]), "sc-new")[1])
        res = supervise([c], st, ob, T)
        out.append({"scope args": seen, "res": res})
    return out


@scen
def supervise_overbudget_when_budget_is_zero():
    c = SD.conductor()
    r = run("u0", T - 60, budget=0)
    r2 = run("u1", T - 60, budget=None)
    st = {"roles": {"Conductor": {"done": {}, "runs": [r, r2]}}}
    ob = sobs({"u0": "inactive", "u1": "inactive"}, {"u0": cli(1, subtype="success"),
                                                       "u1": cli(1, subtype="success")})
    return supervise([c], st, ob, T)


@scen
def supervise_overbudget_repeats_tell_the_conductor():
    c = SD.conductor()
    st = {"roles": {"Conductor": {"done": {}, "runs": [run("u0", T - 60, budget=0)],
                                  "over_at": [T - 8 * 86400, T - 86400, T - 3600]}}}
    return supervise([c], st, sobs({"u0": "inactive"}, {"u0": cli(1, subtype="success")}), T)


def _first_launching_cap(role, band_cfg, t, lo_, hi_, step):
    al = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}}
    for cap in range(lo_, hi_, step):
        r = dict(role, daily_token_cap=cap, throttle_bands=band_cfg)
        res = decide([r], fresh_st(), SD.robs(SD.ops_status(t, alarms=al)), t, busy=set())
        if any(a["do"] == "role_launch" for a in res["acts"]):
            return cap
    return None


@scen
def alarm_reserve_sweeps_the_daily_cap_for_every_band_shape():
    t = SD.at_local("07:00")
    p = SD.operations(after_role=None, runs_local=["08:00", "10:00", "12:00", "14:00"], run_token_cap=40000,
                      quick_token_cap=20000, economy_pass_local="12:00", economy_token_cap=10000)
    shapes = {
        "x1 all": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"}},
        "x1.5 all": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.5, "slots": "all"}},
        "x2 first": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 2.0, "slots": "first"}},
        "x1 last": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "last"}},
        "x1 quick": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "quick"}},
        "x1 quick_one": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "quick_one"}},
        "x1 none": {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "none"}},
    }
    return {name: _first_launching_cap(p, bc, t, 20000, 400000, 1000) for name, bc in shapes.items()}


@scen
def alarm_reserve_edges_one_cap_apart():
    # the sweep above is coarse (1000): pin the exact boundary for the default shape
    t = SD.at_local("07:00")
    p = SD.operations(after_role=None, runs_local=["08:00", "10:00"], economy_pass_local=None, run_token_cap=40000,
                      quick_token_cap=20000)
    bc = {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.5, "slots": "all"}}
    return _first_launching_cap(p, bc, t, 60000, 140000, 1)


# GOLDEN-BEGIN
GOLDEN = {'after_ready_every_reason': {'alarm job': None,
                              'band skipped both': 'every Operations slot in the last 24 h was skipped by its band '
                                                   '(2026-10-28 07:30, 2026-10-27 19:30)',
                              'band skipped then ok': None,
                              'busy': 'an Operations run is still going',
                              'disabled': 'Operations is not enabled',
                              'done': None,
                              'ended': 'the Operations 2026-10-28 07:30 run ended failed',
                              'ended last of two': 'the Operations 2026-10-28 07:30 run ended running',
                              'no after_role': None,
                              'no slots': 'Operations has no scheduled slots to follow',
                              'not run (how)': 'the Operations 2026-10-28 07:30 slot was not run (missed)',
                              'not run yet': 'the Operations 2026-10-28 07:30 run has not run yet'},
 'after_slots_window_is_a_24h_half_open_interval': {'07:59': ['2026-10-27 12:00', '2026-10-27 08:00'],
                                                    '08:00': ['2026-10-28 08:00', '2026-10-27 12:00'],
                                                    '08:01': ['2026-10-28 08:00', '2026-10-27 12:00'],
                                                    '12:00': ['2026-10-28 12:00', '2026-10-28 08:00']},
 'alarm_reserve_edges_one_cap_apart': 100000,
 'alarm_reserve_sweeps_the_daily_cap_for_every_band_shape': {'x1 all': 110000,
                                                             'x1 last': 60000,
                                                             'x1 none': None,
                                                             'x1 quick': 100000,
                                                             'x1 quick_one': None,
                                                             'x1.5 all': 140000,
                                                             'x2 first': 80000},
 'decide_after_role_waits_once_and_follows': [{'acts': [{'account': None,
                                                         'band': 'NONE',
                                                         'blind': {'mode': 'economy',
                                                                   'outcome': 'launched',
                                                                   'role': 'Operations',
                                                                   'unit': 'rm-role-operations-1793174460'},
                                                         'budget': 150000,
                                                         'do': 'role_launch',
                                                         'message': '<message>',
                                                         'mode': 'economy',
                                                         'note': True,
                                                         'role': 'Operations',
                                                         'run_max_s': 1800,
                                                         'seat': 'BENCH',
                                                         'slot': '2026-10-28 07:30',
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'unit': 'rm-role-operations-1793174460',
                                                         'why': 'Operations slot 07:30 local, band NONE, budget '
                                                                '150000 (cap 150000 x 1.0), 0 used today, unit '
                                                                'rm-role-operations-1793174460, model sonnet'},
                                                        {'do': 'role_hold',
                                                         'role': 'Conductor',
                                                         'why': 'Conductor slot 08:00 local waits: runs after a '
                                                                'finished Operations run; an Operations run is still '
                                                                'going'}],
                                               'ledger_blind': None,
                                               'roles': {'Conductor': {'done': {},
                                                                       'runs': [],
                                                                       'waiting': ['2026-10-28 08:00',
                                                                                   'an Operations run is still '
                                                                                   'going']},
                                                         'Operations': {'alarms_seen': [],
                                                                        'done': {'2026-10-28 07:30': 'launch'},
                                                                        'pending_launch': {'alarm_day': None,
                                                                                           'alarm_last_run': None,
                                                                                           'alarms_seen': [],
                                                                                           'done': None,
                                                                                           'had_done': False,
                                                                                           'key': '2026-10-28 07:30',
                                                                                           'mode': 'economy',
                                                                                           'unit': 'rm-role-operations-1793174460'},
                                                                        'runs': []}}},
                                              {'acts': [],
                                               'ledger_blind': None,
                                               'roles': {'Conductor': {'done': {},
                                                                       'runs': [],
                                                                       'waiting': ['2026-10-28 08:00',
                                                                                   'an Operations run is still '
                                                                                   'going']},
                                                         'Operations': {'alarms_seen': [],
                                                                        'done': {'2026-10-28 07:30': 'launch'},
                                                                        'pending_launch': {'alarm_day': None,
                                                                                           'alarm_last_run': None,
                                                                                           'alarms_seen': [],
                                                                                           'done': None,
                                                                                           'had_done': False,
                                                                                           'key': '2026-10-28 07:30',
                                                                                           'mode': 'economy',
                                                                                           'unit': 'rm-role-operations-1793174460'},
                                                                        'runs': []}}}],
 'decide_alarm_daily_limits': {'per_day unused: launches': {'acts': [{'do': 'role_hold',
                                                                      'role': 'Operations',
                                                                      'why': 'Operations slot 07:30 missed (tick '
                                                                             '16260 s late > slot_late_s)'},
                                                                     {'account': None,
                                                                      'band': 'NONE',
                                                                      'blind': {'mode': 'alarm',
                                                                                'outcome': 'launched',
                                                                                'role': 'Operations',
                                                                                'unit': 'rm-role-operations-1793188860'},
                                                                      'budget': 60000,
                                                                      'do': 'role_launch',
                                                                      'message': '<message>',
                                                                      'mode': 'alarm',
                                                                      'note': True,
                                                                      'role': 'Operations',
                                                                      'run_max_s': 1800,
                                                                      'seat': 'BENCH',
                                                                      'slot': 'alarm ITEM_ONE',
                                                                      'ticket': 'ITEM_ONE',
                                                                      'unit': 'rm-role-operations-1793188860',
                                                                      'why': 'Operations ops_watch alarm ITEM_ONE, '
                                                                             'ITEM_TWO, band NONE, budget 60000 (cap '
                                                                             '60000 x 1.0), 0 used today, unit '
                                                                             'rm-role-operations-1793188860, model '
                                                                             'sonnet'}],
                                                            'ledger_blind': None,
                                                            'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                   'keys': {'ITEM_ONE': 1,
                                                                                                            'ITEM_TWO': 1},
                                                                                                   'n': 1},
                                                                                     'alarm_last_run': 1793188860.0,
                                                                                     'alarms_seen': ['ITEM_ONE',
                                                                                                     'ITEM_TWO'],
                                                                                     'done': {'2026-10-28 07:30': 'missed'},
                                                                                     'pending_launch': {'alarm_day': None,
                                                                                                        'alarm_last_run': None,
                                                                                                        'alarms_seen': [],
                                                                                                        'done': None,
                                                                                                        'had_done': False,
                                                                                                        'key': 'alarm '
                                                                                                               'ITEM_ONE',
                                                                                                        'mode': 'alarm',
                                                                                                        'unit': 'rm-role-operations-1793188860'},
                                                                                     'runs': []}}},
                               'per_day used: held once': [{'acts': [{'do': 'role_hold',
                                                                      'role': 'Operations',
                                                                      'why': 'Operations slot 07:30 missed (tick '
                                                                             '16260 s late > slot_late_s)'},
                                                                     {'do': 'role_hold',
                                                                      'role': 'Operations',
                                                                      'why': 'Operations alarm run for ITEM_ONE, '
                                                                             'ITEM_TWO waits: the daily alarm-run '
                                                                             'limit is used '
                                                                             '(alarm_runs_per_alarm_per_day None, '
                                                                             'alarm_runs_per_day 1); the scheduled '
                                                                             'running checks read it'}],
                                                            'ledger_blind': None,
                                                            'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                   'keys': {},
                                                                                                   'n': 1},
                                                                                     'alarm_limit_hold': ['2026-10-28',
                                                                                                          'ITEM_ONE',
                                                                                                          'ITEM_TWO'],
                                                                                     'alarms_seen': [],
                                                                                     'done': {'2026-10-28 07:30': 'missed'},
                                                                                     'runs': []}}},
                                                           {'acts': [],
                                                            'ledger_blind': None,
                                                            'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                   'keys': {},
                                                                                                   'n': 1},
                                                                                     'alarm_limit_hold': ['2026-10-28',
                                                                                                          'ITEM_ONE',
                                                                                                          'ITEM_TWO'],
                                                                                     'alarms_seen': [],
                                                                                     'done': {'2026-10-28 07:30': 'missed'},
                                                                                     'runs': []}}}],
                               'per_key not yet used': {'acts': [{'do': 'role_hold',
                                                                  'role': 'Operations',
                                                                  'why': 'Operations slot 07:30 missed (tick 16260 s '
                                                                         'late > slot_late_s)'},
                                                                 {'account': None,
                                                                  'band': 'NONE',
                                                                  'blind': {'mode': 'alarm',
                                                                            'outcome': 'launched',
                                                                            'role': 'Operations',
                                                                            'unit': 'rm-role-operations-1793188860'},
                                                                  'budget': 60000,
                                                                  'do': 'role_launch',
                                                                  'message': '<message>',
                                                                  'mode': 'alarm',
                                                                  'note': True,
                                                                  'role': 'Operations',
                                                                  'run_max_s': 1800,
                                                                  'seat': 'BENCH',
                                                                  'slot': 'alarm ITEM_ONE',
                                                                  'ticket': 'ITEM_ONE',
                                                                  'unit': 'rm-role-operations-1793188860',
                                                                  'why': 'Operations ops_watch alarm ITEM_ONE, '
                                                                         'ITEM_TWO, band NONE, budget 60000 (cap '
                                                                         '60000 x 1.0), 0 used today, unit '
                                                                         'rm-role-operations-1793188860, model '
                                                                         'sonnet'}],
                                                        'ledger_blind': None,
                                                        'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                               'keys': {'ITEM_ONE': 2,
                                                                                                        'ITEM_TWO': 1},
                                                                                               'n': 2},
                                                                                 'alarm_last_run': 1793188860.0,
                                                                                 'alarms_seen': ['ITEM_ONE',
                                                                                                 'ITEM_TWO'],
                                                                                 'done': {'2026-10-28 07:30': 'missed'},
                                                                                 'pending_launch': {'alarm_day': {'day': '2026-10-28',
                                                                                                                  'keys': {'ITEM_ONE': 1},
                                                                                                                  'n': 1},
                                                                                                    'alarm_last_run': None,
                                                                                                    'alarms_seen': [],
                                                                                                    'done': None,
                                                                                                    'had_done': False,
                                                                                                    'key': 'alarm '
                                                                                                           'ITEM_ONE',
                                                                                                    'mode': 'alarm',
                                                                                                    'unit': 'rm-role-operations-1793188860'},
                                                                                 'runs': []}}},
                               'per_key used for one key': [{'acts': [{'do': 'role_hold',
                                                                       'role': 'Operations',
                                                                       'why': 'Operations slot 07:30 missed (tick '
                                                                              '16260 s late > slot_late_s)'},
                                                                      {'do': 'role_hold',
                                                                       'role': 'Operations',
                                                                       'why': 'Operations alarm run for ITEM_ONE '
                                                                              'waits: the daily alarm-run limit is '
                                                                              'used (alarm_runs_per_alarm_per_day 1, '
                                                                              'alarm_runs_per_day None); the '
                                                                              'scheduled running checks read it'},
                                                                      {'account': None,
                                                                       'band': 'NONE',
                                                                       'blind': {'mode': 'alarm',
                                                                                 'outcome': 'launched',
                                                                                 'role': 'Operations',
                                                                                 'unit': 'rm-role-operations-1793188860'},
                                                                       'budget': 60000,
                                                                       'do': 'role_launch',
                                                                       'message': '<message>',
                                                                       'mode': 'alarm',
                                                                       'note': True,
                                                                       'role': 'Operations',
                                                                       'run_max_s': 1800,
                                                                       'seat': 'BENCH',
                                                                       'slot': 'alarm ITEM_TWO',
                                                                       'ticket': 'ITEM_TWO',
                                                                       'unit': 'rm-role-operations-1793188860',
                                                                       'why': 'Operations ops_watch alarm ITEM_TWO, '
                                                                              'band NONE, budget 60000 (cap 60000 x '
                                                                              '1.0), 0 used today, unit '
                                                                              'rm-role-operations-1793188860, model '
                                                                              'sonnet'}],
                                                             'ledger_blind': None,
                                                             'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                    'keys': {'ITEM_ONE': 1,
                                                                                                             'ITEM_TWO': 1},
                                                                                                    'n': 2},
                                                                                      'alarm_last_run': 1793188860.0,
                                                                                      'alarm_limit_hold': ['2026-10-28',
                                                                                                           'ITEM_ONE'],
                                                                                      'alarms_seen': ['ITEM_TWO'],
                                                                                      'done': {'2026-10-28 07:30': 'missed'},
                                                                                      'pending_launch': {'alarm_day': {'day': '2026-10-28',
                                                                                                                       'keys': {'ITEM_ONE': 1},
                                                                                                                       'n': 1},
                                                                                                         'alarm_last_run': None,
                                                                                                         'alarms_seen': [],
                                                                                                         'done': None,
                                                                                                         'had_done': False,
                                                                                                         'key': 'alarm '
                                                                                                                'ITEM_TWO',
                                                                                                         'mode': 'alarm',
                                                                                                         'unit': 'rm-role-operations-1793188860'},
                                                                                      'runs': []}}},
                                                            {'acts': [],
                                                             'ledger_blind': None,
                                                             'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                    'keys': {'ITEM_ONE': 1,
                                                                                                             'ITEM_TWO': 1},
                                                                                                    'n': 2},
                                                                                      'alarm_last_run': 1793188860.0,
                                                                                      'alarm_limit_hold': ['2026-10-28',
                                                                                                           'ITEM_ONE'],
                                                                                      'alarms_seen': ['ITEM_TWO'],
                                                                                      'done': {'2026-10-28 07:30': 'missed'},
                                                                                      'pending_launch': {'alarm_day': {'day': '2026-10-28',
                                                                                                                       'keys': {'ITEM_ONE': 1},
                                                                                                                       'n': 1},
                                                                                                         'alarm_last_run': None,
                                                                                                         'alarms_seen': [],
                                                                                                         'done': None,
                                                                                                         'had_done': False,
                                                                                                         'key': 'alarm '
                                                                                                                'ITEM_TWO',
                                                                                                         'mode': 'alarm',
                                                                                                         'unit': 'rm-role-operations-1793188860'},
                                                                                      'runs': []}}}],
                               "yesterday's count does not carry": {'acts': [{'do': 'role_hold',
                                                                              'role': 'Operations',
                                                                              'why': 'Operations slot 07:30 missed '
                                                                                     '(tick 16260 s late > '
                                                                                     'slot_late_s)'},
                                                                             {'account': None,
                                                                              'band': 'NONE',
                                                                              'blind': {'mode': 'alarm',
                                                                                        'outcome': 'launched',
                                                                                        'role': 'Operations',
                                                                                        'unit': 'rm-role-operations-1793188860'},
                                                                              'budget': 60000,
                                                                              'do': 'role_launch',
                                                                              'message': '<message>',
                                                                              'mode': 'alarm',
                                                                              'note': True,
                                                                              'role': 'Operations',
                                                                              'run_max_s': 1800,
                                                                              'seat': 'BENCH',
                                                                              'slot': 'alarm ITEM_ONE',
                                                                              'ticket': 'ITEM_ONE',
                                                                              'unit': 'rm-role-operations-1793188860',
                                                                              'why': 'Operations ops_watch alarm '
                                                                                     'ITEM_ONE, ITEM_TWO, band NONE, '
                                                                                     'budget 60000 (cap 60000 x '
                                                                                     '1.0), 0 used today, unit '
                                                                                     'rm-role-operations-1793188860, '
                                                                                     'model sonnet'}],
                                                                    'ledger_blind': None,
                                                                    'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                           'keys': {'ITEM_ONE': 1,
                                                                                                                    'ITEM_TWO': 1},
                                                                                                           'n': 1},
                                                                                             'alarm_last_run': 1793188860.0,
                                                                                             'alarms_seen': ['ITEM_ONE',
                                                                                                             'ITEM_TWO'],
                                                                                             'done': {'2026-10-28 07:30': 'missed'},
                                                                                             'pending_launch': {'alarm_day': {'day': '2000-01-01',
                                                                                                                              'keys': {},
                                                                                                                              'n': 9},
                                                                                                                'alarm_last_run': None,
                                                                                                                'alarms_seen': [],
                                                                                                                'done': None,
                                                                                                                'had_done': False,
                                                                                                                'key': 'alarm '
                                                                                                                       'ITEM_ONE',
                                                                                                                'mode': 'alarm',
                                                                                                                'unit': 'rm-role-operations-1793188860'},
                                                                                             'runs': []}}}},
 'decide_alarm_reserve_the_days_scheduled_runs': {'alarm fits exactly': {'acts': [{'do': 'role_hold',
                                                                                   'role': 'Operations',
                                                                                   'why': 'Operations slot 06:00 '
                                                                                          'missed (tick 3660 s late '
                                                                                          '> slot_late_s)'},
                                                                                  {'account': None,
                                                                                   'band': 'NONE',
                                                                                   'blind': {'mode': 'alarm',
                                                                                             'outcome': 'launched',
                                                                                             'role': 'Operations',
                                                                                             'unit': 'rm-role-operations-1793170860'},
                                                                                   'budget': 60000,
                                                                                   'do': 'role_launch',
                                                                                   'message': '<message>',
                                                                                   'mode': 'alarm',
                                                                                   'note': True,
                                                                                   'role': 'Operations',
                                                                                   'run_max_s': 1800,
                                                                                   'seat': 'BENCH',
                                                                                   'slot': 'alarm ITEM_ONE',
                                                                                   'ticket': 'ITEM_ONE',
                                                                                   'unit': 'rm-role-operations-1793170860',
                                                                                   'why': 'Operations ops_watch '
                                                                                          'alarm ITEM_ONE, band '
                                                                                          'NONE, budget 60000 (cap '
                                                                                          '60000 x 1.0), 0 used '
                                                                                          'today, unit '
                                                                                          'rm-role-operations-1793170860, '
                                                                                          'model sonnet'}],
                                                                         'ledger_blind': None,
                                                                         'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                                'keys': {'ITEM_ONE': 1},
                                                                                                                'n': 1},
                                                                                                  'alarm_last_run': 1793170860.0,
                                                                                                  'alarms_seen': ['ITEM_ONE'],
                                                                                                  'done': {'2026-10-28 06:00': 'missed'},
                                                                                                  'pending_launch': {'alarm_day': None,
                                                                                                                     'alarm_last_run': None,
                                                                                                                     'alarms_seen': [],
                                                                                                                     'done': None,
                                                                                                                     'had_done': False,
                                                                                                                     'key': 'alarm '
                                                                                                                            'ITEM_ONE',
                                                                                                                     'mode': 'alarm',
                                                                                                                     'unit': 'rm-role-operations-1793170860'},
                                                                                                  'runs': []}}},
                                                  'alarm over the cap waits': [{'acts': [{'do': 'role_hold',
                                                                                          'role': 'Operations',
                                                                                          'why': 'Operations slot '
                                                                                                 '06:00 missed (tick '
                                                                                                 '3660 s late > '
                                                                                                 'slot_late_s)'},
                                                                                         {'do': 'role_hold',
                                                                                          'role': 'Operations',
                                                                                          'why': 'Operations '
                                                                                                 'ops_watch alarm '
                                                                                                 'ITEM_ONE waits: '
                                                                                                 "the day's "
                                                                                                 'scheduled run(s) '
                                                                                                 'still to come keep '
                                                                                                 'their share of the '
                                                                                                 'daily cap; it runs '
                                                                                                 'once they leave '
                                                                                                 'room'}],
                                                                                'ledger_blind': None,
                                                                                'roles': {'Operations': {'alarms_seen': [],
                                                                                                         'done': {'2026-10-28 06:00': 'missed'},
                                                                                                         'event_reserve_day': '2026-10-28',
                                                                                                         'runs': []}}},
                                                                               {'acts': [],
                                                                                'ledger_blind': None,
                                                                                'roles': {'Operations': {'alarms_seen': [],
                                                                                                         'done': {'2026-10-28 06:00': 'missed'},
                                                                                                         'event_reserve_day': '2026-10-28',
                                                                                                         'runs': []}}}]},
 'decide_alarm_runs': {'after gap launches': {'acts': [{'do': 'role_hold',
                                                        'role': 'Operations',
                                                        'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                               'slot_late_s)'},
                                                       {'account': None,
                                                        'band': 'NONE',
                                                        'blind': {'mode': 'alarm',
                                                                  'outcome': 'launched',
                                                                  'role': 'Operations',
                                                                  'unit': 'rm-role-operations-1793188860'},
                                                        'budget': 60000,
                                                        'do': 'role_launch',
                                                        'message': '<message>',
                                                        'mode': 'alarm',
                                                        'note': True,
                                                        'role': 'Operations',
                                                        'run_max_s': 1800,
                                                        'seat': 'BENCH',
                                                        'slot': 'alarm ITEM_ONE',
                                                        'ticket': 'ITEM_ONE',
                                                        'unit': 'rm-role-operations-1793188860',
                                                        'why': 'Operations ops_watch alarm ITEM_ONE, alarm:a2, band '
                                                               'NONE, budget 60000 (cap 60000 x 1.0), 0 used today, '
                                                               'unit rm-role-operations-1793188860, model sonnet'}],
                                              'ledger_blind': None,
                                              'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                     'keys': {'ITEM_ONE': 1,
                                                                                              'alarm:a2': 1},
                                                                                     'n': 1},
                                                                       'alarm_last_run': 1793188860.0,
                                                                       'alarms_seen': ['ITEM_ONE', 'alarm:a2'],
                                                                       'done': {'2026-10-28 07:30': 'missed'},
                                                                       'pending_launch': {'alarm_day': None,
                                                                                          'alarm_last_run': 1793183860.0,
                                                                                          'alarms_seen': [],
                                                                                          'done': None,
                                                                                          'had_done': False,
                                                                                          'key': 'alarm ITEM_ONE',
                                                                                          'mode': 'alarm',
                                                                                          'unit': 'rm-role-operations-1793188860'},
                                                                       'runs': []}}},
                       'alarms unreadable': [{'acts': [{'do': 'role_hold',
                                                        'role': 'Operations',
                                                        'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                               'slot_late_s)'},
                                                       {'do': 'role_hold',
                                                        'role': 'Operations',
                                                        'why': 'Operations alarm runs held: ops_watch alarms '
                                                               'unreadable in status.json; none launches until both '
                                                               'read'}],
                                              'ledger_blind': None,
                                              'roles': {'Operations': {'alarm_blind': True,
                                                                       'done': {'2026-10-28 07:30': 'missed'},
                                                                       'runs': []}}},
                                             {'acts': [],
                                              'ledger_blind': None,
                                              'roles': {'Operations': {'alarm_blind': True,
                                                                       'done': {'2026-10-28 07:30': 'missed'},
                                                                       'runs': []}}}],
                       'all seen: nothing': {'acts': [{'do': 'role_hold',
                                                       'role': 'Operations',
                                                       'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                              'slot_late_s)'}],
                                             'ledger_blind': None,
                                             'roles': {'Operations': {'alarms_seen': ['ITEM_ONE', 'alarm:a2'],
                                                                      'done': {'2026-10-28 07:30': 'missed'},
                                                                      'runs': []}}},
                       'blind clears': {'acts': [{'do': 'role_hold',
                                                  'role': 'Operations',
                                                  'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                         'slot_late_s)'},
                                                 {'account': None,
                                                  'band': 'NONE',
                                                  'blind': {'mode': 'alarm',
                                                            'outcome': 'launched',
                                                            'role': 'Operations',
                                                            'unit': 'rm-role-operations-1793188860'},
                                                  'budget': 60000,
                                                  'do': 'role_launch',
                                                  'message': '<message>',
                                                  'mode': 'alarm',
                                                  'note': True,
                                                  'role': 'Operations',
                                                  'run_max_s': 1800,
                                                  'seat': 'BENCH',
                                                  'slot': 'alarm ITEM_ONE',
                                                  'ticket': 'ITEM_ONE',
                                                  'unit': 'rm-role-operations-1793188860',
                                                  'why': 'Operations ops_watch alarm ITEM_ONE, alarm:a2, band NONE, '
                                                         'budget 60000 (cap 60000 x 1.0), 0 used today, unit '
                                                         'rm-role-operations-1793188860, model sonnet'}],
                                        'ledger_blind': None,
                                        'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                               'keys': {'ITEM_ONE': 1, 'alarm:a2': 1},
                                                                               'n': 1},
                                                                 'alarm_last_run': 1793188860.0,
                                                                 'alarms_seen': ['ITEM_ONE', 'alarm:a2'],
                                                                 'done': {'2026-10-28 07:30': 'missed'},
                                                                 'pending_launch': {'alarm_day': None,
                                                                                    'alarm_last_run': None,
                                                                                    'alarms_seen': [],
                                                                                    'done': None,
                                                                                    'had_done': False,
                                                                                    'key': 'alarm ITEM_ONE',
                                                                                    'mode': 'alarm',
                                                                                    'unit': 'rm-role-operations-1793188860'},
                                                                 'runs': []}}},
                       'fresh one launches, stale pruned': {'acts': [{'do': 'role_hold',
                                                                      'role': 'Operations',
                                                                      'why': 'Operations slot 07:30 missed (tick '
                                                                             '16260 s late > slot_late_s)'},
                                                                     {'account': None,
                                                                      'band': 'NONE',
                                                                      'blind': {'mode': 'alarm',
                                                                                'outcome': 'launched',
                                                                                'role': 'Operations',
                                                                                'unit': 'rm-role-operations-1793188860'},
                                                                      'budget': 60000,
                                                                      'do': 'role_launch',
                                                                      'message': '<message>',
                                                                      'mode': 'alarm',
                                                                      'note': True,
                                                                      'role': 'Operations',
                                                                      'run_max_s': 1800,
                                                                      'seat': 'BENCH',
                                                                      'slot': 'alarm alarm:a2',
                                                                      'ticket': 'ROLES_ITEM_X',
                                                                      'unit': 'rm-role-operations-1793188860',
                                                                      'why': 'Operations ops_watch alarm alarm:a2, '
                                                                             'band NONE, budget 60000 (cap 60000 x '
                                                                             '1.0), 0 used today, unit '
                                                                             'rm-role-operations-1793188860, model '
                                                                             'sonnet'}],
                                                            'ledger_blind': None,
                                                            'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                                   'keys': {'alarm:a2': 1},
                                                                                                   'n': 1},
                                                                                     'alarm_last_run': 1793188860.0,
                                                                                     'alarms_seen': ['ITEM_ONE',
                                                                                                     'alarm:a2'],
                                                                                     'done': {'2026-10-28 07:30': 'missed'},
                                                                                     'pending_launch': {'alarm_day': None,
                                                                                                        'alarm_last_run': None,
                                                                                                        'alarms_seen': ['ITEM_ONE'],
                                                                                                        'done': None,
                                                                                                        'had_done': False,
                                                                                                        'key': 'alarm '
                                                                                                               'alarm:a2',
                                                                                                        'mode': 'alarm',
                                                                                                        'unit': 'rm-role-operations-1793188860'},
                                                                                     'runs': []}}},
                       'gap exactly over launches': {'acts': [{'do': 'role_hold',
                                                               'role': 'Operations',
                                                               'why': 'Operations slot 07:30 missed (tick 16260 s '
                                                                      'late > slot_late_s)'},
                                                              {'account': None,
                                                               'band': 'NONE',
                                                               'blind': {'mode': 'alarm',
                                                                         'outcome': 'launched',
                                                                         'role': 'Operations',
                                                                         'unit': 'rm-role-operations-1793188860'},
                                                               'budget': 60000,
                                                               'do': 'role_launch',
                                                               'message': '<message>',
                                                               'mode': 'alarm',
                                                               'note': True,
                                                               'role': 'Operations',
                                                               'run_max_s': 1800,
                                                               'seat': 'BENCH',
                                                               'slot': 'alarm ITEM_ONE',
                                                               'ticket': 'ITEM_ONE',
                                                               'unit': 'rm-role-operations-1793188860',
                                                               'why': 'Operations ops_watch alarm ITEM_ONE, '
                                                                      'alarm:a2, band NONE, budget 60000 (cap 60000 '
                                                                      'x 1.0), 0 used today, unit '
                                                                      'rm-role-operations-1793188860, model sonnet'}],
                                                     'ledger_blind': None,
                                                     'roles': {'Operations': {'alarm_day': {'day': '2026-10-28',
                                                                                            'keys': {'ITEM_ONE': 1,
                                                                                                     'alarm:a2': 1},
                                                                                            'n': 1},
                                                                              'alarm_last_run': 1793188860.0,
                                                                              'alarms_seen': ['ITEM_ONE', 'alarm:a2'],
                                                                              'done': {'2026-10-28 07:30': 'missed'},
                                                                              'pending_launch': {'alarm_day': None,
                                                                                                 'alarm_last_run': 1793187860.0,
                                                                                                 'alarms_seen': [],
                                                                                                 'done': None,
                                                                                                 'had_done': False,
                                                                                                 'key': 'alarm '
                                                                                                        'ITEM_ONE',
                                                                                                 'mode': 'alarm',
                                                                                                 'unit': 'rm-role-operations-1793188860'},
                                                                              'runs': []}}},
                       'gap held': [{'acts': [{'do': 'role_hold',
                                               'role': 'Operations',
                                               'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                      'slot_late_s)'},
                                              {'do': 'role_hold',
                                               'role': 'Operations',
                                               'why': 'Operations alarm run for ITEM_ONE, alarm:a2 waits: the last '
                                                      'alarm run was 999 s ago (alarm_run_gap_s 1000)'}],
                                     'ledger_blind': None,
                                     'roles': {'Operations': {'alarm_gap_hold': ['ITEM_ONE', 'alarm:a2'],
                                                              'alarm_last_run': 1793187861.0,
                                                              'alarms_seen': [],
                                                              'done': {'2026-10-28 07:30': 'missed'},
                                                              'runs': []}}},
                                    {'acts': [],
                                     'ledger_blind': None,
                                     'roles': {'Operations': {'alarm_gap_hold': ['ITEM_ONE', 'alarm:a2'],
                                                              'alarm_last_run': 1793187861.0,
                                                              'alarms_seen': [],
                                                              'done': {'2026-10-28 07:30': 'missed'},
                                                              'runs': []}}}],
                       'status unmeasured': [{'acts': [{'do': 'role_hold',
                                                        'role': 'Operations',
                                                        'why': 'Operations slot 07:30 missed (tick 16260 s late > '
                                                               'slot_late_s)'},
                                                       {'do': 'role_hold',
                                                        'role': 'Operations',
                                                        'why': 'Operations alarm runs held: ops_watch status.json '
                                                               'missing or unreadable; none launches until both '
                                                               'read'}],
                                              'ledger_blind': None,
                                              'roles': {'Operations': {'alarm_blind': True,
                                                                       'done': {'2026-10-28 07:30': 'missed'},
                                                                       'runs': []}}},
                                             {'acts': [],
                                              'ledger_blind': None,
                                              'roles': {'Operations': {'alarm_blind': True,
                                                                       'done': {'2026-10-28 07:30': 'missed'},
                                                                       'runs': []}}}]},
 'decide_blocked_by_reading_band_and_caps': {'AMBER: second slot held': [{'acts': [{'do': 'role_hold',
                                                                                    'role': 'Conductor',
                                                                                    'why': 'Conductor slot 08:00 '
                                                                                           'missed (tick 43260 s '
                                                                                           'late > slot_late_s)'},
                                                                                   {'do': 'role_hold',
                                                                                    'role': 'Conductor',
                                                                                    'why': 'Conductor slot 20:00 '
                                                                                           'local not run: band '
                                                                                           'AMBER runs first '
                                                                                           'scheduled slots (runway '
                                                                                           '1.20 MEASURED, week left '
                                                                                           '40%)'}],
                                                                          'ledger_blind': None,
                                                                          'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'missed',
                                                                                                           '2026-10-28 20:00': 'band '
                                                                                                                               'AMBER'},
                                                                                                  'runs': []}}}],
                                             'band FLOOR blocks the slot': {'acts': [{'do': 'role_hold',
                                                                                      'role': 'Conductor',
                                                                                      'why': 'Conductor slot 08:00 '
                                                                                             'local not run: band '
                                                                                             'FLOOR runs none '
                                                                                             'scheduled slots '
                                                                                             '(runway 2.00 MEASURED, '
                                                                                             'week left 5%)'}],
                                                                            'ledger_blind': None,
                                                                            'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'band '
                                                                                                                                 'FLOOR'},
                                                                                                    'runs': []}}},
                                             'daily cap 0': {'acts': [{'do': 'alarm',
                                                                       'kind': 'role:Conductor:cap',
                                                                       'note': True,
                                                                       'ticket': 'ROLES_ITEM_X',
                                                                       'why': 'Conductor slot 08:00 local REFUSED: '
                                                                              'daily_token_cap 0, 0 used today + '
                                                                              '30000 budget'}],
                                                             'ledger_blind': None,
                                                             'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'daily '
                                                                                                                  'cap'},
                                                                                     'runs': []}}},
                                             'daily cap exactly fits': {'acts': [{'account': None,
                                                                                  'band': 'GREEN',
                                                                                  'blind': {'mode': 'quick',
                                                                                            'outcome': 'launched',
                                                                                            'role': 'Conductor',
                                                                                            'unit': 'rm-role-conductor-1793174460'},
                                                                                  'budget': 30000,
                                                                                  'do': 'role_launch',
                                                                                  'message': '<message>',
                                                                                  'mode': 'quick',
                                                                                  'note': True,
                                                                                  'role': 'Conductor',
                                                                                  'run_max_s': 1800,
                                                                                  'seat': 'BENCH',
                                                                                  'slot': '2026-10-28 08:00',
                                                                                  'ticket': 'ROLES_ITEM_X',
                                                                                  'unit': 'rm-role-conductor-1793174460',
                                                                                  'why': 'Conductor slot 08:00 '
                                                                                         'local, band GREEN, budget '
                                                                                         '30000 (cap 30000 x 1.0), 0 '
                                                                                         'used today, unit '
                                                                                         'rm-role-conductor-1793174460, '
                                                                                         'model sonnet'}],
                                                                        'ledger_blind': None,
                                                                        'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                                                'pending_launch': {'alarm_day': None,
                                                                                                                   'alarm_last_run': None,
                                                                                                                   'alarms_seen': None,
                                                                                                                   'done': None,
                                                                                                                   'had_done': False,
                                                                                                                   'key': '2026-10-28 '
                                                                                                                          '08:00',
                                                                                                                   'mode': 'quick',
                                                                                                                   'unit': 'rm-role-conductor-1793174460'},
                                                                                                'runs': []}}},
                                             'daily cap one short': {'acts': [{'do': 'alarm',
                                                                               'kind': 'role:Conductor:cap',
                                                                               'note': True,
                                                                               'ticket': 'ROLES_ITEM_X',
                                                                               'why': 'Conductor slot 08:00 local '
                                                                                      'REFUSED: daily_token_cap '
                                                                                      '29999, 0 used today + 30000 '
                                                                                      'budget'}],
                                                                     'ledger_blind': None,
                                                                     'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'daily '
                                                                                                                          'cap'},
                                                                                             'runs': []}}},
                                             'daily cap used up by a run today': {'acts': [{'do': 'alarm',
                                                                                            'kind': 'role:Conductor:cap',
                                                                                            'note': True,
                                                                                            'ticket': 'ROLES_ITEM_X',
                                                                                            'why': 'Conductor slot '
                                                                                                   '08:00 local '
                                                                                                   'REFUSED: '
                                                                                                   'daily_token_cap '
                                                                                                   '200000, 190000 '
                                                                                                   'used today + '
                                                                                                   '30000 budget'}],
                                                                                  'ledger_blind': None,
                                                                                  'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'daily '
                                                                                                                                       'cap'},
                                                                                                          'runs': [{'at': 1793167260.0,
                                                                                                                    'budget': 190000,
                                                                                                                    'day': '2026-10-28',
                                                                                                                    'item': 'ROLES_ITEM_X',
                                                                                                                    'mode': 'quick',
                                                                                                                    'run_max_s': 1800,
                                                                                                                    'scope': 'sc-r1',
                                                                                                                    'seat': 'BENCH',
                                                                                                                    'state': 'done',
                                                                                                                    'tokens': 190000,
                                                                                                                    'unit': 'r1'}]}}},
                                             'gate holds, once': [{'acts': [{'do': 'role_hold',
                                                                             'role': 'Conductor',
                                                                             'why': 'Conductor slot 08:00 local held '
                                                                                    'for the account switch: '
                                                                                    'switching to acctB'}],
                                                                   'ledger_blind': None,
                                                                   'roles': {'Conductor': {'account_hold': '2026-10-28 '
                                                                                                           '08:00',
                                                                                           'done': {},
                                                                                           'runs': []}}},
                                                                  {'acts': [],
                                                                   'ledger_blind': None,
                                                                   'roles': {'Conductor': {'account_hold': '2026-10-28 '
                                                                                                           '08:00',
                                                                                           'done': {},
                                                                                           'runs': []}}}],
                                             'no cap': {'acts': [{'conductor_log': True,
                                                                  'do': 'alarm',
                                                                  'kind': 'role:Conductor',
                                                                  'note': True,
                                                                  'why': 'role Conductor has no token cap for '
                                                                         'quick'}],
                                                        'ledger_blind': None,
                                                        'roles': {'Conductor': {'done': {}, 'runs': []}}},
                                             'ops unreadable': {'acts': [{'do': 'alarm',
                                                                          'kind': 'role:Conductor:ops',
                                                                          'note': True,
                                                                          'ticket': 'ROLES_ITEM_X',
                                                                          'why': 'Conductor slot 08:00 local '
                                                                                 'REFUSED: ops_watch status.json '
                                                                                 'missing or unreadable'}],
                                                                'ledger_blind': None,
                                                                'roles': {'Conductor': {'done': {}, 'runs': []}}}},
 'decide_busy_role_waits_and_is_not_marked': {'acts': [],
                                              'ledger_blind': None,
                                              'roles': {'Conductor': {'done': {}, 'runs': []}}},
 'decide_default_busy_is_the_supervised_set': {'acts': [],
                                               'ledger_blind': None,
                                               'roles': {'Conductor': {'done': {},
                                                                       'runs': [{'at': 1793174430.0,
                                                                                 'budget': 1000,
                                                                                 'day': '2026-10-28',
                                                                                 'item': 'ROLES_ITEM_X',
                                                                                 'mode': 'quick',
                                                                                 'run_max_s': 1800,
                                                                                 'scope': 'sc',
                                                                                 'seat': 'BENCH',
                                                                                 'state': 'running',
                                                                                 'unit': 'live'}]}}},
 'decide_done_retention': ['2026-10-26 09:00', '2026-10-27 09:00', '2026-10-28 09:00'],
 'decide_exception_without_a_launch_alarms_with_the_roles_item': [{'acts': [{'do': 'alarm',
                                                                             'kind': 'role:Conductor:schedule',
                                                                             'note': True,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'why': 'role Conductor NOT RUN this '
                                                                                    'tick: deciding it raised '
                                                                                    'ZeroDivisionError: division by '
                                                                                    'zero'}],
                                                                   'ledger_blind': None,
                                                                   'roles': {'Conductor': {'done': {}, 'runs': []}}},
                                                                  {'acts': [{'blind': {'mode': None,
                                                                                       'outcome': 'schedule_unreadable',
                                                                                       'role': 'Bad',
                                                                                       'unit': None},
                                                                             'do': 'alarm',
                                                                             'kind': 'role:Bad:schedule',
                                                                             'note': True,
                                                                             'ticket': 'I',
                                                                             'why': 'role Bad NOT RUN: its schedule '
                                                                                    'entry is unreadable: '
                                                                                    "quick_token_cap 'z' is not a "
                                                                                    'number >= 0'}],
                                                                   'ledger_blind': None,
                                                                   'roles': {'Bad': {'done': {}, 'runs': []}}}],
 'decide_failure_after_consuming_gives_it_back': {'acts': [{'do': 'alarm',
                                                            'kind': 'role:Conductor:schedule',
                                                            'note': True,
                                                            'ticket': 'ROLES_ITEM_X',
                                                            'why': 'role Conductor NOT RUN this tick: deciding it '
                                                                   'raised RuntimeError: act failed'}],
                                                  'roles': {'Conductor': {'done': {}, 'runs': []}}},
 'decide_launch_golden_with_and_without_account': [{'acts': [{'account': 'acctA',
                                                              'band': 'GREEN',
                                                              'blind': {'mode': 'quick',
                                                                        'outcome': 'launched',
                                                                        'role': 'Conductor',
                                                                        'unit': 'rm-role-conductor-1793174460'},
                                                              'budget': 30000,
                                                              'do': 'role_launch',
                                                              'message': '<message>',
                                                              'mode': 'quick',
                                                              'note': True,
                                                              'role': 'Conductor',
                                                              'run_max_s': 1800,
                                                              'seat': 'BENCH',
                                                              'slot': '2026-10-28 08:00',
                                                              'ticket': 'ROLES_ITEM_X',
                                                              'unit': 'rm-role-conductor-1793174460',
                                                              'why': 'Conductor slot 08:00 local, band GREEN, budget '
                                                                     '30000 (cap 30000 x 1.0), 0 used today, unit '
                                                                     'rm-role-conductor-1793174460, model sonnet, '
                                                                     'account acctA (ready)'}],
                                                    'ledger_blind': None,
                                                    'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                            'pending_launch': {'alarm_day': None,
                                                                                               'alarm_last_run': None,
                                                                                               'alarms_seen': None,
                                                                                               'done': None,
                                                                                               'had_done': False,
                                                                                               'key': '2026-10-28 '
                                                                                                      '08:00',
                                                                                               'mode': 'quick',
                                                                                               'unit': 'rm-role-conductor-1793174460'},
                                                                            'runs': []}}},
                                                   {'acts': [{'account': None,
                                                              'band': 'AMBER',
                                                              'blind': {'mode': 'quick',
                                                                        'outcome': 'launched',
                                                                        'role': 'Conductor',
                                                                        'unit': 'rm-role-conductor-1793174460'},
                                                              'budget': 18000,
                                                              'do': 'role_launch',
                                                              'message': '<message>',
                                                              'mode': 'quick',
                                                              'note': True,
                                                              'role': 'Conductor',
                                                              'run_max_s': 1800,
                                                              'seat': 'BENCH',
                                                              'slot': '2026-10-28 08:00',
                                                              'ticket': 'ROLES_ITEM_X',
                                                              'unit': 'rm-role-conductor-1793174460',
                                                              'why': 'Conductor slot 08:00 local, band AMBER, budget '
                                                                     '18000 (cap 30000 x 0.6), 0 used today, unit '
                                                                     'rm-role-conductor-1793174460, model sonnet'}],
                                                    'ledger_blind': None,
                                                    'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                            'pending_launch': {'alarm_day': None,
                                                                                               'alarm_last_run': None,
                                                                                               'alarms_seen': None,
                                                                                               'done': None,
                                                                                               'had_done': False,
                                                                                               'key': '2026-10-28 '
                                                                                                      '08:00',
                                                                                               'mode': 'quick',
                                                                                               'unit': 'rm-role-conductor-1793174460'},
                                                                            'runs': []}}}],
 'decide_off_switch_and_window': {'no off_file: asked with empty path': [''],
                                  'off path': ['<TMP>/CONDUCTOR_OFF'],
                                  'off reason': {'acts': [{'do': 'role_hold',
                                                           'role': 'Conductor',
                                                           'why': 'Conductor slot 08:00 local skipped: off switch '
                                                                  '<TMP>/CONDUCTOR_OFF (owner: stop)'}],
                                                 'ledger_blind': None,
                                                 'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'off'},
                                                                         'runs': []}}},
                                  'off without an off_file': {'acts': [{'account': None,
                                                                        'band': 'GREEN',
                                                                        'blind': {'mode': 'quick',
                                                                                  'outcome': 'launched',
                                                                                  'role': 'Conductor',
                                                                                  'unit': 'rm-role-conductor-1793174460'},
                                                                        'budget': 30000,
                                                                        'do': 'role_launch',
                                                                        'message': '<message>',
                                                                        'mode': 'quick',
                                                                        'note': True,
                                                                        'role': 'Conductor',
                                                                        'run_max_s': 1800,
                                                                        'seat': 'BENCH',
                                                                        'slot': '2026-10-28 08:00',
                                                                        'ticket': 'ROLES_ITEM_X',
                                                                        'unit': 'rm-role-conductor-1793174460',
                                                                        'why': 'Conductor slot 08:00 local, band '
                                                                               'GREEN, budget 30000 (cap 30000 x '
                                                                               '1.0), 0 used today, unit '
                                                                               'rm-role-conductor-1793174460, model '
                                                                               'sonnet'}],
                                                              'ledger_blind': None,
                                                              'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                                      'pending_launch': {'alarm_day': None,
                                                                                                         'alarm_last_run': None,
                                                                                                         'alarms_seen': None,
                                                                                                         'done': None,
                                                                                                         'had_done': False,
                                                                                                         'key': '2026-10-28 '
                                                                                                                '08:00',
                                                                                                         'mode': 'quick',
                                                                                                         'unit': 'rm-role-conductor-1793174460'},
                                                                                      'runs': []}}},
                                  'off, no reason': {'acts': [{'do': 'role_hold',
                                                               'role': 'Conductor',
                                                               'why': 'Conductor slot 08:00 local skipped: off '
                                                                      'switch <TMP>/CONDUCTOR_OFF (no reason '
                                                                      'given)'}],
                                                     'ledger_blind': None,
                                                     'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'off'},
                                                                             'runs': []}}},
                                  'window gone clears hold': {'acts': [{'account': None,
                                                                        'band': 'GREEN',
                                                                        'blind': {'mode': 'quick',
                                                                                  'outcome': 'launched',
                                                                                  'role': 'Conductor',
                                                                                  'unit': 'rm-role-conductor-1793174460'},
                                                                        'budget': 30000,
                                                                        'do': 'role_launch',
                                                                        'message': '<message>',
                                                                        'mode': 'quick',
                                                                        'note': True,
                                                                        'role': 'Conductor',
                                                                        'run_max_s': 1800,
                                                                        'seat': 'BENCH',
                                                                        'slot': '2026-10-28 08:00',
                                                                        'ticket': 'ROLES_ITEM_X',
                                                                        'unit': 'rm-role-conductor-1793174460',
                                                                        'why': 'Conductor slot 08:00 local, band '
                                                                               'GREEN, budget 30000 (cap 30000 x '
                                                                               '1.0), 0 used today, unit '
                                                                               'rm-role-conductor-1793174460, model '
                                                                               'sonnet'}],
                                                              'ledger_blind': None,
                                                              'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                                      'pending_launch': {'alarm_day': None,
                                                                                                         'alarm_last_run': None,
                                                                                                         'alarms_seen': None,
                                                                                                         'done': None,
                                                                                                         'had_done': False,
                                                                                                         'key': '2026-10-28 '
                                                                                                                '08:00',
                                                                                                         'mode': 'quick',
                                                                                                         'unit': 'rm-role-conductor-1793174460'},
                                                                                      'runs': []}}},
                                  'window live': [{'acts': [{'do': 'role_hold',
                                                             'role': 'Conductor',
                                                             'why': 'Conductor slot 08:00 local not launched: '
                                                                    'conductor window live (window found; the window '
                                                                    'does the check)'}],
                                                   'ledger_blind': None,
                                                   'roles': {'Conductor': {'done': {},
                                                                           'runs': [],
                                                                           'window_hold': '2026-10-28 08:00'}}},
                                                  {'acts': [],
                                                   'ledger_blind': None,
                                                   'roles': {'Conductor': {'done': {},
                                                                           'runs': [],
                                                                           'window_hold': '2026-10-28 08:00'}}}],
                                  'window live asked': ['Conductor RC', 'Conductor RC'],
                                  'window not live': [{'acts': [{'account': None,
                                                                 'band': 'GREEN',
                                                                 'blind': {'mode': 'quick',
                                                                           'outcome': 'launched',
                                                                           'role': 'Conductor',
                                                                           'unit': 'rm-role-conductor-1793174460'},
                                                                 'budget': 30000,
                                                                 'do': 'role_launch',
                                                                 'message': '<message>',
                                                                 'mode': 'quick',
                                                                 'note': True,
                                                                 'role': 'Conductor',
                                                                 'run_max_s': 1800,
                                                                 'seat': 'BENCH',
                                                                 'slot': '2026-10-28 08:00',
                                                                 'ticket': 'ROLES_ITEM_X',
                                                                 'unit': 'rm-role-conductor-1793174460',
                                                                 'why': 'Conductor slot 08:00 local, band GREEN, '
                                                                        'budget 30000 (cap 30000 x 1.0), 0 used '
                                                                        'today, unit rm-role-conductor-1793174460, '
                                                                        'model sonnet'}],
                                                       'ledger_blind': None,
                                                       'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                               'pending_launch': {'alarm_day': None,
                                                                                                  'alarm_last_run': None,
                                                                                                  'alarms_seen': None,
                                                                                                  'done': None,
                                                                                                  'had_done': False,
                                                                                                  'key': '2026-10-28 '
                                                                                                         '08:00',
                                                                                                  'mode': 'quick',
                                                                                                  'unit': 'rm-role-conductor-1793174460'},
                                                                               'runs': []}}},
                                                      {'acts': [],
                                                       'ledger_blind': None,
                                                       'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                               'pending_launch': {'alarm_day': None,
                                                                                                  'alarm_last_run': None,
                                                                                                  'alarms_seen': None,
                                                                                                  'done': None,
                                                                                                  'had_done': False,
                                                                                                  'key': '2026-10-28 '
                                                                                                         '08:00',
                                                                                                  'mode': 'quick',
                                                                                                  'unit': 'rm-role-conductor-1793174460'},
                                                                               'runs': []}}}],
                                  'window not live asked': ['Conductor RC'],
                                  'window unmeasured': [{'acts': [{'do': 'role_hold',
                                                                   'role': 'Conductor',
                                                                   'why': 'Conductor slot 08:00 local not launched: '
                                                                          'window UNMEASURED (enumeration failed)'}],
                                                         'ledger_blind': None,
                                                         'roles': {'Conductor': {'done': {},
                                                                                 'runs': [],
                                                                                 'window_hold': '2026-10-28 08:00'}}},
                                                        {'acts': [],
                                                         'ledger_blind': None,
                                                         'roles': {'Conductor': {'done': {},
                                                                                 'runs': [],
                                                                                 'window_hold': '2026-10-28 '
                                                                                                '08:00'}}}],
                                  'window unmeasured asked': ['Conductor RC', 'Conductor RC']},
 'decide_role_entries_and_schedule_errors': {'bad slot_late_s': {'acts': [{'blind': {'mode': None,
                                                                                     'outcome': 'schedule_unreadable',
                                                                                     'role': 'Conductor',
                                                                                     'unit': None},
                                                                           'do': 'alarm',
                                                                           'kind': 'role:Conductor:schedule',
                                                                           'note': True,
                                                                           'ticket': 'ROLES_ITEM_X',
                                                                           'why': 'role Conductor NOT RUN: its '
                                                                                  'schedule entry is unreadable: '
                                                                                  'slot_late_s 0 is not a number > '
                                                                                  '0'}],
                                                                 'ledger_blind': None,
                                                                 'roles': {'Conductor': {'done': {}, 'runs': []}}},
                                             'disabled role': {'acts': [], 'ledger_blind': None, 'roles': {}},
                                             'missing launch keys': {'acts': [{'conductor_log': True,
                                                                               'do': 'alarm',
                                                                               'kind': 'role:Nobody',
                                                                               'note': True,
                                                                               'why': 'role Nobody is enabled but '
                                                                                      'cannot be launched: no '
                                                                                      'instructions, clone, model, '
                                                                                      'ledger_item in the schedule'}],
                                                                     'ledger_blind': None,
                                                                     'roles': {}},
                                             'non-mapping entries': {'acts': [{'do': 'alarm',
                                                                               'kind': 'role:schedule',
                                                                               'note': True,
                                                                               'why': '2 roles entr(y/ies) in the '
                                                                                      'schedule are not mappings '
                                                                                      '(str, int): skipped; the '
                                                                                      'other roles are decided'}],
                                                                     'ledger_blind': None,
                                                                     'roles': {}},
                                             'parent disabled': {'acts': [{'blind': {'mode': None,
                                                                                     'outcome': 'after_disabled',
                                                                                     'role': 'Conductor',
                                                                                     'unit': None},
                                                                           'do': 'alarm',
                                                                           'kind': 'role:Conductor:after',
                                                                           'note': True,
                                                                           'ticket': 'ROLES_ITEM_X',
                                                                           'why': 'role Conductor runs only after a '
                                                                                  'Operations run, and Operations is '
                                                                                  'not enabled: its scheduled checks '
                                                                                  'will not run'},
                                                                          {'do': 'role_hold',
                                                                           'role': 'Conductor',
                                                                           'why': 'Conductor slot 08:00 local waits: '
                                                                                  'runs after a finished Operations '
                                                                                  'run; Operations is not enabled'}],
                                                                 'ledger_blind': None,
                                                                 'roles': {'Conductor': {'done': {},
                                                                                         'runs': [],
                                                                                         'waiting': ['2026-10-28 '
                                                                                                     '08:00',
                                                                                                     'Operations is '
                                                                                                     'not '
                                                                                                     'enabled']}}},
                                             'parent slots unreadable': {'acts': [{'blind': {'mode': None,
                                                                                             'outcome': 'schedule_unreadable',
                                                                                             'role': 'Operations',
                                                                                             'unit': None},
                                                                                   'do': 'alarm',
                                                                                   'kind': 'role:Operations:schedule',
                                                                                   'note': True,
                                                                                   'ticket': 'ROLES_ITEM_X',
                                                                                   'why': 'role Operations NOT RUN: '
                                                                                          'its schedule entry is '
                                                                                          "unreadable: slot 'Wdy "
                                                                                          "07:30': weekday 'Wdy' is "
                                                                                          'not one of '
                                                                                          'Mon,Tue,Wed,Thu,Fri,Sat,Sun'},
                                                                                  {'blind': {'mode': None,
                                                                                             'outcome': 'schedule_unreadable',
                                                                                             'role': 'Conductor',
                                                                                             'unit': None},
                                                                                   'do': 'alarm',
                                                                                   'kind': 'role:Conductor:schedule',
                                                                                   'note': True,
                                                                                   'ticket': 'ROLES_ITEM_X',
                                                                                   'why': 'role Conductor NOT RUN: '
                                                                                          'its schedule entry is '
                                                                                          "unreadable: slot 'Wdy "
                                                                                          "07:30': weekday 'Wdy' is "
                                                                                          'not one of '
                                                                                          'Mon,Tue,Wed,Thu,Fri,Sat,Sun'}],
                                                                         'ledger_blind': None,
                                                                         'roles': {'Conductor': {'done': {},
                                                                                                 'runs': []},
                                                                                   'Operations': {'done': {},
                                                                                                  'runs': []}}},
                                             'parent unknown': {'acts': [{'blind': {'mode': None,
                                                                                    'outcome': 'after_disabled',
                                                                                    'role': 'Conductor',
                                                                                    'unit': None},
                                                                          'do': 'alarm',
                                                                          'kind': 'role:Conductor:after',
                                                                          'note': True,
                                                                          'ticket': 'ROLES_ITEM_X',
                                                                          'why': 'role Conductor runs only after a '
                                                                                 'Operations run, and Operations is '
                                                                                 'not enabled: its scheduled checks '
                                                                                 'will not run'},
                                                                         {'do': 'role_hold',
                                                                          'role': 'Conductor',
                                                                          'why': 'Conductor slot 08:00 local waits: '
                                                                                 'runs after a finished Operations '
                                                                                 'run; Operations is not enabled'}],
                                                                'ledger_blind': None,
                                                                'roles': {'Conductor': {'done': {},
                                                                                        'runs': [],
                                                                                        'waiting': ['2026-10-28 '
                                                                                                    '08:00',
                                                                                                    'Operations is '
                                                                                                    'not '
                                                                                                    'enabled']}}}},
 'decide_slot_timing_edges': {'before': {'acts': [],
                                         'ledger_blind': None,
                                         'roles': {'Conductor': {'done': {}, 'runs': []}}},
                              'exact': {'acts': [{'account': None,
                                                  'band': 'GREEN',
                                                  'blind': {'mode': 'quick',
                                                            'outcome': 'launched',
                                                            'role': 'Conductor',
                                                            'unit': 'rm-role-conductor-1793174400'},
                                                  'budget': 30000,
                                                  'do': 'role_launch',
                                                  'message': '<message>',
                                                  'mode': 'quick',
                                                  'note': True,
                                                  'role': 'Conductor',
                                                  'run_max_s': 1800,
                                                  'seat': 'BENCH',
                                                  'slot': '2026-10-28 08:00',
                                                  'ticket': 'ROLES_ITEM_X',
                                                  'unit': 'rm-role-conductor-1793174400',
                                                  'why': 'Conductor slot 08:00 local, band GREEN, budget 30000 (cap '
                                                         '30000 x 1.0), 0 used today, unit '
                                                         'rm-role-conductor-1793174400, model sonnet'}],
                                        'ledger_blind': None,
                                        'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                'pending_launch': {'alarm_day': None,
                                                                                   'alarm_last_run': None,
                                                                                   'alarms_seen': None,
                                                                                   'done': None,
                                                                                   'had_done': False,
                                                                                   'key': '2026-10-28 08:00',
                                                                                   'mode': 'quick',
                                                                                   'unit': 'rm-role-conductor-1793174400'},
                                                                'runs': []}}},
                              'late edge': {'acts': [{'account': None,
                                                      'band': 'GREEN',
                                                      'blind': {'mode': 'quick',
                                                                'outcome': 'launched',
                                                                'role': 'Conductor',
                                                                'unit': 'rm-role-conductor-1793175000'},
                                                      'budget': 30000,
                                                      'do': 'role_launch',
                                                      'message': '<message>',
                                                      'mode': 'quick',
                                                      'note': True,
                                                      'role': 'Conductor',
                                                      'run_max_s': 1800,
                                                      'seat': 'BENCH',
                                                      'slot': '2026-10-28 08:00',
                                                      'ticket': 'ROLES_ITEM_X',
                                                      'unit': 'rm-role-conductor-1793175000',
                                                      'why': 'Conductor slot 08:00 local, band GREEN, budget 30000 '
                                                             '(cap 30000 x 1.0), 0 used today, unit '
                                                             'rm-role-conductor-1793175000, model sonnet'}],
                                            'ledger_blind': None,
                                            'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'launch'},
                                                                    'pending_launch': {'alarm_day': None,
                                                                                       'alarm_last_run': None,
                                                                                       'alarms_seen': None,
                                                                                       'done': None,
                                                                                       'had_done': False,
                                                                                       'key': '2026-10-28 08:00',
                                                                                       'mode': 'quick',
                                                                                       'unit': 'rm-role-conductor-1793175000'},
                                                                    'runs': []}}},
                              'missed': {'acts': [{'do': 'role_hold',
                                                   'role': 'Conductor',
                                                   'why': 'Conductor slot 08:00 missed (tick 601 s late > '
                                                          'slot_late_s)'}],
                                         'ledger_blind': None,
                                         'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'missed'},
                                                                 'runs': []}}},
                              'missed after waiting': {'acts': [{'account': None,
                                                                 'band': 'NONE',
                                                                 'blind': {'mode': 'economy',
                                                                           'outcome': 'launched',
                                                                           'role': 'Operations',
                                                                           'unit': 'rm-role-operations-1793175100'},
                                                                 'budget': 150000,
                                                                 'do': 'role_launch',
                                                                 'message': '<message>',
                                                                 'mode': 'economy',
                                                                 'note': True,
                                                                 'role': 'Operations',
                                                                 'run_max_s': 1800,
                                                                 'seat': 'BENCH',
                                                                 'slot': '2026-10-28 07:30',
                                                                 'ticket': 'ROLES_ITEM_X',
                                                                 'unit': 'rm-role-operations-1793175100',
                                                                 'why': 'Operations slot 07:30 local, band NONE, '
                                                                        'budget 150000 (cap 150000 x 1.0), 0 used '
                                                                        'today, unit rm-role-operations-1793175100, '
                                                                        'model sonnet'},
                                                                {'do': 'role_hold',
                                                                 'role': 'Conductor',
                                                                 'why': 'Conductor slot 08:00 missed (tick 700 s '
                                                                        'late > slot_late_s); it waited: the '
                                                                        'Operations x'}],
                                                       'ledger_blind': None,
                                                       'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'missed'},
                                                                               'runs': [],
                                                                               'waiting': ['2026-10-28 08:00',
                                                                                           'the Operations x']},
                                                                 'Operations': {'alarms_seen': [],
                                                                                'done': {'2026-10-28 07:30': 'launch'},
                                                                                'pending_launch': {'alarm_day': None,
                                                                                                   'alarm_last_run': None,
                                                                                                   'alarms_seen': [],
                                                                                                   'done': None,
                                                                                                   'had_done': False,
                                                                                                   'key': '2026-10-28 '
                                                                                                          '07:30',
                                                                                                   'mode': 'economy',
                                                                                                   'unit': 'rm-role-operations-1793175100'},
                                                                                'runs': []}}},
                              'missed, waiting for another slot': {'acts': [{'account': None,
                                                                             'band': 'NONE',
                                                                             'blind': {'mode': 'economy',
                                                                                       'outcome': 'launched',
                                                                                       'role': 'Operations',
                                                                                       'unit': 'rm-role-operations-1793175100'},
                                                                             'budget': 150000,
                                                                             'do': 'role_launch',
                                                                             'message': '<message>',
                                                                             'mode': 'economy',
                                                                             'note': True,
                                                                             'role': 'Operations',
                                                                             'run_max_s': 1800,
                                                                             'seat': 'BENCH',
                                                                             'slot': '2026-10-28 07:30',
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'unit': 'rm-role-operations-1793175100',
                                                                             'why': 'Operations slot 07:30 local, '
                                                                                    'band NONE, budget 150000 (cap '
                                                                                    '150000 x 1.0), 0 used today, '
                                                                                    'unit '
                                                                                    'rm-role-operations-1793175100, '
                                                                                    'model sonnet'},
                                                                            {'do': 'role_hold',
                                                                             'role': 'Conductor',
                                                                             'why': 'Conductor slot 08:00 missed '
                                                                                    '(tick 700 s late > '
                                                                                    'slot_late_s)'}],
                                                                   'ledger_blind': None,
                                                                   'roles': {'Conductor': {'done': {'2026-10-28 08:00': 'missed'},
                                                                                           'runs': [],
                                                                                           'waiting': ['other key',
                                                                                                       'the '
                                                                                                       'Operations '
                                                                                                       'x']},
                                                                             'Operations': {'alarms_seen': [],
                                                                                            'done': {'2026-10-28 07:30': 'launch'},
                                                                                            'pending_launch': {'alarm_day': None,
                                                                                                               'alarm_last_run': None,
                                                                                                               'alarms_seen': [],
                                                                                                               'done': None,
                                                                                                               'had_done': False,
                                                                                                               'key': '2026-10-28 '
                                                                                                                      '07:30',
                                                                                                               'mode': 'economy',
                                                                                                               'unit': 'rm-role-operations-1793175100'},
                                                                                            'runs': []}}}},
 'signal_marked_every_line': {'blind empty': 'marker scan UNMEASURED (proc unlistable)',
                              'blind with pid': 'TERM to 1 of 1 process(es) marked m; scan partly UNMEASURED '
                                                '(environ unreadable)',
                              'clear': 'no process marked m',
                              'empty': 'no process marked m',
                              'kill': 'KILL to 1 of 1 process(es) marked m',
                              'killed': [[11, 15], [12, 15], [13, 9], [22, 15], [31, 15]],
                              'none': 'marker scan UNMEASURED',
                              'partly': 'TERM to 1 of 2 process(es) marked m',
                              'raise': 'marker scan raised ZeroDivisionError: UNMEASURED',
                              'scan raised': 'marker scan raised ZeroDivisionError: UNMEASURED',
                              'term': 'TERM to 2 of 2 process(es) marked m'},
 'slot_blocked_table_and_slots_edges': {'Thu': [['Thu 09:00', 'run', 100000]],
                                        'Wed': [['Wed 09:00', 'run', 100000], ['Wed 15:00', 'run', 100000]],
                                        'all': [False, False, False, False, False],
                                        'bogus': [False, False, False, False, False],
                                        'first': [False, True, True, False, False],
                                        'last': [True, True, False, False, False],
                                        'no day': [['Wed 09:00', 'run', 100000],
                                                   ['Wed 15:00', 'run', 100000],
                                                   ['Thu 09:00', 'run', 100000]],
                                        'none': [True, True, True, True, True],
                                        'quick': [False, True, False, False, False],
                                        'quick_one': [False, True, True, True, True],
                                        'quick_one, only economy': [False],
                                        'slots': [['09:00', 'quick', 30000],
                                                  ['13:00', 'economy', 5000],
                                                  ['19:30', 'quick', 30000]]},
 'sup_done_runs_and_budget_alarm': {'acts': [{'blind': {'mode': 'quick',
                                                        'outcome': 'completed',
                                                        'role': 'Conductor',
                                                        'unit': 'ok'},
                                              'do': 'role_done',
                                              'note': True,
                                              'role': 'Conductor',
                                              'ticket': 'ROLES_ITEM_X',
                                              'unit': 'ok',
                                              'why': 'Conductor quick run ok done: 999 weighted tokens of a 1000 '
                                                     'budget (raw 999), model claude-opus-5-5,claude-sonnet-5-5, '
                                                     'success'},
                                             {'blind': {'mode': 'quick',
                                                        'outcome': 'completed',
                                                        'role': 'Conductor',
                                                        'unit': 'eq'},
                                              'do': 'role_done',
                                              'note': True,
                                              'role': 'Conductor',
                                              'ticket': 'ROLES_ITEM_X',
                                              'unit': 'eq',
                                              'why': 'Conductor quick run eq done: 1000 weighted tokens of a 1000 '
                                                     'budget (raw 1000), model claude-opus-5-5, success'},
                                             {'blind': {'mode': 'quick',
                                                        'outcome': 'completed',
                                                        'role': 'Conductor',
                                                        'unit': 'over'},
                                              'do': 'role_done',
                                              'note': True,
                                              'role': 'Conductor',
                                              'ticket': 'ROLES_ITEM_X',
                                              'unit': 'over',
                                              'why': 'Conductor quick run over done: 1001 weighted tokens of a 1000 '
                                                     'budget (raw 1001), model claude-opus-5-5, no result'},
                                             {'do': 'alarm',
                                              'kind': 'role:Conductor:overbudget',
                                              'note': True,
                                              'ticket': 'ROLES_ITEM_X',
                                              'why': 'Conductor run over used 1001 weighted tokens (raw 1001), '
                                                     'budget 1000'},
                                             {'blind': {'mode': 'quick',
                                                        'outcome': 'completed',
                                                        'role': 'Conductor',
                                                        'unit': 'nobud'},
                                              'do': 'role_done',
                                              'note': True,
                                              'role': 'Conductor',
                                              'ticket': 'ROLES_ITEM_X',
                                              'unit': 'nobud',
                                              'why': 'Conductor quick run nobud done: 5 weighted tokens of a 0 '
                                                     'budget (raw 5), model claude-opus-5-5, success'},
                                             {'do': 'alarm',
                                              'kind': 'role:Conductor:overbudget',
                                              'note': True,
                                              'ticket': 'ROLES_ITEM_X',
                                              'why': 'Conductor run nobud used 5 weighted tokens (raw 5), budget 0'},
                                             {'blind': {'mode': 'quick',
                                                        'outcome': 'completed',
                                                        'role': 'Conductor',
                                                        'unit': 'stopped'},
                                              'do': 'role_done',
                                              'note': True,
                                              'role': 'Conductor',
                                              'ticket': 'ROLES_ITEM_X',
                                              'unit': 'stopped',
                                              'why': 'Conductor quick run stopped done (after 2 stop(s)): 1 weighted '
                                                     'tokens of a 1000 budget (raw 1), model claude-opus-5-5, '
                                                     'error_max_turns'}],
                                    'busy': [],
                                    'runs': {'Conductor': [{'at': 1793174400.0,
                                                            'budget': 1000,
                                                            'day': '2026-10-28',
                                                            'item': 'ROLES_ITEM_X',
                                                            'mode': 'quick',
                                                            'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                'cacheReadInputTokens': 0,
                                                                                                'inputTokens': 999,
                                                                                                'outputTokens': 0},
                                                                            'claude-sonnet-5-5': {'inputTokens': 0,
                                                                                                  'outputTokens': 0}},
                                                            'raw_tokens': 999,
                                                            'run_max_s': 1800,
                                                            'scope': 'sc-ok',
                                                            'seat': 'BENCH',
                                                            'state': 'done',
                                                            'token_unit': 'weighted_v2',
                                                            'tokens': 999,
                                                            'unit': 'ok'},
                                                           {'at': 1793174400.0,
                                                            'budget': 1000,
                                                            'day': '2026-10-28',
                                                            'item': 'ROLES_ITEM_X',
                                                            'mode': 'quick',
                                                            'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                'cacheReadInputTokens': 0,
                                                                                                'inputTokens': 1000,
                                                                                                'outputTokens': 0}},
                                                            'raw_tokens': 1000,
                                                            'run_max_s': 1800,
                                                            'scope': 'sc-eq',
                                                            'seat': 'BENCH',
                                                            'state': 'done',
                                                            'token_unit': 'weighted_v2',
                                                            'tokens': 1000,
                                                            'unit': 'eq'},
                                                           {'at': 1793174400.0,
                                                            'budget': 1000,
                                                            'day': '2026-10-28',
                                                            'item': 'ROLES_ITEM_X',
                                                            'mode': 'quick',
                                                            'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                'cacheReadInputTokens': 0,
                                                                                                'inputTokens': 1001,
                                                                                                'outputTokens': 0}},
                                                            'raw_tokens': 1001,
                                                            'run_max_s': 1800,
                                                            'scope': 'sc-over',
                                                            'seat': 'BENCH',
                                                            'state': 'done',
                                                            'token_unit': 'weighted_v2',
                                                            'tokens': 1001,
                                                            'unit': 'over'},
                                                           {'at': 1793174400.0,
                                                            'budget': None,
                                                            'day': '2026-10-28',
                                                            'item': 'ROLES_ITEM_X',
                                                            'mode': 'quick',
                                                            'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                'cacheReadInputTokens': 0,
                                                                                                'inputTokens': 5,
                                                                                                'outputTokens': 0}},
                                                            'raw_tokens': 5,
                                                            'run_max_s': 1800,
                                                            'scope': 'sc-nobud',
                                                            'seat': 'BENCH',
                                                            'state': 'done',
                                                            'token_unit': 'weighted_v2',
                                                            'tokens': 5,
                                                            'unit': 'nobud'},
                                                           {'at': 1793174400.0,
                                                            'budget': 1000,
                                                            'day': '2026-10-28',
                                                            'item': 'ROLES_ITEM_X',
                                                            'mode': 'quick',
                                                            'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                'cacheReadInputTokens': 0,
                                                                                                'inputTokens': 1,
                                                                                                'outputTokens': 0}},
                                                            'raw_tokens': 1,
                                                            'run_max_s': 1800,
                                                            'scope': 'sc-stopped',
                                                            'seat': 'BENCH',
                                                            'state': 'done',
                                                            'stop_tries': 2,
                                                            'token_unit': 'weighted_v2',
                                                            'tokens': 1,
                                                            'unit': 'stopped'}]}},
 'sup_failed_runs_say_why': {'acts': [{'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'nofile'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'nofile',
                                       'why': 'Conductor quick run nofile failed: UNMEASURED (counted at its budget) '
                                              'weighted tokens of a 1000 budget (raw ?), model ?, no result'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'nofile'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run nofile ended without a good result (no result file)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'iserr'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'iserr',
                                       'why': 'Conductor quick run iserr failed: 3 weighted tokens of a 1000 budget '
                                              '(raw 3), model claude-opus-5-5, no result but is_error (?)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'iserr'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run iserr ended without a good result (boom)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'nousage'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'nousage',
                                       'why': 'Conductor quick run nousage failed: UNMEASURED (counted at its '
                                              'budget) weighted tokens of a 1000 budget (raw ?), model ?, no result'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'nousage'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run nousage ended without a good result (usage UNMEASURED: '
                                              'usage limit)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'emptyres'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'emptyres',
                                       'why': 'Conductor quick run emptyres failed: UNMEASURED (counted at its '
                                              'budget) weighted tokens of a 1000 budget (raw ?), model ?, no result'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'emptyres'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run emptyres ended without a good result (TAIL)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'both'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'both',
                                       'why': 'Conductor quick run both failed: 1 weighted tokens of a 1000 budget '
                                              '(raw 1), model claude-opus-5-5, no result but is_error (?)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'both'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run both ended without a good result (RES)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'long'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'long',
                                       'why': 'Conductor quick run long failed: 1 weighted tokens of a 1000 budget '
                                              '(raw 1), model claude-opus-5-5, no result but is_error (?)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'long'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run long ended without a good result '
                                              '(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'noprice'},
                                       'do': 'role_done',
                                       'note': True,
                                       'role': 'Conductor',
                                       'ticket': 'ROLES_ITEM_X',
                                       'unit': 'noprice',
                                       'why': 'Conductor quick run noprice failed: UNMEASURED (counted at its '
                                              "budget: unknown model 'claude-nonesuch-9-9' (as "
                                              "'claude-nonesuch-9-9'): not in role_launch.MODEL_PRICES; add its list "
                                              "prices from Anthropic's pricing page, there is no fallback weight) "
                                              'weighted tokens of a 1000 budget (raw 7), model ?, success'},
                                      {'blind': {'mode': 'quick',
                                                 'outcome': 'failed',
                                                 'role': 'Conductor',
                                                 'unit': 'noprice'},
                                       'conductor_log': True,
                                       'do': 'alarm',
                                       'kind': 'role:Conductor:failed',
                                       'note': True,
                                       'raise_first': 'Conductor run failed.',
                                       'ticket': 'ROLES_ITEM_X',
                                       'why': 'Conductor run noprice ended without a good result (usage UNMEASURED '
                                              "(unknown model 'claude-nonesuch-9-9' (as 'claude-nonesuch-9-9'): not "
                                              "in role_launch.MODEL_PRICES; add its list prices from Anthropic's "
                                              'pricing page, there is no fallback weight): no result text)'}],
                             'busy': [],
                             'runs': {'Conductor': [{'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'raw_tokens': None,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-nofile',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': None,
                                                     'unit': 'nofile'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                         'cacheReadInputTokens': 0,
                                                                                         'inputTokens': 3,
                                                                                         'outputTokens': 0}},
                                                     'raw_tokens': 3,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-iserr',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': 3,
                                                     'unit': 'iserr'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'raw_tokens': None,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-nousage',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': None,
                                                     'unit': 'nousage'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'err_tail': 'TAIL',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'raw_tokens': None,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-emptyres',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': None,
                                                     'unit': 'emptyres'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'err_tail': 'TAIL',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                         'cacheReadInputTokens': 0,
                                                                                         'inputTokens': 1,
                                                                                         'outputTokens': 0}},
                                                     'raw_tokens': 1,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-both',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': 1,
                                                     'unit': 'both'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                         'cacheReadInputTokens': 0,
                                                                                         'inputTokens': 1,
                                                                                         'outputTokens': 0}},
                                                     'raw_tokens': 1,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-long',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': 1,
                                                     'unit': 'long'},
                                                    {'at': 1793174400.0,
                                                     'budget': 1000,
                                                     'day': '2026-10-28',
                                                     'item': 'ROLES_ITEM_X',
                                                     'mode': 'quick',
                                                     'model_id': 'claude-nonesuch-9-9',
                                                     'raw_tokens': 7,
                                                     'run_max_s': 1800,
                                                     'scope': 'sc-noprice',
                                                     'seat': 'BENCH',
                                                     'state': 'failed',
                                                     'token_unit': 'weighted_v2',
                                                     'tokens': None,
                                                     'unit': 'noprice',
                                                     'unknown_model': "unknown model 'claude-nonesuch-9-9' (as "
                                                                      "'claude-nonesuch-9-9'): not in "
                                                                      'role_launch.MODEL_PRICES; add its list prices '
                                                                      "from Anthropic's pricing page, there is no "
                                                                      'fallback weight'}]}},
 'sup_learns_the_scope_of_an_unscoped_active_run': [{'acts': [],
                                                     'busy': ['Conductor'],
                                                     'runs': {'Conductor': [{'at': 1793174450.0,
                                                                             'budget': 1000,
                                                                             'day': '2026-10-28',
                                                                             'item': 'ROLES_ITEM_X',
                                                                             'mode': 'quick',
                                                                             'run_max_s': 1800,
                                                                             'scope': 'scope-of-u1-BENCH',
                                                                             'seat': 'BENCH',
                                                                             'state': 'running',
                                                                             'unit': 'u1'}]}},
                                                    {'acts': [],
                                                     'busy': ['Conductor'],
                                                     'runs': {'Conductor': [{'at': 1793174450.0,
                                                                             'budget': 1000,
                                                                             'day': '2026-10-28',
                                                                             'item': 'ROLES_ITEM_X',
                                                                             'mode': 'quick',
                                                                             'run_max_s': 1800,
                                                                             'scope': 'kept',
                                                                             'seat': 'BENCH',
                                                                             'state': 'running',
                                                                             'unit': 'u1'}]}}],
 'sup_old_runs_pruned_after_two_days': {'acts': [{'do': 'role_stop',
                                                  'force': False,
                                                  'marker': None,
                                                  'note': True,
                                                  'role': 'Conductor',
                                                  'scope': 'sc-live',
                                                  'seat': 'BENCH',
                                                  'since': 1792742460.0,
                                                  'ticket': 'ROLES_ITEM_X',
                                                  'unit': 'live',
                                                  'unit_gone': False,
                                                  'why': 'Conductor run live still active after 432000 s (run_max_s '
                                                         '1800): stop #1'},
                                                 {'do': 'alarm',
                                                  'kind': 'role:Conductor:overtime',
                                                  'note': True,
                                                  'ticket': 'ROLES_ITEM_X',
                                                  'why': 'Conductor run live passed run_max_s 1800'}],
                                        'busy': ['Conductor'],
                                        'runs': {'Conductor': [{'at': 1793001665.0,
                                                                'budget': 1000,
                                                                'day': '2026-10-28',
                                                                'item': 'ROLES_ITEM_X',
                                                                'mode': 'quick',
                                                                'run_max_s': 1800,
                                                                'scope': 'sc-fresh',
                                                                'seat': 'BENCH',
                                                                'state': 'done',
                                                                'unit': 'fresh'},
                                                               {'at': 1792742460.0,
                                                                'budget': 1000,
                                                                'day': '2026-10-28',
                                                                'item': 'ROLES_ITEM_X',
                                                                'mode': 'quick',
                                                                'run_max_s': 1800,
                                                                'scope': 'sc-live',
                                                                'seat': 'BENCH',
                                                                'state': 'running',
                                                                'stop_tries': 1,
                                                                'unit': 'live'}]}},
 'sup_one_roles_exception_alarms_with_its_item_and_is_busy': {'acts': [{'do': 'alarm',
                                                                        'kind': 'role:Conductor:supervise',
                                                                        'note': True,
                                                                        'ticket': 'ROLES_ITEM_X',
                                                                        'why': 'role Conductor supervision raised '
                                                                               'RuntimeError: '
                                                                               'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; '
                                                                               'its runs are kept as running and '
                                                                               'checked again next tick'},
                                                                       {'do': 'alarm',
                                                                        'kind': 'role:Ghost:supervise',
                                                                        'note': True,
                                                                        'ticket': None,
                                                                        'why': 'role Ghost supervision raised '
                                                                               'RuntimeError: '
                                                                               'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; '
                                                                               'its runs are kept as running and '
                                                                               'checked again next tick'}],
                                                              'busy': ['Conductor', 'Ghost'],
                                                              'runs': {'Conductor': [{'at': 1793174450.0,
                                                                                      'budget': 1000,
                                                                                      'day': '2026-10-28',
                                                                                      'item': 'ROLES_ITEM_X',
                                                                                      'mode': 'quick',
                                                                                      'run_max_s': 1800,
                                                                                      'scope': 'sc-u1',
                                                                                      'seat': 'BENCH',
                                                                                      'state': 'running',
                                                                                      'unit': 'u1'}],
                                                                       'Ghost': [{'at': 1793174450.0,
                                                                                  'budget': 1000,
                                                                                  'day': '2026-10-28',
                                                                                  'item': 'ROLES_ITEM_X',
                                                                                  'mode': 'quick',
                                                                                  'run_max_s': 1800,
                                                                                  'scope': 'sc-g1',
                                                                                  'seat': 'BENCH',
                                                                                  'state': 'running',
                                                                                  'unit': 'g1'}]}},
 'sup_skips_finished_runs_then_looks_at_the_next': {'acts': [],
                                                    'busy': ['Conductor'],
                                                    'runs': {'Conductor': [{'at': 1793174360.0,
                                                                            'budget': 1000,
                                                                            'day': '2026-10-28',
                                                                            'item': 'ROLES_ITEM_X',
                                                                            'mode': 'quick',
                                                                            'run_max_s': 1800,
                                                                            'scope': 'sc-old',
                                                                            'seat': 'BENCH',
                                                                            'state': 'done',
                                                                            'unit': 'old'},
                                                                           {'at': 1793174450.0,
                                                                            'budget': 1000,
                                                                            'day': '2026-10-28',
                                                                            'item': 'ROLES_ITEM_X',
                                                                            'mode': 'quick',
                                                                            'run_max_s': 1800,
                                                                            'scope': 'sc-u2',
                                                                            'seat': 'BENCH',
                                                                            'state': 'running',
                                                                            'unit': 'u2'}]}},
 'sup_unit_ended_without_scope_keeps_busy_and_next_run_still_seen': {'acts': [{'do': 'alarm',
                                                                               'kind': 'role:Conductor:scope',
                                                                               'note': True,
                                                                               'ticket': 'ROLES_ITEM_X',
                                                                               'why': 'Conductor run u1: unit '
                                                                                      'inactive, scope never '
                                                                                      'resolved: termination '
                                                                                      'UNCONFIRMED, kept busy (stop '
                                                                                      'claude-seat-?-* by hand); '
                                                                                      'kept as running, checked '
                                                                                      'again next tick'},
                                                                              {'do': 'role_stop',
                                                                               'force': False,
                                                                               'marker': 'm1',
                                                                               'note': True,
                                                                               'role': 'Conductor',
                                                                               'scope': None,
                                                                               'seat': 'BENCH',
                                                                               'since': 1793172460.0,
                                                                               'ticket': 'ROLES_ITEM_X',
                                                                               'unit': 'u1',
                                                                               'unit_gone': True,
                                                                               'why': 'Conductor run u1 still unit '
                                                                                      'inactive, scope never '
                                                                                      'resolved: termination '
                                                                                      'UNCONFIRMED, kept busy (stop '
                                                                                      'claude-seat-?-* by hand) '
                                                                                      'after 2000 s (run_max_s '
                                                                                      '1800): stop #1'},
                                                                              {'do': 'alarm',
                                                                               'kind': 'role:Conductor:overtime',
                                                                               'note': True,
                                                                               'ticket': 'ROLES_ITEM_X',
                                                                               'why': 'Conductor run u1 passed '
                                                                                      'run_max_s 1800'},
                                                                              {'blind': {'mode': 'quick',
                                                                                         'outcome': 'completed',
                                                                                         'role': 'Conductor',
                                                                                         'unit': 'u2'},
                                                                               'do': 'role_done',
                                                                               'note': True,
                                                                               'role': 'Conductor',
                                                                               'ticket': 'ROLES_ITEM_X',
                                                                               'unit': 'u2',
                                                                               'why': 'Conductor quick run u2 done: '
                                                                                      '200 weighted tokens of a 500 '
                                                                                      'budget (raw 400), model '
                                                                                      'claude-sonnet-5-5, success'}],
                                                                     'busy': ['Conductor'],
                                                                     'runs': {'Conductor': [{'at': 1793172460.0,
                                                                                             'budget': 1000,
                                                                                             'day': '2026-10-28',
                                                                                             'item': 'ROLES_ITEM_X',
                                                                                             'marker': 'm1',
                                                                                             'mode': 'quick',
                                                                                             'run_max_s': 1800,
                                                                                             'scope': None,
                                                                                             'seat': None,
                                                                                             'state': 'running',
                                                                                             'stop_tries': 1,
                                                                                             'unit': 'u1'},
                                                                                            {'at': 1793174410.0,
                                                                                             'budget': 500,
                                                                                             'day': '2026-10-28',
                                                                                             'item': 'ROLES_ITEM_X',
                                                                                             'mode': 'quick',
                                                                                             'model_usage': {'claude-sonnet-5-5': {'cacheCreationInputTokens': 0,
                                                                                                                                   'cacheReadInputTokens': 0,
                                                                                                                                   'inputTokens': 400,
                                                                                                                                   'outputTokens': 0}},
                                                                                             'raw_tokens': 400,
                                                                                             'run_max_s': 1800,
                                                                                             'scope': 'sc-u2',
                                                                                             'seat': 'BENCH',
                                                                                             'state': 'done',
                                                                                             'token_unit': 'weighted_v2',
                                                                                             'tokens': 200,
                                                                                             'unit': 'u2'}]}},
 'sup_unit_state_unmeasured_and_stop_ladder': {'acts': [{'do': 'alarm',
                                                         'kind': 'role:Conductor:unit',
                                                         'note': True,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run weird unit state UNMEASURED '
                                                                '(unknown): kept as running, retried next tick'},
                                                        {'do': 'alarm',
                                                         'kind': 'role:Conductor:scope',
                                                         'note': True,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run noscope: unit inactive, scope never '
                                                                'resolved: termination UNCONFIRMED, kept busy (stop '
                                                                'claude-seat-BENCH-* by hand); kept as running, '
                                                                'checked again next tick'},
                                                        {'do': 'role_stop',
                                                         'force': False,
                                                         'marker': 'm0',
                                                         'note': True,
                                                         'role': 'Conductor',
                                                         'scope': 's0',
                                                         'seat': 'BENCH',
                                                         'since': 1793172560.0,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'unit': 't0',
                                                         'unit_gone': False,
                                                         'why': 'Conductor run t0 still active after 1900 s '
                                                                '(run_max_s 1800): stop #1'},
                                                        {'do': 'alarm',
                                                         'kind': 'role:Conductor:overtime',
                                                         'note': True,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run t0 passed run_max_s 1800'},
                                                        {'do': 'role_stop',
                                                         'force': False,
                                                         'marker': None,
                                                         'note': False,
                                                         'role': 'Conductor',
                                                         'scope': 's1',
                                                         'seat': 'BENCH',
                                                         'since': 1793172560.0,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'unit': 't1',
                                                         'unit_gone': False,
                                                         'why': 'Conductor run t1 still active after 1900 s '
                                                                '(run_max_s 1800): stop #2'},
                                                        {'conductor_log': True,
                                                         'do': 'alarm',
                                                         'kind': 'role:Conductor:stop_failed',
                                                         'note': True,
                                                         'raise_first': 'Conductor run will not stop: its slot stays '
                                                                        'held.',
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run t1 still active after 1 stop(s): NOT '
                                                                'confirmed stopped, kept as running'},
                                                        {'do': 'role_stop',
                                                         'force': True,
                                                         'marker': None,
                                                         'note': False,
                                                         'role': 'Conductor',
                                                         'scope': 's2',
                                                         'seat': 'BENCH',
                                                         'since': 1793172560.0,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'unit': 't2',
                                                         'unit_gone': False,
                                                         'why': 'Conductor run t2 still active after 1900 s '
                                                                '(run_max_s 1800): stop #3'},
                                                        {'conductor_log': True,
                                                         'do': 'alarm',
                                                         'kind': 'role:Conductor:stop_failed',
                                                         'note': True,
                                                         'raise_first': 'Conductor run will not stop: its slot stays '
                                                                        'held.',
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run t2 still active after 2 stop(s): NOT '
                                                                'confirmed stopped, kept as running'},
                                                        {'do': 'role_stop',
                                                         'force': False,
                                                         'marker': None,
                                                         'note': True,
                                                         'role': 'Conductor',
                                                         'scope': 'sc-exact',
                                                         'seat': 'BENCH',
                                                         'since': 1793172660.0,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'unit': 'exact',
                                                         'unit_gone': False,
                                                         'why': 'Conductor run exact still active after 1800 s '
                                                                '(run_max_s 1800): stop #1'},
                                                        {'do': 'alarm',
                                                         'kind': 'role:Conductor:overtime',
                                                         'note': True,
                                                         'ticket': 'ROLES_ITEM_X',
                                                         'why': 'Conductor run exact passed run_max_s 1800'}],
                                               'busy': ['Conductor'],
                                               'runs': {'Conductor': [{'at': 1793174450.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 'sc-weird',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'unit': 'weird'},
                                                                      {'at': 1793174450.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': None,
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'unit': 'noscope'},
                                                                      {'at': 1793172560.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'marker': 'm0',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 's0',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'stop_tries': 1,
                                                                       'unit': 't0'},
                                                                      {'at': 1793172560.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 's1',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'stop_tries': 2,
                                                                       'unit': 't1'},
                                                                      {'at': 1793172560.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 's2',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'stop_tries': 3,
                                                                       'unit': 't2'},
                                                                      {'at': 1793172661.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 'sc-short',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'unit': 'short'},
                                                                      {'at': 1793172660.0,
                                                                       'budget': 1000,
                                                                       'day': '2026-10-28',
                                                                       'item': 'ROLES_ITEM_X',
                                                                       'mode': 'quick',
                                                                       'run_max_s': 1800,
                                                                       'scope': 'sc-exact',
                                                                       'seat': 'BENCH',
                                                                       'state': 'running',
                                                                       'stop_tries': 1,
                                                                       'unit': 'exact'}]}},
 'supervise_overbudget_repeats_tell_the_conductor': {'acts': [{'blind': {'mode': 'quick',
                                                                         'outcome': 'completed',
                                                                         'role': 'Conductor',
                                                                         'unit': 'u0'},
                                                               'do': 'role_done',
                                                               'note': True,
                                                               'role': 'Conductor',
                                                               'ticket': 'ROLES_ITEM_X',
                                                               'unit': 'u0',
                                                               'why': 'Conductor quick run u0 done: 1 weighted '
                                                                      'tokens of a 0 budget (raw 1), model '
                                                                      'claude-opus-5-5, success'},
                                                              {'do': 'alarm',
                                                               'kind': 'role:Conductor:overbudget',
                                                               'note': True,
                                                               'ticket': 'ROLES_ITEM_X',
                                                               'why': 'Conductor run u0 used 1 weighted tokens (raw '
                                                                      '1), budget 0'},
                                                              {'blind': {'mode': 'quick',
                                                                         'outcome': 'overbudget',
                                                                         'role': 'Conductor',
                                                                         'unit': 'u0'},
                                                               'conductor_log': True,
                                                               'do': 'alarm',
                                                               'kind': 'role:Conductor:overbudget_repeat',
                                                               'note': True,
                                                               'raise_first': 'Conductor keeps overrunning: re-set '
                                                                              'its budget or narrow its scope.',
                                                               'ticket': 'ROLES_ITEM_X',
                                                               'why': 'Conductor ran over budget 3 times in 7 days '
                                                                      '(of 1 measured runs): its budget or its scope '
                                                                      'is wrong'}],
                                                     'busy': [],
                                                     'runs': {'Conductor': [{'at': 1793174400.0,
                                                                             'budget': 0,
                                                                             'day': '2026-10-28',
                                                                             'item': 'ROLES_ITEM_X',
                                                                             'mode': 'quick',
                                                                             'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                                 'cacheReadInputTokens': 0,
                                                                                                                 'inputTokens': 1,
                                                                                                                 'outputTokens': 0}},
                                                                             'raw_tokens': 1,
                                                                             'run_max_s': 1800,
                                                                             'scope': 'sc-u0',
                                                                             'seat': 'BENCH',
                                                                             'state': 'done',
                                                                             'token_unit': 'weighted_v2',
                                                                             'tokens': 1,
                                                                             'unit': 'u0'}]}},
 'supervise_overbudget_when_budget_is_zero': {'acts': [{'blind': {'mode': 'quick',
                                                                  'outcome': 'completed',
                                                                  'role': 'Conductor',
                                                                  'unit': 'u0'},
                                                        'do': 'role_done',
                                                        'note': True,
                                                        'role': 'Conductor',
                                                        'ticket': 'ROLES_ITEM_X',
                                                        'unit': 'u0',
                                                        'why': 'Conductor quick run u0 done: 1 weighted tokens of a '
                                                               '0 budget (raw 1), model claude-opus-5-5, success'},
                                                       {'do': 'alarm',
                                                        'kind': 'role:Conductor:overbudget',
                                                        'note': True,
                                                        'ticket': 'ROLES_ITEM_X',
                                                        'why': 'Conductor run u0 used 1 weighted tokens (raw 1), '
                                                               'budget 0'},
                                                       {'blind': {'mode': 'quick',
                                                                  'outcome': 'completed',
                                                                  'role': 'Conductor',
                                                                  'unit': 'u1'},
                                                        'do': 'role_done',
                                                        'note': True,
                                                        'role': 'Conductor',
                                                        'ticket': 'ROLES_ITEM_X',
                                                        'unit': 'u1',
                                                        'why': 'Conductor quick run u1 done: 1 weighted tokens of a '
                                                               '0 budget (raw 1), model claude-opus-5-5, success'},
                                                       {'do': 'alarm',
                                                        'kind': 'role:Conductor:overbudget',
                                                        'note': True,
                                                        'ticket': 'ROLES_ITEM_X',
                                                        'why': 'Conductor run u1 used 1 weighted tokens (raw 1), '
                                                               'budget 0'}],
                                              'busy': [],
                                              'runs': {'Conductor': [{'at': 1793174400.0,
                                                                      'budget': 0,
                                                                      'day': '2026-10-28',
                                                                      'item': 'ROLES_ITEM_X',
                                                                      'mode': 'quick',
                                                                      'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                          'cacheReadInputTokens': 0,
                                                                                                          'inputTokens': 1,
                                                                                                          'outputTokens': 0}},
                                                                      'raw_tokens': 1,
                                                                      'run_max_s': 1800,
                                                                      'scope': 'sc-u0',
                                                                      'seat': 'BENCH',
                                                                      'state': 'done',
                                                                      'token_unit': 'weighted_v2',
                                                                      'tokens': 1,
                                                                      'unit': 'u0'},
                                                                     {'at': 1793174400.0,
                                                                      'budget': None,
                                                                      'day': '2026-10-28',
                                                                      'item': 'ROLES_ITEM_X',
                                                                      'mode': 'quick',
                                                                      'model_usage': {'claude-opus-5-5': {'cacheCreationInputTokens': 0,
                                                                                                          'cacheReadInputTokens': 0,
                                                                                                          'inputTokens': 1,
                                                                                                          'outputTokens': 0}},
                                                                      'raw_tokens': 1,
                                                                      'run_max_s': 1800,
                                                                      'scope': 'sc-u1',
                                                                      'seat': 'BENCH',
                                                                      'state': 'done',
                                                                      'token_unit': 'weighted_v2',
                                                                      'tokens': 1,
                                                                      'unit': 'u1'}]}},
 'supervise_seat_passes_the_runs_seat_before_the_roles': [{'res': {'acts': [{'do': 'role_stop',
                                                                             'force': False,
                                                                             'marker': None,
                                                                             'note': True,
                                                                             'role': 'Conductor',
                                                                             'scope': 'sc-new',
                                                                             'seat': 'RS',
                                                                             'since': 1793170860.0,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'unit': 'u1',
                                                                             'unit_gone': False,
                                                                             'why': 'Conductor run u1 still active '
                                                                                    'after 3600 s (run_max_s 1800): '
                                                                                    'stop #1'},
                                                                            {'do': 'alarm',
                                                                             'kind': 'role:Conductor:overtime',
                                                                             'note': True,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'why': 'Conductor run u1 passed '
                                                                                    'run_max_s 1800'}],
                                                                   'busy': ['Conductor'],
                                                                   'runs': {'Conductor': [{'at': 1793170860.0,
                                                                                           'budget': 1000,
                                                                                           'day': '2026-10-28',
                                                                                           'item': 'ROLES_ITEM_X',
                                                                                           'mode': 'quick',
                                                                                           'run_max_s': 1800,
                                                                                           'scope': 'sc-new',
                                                                                           'seat': 'RS',
                                                                                           'state': 'running',
                                                                                           'stop_tries': 1,
                                                                                           'unit': 'u1'}]}},
                                                           'scope args': [['u1', 'RS']]},
                                                          {'res': {'acts': [{'do': 'role_stop',
                                                                             'force': False,
                                                                             'marker': None,
                                                                             'note': True,
                                                                             'role': 'Conductor',
                                                                             'scope': 'sc-new',
                                                                             'seat': 'CS',
                                                                             'since': 1793170860.0,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'unit': 'u1',
                                                                             'unit_gone': False,
                                                                             'why': 'Conductor run u1 still active '
                                                                                    'after 3600 s (run_max_s 1800): '
                                                                                    'stop #1'},
                                                                            {'do': 'alarm',
                                                                             'kind': 'role:Conductor:overtime',
                                                                             'note': True,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'why': 'Conductor run u1 passed '
                                                                                    'run_max_s 1800'}],
                                                                   'busy': ['Conductor'],
                                                                   'runs': {'Conductor': [{'at': 1793170860.0,
                                                                                           'budget': 1000,
                                                                                           'day': '2026-10-28',
                                                                                           'item': 'ROLES_ITEM_X',
                                                                                           'mode': 'quick',
                                                                                           'run_max_s': 1800,
                                                                                           'scope': 'sc-new',
                                                                                           'seat': None,
                                                                                           'state': 'running',
                                                                                           'stop_tries': 1,
                                                                                           'unit': 'u1'}]}},
                                                           'scope args': [['u1', 'CS']]},
                                                          {'res': {'acts': [{'do': 'role_stop',
                                                                             'force': False,
                                                                             'marker': None,
                                                                             'note': True,
                                                                             'role': 'Conductor',
                                                                             'scope': 'sc-new',
                                                                             'seat': 'RS',
                                                                             'since': 1793170860.0,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'unit': 'u1',
                                                                             'unit_gone': False,
                                                                             'why': 'Conductor run u1 still active '
                                                                                    'after 3600 s (run_max_s 1800): '
                                                                                    'stop #1'},
                                                                            {'do': 'alarm',
                                                                             'kind': 'role:Conductor:overtime',
                                                                             'note': True,
                                                                             'ticket': 'ROLES_ITEM_X',
                                                                             'why': 'Conductor run u1 passed '
                                                                                    'run_max_s 1800'}],
                                                                   'busy': ['Conductor'],
                                                                   'runs': {'Conductor': [{'at': 1793170860.0,
                                                                                           'budget': 1000,
                                                                                           'day': '2026-10-28',
                                                                                           'item': 'ROLES_ITEM_X',
                                                                                           'mode': 'quick',
                                                                                           'run_max_s': 1800,
                                                                                           'scope': 'sc-new',
                                                                                           'seat': 'RS',
                                                                                           'state': 'running',
                                                                                           'stop_tries': 1,
                                                                                           'unit': 'u1'}]}},
                                                           'scope args': [['u1', 'RS']]}]}
# GOLDEN-END


def main():
    SD.strict_roles()       # strict gates under test; the advisory default: selftest_role_caps_advisory A7
    got = {}
    for fn in SCEN:
        try:
            got[fn.__name__] = norm(fn())
        except Exception as e:  # noqa: BLE001
            FAILS.append("%s raised %r" % (fn.__name__, e))
            print("FAIL: %s raised %r" % (fn.__name__, e))
    if "--show" in sys.argv:
        for name, v in got.items():
            print("==", name)
            for a in (v.get("acts") if isinstance(v, dict) else None) or []:
                print("  ", a.get("do"), a.get("kind", ""), "note=%s" % a.get("note"), "|", a.get("why", ""))
        return
    if "--gen" in sys.argv:
        path = os.path.abspath(__file__)
        text = open(path, encoding="utf-8").read()
        body = "GOLDEN = " + pprint.pformat(got, width=118, sort_dicts=True) + "\n"
        text = re.sub(r"# GOLDEN-BEGIN\n.*?# GOLDEN-END", lambda m: "# GOLDEN-BEGIN\n" + body + "# GOLDEN-END", text,
                      flags=re.S)
        open(path, "w", encoding="utf-8").write(text)
        print("golden written: %d scenarios" % len(got))
        return
    for name, v in got.items():
        ok = GOLDEN.get(name) == v
        print(("ok    " if ok else "FAIL  ") + name)
        if not ok:
            FAILS.append(name)
            print("   want:", json.dumps(GOLDEN.get(name), sort_keys=True)[:1500])
            print("   got: ", json.dumps(v, sort_keys=True)[:1500])
    for name in GOLDEN:
        if name not in got:
            FAILS.append("golden without scenario: " + name)


def alarm_dedupe():
    """ALARM_RUN_DEDUPE_SAID_IT_TWICE: a scheduled run that finishes covers the alarms open at its launch, a failed one
    covers nothing. Not a golden scenario: it reads the marks, not the journal."""
    def want(name, ok, got):
        print(("ok    " if ok else "FAIL  ") + name + ": %s" % (got,))
        if not ok:
            FAILS.append(name)
    for state, seen in (("done", ["ITEM_ONE"]), ("failed", [])):
        rs = {"alarms_seen": [], "slot_alarms": {"unit": "u", "keys": ["ITEM_ONE"]}}
        RL.finish_slot_alarms(rs, {"unit": "u", "state": state})
        want("slot run %s marks %s" % (state, seen), rs["alarms_seen"] == seen and "slot_alarms" not in rs, rs)
    rs = {"slot_alarms": {"unit": "u", "keys": ["ITEM_ONE"]}}
    RL.finish_slot_alarms(rs, {"unit": "other", "state": "done"})
    want("another unit's finish leaves the launch's list", "alarms_seen" not in rs and "slot_alarms" in rs, rs)
    op = SD.operations(alarm_runs=True, runs_local=["12:00"], economy_pass_local=None, alarm_run_gap_s=100000)
    now = SD.at_local("12:00")
    st = fresh_st(Operations={"done": {}, "runs": [], "alarm_last_run": now - 10})
    decide([op], st, SD.robs(SD.ops_status(now, alarms={"a1": {"state": "OPEN", "item": "ITEM_ONE"}})), now, busy=set())
    sa = st["roles"]["Operations"].get("slot_alarms")
    want("a scheduled launch holds the open alarms for its finish", bool(sa) and sa["keys"] == ["ITEM_ONE"], sa)


_REACHED = []
main()
alarm_dedupe()
_REACHED.append(1)
print("%d failure(s)" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if (FAILS or _REACHED != [1]) else 0)
