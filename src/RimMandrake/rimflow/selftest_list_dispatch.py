#!/usr/bin/env python3
"""selftest_list_dispatch.py - the Workshop Pipeline's Waiting, Ready and Work stages (list_dispatch.py).

Item RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST; page design/specs/2026-11-23-list-dispatch/boundary.md
(each t_ function is one promise of it, by name). Offline: fake facts, fake launch, close and need functions, a
throwaway state dir. Written before the code; seen failing on the base (list_dispatch.py absent).
"""
import json
import os
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ld_selftest_")
os.environ["RM_WORK_BUNDLE_DIR"] = tempfile.mkdtemp(prefix="ld_bundles_")     # gather reads the work-bundle store

FAILS = []
CFG = {"enabled": True, "max_live": 2, "max_chain_depth": 2, "max_runs_per_item": 2, "max_never_started": 2,
       "sonnet_cap_usd": 5, "opus_cap_usd": 12, "seat": "BENCH"}
NOW = 1_800_000_000.0


def chk(cond_fn, what):
    try:
        cond = cond_fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def LD():
    import list_dispatch
    return list_dispatch


def it(state="open", blocked=False, effect="cmd:false", verdict="fails", depth=0, waits_on=(), **kw):
    d = {"state": state, "blocked": blocked, "effect": effect, "verdict": verdict, "depth": depth,
         "waits_on": list(waits_on), "out": "the text is not in the file", "title": "a title"}
    d.update(kw)
    return d


def run(items, runs=None, st=None, cfg=None, account=(True, ""), **top):
    facts = {"items": items, "runs": runs or {}, "other_live": 0}
    facts.update(top)
    st = st if st is not None else {"items": {}}
    rows, launches = LD().decide(dict(cfg or CFG), st, facts, NOW, account=account)
    return {r["item"]: r for r in rows}, launches, st


def dec(items, iid="A", **kw):
    rows, launches, _ = run(items, **kw)
    return rows[iid]["decision"], launches


def att(*specs):
    return {"items": {"A": {"attempts": [dict(s) for s in specs]}}}


# ---- promises -------------------------------------------------------------------------------------------------------

def t_decide_is_pure_and_says_why_on_every_row():
    items = {"A": it(), "B": it(verdict="holds"), "C": it(effect=None, verdict=None), "D": it(waits_on=["X"]),
             "E": it(blocked=True), "F": it(depth=5), "G": it(verdict="unmeasured")}
    snap = json.dumps(items, sort_keys=True)
    rows, launches, _ = run(items)
    chk(lambda: json.dumps(items, sort_keys=True) == snap, "decide does not change its facts")
    chk(lambda: all(str(r.get("why") or "").strip() for r in rows.values()), "every row says why in words")
    chk(lambda: set(rows) == set(items), "one row per item")
    r2, l2, _ = run(None)
    chk(lambda: len(r2) == 1 and list(r2.values())[0]["decision"] == "blind" and l2 == [],
        "an unreadable ledger is one blind row and no launch")


def t_the_check_runs_before_every_attempt():
    chk(lambda: dec({"A": it(verdict="holds")}, st=att({"unit": "u1", "failed": None, "next": None},
                                                       {"unit": "u2", "failed": None, "next": None}),
                    runs={"A": {"live": [], "ended": ["u1", "u2"]}}) == ("close", []),
        "a check that holds after two runs: close, not stopped")
    chk(lambda: dec({"A": it(verdict="unmeasured")}) == ("blind", []), "unmeasured: blind")
    # OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK_WTHJ, 2026-11-26 21:54Z: a live run shaped its item's check onto
    # the selftest it was still writing; the dispatch clone had no such file (exit 2) and the alarm rang on work that
    # was running. A live run or bundle on the item outranks an unmeasured check: nothing is held, nothing launches.
    chk(lambda: dec({"A": it(verdict="unmeasured")}, runs={"A": {"live": ["u1"]}})[0] == "live",
        "unmeasured with a live run: live, not blind")
    chk(lambda: dec({"A": it(verdict="unmeasured")}, runs={"A": {"live": [], "bundle": "WB-x"}})[0] == "in_bundle",
        "unmeasured in a live bundle: in_bundle, not blind")
    chk(lambda: dec({"A": it(effect=None, verdict=None)}) == ("no_effect", []), "no check: no_effect")
    calls = []
    fx = {"facts": lambda st: {"items": {"A": it(verdict="holds")}, "runs": {}, "other_live": 0},
          "account": lambda: (True, ""), "close": lambda *a: calls.append(a) or (0, "closed"),
          "launch": lambda *a: (_ for _ in ()).throw(AssertionError("launched on a passing item")),
          "need": lambda *a: None, "effect": lambda *a: (0, "")}
    rd = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    chk(lambda: len(calls) == 1 and calls[0][0] == "A" and rd["items"]["A"]["decision"] == "closed_by_check",
        "the tick closes a passing item and launches nothing")
    chk(lambda: LD().UNIT == "rm-list-dispatch.service", "the close is the lane unit's act")


def t_one_work_run_then_one_more_only_on_a_named_next_act():
    one = {"unit": "u1", "failed": None, "next": None}
    nxt = {"unit": "u1", "failed": None, "next": "apply the 103 commands"}
    chk(lambda: dec({"A": it()}) == ("launch", ["A"]), "a failing check, no run yet: launch")
    chk(lambda: dec({"A": it()}, st=att(nxt), runs={"A": {"live": [], "ended": ["u1"]}}) == ("launch", ["A"]),
        "a run ended with a next act: one more run")
    chk(lambda: dec({"A": it()}, st=att(one), runs={"A": {"live": [], "ended": ["u1"]}}) == ("stopped", []),
        "a run ended with no next act: stopped")
    two = att(dict(nxt), {"unit": "u2", "failed": None, "next": "more"})
    chk(lambda: dec({"A": it()}, st=two, runs={"A": {"live": [], "ended": ["u1", "u2"]}}) == ("stopped", []),
        "two runs is the most, even with a next act")
    chk(lambda: dec({"A": it()}, st=att(nxt), runs={"A": {"live": [], "ended": []}})[1] == [],
        "a run that is neither live nor seen ended: no second launch")


def t_a_launch_that_never_started_is_not_spent():
    never = {"unit": None, "failed": "never started: pool full", "at": NOW - 60}
    chk(lambda: dec({"A": it()}, st=att(never)) == ("launch", ["A"]), "one never-started launch: launch again")
    chk(lambda: dec({"A": it()}, st=att(never, dict(never))) == ("system_wait", []),
        "max_never_started never-started launches in a row: it waits, it is not stopped")
    rows, _, st2 = run({"A": it()}, st=att(never, dict(never)))
    chk(lambda: rows["A"].get("need") and "pool full" in rows["A"]["need"]["why_not_recovered"], "and says so to the Conductor")
    old = dict(never, at=NOW - 3700)
    chk(lambda: dec({"A": it()}, st=att(old, dict(old))) == ("launch", ["A"]), "past SYSTEM_WAIT_S: launch again")
    form = dict(never, failed="never started: REFUSED (form): no model named\nREPAIR: pass --model")
    chk(lambda: dec({"A": it()}, st=att(form, dict(form))) == ("stopped", []),
        "a refusal of form is never sent again unchanged: stopped, its repair named")


def t_a_list_run_that_died_spends_no_run():
    dead = {"A": {"live": [], "ended": ["u1", "u2"], "system": {"u2": "KILLED (killed: signal)"}}}
    nxt = {"unit": "u1", "failed": None, "next": "go on"}
    two = att(nxt, {"unit": "u2", "failed": None})
    rows, l, st2 = run({"A": it()}, st=two, runs=dead)
    chk(lambda: (rows["A"]["decision"], l) == ("system_wait", []) and "KILLED" in rows["A"]["why"],
        "a killed second run waits: it is not one of the two, and it does not stop the item")
    chk(lambda: st2["items"]["A"]["attempts"][1].get("void") and LD().spent(st2["items"]["A"]["attempts"]) == [nxt],
        "the killed run is marked void and is not spent")
    st2["items"]["A"]["attempts"][1]["void_at"] = NOW - 3700
    chk(lambda: dec({"A": it()}, st=st2, runs=dead) == ("launch", ["A"]), "past the wait: one more run")
    shp = att({"unit": "u2", "failed": None, "kind": "shape"})
    chk(lambda: dec({"A": it(effect=None, verdict=None, shape_due=True)}, st=shp, runs=dead) == ("system_wait", []),
        "a killed Shape run does not stop the item")
    chk(lambda: dec({"A": it()}, st=att({"unit": "u1", "failed": None, "next": None}),
                    runs={"A": {"live": [], "ended": ["u1"], "system": {}}}) == ("stopped", []),
        "a run that ended on its own merits with no next act still stops it")
    fx = {"facts": lambda st: {"items": {"A": it()}, "runs": {}, "other_live": 0}, "account": lambda: (True, ""),
          "launch": lambda *a: (2, "REFUSED by control", None), "need": lambda *a: None,
          "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    rd = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    st = json.load(open(os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")))
    a = st["items"]["A"]["attempts"][-1]
    chk(lambda: rd["items"]["A"]["decision"] == "launch_failed" and a.get("failed") and not a.get("unit"),
        "a refused launch is recorded with failed set and no unit")
    os.remove(os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json"))


def t_a_stop_names_the_outcome_the_reason_and_the_smallest_act():
    st = att({"unit": "u1", "failed": None, "next": None})
    rows, _, st2 = run({"A": it()}, runs={"A": {"live": [], "ended": ["u1"]}}, st=st)
    need = rows["A"].get("need") or {}
    chk(lambda: all(str(need.get(k) or "").strip() for k in ("outcome", "why_not_recovered", "smallest_act")),
        "a stopped row carries outcome, why_not_recovered and smallest_act")
    told = []
    fx = {"facts": lambda s: {"items": {"A": it()}, "runs": {"A": {"live": [], "ended": ["u1"]}}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a: (0, "", "u9"), "need": lambda t, n: told.append(t),
          "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    p = os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")
    json.dump(st, open(p, "w"))
    LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    LD().tick(dict(CFG), apply=True, fx=fx, now=NOW + 900)
    chk(lambda: len(told) == 1, "the stop is said once on the Needs Conductor line, not every tick (%d)" % len(told))
    os.remove(p)


def t_a_run_carries_a_mod_only_when_mod_work_reads_the_ticket_as_that_mods():
    """A ticket that names a mod only in its title (a pipeline-tool repair with the mod as its example) launches a run
    tied to no mod: the status page read such a run as work on the mod (RIMMANDRAKE_FIX_PASSED_MOD_BADGE_HELPER_WAS_TOOL_REPAIR).
    The word tie (`mod`) still gates the launch (a stop or a hold on the mod); it is never the run's recorded mod."""
    seen = []
    tool = it(mod="FlowWorks", mod_work={"mod": None, "why": "no home and no path inside one mod", "unreadable": None})
    fx = {"facts": lambda s: {"items": {"A": tool}, "runs": {}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a, **k: seen.append(a) or (0, "", "u9"),
          "need": lambda *a: None, "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    chk(lambda: len(seen) == 1 and seen[0][5] is None,
        "a ticket that names a mod only by a word launches a run tied to no mod (got %r)" % (seen[0][5] if seen else "no launch"))
    p = os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")
    if os.path.exists(p):
        os.remove(p)


def t_waits_are_not_launched():
    r, l, _ = run({"A": it(waits_on=["B_OPEN"])})
    chk(lambda: r["A"]["decision"] == "waits_on" and "B_OPEN" in r["A"]["why"] and l == [], "waits on an open item")
    chk(lambda: dec({"A": it(wait_until=NOW + 3600)}) == ("waiting", []), "a dated wait in the future: waiting")
    chk(lambda: dec({"A": it(wait_until=NOW - 3600)}) == ("reshape", []), "a dated wait passed: reshape, no launch")
    chk(lambda: dec({"A": it(blocked=True)}) == ("blocked", []), "blocked: nothing")


def t_a_passed_wait_gets_one_second_look():
    past = dict(wait_until=NOW - 3600, wait_reason="three more launches", second_look=True)
    rows, l, _ = run({"A": it(**past)})
    chk(lambda: rows["A"]["decision"] == "launch" and l == ["A"] and rows["A"]["model"] == "opus"
        and rows["A"].get("look") == "three more launches", "a wait passed on a lane item: one second look (%s)" % rows["A"])
    ended = {"A": {"live": [], "ended": ["u1"]}}
    own = att({"unit": "u1", "at": NOW - 90000, "failed": None, "next": None, "kind": "shape"})
    rows, l, _ = run({"A": it(**past)}, st=own, runs=ended)
    chk(lambda: rows["A"]["decision"] == "launch" and rows["A"]["run_n"] == 2,
        "the wait that its own run left counts as that run's next act (%s)" % rows["A"]["why"])
    two = att({"unit": "u0", "at": NOW - 95000, "failed": None, "next": "x"},
              {"unit": "u1", "at": NOW - 90000, "failed": None, "next": None})
    rows, l, _ = run({"A": it(**past)}, st=two, runs={"A": {"live": [], "ended": ["u0", "u1"]}})
    chk(lambda: rows["A"]["decision"] == "stopped" and rows["A"].get("need") and not l,
        "the two-run rule holds on a second look, and says so (%s)" % rows["A"]["why"])
    after = att({"unit": "u1", "at": NOW - 60, "failed": None, "next": None})
    rows, l, _ = run({"A": it(**past)}, st=after, runs=ended)
    chk(lambda: rows["A"]["decision"] == "stopped" and not l,
        "a run since the date is the look: its end decides (%s)" % rows["A"]["decision"])
    chk(lambda: dec({"A": it(wait_until=NOW - 3600)}) == ("reshape", []), "an old item with no name: a date launches nothing")
    chk(lambda: dec({"A": it(**past)}, account=(False, "drain")) == ("account_hold", []), "every gate still stops it")
    chk(lambda: dec({"A": it(**dict(past, route={"who": "owner", "ask": "a", "resumes": "b"}))})[0] == "routed",
        "a routed item gets no look")
    b = LD().brief_text("A", it(**past), {"run_n": 2, "look": "three more launches"})
    chk(lambda: "second look" in b and "three more launches" in b, "the brief says what the wait was for")
    chk(lambda: "second look" not in LD().brief_text("A", it(), {"run_n": 1}), "a plain Work brief has no second look")
    import shlex
    q = "cmd:python3 -c 'import sys; sys.exit(1)'"                    # a check that holds single quotes (polish line)
    line = next((x.strip() for x in LD().brief_text("A", it(effect=q), {"run_n": 1}).splitlines()
                 if "list_effect.py check" in x), "")
    chk(lambda: shlex.split(line)[-1] == q, "the brief's check command runs as written for a check with quotes (%s)" % line)



def t_a_block_whose_predecessor_is_done_is_not_a_block():
    import model as LM
    def ev(**k):
        ev.n += 1
        return dict({"seat": "BENCH", "ts": "2026-11-23T%02d:%02d:00Z" % (ev.n // 60, ev.n % 60), "tsn": ev.n}, **k)
    ev.n = 0

    def world(*acts):
        ids = sorted({a["id"] for a in acts} | {"LD_FIRST_PART_OF_CHAIN_ONE", "LD_SECOND_PART_OF_CHAIN_TWO",
                                                 "LD_OTHER_PART_OF_CHAIN_THREE"})
        evs = [ev(event="file", id=i, title="t", kind="task", **{"for": "BENCH"}) for i in ids] + \
            [ev(**a) for a in acts]
        return LM.replay(evs)
    one, two, three = "LD_FIRST_PART_OF_CHAIN_ONE", "LD_SECOND_PART_OF_CHAIN_TWO", "LD_OTHER_PART_OF_CHAIN_THREE"
    blk = {"event": "block", "id": two, "reason": "runs after one", "on": one}
    fin = {"event": "close", "id": one, "sha": "a" * 40}

    def bf(*acts):
        w = world(*(a for a in acts if a is not fin))
        if fin in acts:
            w.items[one].state = "done"
        return LD().block_facts(w, w.items[two], NOW)
    chk(lambda: bf(blk) == ([one], False), "its predecessor is open: it waits on it")
    chk(lambda: bf(blk, fin) == ([], False), "its predecessor is done: no wait and no block (the block of 2026-11-23)")
    chk(lambda: bf(blk, {"event": "supersede", "id": one, "by": three}) == ([three], False),
        "its predecessor was superseded: it waits on the successor")
    chk(lambda: bf(blk, {"event": "drop", "id": one, "reason": "dead"}) == ([], True),
        "its predecessor was dropped with nothing released: still blocked")
    chk(lambda: bf({"event": "block", "id": two, "reason": "no event named", "kind": "external"}) == ([], True),
        "a block of another kind holds until unblock")
    chk(lambda: bf() == ([], False), "an item with no block")


def t_the_gates_launch_nothing():
    chk(lambda: dec({"A": it()}, cfg=dict(CFG, enabled=False)) == ("disabled", []), "disabled")
    chk(lambda: dec({"A": it()}, paused="paused by the Conductor") == ("pipeline_paused", []), "the pause")
    chk(lambda: dec({"A": it(off="pipe off family:list_dispatch")}) == ("off", []), "pipe off")
    chk(lambda: dec({"A": it(held="HELD BY OWNER: FeverWood")}) == ("held", []), "a held mod")
    chk(lambda: dec({"A": it(off_unreadable="control store unreadable")}) == ("blind", []), "an unreadable store")
    chk(lambda: dec({"A": it(verdict="holds")}, paused="paused") == ("pipeline_paused", []), "the pause closes nothing")
    chk(lambda: dec({"A": it(verdict="holds", off="pipe off item:A")}) == ("off", []), "pipe off closes nothing")
    chk(lambda: dec({"A": it(effect=None, verdict=None, accept="a/b_accept.py", off="pipe off all")}) == ("off", []),
        "pipe off attaches nothing")
    chk(lambda: dec({"A": it(verdict="holds")}, cfg=dict(CFG, enabled=False)) == ("disabled", []),
        "a disabled lane closes nothing")
    chk(lambda: dec({"A": it()}, account=(False, "drain")) == ("account_hold", []), "an account hold")
    chk(lambda: dec({"A": it()}, pool="pool full: 16 clones") == ("pool_full", []), "the pool refuses a new clone")
    chk(lambda: dec({"A": it(clone_exists=True)}, pool="pool full: 16 clones") == ("launch", ["A"]),
        "the pool does not stop a launch that reuses the item's own clone")
    chk(lambda: LD().account_gate(gate=lambda: (True, "KEEP"), drain=lambda now: "the plan drains steven")
        == (False, "the plan drains steven"), "the switching plan's drain is an account hold, before any launch")
    chk(lambda: LD().account_gate(gate=lambda: (True, "KEEP"), drain=lambda now: None) == (True, "KEEP"),
        "no drain: the Dispatcher's pick decides")
    ml = dict(CFG, machine_load_per_core=2)
    chk(lambda: dec({"A": it()}, cfg=ml, load=40.0, cores=14) == ("machine_load", []),
        "load 40 on 14 cores: a ready item reads machine_load and launches nothing, own slots free")
    chk(lambda: "40.0" in run({"A": it()}, cfg=ml, load=40.0, cores=14)[0]["A"]["why"], "and the row names the load")
    chk(lambda: dec({"A": it()}, cfg=ml, load=10.0, cores=14) == ("launch", ["A"]), "load 10 on 14 cores launches")
    chk(lambda: dec({"A": it()}, cfg=ml, load=28.0, cores=14) == ("machine_load", []), "at the line launches nothing")
    for what, top in (("load", {"load": None, "cores": 14}), ("core count", {"load": 40.0, "cores": None})):
        r, l, _ = run({"A": it()}, cfg=ml, **top)
        chk(lambda r=r, l=l: l == ["A"] and "could not be read" in r["A"].get("load_could_not_look", "")
            and "could not look" in r["A"]["why"] and not r["A"].get("could_not_look"),
            "an unreadable %s says could not look and launches (never read as 0, never a hold)" % what)
    chk(lambda: dec({"A": it()}, cfg=dict(ml, hosts={"SteveDesktop": {"max_live": 2, "min_left_pct": 5}}), load=40.0,
                    cores=14, hosts={"SteveDesktop": {"live": 0, "left": 50.0}}) == ("launch", ["A"]),
        "over the line a host with room still takes the run: its load lands there")
    chk(lambda: LD().load_cfg().get("machine_load_per_core") == 2, "the shipped lane carries the machine line")
    import control
    chk(lambda: "list_dispatch" in control.FAMILIES, "list_dispatch is a control family (pipe off family:list_dispatch)")


def t_the_lane_has_its_own_slots_and_chain_rule():
    runs = {"A": {"live": ["u1"], "ended": []}, "B": {"live": ["u2"], "ended": []}}
    chk(lambda: dec({"A": it(), "B": it(), "C": it()}, iid="C", runs=runs) == ("slots_full", []), "max_live")
    chk(lambda: dec({"A": it()}, runs={"Z": {"live": ["m1", "m2", "m3"], "ended": []}}) == ("launch", ["A"]),
        "other runs do not count: live runs on an item that is not the lane's (a mod run) fill no lane slot")
    chk(lambda: dec({"A": it(effect=None, verdict=None), "B": it(effect=None, verdict=None), "C": it()}, iid="C",
                    runs=runs) == ("launch", ["C"]), "live runs on items with no check do not fill the lane's slots")
    chk(lambda: dec({"A": it(depth=2)}) == ("chain_stop", []), "chain depth")
    rows, l, _ = run({"A": it(), "B": it(), "C": it()})
    chk(lambda: l == ["A", "B"] and rows["C"]["decision"] == "slots_full", "two launches in one tick, then full")
    spare = dict(CFG, load_line=28, load_per_run=2)
    five = {k: it() for k in "ABCDE"}
    rows, l, _ = run(five, cfg=spare, load=21.0)
    chk(lambda: l == ["A", "B", "C", "D"] and rows["E"]["decision"] == "slots_full" and "28" in rows["E"]["why"],
        "past its own slots the lane launches while the load, and its launches of this tick, stay under the line (%s)" % l)
    chk(lambda: dec(five, iid="C", cfg=spare, load=40.0) == ("slots_full", ["A", "B"]),
        "over the line the lane keeps its own slots and takes no more")
    chk(lambda: dec(five, iid="C", cfg=spare, load=24.0)[1] == ["A", "B"], "24 + two launches of 2 is at the line")
    chk(lambda: dec(five, iid="C", cfg=spare, load=None) == ("slots_full", ["A", "B"]),
        "a load that could not be read is no spare room")
    chk(lambda: "could not be read" in run(five, cfg=spare, load=None)[0]["C"]["why"], "and the row says so")
    chk(lambda: dec({"A": it(), "B": it(), "C": it()}, iid="C", runs=runs, cfg=spare, load=1.0) == ("launch", ["C"]),
        "live lane runs past max_live: the load decides")
    w = {"A": {"caused_by": None}, "B": {"caused_by": "A"}, "C": {"caused_by": "B"}}
    st = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None}]},
                    "B": {"attempts": [{"unit": "u2", "failed": None}, {"unit": None, "failed": "never started"}]}}}
    chk(lambda: LD().chain_depth("C", lambda i: w.get(i, {}).get("caused_by"), st) == 2,
        "chain depth counts spent lane runs on the ancestors only")


def t_a_ticket_of_an_archmagi_only_home_runs_on_archmagi():
    """2026-11-26: game:art-canon tickets went to SteveDesktop, where the art queue, art_eval and the observed inventory
    are absent. A ticket whose home archmagi_only_homes names takes Archmagi's room though the host has room."""
    hcfg = dict(CFG, hosts={"SteveDesktop": {"max_live": 2, "min_left_pct": 5}},
                archmagi_only_homes={"game:art-canon": "fixture: the art tools are on Archmagi"})
    room = {"SteveDesktop": {"live": 0, "left": 50.0}}
    r, l, _ = run({"A": it(home="game:art-canon"), "B": it(home="game:audio")}, cfg=hcfg, hosts=room)
    chk(lambda: l == ["A", "B"] and not r["A"].get("host") and r["B"].get("host") == "SteveDesktop",
        "an art-canon ticket runs on Archmagi, another home's ticket still goes to the host (%s)"
        % {k: r[k].get("host") for k in "AB"})


def t_a_ready_ticket_goes_to_a_host_with_room_first():
    """A ready ticket that is not mod work goes to a host of cfg["hosts"] first, while the host has fewer live runs than
    its max_live, its account has more than min_left_pct of the week left, its disk holds another clone, its work switch
    allows the ticket, and the ticket needs nothing but offline work. Archmagi takes the run otherwise (its own slots,
    then spare load). Item RIMMANDRAKE_SEND_PIPELINE_TICKETS_TO_STEVEDESKTOP_FIRST_IT_SAT_IDLE: 2026-11-25 SteveDesktop
    sat idle all evening while every lane run started on Archmagi."""
    hcfg = dict(CFG, hosts={"SteveDesktop": {"max_live": 2, "min_left_pct": 5}})
    room = {"SteveDesktop": {"live": 0, "left": 50.0}}
    rows, l, _ = run({k: it() for k in "ABCDE"}, cfg=hcfg, hosts=room)
    chk(lambda: l == ["A", "B", "C", "D"] and rows["A"].get("host") == "SteveDesktop"
        and rows["B"].get("host") == "SteveDesktop" and not rows["C"].get("host") and not rows["D"].get("host")
        and rows["E"]["decision"] == "slots_full" and "SteveDesktop" in rows["E"]["why"],
        "two on the host first, then two own slots, then full, and the row names the host (%s, %s)"
        % (l, [rows[k].get("host") for k in "ABCD"]))
    chk(lambda: "SteveDesktop" in rows["A"]["why"], "the host row says where it runs")
    r, l, _ = run({"A": it()}, cfg=hcfg, hosts=room)
    chk(lambda: r["A"].get("host") == "SteveDesktop" and l == ["A"],
        "one ready ticket with Archmagi's own slots free still goes to the host (%s)" % r["A"].get("host"))
    r, l, _ = run({"A": it()}, cfg=hcfg, hosts={"SteveDesktop": {"live": 0, "left": 4.0}})
    chk(lambda: not r["A"].get("host") and l == ["A"], "an account at or under its line: Archmagi takes it")
    r, l, _ = run({"A": it()}, cfg=hcfg)
    chk(lambda: not r["A"].get("host") and l == ["A"], "a host that could not be read: Archmagi takes it")
    r, l, _ = run({"A": it()}, cfg=hcfg, hosts={"SteveDesktop": {"live": 2, "left": 50.0}})
    chk(lambda: not r["A"].get("host") and l == ["A"], "a host at its max_live: Archmagi takes it")
    r, l, _ = run({"A": it()}, cfg=hcfg, hosts={"SteveDesktop": {"live": 0, "left": 50.0, "pool_more": 0}})
    chk(lambda: not r["A"].get("host") and l == ["A"] and "clone" in r["A"]["why"],
        "a host whose disk holds no more clone (rm-pool-room): Archmagi takes it, and says why (%s)" % r["A"]["why"])
    r, l, _ = run({k: it() for k in "AB"}, cfg=hcfg, hosts={"SteveDesktop": {"live": 0, "left": 50.0, "pool_more": 1}})
    chk(lambda: r["A"].get("host") == "SteveDesktop" and not r["B"].get("host"),
        "a disk that holds one more clone takes one run this tick")
    r, l, _ = run({"A": it(needs="bridge")}, cfg=hcfg, hosts=room)
    chk(lambda: not r["A"].get("host") and l == ["A"] and "needs bridge" in r["A"]["why"],
        "a ticket whose needs is not offline stays on Archmagi and says so (%s)" % r["A"]["why"])
    r, l, _ = run({"A": it(needs="offline")}, cfg=hcfg, hosts=room)
    chk(lambda: r["A"].get("host") == "SteveDesktop", "needs offline goes to the host")
    with patch.object(LD(), "switch_refuses", lambda host, i: "SteveDesktop takes no mod work (Pyre)"):
        r, l, _ = run({"A": it()}, cfg=hcfg, hosts=room)
    chk(lambda: not r["A"].get("host") and l == ["A"] and "no mod work" in r["A"]["why"],
        "a host whose work switch refuses the ticket: Archmagi takes it and says why (%s)" % r["A"]["why"])
    with patch.object(LD(), "switch_refuses", lambda host, i: "SteveDesktop takes no mod work (Pyre)"):
        r, l, _ = run({k: it() for k in "ABC"}, cfg=hcfg, hosts=room)
    chk(lambda: r["C"]["decision"] == "slots_full", "refused by the host and Archmagi's slots full: slots_full")
    chk(lambda: dec({"A": it()}, cfg=hcfg, hosts=room, pool="pool full: 16 clones") == ("launch", ["A"]),
        "Archmagi's full clone pool does not stop a run placed on the host")
    runs = {"A": {"live": ["u1"], "ended": [], "host_live": ["u1"]}}
    chk(lambda: dec({"A": it(), "B": it(), "C": it()}, iid="C", runs=runs, cfg=hcfg) == ("launch", ["B", "C"]),
        "a live host run holds its item but no own slot")
    chk(lambda: LD().load_cfg().get("hosts", {}).get("SteveDesktop"), "the shipped lane names SteveDesktop")


def t_the_reading_says_each_machines_room():
    """reading.json carries `machines`: Archmagi's own live lane runs, slots and load, and each host's facts with its
    max_live and leave line, so the page draws each machine's room as the tick measured it; a host that could not be
    read keeps its None (could not look), never 0."""
    hcfg = dict(CFG, hosts={"SteveDesktop": {"max_live": 6, "min_left_pct": 5}}, load_line=28)
    facts = {"items": {"A": it(), "B": it()}, "runs": {"A": {"live": ["u1"], "ended": []}}, "load": 6.6, "cores": 14,
             "hosts": {"SteveDesktop": {"live": None, "left": None, "left_why": "no ssh", "pool_more": None}}}
    m = LD().machine_reading(hcfg, facts)
    chk(lambda: m["Archmagi"]["live"] == 1 and m["Archmagi"]["max_live"] == 2 and m["Archmagi"]["load"] == 6.6
        and m["Archmagi"]["load_line"] == 28, "Archmagi's own runs, slots and load (%s)" % m.get("Archmagi"))
    chk(lambda: m["SteveDesktop"]["live"] is None and m["SteveDesktop"]["max_live"] == 6
        and m["SteveDesktop"]["min_left_pct"] == 5, "a host that could not be read stays None (%s)" % m.get("SteveDesktop"))
    fx = {"facts": lambda st: facts, "account": lambda: (True, ""), "launch": lambda *a, **k: (0, "DETACHED u9", "u9"),
          "need": lambda *a: None, "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    rd = LD().tick(hcfg, apply=False, fx=fx, now=NOW)
    chk(lambda: set(rd.get("machines") or {}) == {"Archmagi", "SteveDesktop"}, "the reading carries both machines")


def t_a_chain_counts_only_links_that_a_lane_run_filed():
    """chain_stop guards a lane run that files an item that the lane then works. A link of the chain counts only when
    the child was filed by a lane run on its parent (the filing's role unit is one of the parent's lane attempts); a
    child that a hand, the Conductor or another run filed ends the chain there. Measured 2026-11-25 10:52 PM PST: 2 of 5
    chain_stop items had been filed by no lane run."""
    w = {"A": {"caused_by": None}, "B": {"caused_by": "A"}, "C": {"caused_by": "B"}}
    st = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None}]},
                    "B": {"attempts": [{"unit": "u2", "failed": None}]}}}
    par = lambda i: w.get(i, {}).get("caused_by")  # noqa: E731
    chk(lambda: LD().chain_depth("C", par, st, filed_by={"C": "u2", "B": "u1"}.get) == 2,
        "each link filed by a lane run on its parent: both count")
    chk(lambda: LD().chain_depth("C", par, st, filed_by={"C": None, "B": "u1"}.get) == 0,
        "the item filed by a hand: no lane chain feeds it")
    chk(lambda: LD().chain_depth("C", par, st, filed_by={"C": "rm-detached-other-1", "B": "u1"}.get) == 0,
        "the item filed by a run that is no lane run on its parent: the chain ends there")
    chk(lambda: LD().chain_depth("C", par, st, filed_by={"C": "u2", "B": None}.get) == 1,
        "the parent filed by a hand: only the parent's runs count")
    chk(lambda: LD().chain_depth("C", par, st) == 2, "no filing reading: every ancestor counts, as before")


def t_a_clear_grants_one_run_past_the_chain_stop():
    """2026-11-27 5:54 AM PST: three Conductor clears of chain_stop items printed CLEARED and no run started in 50 min;
    the gate read depth and never read `cleared`. A clear by a hand grants one lane run past the chain stop, spent
    when that run launches; a run that never started or did not count (void) spends nothing."""
    clr = lambda at, why="Conductor: one more run": {"at": at, "why": why, "attempts": []}  # noqa: E731
    st = lambda **s: {"items": {"A": dict(s)}}  # noqa: E731
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 60)], attempts=[])) == ("launch", ["A"]),
        "cleared at the chain limit: one launch")
    rows, _, _ = run({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 60, "the gravship call")], attempts=[]))
    chk(lambda: "clear" in rows["A"]["why"] and "the gravship call" in rows["A"]["why"],
        "and the row names the clear and its why (%s)" % rows["A"].get("why"))
    ran = {"at": NOW - 30, "unit": "u9", "failed": None, "next": "LEFT OPEN: more"}
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 60)], attempts=[dict(ran)]),
                    runs={"A": {"live": [], "ended": ["u9"]}}) == ("chain_stop", []),
        "the tick after that run ended: chain_stop again, the grant is spent")
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 60)], attempts=[dict(ran)]),
                    runs={"A": {"live": ["u9"], "ended": []}}) == ("live", []),
        "while the granted run is live: live, no second launch")
    chk(lambda: dec({"A": it(depth=2)}) == ("chain_stop", []), "never cleared: chain_stop")
    old = {"at": NOW - 300, "unit": "u1", "failed": None, "next": "LEFT OPEN: more"}
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 600)], attempts=[dict(old)]),
                    runs={"A": {"live": [], "ended": ["u1"]}}) == ("chain_stop", []),
        "a cleared record older than the item's last run grants nothing")
    chk(lambda: dec({"A": it(depth=2)}, st=st(attempts=[])) == ("chain_stop", []), "a state with no `cleared` key")
    chk(lambda: dec({"A": it(depth=2)}, st={}) == ("chain_stop", []), "a state with no items at all")
    never = {"at": NOW - 30, "unit": None, "failed": "never started: pool full"}
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 60)], attempts=[dict(never)])) == ("launch", ["A"]),
        "a granted launch that never started spends no grant")
    void = {"at": NOW - 7200, "unit": "u9", "failed": None, "void": "killed by a reboot", "void_at": NOW - 7000}
    chk(lambda: dec({"A": it(depth=2)}, st=st(cleared=[clr(NOW - 7300)], attempts=[dict(void)]),
                    runs={"A": {"live": [], "ended": ["u9"]}}) == ("launch", ["A"]),
        "a granted run that did not count (void) spends no grant")
    rows, l, _ = run({"A": it(depth=2), "B": it(depth=2)}, st=st(cleared=[clr(NOW - 60)], attempts=[]))
    chk(lambda: l == ["A"] and rows["B"]["decision"] == "chain_stop", "the grant is the cleared item's only")
    # the command itself: `clear` writes the record that the next tick reads
    p = os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")
    with patch.object(LD().time, "time", return_value=NOW - 5):
        LD().main(["clear", "A", "--why", "Conductor: one more run"])
    with open(p) as f:
        disk = json.load(f)
    chk(lambda: dec({"A": it(depth=2)}, st=disk) == ("launch", ["A"]), "`list_dispatch.py clear` then a tick: launch")
    os.remove(p)


def t_a_clear_is_never_lost_to_a_tick():
    """2026-11-27 10:10 AM PST: `clear` of the split-actuator ticket printed CLEARED while a tick ran; the tick had read
    state.json before the clear and wrote its own copy after, so the 11:00 AM tick still read the item `stopped` and
    the clear was gone. The clear takes the tick's lock: it waits for a running tick and writes on top of its state."""
    import fcntl
    import threading
    d = os.environ["RM_LIST_DISPATCH_DIR"]
    p = os.path.join(d, "state.json")
    with open(p, "w") as f:
        json.dump({"items": {"C": {"attempts": [{"at": NOW - 900, "unit": "u7", "failed": None}]}}}, f)
    held, done = threading.Event(), threading.Event()

    def a_tick():       # what tick() does under apply: lock, read, decide (slow), write its copy, unlock
        with open(os.path.join(d, "tick.lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            with open(p) as f:
                st = json.load(f)
            held.set()
            done.wait(1.5)          # the tick is still deciding when the clear comes
            st["ticked"] = True
            with open(p, "w") as f:
                json.dump(st, f)
    th = threading.Thread(target=a_tick)
    th.start()
    held.wait(5)
    out = []
    cl = threading.Thread(target=lambda: out.append(LD().main(["clear", "C", "--why", "Conductor: one more run"])))
    cl.start()
    cl.join(0.5)
    done.set()
    th.join(10)
    cl.join(10)
    with open(p) as f:
        disk = json.load(f)
    c = (disk.get("items") or {}).get("C") or {}
    chk(lambda: out == [0] and c.get("cleared") and c["cleared"][-1]["why"] == "Conductor: one more run"
        and c.get("attempts") == [], "a clear made while a tick holds the lock survives the tick's write (%s)" % c)
    chk(lambda: disk.get("ticked") is True, "and the tick's own write is kept (%s)" % sorted(disk))


def t_a_clear_keeps_the_runs_in_the_chain():
    """A clear moves an item's attempts under `cleared`. Those runs still filed its children: a clear of the parent
    must not shorten a child's chain, or one clear lets the lane feed itself again through every child."""
    w = {"A": {"caused_by": None}, "B": {"caused_by": "A"}, "C": {"caused_by": "B"}}
    par = lambda i: w.get(i, {}).get("caused_by")  # noqa: E731
    st = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None}]},
                    "B": {"attempts": [], "cleared": [{"at": NOW, "why": "w",
                                                       "attempts": [{"unit": "u2", "failed": None}]}]}}}
    chk(lambda: LD().chain_depth("C", par, st, filed_by={"C": "u2", "B": "u1"}.get) == 2,
        "the parent's cleared runs still count in the child's chain")
    st["items"]["B"]["cleared"][0]["attempts"][0]["void"] = "killed"
    chk(lambda: LD().chain_depth("C", par, st) == 1, "a cleared run that did not count still does not count")


def t_the_tick_counts_recent_lane_launches_before_taking_spare_room():
    import detached_helper as DH
    import list_effect as LE
    import model as LM
    import probe_result as PR

    ld = LD()
    ids = ["RIMMANDRAKE_TEST_LOAD_" + c for c in "ABC"]
    world = LM.replay([{"id": iid, "event": "file", "for": "BENCH", "seat": "BENCH", "kind": "task",
                        "title": iid, "effect": "cmd:false", "ts": "2026-11-22T00:00:00Z"} for iid in ids])
    cfg = dict(CFG, load_line=28, load_per_run=2, load_lag_s=90)
    fx = {"account": lambda: (True, "")}
    with tempfile.TemporaryDirectory(prefix="ld_load_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d), \
            patch.object(LE, "_world", return_value=world), patch.object(ld, "_mods", return_value=[]), \
            patch.object(ld, "_off", return_value=(None, None)), patch.object(ld, "_paused", return_value=None), \
            patch.object(ld, "_held", return_value=None), patch.object(ld, "_pool", return_value=None), \
            patch.object(ld, "_clone_exists", return_value=False), \
            patch.object(DH, "live_status", lambda rec, *a: rec["status"]), \
            patch.object(ld, "load_now", return_value=PR.value(20)):
        def record(n, age, lane="list_dispatch", status="running"):
            DH.write_record({"unit": "u%d" % n, "item": ids[n] if n < 2 else "CLOSED%d" % n, "at": NOW - age,
                             "status": status, "next_act_owner": lane})

        def row():
            return ld.tick(cfg, apply=False, fx=fx, now=NOW, only=[ids[2]])["items"][ids[2]]

        for n, age in enumerate((1, 2, 3, 91)):
            record(n, age)
        record(4, 4, lane="quiet_scan")
        record(5, 5, status="done")
        chk(lambda: row()["decision"] == "would_launch", "three recent launches leave room; old, ended and other-lane runs do not count")
        record(3, 89)
        r = row()
        chk(lambda: r["decision"] == "slots_full" and "28" in r["why"],
            "the tick refuses spare room at load 20 plus four recent lane launches (got %s)" % r["decision"])
        with open(DH.record_path("unreadable"), "w", encoding="utf-8") as f:
            f.write("{")
        os.utime(DH.record_path("unreadable"), (NOW - 1, NOW - 1))     # written inside the lag: it could be recent
        record(3, 91)
        r = row()
        chk(lambda: r["decision"] == "slots_full" and "could not be read" in r["why"],
            "unreadable detached records are no spare room (got %s)" % r["decision"])


def _lag_world():
    """The load-gate fixture: three lane items, two recent lane launches at load 20 (20 + 2 x 2 < 28: room)."""
    import detached_helper as DH
    import list_effect as LE
    import model as LM
    import probe_result as PR
    ld = LD()
    ids = ["RIMMANDRAKE_TEST_UNREAD_" + c for c in "ABC"]
    world = LM.replay([{"id": iid, "event": "file", "for": "BENCH", "seat": "BENCH", "kind": "task",
                        "title": iid, "effect": "cmd:false", "ts": "2026-11-22T00:00:00Z"} for iid in ids])
    cfg = dict(CFG, load_line=28, load_per_run=2, load_lag_s=90)
    pats = [patch.object(LE, "_world", return_value=world), patch.object(ld, "_mods", return_value=[]),
            patch.object(ld, "_off", return_value=(None, None)), patch.object(ld, "_paused", return_value=None),
            patch.object(ld, "_held", return_value=None), patch.object(ld, "_pool", return_value=None),
            patch.object(ld, "_clone_exists", return_value=False),
            patch.object(DH, "live_status", lambda rec, *a: rec["status"]),
            patch.object(ld, "load_now", return_value=PR.value(20))]
    return ld, ids, cfg, pats


def _plant(path, text, age):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.utime(path, (NOW - age, NOW - age))


def t_an_unreadable_record_blinds_only_what_it_can_change():
    import contextlib
    import detached_helper as DH
    ld, ids, cfg, pats = _lag_world()
    fx = {"account": lambda: (True, "")}
    with tempfile.TemporaryDirectory(prefix="ld_unread_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d), \
            contextlib.ExitStack() as es:
        for p in pats:
            es.enter_context(p)
        for n in range(2):
            DH.write_record({"unit": "u%d" % n, "item": ids[n], "at": NOW - 1 - n, "status": "running",
                             "next_act_owner": "list_dispatch"})

        def row():
            return ld.tick(cfg, apply=False, fx=fx, now=NOW, only=[ids[2]])["items"][ids[2]]
        chk(lambda: row()["decision"] == "would_launch", "the fixture leaves room: load 20 plus two recent launches")
        _plant(os.path.join(DH.runs_dir(), "old.json"), "{", 3600)
        r = row()
        chk(lambda: r["decision"] == "would_launch",
            "an unreadable record last written an hour ago cannot be a launch inside the 90 s lag: room is still "
            "counted (got %s: %s)" % (r["decision"], r["why"]))
        facts = ld.gather({}, NOW, load_lag_s=90)
        chk(lambda: facts["unread_old"] == [os.path.join(DH.runs_dir(), "old.json")] and facts["recent"].ok,
            "the old unreadable record is kept in facts, out of the decision (%s)" % facts.get("unread_old"))
        _plant(os.path.join(DH.runs_dir(), "u0.heartbeat.json"), "{", 1)
        _plant(os.path.join(DH.runs_dir(), "u1.alive.json"), '{"act": "renewed"}', 1)
        r = row()
        chk(lambda: r["decision"] == "would_launch",
            "another writer's fresh file in the folder is not a record and blinds nothing (got %s: %s)"
            % (r["decision"], r["why"]))
        fresh = os.path.join(DH.runs_dir(), "fresh.json")
        _plant(fresh, "{", 5)
        r = row()
        chk(lambda: r["decision"] == "slots_full" and fresh in r["why"] and "could not be read" in r["why"],
            "an unreadable record written inside the lag is no spare room, and the row names its file (got %s: %s)"
            % (r["decision"], r["why"]))
        os.remove(fresh)
        notdir = os.path.join(d, "not_a_folder")
        _plant(notdir, "", 1)
        with patch.object(DH, "runs_dir", lambda root=None: notdir):
            r = row()
        chk(lambda: r["decision"] == "blind" and "could not be listed" in r["why"],
            "a run-record folder that cannot be listed hides which runs are live: the row is blind, said, and nothing "
            "launches (got %s: %s)" % (r["decision"], r["why"]))


def t_a_gate_held_on_could_not_look_is_told():
    import list_effect as LE
    import probe_result as PR
    import ops_watch as OW
    d = tempfile.mkdtemp(prefix="ld_blind_")
    os.environ["RM_LIST_DISPATCH_DIR"] = d
    spare = dict(CFG, load_line=28, load_per_run=2)
    runs = {"A": {"live": ["u1"], "ended": []}, "B": {"live": ["u2"], "ended": []}}
    cause = "the run record /x/detached/rm-detached-y.json could not be read and it was written 5 s ago"
    blind = {"items": {"A": it(), "B": it(), "C": it()}, "runs": runs, "other_live": 0, "load": 20.0,
             "recent": PR.could_not_look(cause)}
    clear = dict(blind, recent=PR.value(0), load=99.0)      # no room, read: held, but not on a could-not-look
    acts = []
    fx = {"account": lambda: (True, ""), "launch": lambda *a: acts.append("launch") or (0, "", "u"),
          "need": lambda *a: acts.append("need"), "close": lambda *a: acts.append("close") or (0, ""),
          "effect": lambda *a: acts.append("effect") or (0, "")}

    def tick(facts, t):
        return LD().tick(dict(spare), apply=True, fx=dict(fx, facts=lambda st: facts), now=t)
    rd = None
    for k in range(4):
        rd = tick(blind, NOW + 600 * k)
    bh = rd.get("blind_hold") or {}
    chk(lambda: rd["items"]["C"]["decision"] == "slots_full" and bh.get("passes") == 4 and bh.get("held") == 1
        and bh.get("gate") == "list_dispatch slots_full" and "rm-detached-y.json" in str(bh.get("cause")),
        "four ticks held on an unreadable record: the reading counts 4 passes, 1 held item, the gate and the file (%s)" % bh)
    pt = OW.list_gate_blind(NOW + 1800)
    tg = [t for t in json.load(open(os.path.join(REPO, "src", "RimMandrake", "Utils", "ops_watch_rules.json")))["targets"]
          if t.get("key") == OW.LIST_BLIND_KEY]
    chk(lambda: pt.get("m") == "MEASURED" and pt["v"] == 4 and "rm-detached-y.json" in pt["x"]["said"]
        and "1 item" in pt["x"]["said"] and "list_dispatch slots_full" in pt["x"]["said"],
        "ops_watch reads the streak with the gate, the file and the count in the alarm's title field (%s)" % pt)
    chk(lambda: len(tg) == 1 and tg[0].get("alarm") is True and tg[0]["name"] ==
        "OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK" and tg[0]["op"] == ">" and tg[0]["value"] < pt["v"]
        and tg[0].get("title_field") == "said" and "danger" in tg[0].get("why", ""),
        "one alarm with one fixed item id crosses at 4 passes, and its line names its danger (%s)" % tg)
    chk(lambda: tg and tg[0]["value"] >= 3, "a pass or two held does not cross the line")
    rd = tick(clear, NOW + 2400)
    chk(lambda: rd["blind_hold"]["passes"] == 0 and rd["items"]["C"]["decision"] == "slots_full"
        and OW.list_gate_blind(NOW + 2500)["v"] == 0,
        "room used up, read, is no could-not-look: the streak ends at 0, measured (%s)" % rd["blind_hold"])
    rd = tick(dict(blind, recent=PR.value(0), load=None), NOW + 3000)
    chk(lambda: rd["blind_hold"]["passes"] == 1 and "load average" in rd["blind_hold"]["cause"],
        "a load that could not be read starts a new streak and says so (%s)" % rd["blind_hold"])
    chk(lambda: OW.list_gate_blind(NOW + 3000 + OW.LIST_READING_MAX_AGE_S + 1)["m"] == "UNMEASURED",
        "a stale reading is UNMEASURED, never 0")
    os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ld_none_")
    chk(lambda: OW.list_gate_blind(NOW)["m"] == "UNMEASURED", "no reading is UNMEASURED, never 0")
    chk(lambda: acts == [], "held ticks launched nothing (%s)" % acts)
    os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ld_blind2_")
    rd = None
    for k in range(2):
        rd = LD().tick(dict(spare), apply=True, fx=dict(fx, facts=lambda st: {"items": None}), now=NOW + 600 * k)
    chk(lambda: rd["blind_hold"]["passes"] == 2 and "ledger" in rd["blind_hold"]["cause"],
        "an unreadable ledger is a hold on a could-not-look too (%s)" % rd["blind_hold"])
    rd = LD().tick(dict(spare), apply=True, fx=dict(fx, facts=lambda st: clear), now=NOW + 1300, only=["C"])
    chk(lambda: rd["blind_hold"]["passes"] == 2,
        "a run-now (--only) tick sees part of the lane: it neither ends nor counts the streak (%s)" % rd["blind_hold"])
    rd = LD().tick(dict(spare), apply=True, now=NOW + 1900, fx=dict(
        fx, facts=lambda st: {"items": {"Z": it(verdict="holds", out="x")}, "runs": {}, "other_live": 0},
        close=lambda *a: (LE.LIVE_BLIND, "the check could not be read live")))
    chk(lambda: rd["items"]["Z"]["decision"] == "blind" and rd["blind_hold"]["passes"] == 3,
        "a close that the live check could not decide is a hold on a could-not-look (%s, %s)"
        % (rd["items"]["Z"], rd["blind_hold"]))


def t_a_lane_run_on_a_mod_takes_no_mod_slot():
    import maturation_dispatch as MD
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import maturation_now as MN
    v = MN.run_view({"unit": "u-lane", "item": "X", "status": "running", "at": NOW, "next_act_owner": "list_dispatch"}, NOW)
    chk(lambda: v.get("lane") == "list_dispatch", "a run's view carries the lane that launched it (%s)" % v.get("lane"))
    f = {"FlowWorks": {"live_units": ["u-drive", "u-lane"], "lane_units": ["u-lane"]},
         "Pyrelands": {"live_units": ["u-pyre"], "lane_units": []}, "ExplosiveKnockback": {"live_units": []}}
    chk(lambda: MD.occupancy(f) == 2, "the mod tick's slots count mod runs, not the Workshop Pipeline's (%s)" % MD.occupancy(f))
    chk(lambda: MD.occupancy({"A": {"live_units": MD.UNM, "lane_units": ["u"]}}) is None,
        "an unreadable mod is still an unknown occupancy")
    keep = MD.MN.gather, MD.M.build_facts, MD.M.load
    MD.MN.gather = lambda root, live=True: {"mods": [{"name": "FlowWorks", "boxes": {}, "runs": [
        dict(v, unit="u-lane", live=True, end=None), dict(v, unit="u-drive", lane=None, live=True, end=None),
        dict(v, unit="u-old", live=False, end=NOW)]}]}
    MD.M.build_facts = lambda root, mod: {"mod": mod, "stage": "designer"}
    MD.M.load = lambda root, mod: {"stage": "designer"}
    try:
        g = MD.gather(REPO, {"advancing": ["FlowWorks"]})["FlowWorks"]
    finally:
        MD.MN.gather, MD.M.build_facts, MD.M.load = keep
    chk(lambda: g["live_units"] == ["u-lane", "u-drive"] and g["lane_units"] == ["u-lane"],
        "gather: the lane's run is live on the mod, and named as the lane's (%s, %s)" % (g.get("live_units"), g.get("lane_units")))


def t_a_claimed_item_is_not_the_lanes():
    chk(lambda: dec({"A": it(claimed="BENCH holds a live lease")}) == ("claimed", []), "a claimed item: no launch")
    chk(lambda: dec({"A": it(effect=None, verdict=None, accept="a/b_accept.py", claimed="BENCH holds a live lease")})
        == ("claimed", []), "a claimed item is not adopted")
    chk(lambda: dec({"A": it(claimed="BENCH")}, st=att({"unit": "u1", "failed": None, "next": "x"}),
                    runs={"A": {"live": [], "ended": ["u1"]}}) == ("launch", ["A"]),
        "the lane's own run's lease does not stop its second run")


def t_a_raised_item_goes_first():
    items = {"OLD": it(filed=1.0), "WAITED_ON": it(filed=2.0, blocks_others=True),
             "SECOND": it(filed=9.0, raised=(0, "2026-11-24T17:02:00Z", 0)),
             "FIRST": it(filed=8.0, raised=(0, "2026-11-24T17:01:00Z", 0))}
    chk(lambda: LD().order_ids(items) == ["FIRST", "SECOND", "WAITED_ON", "OLD"],
        "raised items first, in the order they were raised (%s)" % LD().order_ids(items))


def t_oldest_blocking_item_first():
    items = {"NEW": {"filed": 30, "blocks_others": False}, "OLD": {"filed": 10, "blocks_others": False},
             "BLK": {"filed": 20, "blocks_others": True}}
    chk(lambda: LD().order_ids(items) == ["BLK", "OLD", "NEW"], "blocking first, then oldest")


def t_the_run_owns_no_continuation():
    import left_open_continue as LOC
    rec = {"unit": "u1", "item": "A", "result": "success (exit 0)", "at": 1, "next_act_owner": "list_dispatch"}
    got = {"state": "doing", "notes": [{"id": "A", "event": "note", "ts": "2030-01-01T00:00:00Z",
                                        "text": "LEFT OPEN: do the rest"}]}
    p = LOC.plan(rec, got, {}, now=NOW, gates={})
    chk(lambda: p["act"] == "none" and "list_dispatch" in p["why"], "left_open_continue does not continue a lane run")
    import detached_helper as DH
    src = open(DH.__file__, encoding="utf-8").read()
    chk(lambda: "--next-act-owner" in src, "detached_helper launch takes --next-act-owner")
    calls = []
    import list_dispatch
    orig = list_dispatch.subprocess.run

    class R:
        returncode, stdout, stderr = 0, "DETACHED rm-detached-x\n", ""
    list_dispatch.subprocess.run = lambda argv, **k: calls.append(argv) or R()
    try:
        rc, out, unit = list_dispatch.launch("A", "sonnet", 5, "brief", "BENCH", None)
    finally:
        list_dispatch.subprocess.run = orig
    chk(lambda: unit == "rm-detached-x" and "--next-act-owner" in calls[0] and "list_dispatch" in calls[0],
        "the lane's launch passes --next-act-owner list_dispatch")


def t_the_tick_files_nothing():
    src = open(os.path.join(HERE, "list_dispatch.py"), encoding="utf-8").read()
    chk(lambda: '"file"' not in src and '"spawn"' not in src, "the module names no file or spawn verb")
    adopted = []
    fx = {"facts": lambda st: {"items": {"A": it(effect=None, verdict=None, accept="design/x/step9_accept.py")},
                               "runs": {}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a: (_ for _ in ()).throw(AssertionError("launched")),
          "need": lambda *a: None, "close": lambda *a: (0, ""),
          "effect": lambda iid, check, why: adopted.append((iid, check)) or (0, "PUBLISHED x")}
    rd = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    chk(lambda: adopted == [("A", "cmd:python3 design/x/step9_accept.py")] and rd["items"]["A"]["decision"] == "adopted",
        "an acceptance script in ## verify is attached as the check; nothing is launched that tick")
    chk(lambda: LD().accept_script("## verify\npython3 src/RimMandrake/rimflow/acceptance/step1_outcome_check_accept.py"
                                   "   # exit 0\n", exists=lambda p: True)
        == "src/RimMandrake/rimflow/acceptance/step1_outcome_check_accept.py", "accept_script reads the verify line")
    chk(lambda: LD().accept_script("## spec\npython3 a/b_accept.py\n", exists=lambda p: True) is None,
        "accept_script reads only ## verify and ## criteria")
    chk(lambda: LD().accept_script("## verify\npython3 a/missing_accept.py\n", exists=lambda p: False) is None,
        "a script that does not exist is not adopted")
    os.remove(os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json"))


def t_a_heavy_acceptance_script_is_not_adopted():
    cfg = dict(CFG, max_adopt_check_s=60)
    chk(lambda: dec({"A": it(effect=None, verdict=None, accept="a/b_accept.py", accept_s=None)}, cfg=cfg)
        == ("adopt_too_heavy", []), "a script that outran the bound is not adopted")
    chk(lambda: dec({"A": it(effect=None, verdict=None, accept="a/b_accept.py", accept_s=3.0)}, cfg=cfg)
        == ("adopt", []), "a quick script is adopted")
    import subprocess as SP

    def slow(argv, **k):
        raise SP.TimeoutExpired(argv, k.get("timeout"))
    chk(lambda: not LD().time_script("a/b_accept.py", 60, runner=slow).ok
        and "60" in LD().time_script("a/b_accept.py", 60, runner=slow).cause, "a script past the bound: could not look, why")
    chk(lambda: isinstance(LD().time_script("a/b_accept.py", 60, runner=lambda argv, **k: None).value, float),
        "a script that ends inside the bound reads its seconds")
    st = {"items": {}}
    calls = []
    t = LD().timed_accept("A", "a/b_accept.py", 7, st, 60, runner=lambda argv, **k: calls.append(1))
    t2 = LD().timed_accept("A", "a/b_accept.py", 7, st, 60, runner=lambda argv, **k: calls.append(1))
    chk(lambda: len(calls) == 1 and t == t2, "a script is timed once per item state, not every tick")


def t_a_write_that_stands_unlanded_is_not_a_refusal():
    d = tempfile.mkdtemp(prefix="ld_rc4_")
    os.environ["RM_LIST_DISPATCH_DIR"] = d
    fx = {"facts": lambda st: {"items": {"A": it(verdict="holds"),
                                         "B": it(effect=None, verdict=None, accept="a/b_accept.py", accept_s=1.0)},
                               "runs": {}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a: (0, "", "u"), "need": lambda *a: None,
          "close": lambda *a: (4, "closed at abc. WRITTEN, NOT PUBLISHED: ./publish exited 2: origin moved"),
          "effect": lambda *a: (4, "outcome check attached. WRITTEN, NOT PUBLISHED: ./publish exited 2")}
    rd = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    st = json.load(open(os.path.join(d, "state.json")))
    chk(lambda: rd["items"]["A"]["decision"] == "closed_by_check" and "close_refused" not in st["items"].get("A", {}),
        "exit 4 on close: the close stands (closed_by_check), not refused")
    chk(lambda: rd["items"]["B"]["decision"] == "adopted" and "adopt_refused" not in st["items"].get("B", {}),
        "exit 4 on attach: the check stands (adopted), not refused")
    chk(lambda: "not landed" in rd["items"]["A"]["why"], "the row says the write is not landed yet")


def t_a_refused_close_a_run_can_repair_gets_one_run():
    """Item RIMMANDRAKE_ROUTE_GUARD_REFUSED_CLOSE_TO_A_RUN_TWO_RANG_TONIGHT: a reopened alarm item whose check holds and
    whose close is refused for a cause that a run can repair (a guard owed, a live line, an owed criterion) reads launch,
    not close_refused; its brief carries the refusal; a live run on it owns the close; once that run ended and the close
    still refuses, the lane rings the Conductor once, quoting the refusal."""
    guard = ("close refused (an owed criterion): close: A has not earned its close at f7c41cab4e: guard this fix died 1 "
             "time(s), so it closes only with a class guard test shown failing on the instance; repair: verify the criterion")
    ref = lambda why, ev=5: {"items": {"A": {"close_refused": {"fp": ["cmd:x", ev], "why": why, "at": NOW - 600}}}}  # noqa: E731
    item = lambda ev=5: {"A": it(effect="cmd:x", verdict="holds", events=ev, out="holds")}  # noqa: E731
    rows, launches, _ = run(item(), st=ref(guard))
    r = rows["A"]
    chk(lambda: r["decision"] == "launch" and launches == ["A"] and r.get("kind") == "close_fix",
        "a guard-owed close refusal reads launch, not close_refused (%s, %s)" % (r.get("decision"), launches))
    chk(lambda: "guard" in (r.get("close_fix") or "") and "refused" in r.get("why", ""),
        "the row carries the refusal and says why it launches")
    brief = LD().brief_text("A", item()["A"], r)
    chk(lambda: "class guard test" in brief and "refused" in brief and "holds" in brief,
        "the run's brief carries the refusal and says the check holds")
    live_line = ("close refused (an operational item needs its live line): close: A needs a live line: it is an "
                 "Operations alarm; repair: close with --live naming what must stay alive")
    d, l2 = dec(item(), st=ref(live_line))
    chk(lambda: d == "launch" and l2 == ["A"], "a live-line refusal goes to a run too (%s)" % d)
    other = "close refused (a cause this tool does not know): something odd"
    d, l3 = dec(item(), st=ref(other))
    chk(lambda: d == "close_refused" and l3 == [], "a refusal of a cause no run is known to repair stays close_refused")
    rows, launches, _ = run(item(ev=7), st=ref(guard, ev=5), runs={"A": {"live": ["u-fix"]}})
    chk(lambda: rows["A"]["decision"] == "live" and launches == [],
        "while a run is live on a refused item it owns the close: no second close (%s)" % rows["A"]["decision"])
    st = ref(guard)
    st["items"]["A"]["attempts"] = [{"at": NOW - 300, "unit": "u-fix", "model": "opus", "cap": 12, "kind": "close_fix",
                                     "failed": None}]
    rows, launches, _ = run(item(), st=st, runs={"A": {"ended": ["u-fix"]}})
    r = rows["A"]
    chk(lambda: r["decision"] == "stopped" and launches == [] and r.get("need") and "guard" in str(r.get("need")),
        "after its close-fix run ended and the close still refuses: one stop that rings the Conductor with the refusal "
        "(%s)" % r.get("decision"))
    st["items"]["A"]["attempts"] = [{"at": NOW - 300, "unit": "u-shape", "model": "opus", "cap": 12, "kind": "shape",
                                     "failed": None}]
    d, l4 = dec(item(), st=st, runs={"A": {"ended": ["u-shape"]}})
    chk(lambda: d == "launch" and l4 == ["A"], "a Shape run that wrote the check is no close-fix run: the fix run still "
        "starts (%s)" % d)


def t_a_dry_tick_writes_nothing():
    d = tempfile.mkdtemp(prefix="ld_dry_")
    os.environ["RM_LIST_DISPATCH_DIR"] = d
    acts = []
    fx = {"facts": lambda st: {"items": {"A": it(), "B": it(verdict="holds"),
                                         "C": it(effect=None, verdict=None, accept="a/b_accept.py")},
                               "runs": {}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a: acts.append("launch") or (0, "", "u"),
          "need": lambda *a: acts.append("need"), "close": lambda *a: acts.append("close") or (0, ""),
          "effect": lambda *a: acts.append("effect") or (0, "")}
    rd = LD().tick(dict(CFG), apply=False, fx=fx, now=NOW)
    chk(lambda: acts == [] and os.listdir(d) == [] and rd["items"]["A"]["decision"] == "would_launch",
        "a dry tick acts on nothing and writes no state (%s, %s)" % (acts, os.listdir(d)))


def t_only_narrows_the_items_never_the_gates():
    base = {"items": {"A": it(), "B": it()}, "runs": {}, "other_live": 0}
    fx = {"facts": lambda st: json.loads(json.dumps(base)), "account": lambda: (True, "")}
    rd = LD().tick(dict(CFG), apply=False, fx=fx, now=NOW, only=["B", "GONE"])
    chk(lambda: set(rd["items"]) == {"B", "GONE"} and rd["items"]["B"]["decision"] == "would_launch"
        and rd["items"]["GONE"]["decision"] == "not_found", "--only works only the named items; an unknown one says so")
    fx2 = {"facts": lambda st: json.loads(json.dumps(base)), "account": lambda: (False, "drain")}
    rd2 = LD().tick(dict(CFG), apply=False, fx=fx2, now=NOW, only=["B"])
    chk(lambda: rd2["items"]["B"]["decision"] == "account_hold", "--only still passes every gate")


def t_a_mod_ticket_is_not_the_list_pipelines():
    """A ticket whose home is mod:<folder>, or whose repo paths all lie in one mod's folder, is not offered, launched,
    checked or fed to Codex; its status line names the mod's Maturation Pipeline run. A pipeline ticket that names a
    mod only as its example stays. A home that cannot be read launches nothing and says could not look."""
    import list_effect as LE
    import list_home as LH
    import list_pipeline as LP
    import model as LM
    import mod_work as MW
    mods = {"HugeThings", "FlowWorks"}
    # the tick's stage of a mod ticket with a live run is Work, as list_pipeline.stage_of says over the ledger
    mwi = it(mod_work={"mod": "FlowWorks", "why": "home mod:FlowWorks"})
    rows, _l, _ = run({"A": mwi}, runs={"A": {"live": ["u1"], "ended": []}})
    chk(lambda: rows["A"]["decision"] == "mod_work" and LD().row_stage(mwi, rows["A"], NOW) == "work",
        "a mod ticket with a live run reads stage work on the tick, as on the page (%s)"
        % LD().row_stage(mwi, rows["A"], NOW))
    rows, _l, _ = run({"A": mwi})
    chk(lambda: LD().row_stage(mwi, rows["A"], NOW) == "waiting", "a mod ticket with no live run reads stage waiting")
    of = MW.of
    home = {"home": "mod:HugeThings", "group": "g", "flag": "LOOKS CURRENT"}
    chk(lambda: of({"home": home, "title": "keep the warned edge"}, mods)["mod"] == "HugeThings", "a home mod:X: X's work")
    chk(lambda: of({"title": "crash in src/RimMandrake/HugeThings/Source/Titan.cs"}, mods)["mod"] == "HugeThings",
        "no home, every path inside src/**/HugeThings/: HugeThings' work")
    chk(lambda: of({"title": "t"}, mods, "see design/concepts/FlowWorks/version/bars.md")["mod"] == "FlowWorks",
        "no home, a prose path inside design/concepts/FlowWorks/: FlowWorks' work")
    ex = of({"title": "list_dispatch launches HugeThings twice",
             "effect": "cmd:python3 src/RimMandrake/rimflow/selftest_list_dispatch.py"}, mods,
            "for example src/RimMandrake/HugeThings/About/About.xml")
    chk(lambda: ex["mod"] is None and not ex["unreadable"], "a pipeline ticket that names a mod as its example stays")
    chk(lambda: of({"title": "HugeThings titans rot"}, mods)["mod"] is None, "a mod named by a word only stays")
    chk(lambda: of({"title": "src/RimMandrake/HugeThings/a src/RimMandrake/FlowWorks/b"}, mods)["mod"] is None,
        "paths in two mods: not one mod's work")
    chk(lambda: of({"home": dict(home, home="pipeline:list"), "title": "src/RimMandrake/HugeThings/a"}, mods)["mod"]
        is None, "a home pipeline:<part> stays, whatever its paths")
    chk(lambda: all(of({"home": h, "title": "t"}, mods)["unreadable"] for h in ("mod:HugeThings", {"home": None}, {})),
        "a home that is not a {home: <kind>:<name>} record: could not look")
    chk(lambda: of({"title": "t"}, mods, None)["unreadable"], "prose that could not be read: could not look")
    # the tick: no check, no launch; the row names the mod's run
    mw_mod, mw_ex = of({"home": home}, mods), ex
    mw_blind = of({"home": "x"}, mods)
    rows, launches, _ = run({"A": it(mod_work=mw_mod), "B": it(mod_work=mw_ex), "C": it(mod_work=mw_blind)})
    chk(lambda: rows["A"]["decision"] == "mod_work" and "Maturation Pipeline run of HugeThings" in rows["A"]["why"]
        and "A" not in launches, "decide: a mod ticket reads mod_work, names the mod's run, launches nothing (%s)"
        % rows["A"])
    chk(lambda: rows["B"]["decision"] == "launch" and "B" in launches, "decide: the pipeline example is launched")
    chk(lambda: rows["C"]["decision"] == "blind" and "could not look" in rows["C"]["why"] and "C" not in launches,
        "decide: an unreadable home is blind, could not look, no launch")
    rows2, _l, _ = run({"A": it(mod_work=mw_mod, effect=None, verdict=None, accept="x_accept.py")})
    chk(lambda: rows2["A"]["decision"] == "mod_work", "decide: a mod ticket's acceptance script is not adopted")
    # the status line on the page: one stage function
    st_mod = LP.stage_of(LP.facts({"state": "ready", "effect": "cmd:false"}, mod_work=mw_mod, now=NOW), NOW)
    st_bl = LP.stage_of(LP.facts({"state": "ready", "effect": "cmd:false"}, mod_work=mw_blind, now=NOW), NOW)
    st_ex = LP.stage_of(LP.facts({"state": "ready", "effect": "cmd:false"}, lane_row={"decision": "launch", "why": "w"},
                                 lane_at=NOW, mod_work=mw_ex, now=NOW), NOW)
    chk(lambda: st_mod["stage"] == "waiting" and "Maturation Pipeline run of HugeThings" in st_mod["why"],
        "stage_of: waits for the Maturation Pipeline run of the mod (%s)" % st_mod)
    chk(lambda: st_bl["stage"] == "unmeasured" and "could not look" in st_bl["why"], "stage_of: could not look (%s)" % st_bl)
    chk(lambda: st_ex["stage"] == "ready", "stage_of: the pipeline example stays ready (%s)" % st_ex)
    # the gather of a real tick: the mod ticket's check is not run
    ids = ["RIMMANDRAKE_TEST_MODWORK_" + c for c in "ABC"]
    evs = [{"id": iid, "event": "file", "for": "BENCH", "seat": "BENCH", "kind": "task", "title": t, "effect": "cmd:false",
            "ts": "2026-11-22T00:00:00Z"} for iid, t in zip(ids, ("keep the warned edge",
                                                                    "fix src/RimMandrake/HugeThings/Source/T.cs",
                                                                    "list_dispatch.py names HugeThings as an example"))]
    evs.append(dict(home, id=ids[0], event="home", seat="BENCH", ts="2026-11-22T00:01:00Z"))
    world = LM.replay(evs)
    ran = []
    ld = LD()
    with tempfile.TemporaryDirectory(prefix="ld_mw_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d,
                                                                         RM_CONTROL_MOD_FOLDERS="HugeThings,FlowWorks",
                                                                         RM_CONTROL_MODS="FlowWorks"), \
            patch.object(LE, "_world", return_value=world), patch.object(ld, "_off", return_value=(None, None)), \
            patch.object(ld, "_paused", return_value=None), patch.object(ld, "_held", return_value=None), \
            patch.object(ld, "_pool", return_value=None), patch.object(ld, "_clone_exists", return_value=False), \
            patch.object(LE, "run", lambda eff, root: ran.append(eff) or ("fails", "red")):
        rd = ld.tick(dict(CFG), apply=False, fx={"account": lambda: (True, "")}, now=NOW)["items"]
        chk(lambda: [rd[i]["decision"] for i in ids] == ["mod_work", "mod_work", "would_launch"] and len(ran) == 1,
            "the tick: home and path tickets read mod_work and their checks never run; the example would launch (%s, %d "
            "checks run)" % ([rd.get(i, {}).get("decision") for i in ids], len(ran)))
        # the Codex feed: list_home offer hands out only the example; a broken home is not offered
        world.items[ids[2]].home, keep = "garbled", world.items[ids[2]].home
        o = LH.offer(world.items, ids, MW.mods())
        world.items[ids[2]].home = keep
        o2 = LH.offer(world.items, ids, MW.mods())
    chk(lambda: o2["offer"] == [ids[2]] and o2["mods"] == {"HugeThings": ids[:2]} and not o2["blind"],
        "list_home offer: only the pipeline ticket is offered; the two are counted under HugeThings (%s)" % o2)
    chk(lambda: o["offer"] == [] and list(o["blind"]) == [ids[2]], "list_home offer: an unreadable home is not offered")


def t_a_lane_run_holds_its_mod_only_on_its_files():
    import subprocess
    import time
    import maturation_dispatch as MD
    git = lambda d, *a: subprocess.run(["git", "-C", d] + list(a), capture_output=True, text=True, check=True)  # noqa: E731
    with tempfile.TemporaryDirectory() as td:
        origin, clone = os.path.join(td, "o.git"), os.path.join(td, "c")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
        subprocess.run(["git", "clone", "-q", origin, clone], check=True, capture_output=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            git(clone, "config", k, v)
        os.makedirs(os.path.join(clone, "src", "RimMandrake", "rimflow"))
        os.makedirs(os.path.join(clone, "src", "RimMandrake", "FlowWorks", "northstar"))
        os.makedirs(os.path.join(clone, "design", "concepts", "FlowWorks"))
        open(os.path.join(clone, "README"), "w").write("x\n")
        git(clone, "add", "README")
        git(clone, "commit", "-qm", "base")
        git(clone, "push", "-q", "origin", "HEAD:main")
        rec = {"clone": clone, "item": "RIMMANDRAKE_X_FLOWWORKS_Y", "at": time.time() - 60}
        on = lambda: (lambda a: a.value if a.ok else a.kind)(MD.lane_on_mod_files("u", "FlowWorks", record=lambda u: rec))  # noqa: E731
        chk(lambda: on() is False, "a lane run with no change is beside its mod, not on it (%s)" % on())
        p = os.path.join(clone, "src", "RimMandrake", "rimflow", "tick.py")
        open(p, "w").write("x\n")
        git(clone, "add", p)
        git(clone, "commit", "-qm", "RIMMANDRAKE_X_FLOWWORKS_Y: pipeline code")
        git(clone, "push", "-q", "origin", "HEAD:main")
        chk(lambda: on() is False, "a lane run on pipeline code only is not on its mod's files (%s)" % on())
        q = os.path.join(clone, "src", "RimMandrake", "FlowWorks", "northstar", "p.py")
        open(q, "w").write("x\n")
        chk(lambda: on() is True, "an untracked file in the mod's folder holds the mod (%s)" % on())
        git(clone, "add", q)
        git(clone, "commit", "-qm", "unnamed local commit")
        chk(lambda: on() is True, "a local commit on the mod's files holds the mod (%s)" % on())
        git(clone, "push", "-q", "origin", "HEAD:main")
        git(clone, "fetch", "-q")
        chk(lambda: on() is False, "a pushed commit that names no item is not this run's (%s)" % on())
        c = os.path.join(clone, "design", "concepts", "FlowWorks", "polish.md")
        open(c, "w").write("x\n")
        git(clone, "add", c)
        git(clone, "commit", "-qm", "RIMMANDRAKE_X_FLOWWORKS_Y: polish line")
        git(clone, "push", "-q", "origin", "HEAD:main")
        git(clone, "fetch", "-q")
        chk(lambda: on() is True, "a published commit that names its item, in the concept folder, holds the mod (%s)" % on())
        chk(lambda: MD.lane_on_mod_files("u", "Pyrelands", record=lambda u: rec).value is False,
            "another mod's files do not hold this mod")
        chk(lambda: MD.lane_on_mod_files("u", "FlowWorks", record=lambda u: None).kind == "could_not_look",
            "no record reads could-not-look (held)")
        chk(lambda: MD.lane_on_mod_files("u", "FlowWorks", record=lambda u: dict(rec, clone=os.path.join(td, "gone")))
            .kind == "could_not_look", "a missing clone reads could-not-look (held)")
        bad = lambda *a, **k: subprocess.CompletedProcess(a, 128, "", "fatal")  # noqa: E731
        chk(lambda: MD.lane_on_mod_files("u", "FlowWorks", record=lambda u: rec, run=bad).kind == "could_not_look",
            "a git error reads could-not-look (held)")
    # gather: a lane run beside its mod is not live on it; one held or unreadable stays live
    import maturation_now as MN
    v = MN.run_view({"unit": "u-lane", "item": "X", "status": "running", "at": NOW, "next_act_owner": "list_dispatch"}, NOW)
    keep = MD.MN.gather, MD.M.build_facts, MD.M.load, MD.lane_on_mod_files
    MD.MN.gather = lambda root, live=True: {"mods": [{"name": "FlowWorks", "boxes": {}, "runs": [
        dict(v, unit="u-beside", live=True, end=None), dict(v, unit="u-on", live=True, end=None),
        dict(v, unit="u-blind", live=True, end=None), dict(v, unit="u-drive", lane=None, live=True, end=None)]}]}
    MD.M.build_facts = lambda root, mod: {"mod": mod, "stage": "designer"}
    MD.M.load = lambda root, mod: {"stage": "designer"}
    import probe_result as PR
    seen = {"u-beside": PR.value(False), "u-on": PR.value(True)}
    MD.lane_on_mod_files = lambda u, m: seen[u] if u in seen else PR.could_not_look("unread")
    try:
        g = MD.gather(REPO, {"advancing": ["FlowWorks"]})["FlowWorks"]
    finally:
        MD.MN.gather, MD.M.build_facts, MD.M.load, MD.lane_on_mod_files = keep
    chk(lambda: g["live_units"] == ["u-on", "u-blind", "u-drive"] and g["lane_beside"] == ["u-beside"]
        and g["lane_units"] == ["u-on", "u-blind"],
        "gather: only a lane run on the mod's files, or unreadable, is live on it (%s, %s, %s)"
        % (g.get("live_units"), g.get("lane_units"), g.get("lane_beside")))


def t_each_limit_names_its_danger():
    c = LD().load_cfg()
    nums = [k for k, v in c.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_")]
    chk(lambda: nums and all(str(c.get("_%s_doc" % k) or "").strip() for k in nums),
        "every numeric setting has its _doc (%s)" % ", ".join(k for k in nums if not c.get("_%s_doc" % k)))


def t_blocked_idle_window_open_is_due():
    """The age line (P-5 of the retired Producer, revived by the Conductor 2026-11-25; table
    design/RimMandrake/retired_v3_role_duties_2026-11-23.md): a block idle past block_idle_days whose `needs` window
    opened block_window_min times or more since the item's last own event is due for Shape. Measured 2026-11-24: 30
    items blocked past 3 days, 18 of them with a window that had opened since, and no program looked at one."""
    import model as LM
    L = LD()
    cfg = dict(CFG, block_idle_days=3, block_window_min=2)
    day = 86400.0

    def ts(t):
        import datetime as dt
        return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def world(needs, block_at, opens, verb="game", state="UP", block=True, extra=(), kind="external"):
        n = [0]

        def ev(t, **k):
            n[0] += 1
            return dict({"seat": "BENCH", "ts": ts(t), "tsn": n[0]}, **k)
        evs = [ev(block_at - 60, event="file", id="LD_AGE_LINE_ITEM_ONE", title="t", kind="task", needs=needs,
                  **{"for": "BENCH"})]
        if block:
            evs.append(ev(block_at, event="block", id="LD_AGE_LINE_ITEM_ONE", reason="needs a live game", kind=kind,
                          **({"lift_at": ts(NOW + 30 * day)} if kind == "time" else {})))
        evs += [ev(t, event="bridge", state="released") if verb == "bridge" else
                dict(ev(t, event="game", state=state), seat="OWNER") for t in opens]     # only OWNER stamps the game
        evs += [ev(t, **k) for t, k in extra]
        evs.sort(key=lambda e: e["ts"])
        op = L.Openings()
        w = LM.replay(evs, observe=op.observe)
        return L.block_age(w.items["LD_AGE_LINE_ITEM_ONE"], op, NOW, cfg)

    old = NOW - 5 * day
    due, why = world("game-up", old, [old + day, old + 2 * day])
    chk(lambda: due and "2" in why and "5.0 d" in why and "unblock" in why and "--home mod:" in why,
        "a block idle 5 days whose game came UP twice since: due; the why names both, the repair, and the mod's home "
        "(an old mod ticket that mod_work.of misses: LONGSHADE_BEDAZZLE_MECHANICS_1, 2026-11-25) (%s)" % why)
    chk(lambda: world("bridge", old, [old + day, old + 2 * day], verb="bridge")[0],
        "needs bridge: two bridge releases since open its window")
    chk(lambda: not world("game-up", NOW - 2 * day, [NOW - day, NOW - 3600])[0],
        "idle 2 days: not due yet, however often the window opened")
    chk(lambda: not world("game-up", old, [old + day])[0], "the window opened once: not due")
    chk(lambda: not world("game-up", old, [old - 3 * day, old - 2 * day])[0],
        "openings before its last own event do not count")
    note = (old + 4 * day, {"event": "note", "id": "LD_AGE_LINE_ITEM_ONE", "text": "still blocked: checked"})
    chk(lambda: not world("game-up", old, [old + day, old + 2 * day], extra=[note])[0],
        "a later event of its own restarts the idle clock")
    chk(lambda: not world("game-up", old, [old + day, old + 2 * day], state="DOWN")[0], "a game DOWN opens nothing")
    for needs in ("offline", "deploy", "harvest", "owner", None):
        chk(lambda needs=needs: not world(needs, old, [old + day, old + 2 * day])[0],
            "needs %s: no ledger event opens that window, so the age line never fires" % needs)
    chk(lambda: not world("game-up", old, [old + day, old + 2 * day], block=False)[0], "an item with no block")
    for kind in ("owner", "time"):      # his word, or its own date, lifts it: a game window is never its lift event
        chk(lambda kind=kind: not world("game-up", old, [old + day, old + 2 * day], kind=kind)[0],
            "a block of kind %s never goes stale by its needs window (the faction-work park of 2026-11-26)" % kind)
    stale = "its block (needs a live game) idle 5.0 d; the game came UP 2 times since"
    r, l, _ = run({"A": it(blocked=True, effect=None, verdict=None, shape_due=True, shape_why=stale, block_stale=stale)})
    chk(lambda: r["A"]["decision"] == "shape" and l == ["A"] and stale in r["A"]["why"],
        "a stale block on an item with no check: one Shape run, whose why is the age line (%s)" % r["A"])
    r, l, _ = run({"A": it(blocked=True, block_stale=stale)})
    chk(lambda: r["A"]["decision"] == "launch" and l == ["A"] and r["A"].get("stale_block") == stale,
        "a stale block on an item whose check fails: one Work run, and the row carries the age line (%s)" % r["A"])
    b = L.brief_text("A", it(blocked=True, block_stale=stale), {"run_n": 1, "stale_block": stale})
    chk(lambda: stale in b and "unblock" in b, "the Work brief names the stale block and how to lift it")
    chk(lambda: "stale block" not in L.brief_text("A", it(), {"run_n": 1}).lower(), "a plain Work brief names no block")
    chk(lambda: dec({"A": it(blocked=True)}) == ("blocked", []), "a block that is not stale still reads blocked")
    chk(lambda: dec({"A": it(blocked=True, block_stale=stale, held="held by the owner")})[0] == "held",
        "every later gate still stops a stale block (held)")
    # gather: an item already due for Shape by itself (filed after shape_from, past its grace) whose block is stale.
    # Before the age line its block held it; now it launches, so its Shape why must still name the block.
    import contextlib
    import list_effect as LE
    ld, _ids, _cfg, pats = _lag_world()
    iid = "LD_AGE_LINE_ITEM_ONE"
    base = NOW - 5 * day
    evs = [{"seat": "BENCH", "ts": ts(base - 60), "tsn": 1, "event": "file", "id": iid, "title": "t", "kind": "task",
            "needs": "game-up", "for": "BENCH"},
           {"seat": "BENCH", "ts": ts(base), "tsn": 2, "event": "block", "id": iid, "reason": "needs a live game",
            "kind": "external"}] + [{"seat": "OWNER", "ts": ts(base + k * day), "tsn": 2 + k, "event": "game",
                                     "state": "UP"} for k in (1, 2)]
    with tempfile.TemporaryDirectory(prefix="ld_age_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d), \
            contextlib.ExitStack() as es:
        for p in pats[1:]:
            es.enter_context(p)
        es.enter_context(patch.object(LE, "_world", lambda observe=None: LM.replay(evs, observe=observe)))
        g = ld.gather({}, NOW, load_lag_s=90)["items"][iid]
    chk(lambda: g["shape_due"] and g["block_stale"] and "unblock" in (g["shape_why"] or ""),
        "an item already due for Shape whose block is stale: its Shape why still names the block and `rimflow "
        "unblock` (got due=%s, why=%s)" % (g["shape_due"], g["shape_why"]))


def t_a_shaped_old_item_gets_its_second_look():
    """RIMMANDRAKE_PREPARE_LANE_ROWS_THAT_WAIT_FOR_CONDUCTOR_SIXTEEN_OPEN: an old item that a Shape split gave its check is a
    lane item. On 2026-11-27 two such items (shaped 2026-11-26 by a work bundle) read `reshape` and were told to run
    `rimflow shape <ID> --enter`, which refuses an item that carries a check: no program and no hand could move them.
    An old item with a check from `file --effect` and no split stays out (a date never launches old work)."""
    import contextlib
    import list_effect as LE
    import datetime as _dt
    import model as LM
    ld, _ids, _cfg, pats = _lag_world()
    sh, fe = "LD_SHAPED_OLD_ITEM_SECOND_LOOK", "LD_FILED_EFFECT_OLD_ITEM_NO_LOOK"
    part = {"name": "p", "effect": "cmd:false", "fooled_by": "nothing", "route": None}
    evs = [{"seat": "BENCH", "ts": "2026-10-01T00:00:00Z", "tsn": 1, "event": "file", "id": sh, "title": "t",
            "kind": "task", "for": "BENCH"},
           {"seat": "BENCH", "ts": _dt.datetime.fromtimestamp(NOW - 86400, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tsn": 2, "event": "shape", "id": sh, "parts": [part],
            "check": "cmd:false"},
           {"seat": "BENCH", "ts": "2026-10-01T00:00:00Z", "tsn": 3, "event": "file", "id": fe, "title": "t",
            "kind": "task", "for": "BENCH", "effect": "cmd:false"}]
    with tempfile.TemporaryDirectory(prefix="ld_look_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d), \
            contextlib.ExitStack() as es:
        for p in pats[1:]:
            es.enter_context(p)
        es.enter_context(patch.object(LE, "_world", lambda observe=None: LM.replay(evs, observe=observe)))
        g = ld.gather({"shape_from": "2026-11-20T00:00:00Z"}, NOW, load_lag_s=90)["items"]
    chk(lambda: g[sh]["second_look"] is True, "an old item with a Shape split is a lane item: one second look (%s)"
        % g[sh].get("second_look"))
    chk(lambda: g[fe]["second_look"] is False, "an old item with a filed check, never named or split: no look (%s)"
        % g[fe].get("second_look"))


def t_a_lead_takes_the_ready_tickets_of_its_home():
    """RIMMANDRAKE_BUNDLE_LIST_TICKETS_BY_HOME_TEN_OF_TWELVE_HELD_ONE: an open ticket with no check (no lane row) of the
    lead's home joins the lead's bundle when it is ready; one that waits, is blocked, held, off, leased or refused stays
    out, and so does one whose system has no lead."""
    import types
    L = LD()
    x = lambda **kw: types.SimpleNamespace(**dict({"wait_until": None, "title": "t", "kind": "bug",  # noqa: E731
                                                   "created_at": "2026-11-24T00:00:00Z"}, **kw))
    # the owner's age filter (2026-11-25, work_bundle.age_refusal): a joiner has no check, so only a newer ticket with a
    # recorded failure joins; an old one (O) and a newer one with no recorded failure (N) stay out
    cands = {"B": x(), "C": x(wait_until="2099-01-01T00:00:00Z"), "D": x(), "E": x(), "F": x(), "G": x(), "H": x(),
             "I": x(), "J": x(), "K": x(wait_until="not a date"), "R": x(), "P": x(wait_until="2000-01-01T00:00:00Z"),
             "O": x(created_at="2026-10-01T00:00:00Z"), "N": x(kind="task")}
    sysmap = dict({i: "pipeline:test-lane" for i in cands}, I="pipeline:docs", J="item:J")
    got = L.join_candidates(cands, NOW, want={"pipeline:test-lane", "item:J"}, system=sysmap.get,
                            facts=lambda t: ([], True) if t is cands["E"] else (["Z"], False) if t is cands["G"] else ([], False),
                            lease=lambda t: "live" if t is cands["H"] else None,
                            off=lambda i: ("off by pipe", None) if i == "F" else (None, None),
                            held=lambda i: "HELD BY OWNER" if i == "D" else None,
                            refused=lambda i: "REFUSED BY BUNDLE: not this system" if i == "R" else None)
    chk(lambda: got == {"B": "pipeline:test-lane", "P": "pipeline:test-lane"},
        "join_candidates: a ready ticket and one whose wait passed join; a waiting, held, blocked, off, waiting-on, "
        "leased, refused, unreadable-date, no-lead, item:, old or unvetted ticket stays out (%s)" % got)
    items = {"A": it()}
    rows, launches, _ = run(items, systems={"A": "pipeline:test-lane"}, bundles_live={}, join={"B": "pipeline:test-lane"})
    chk(lambda: rows["A"].get("bundle", {}).get("members") == ["A", "B"] and launches == ["A"],
        "decide: one bundle of the home, with its ready ticket that has no check (%s, %s)"
        % (rows["A"].get("bundle"), launches))
    rows, launches, _ = run({}, systems={}, bundles_live={}, join={"B": "pipeline:test-lane"})
    chk(lambda: launches == [], "decide: a home with no ticket whose check fails launches nothing")

def t_each_row_says_since_when_it_took_its_decision():
    """conductor_stops reads the age of a stop from `since` (RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX)."""
    p = os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")
    st = att({"unit": "u1", "failed": None, "next": None})
    mw = it(mod_work={"mod": "GSS", "why": "its home is mod:GSS", "unreadable": None}, wait_until=NOW + 86400)
    items = {"A": it(), "M": mw}
    fx = {"facts": lambda s: {"items": items, "runs": {"A": {"live": [], "ended": ["u1"]}}, "other_live": 0},
          "account": lambda: (True, ""), "launch": lambda *a: (0, "", "u9"), "need": lambda *a: None,
          "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    json.dump(st, open(p, "w"))
    r1 = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW)
    r2 = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW + 900)
    chk(lambda: r1["items"]["A"]["decision"] == "stopped" and r2["items"]["A"].get("since") == NOW,
        "a row keeps the time it first took its decision (%s)" % r2["items"]["A"].get("since"))
    chk(lambda: r2["items"]["M"].get("mod") == "GSS" and r2["items"]["M"].get("wait_until") == NOW + 86400,
        "a mod_work row names its mod and its own dated wait")
    items["A"] = it(state="done")
    r3 = LD().tick(dict(CFG), apply=True, fx=fx, now=NOW + 1800)
    chk(lambda: r3["items"]["A"].get("since") == NOW + 1800, "a new decision restarts since")
    d = LD().tick(dict(CFG), apply=False, fx=fx, now=NOW + 2700)
    chk(lambda: d["items"]["M"].get("since") == NOW, "a dry tick reads since and writes nothing")
    os.remove(p)


def t_a_block_with_no_end_ages_whatever_its_needs():
    """block_end names what lifts a block; a block with none, idle block_idle_days, is stale whatever its needs, on an
    open route (the Conductor, 2026-11-26, design/specs/2026-11-26-testless-tickets/conductor_decisions.md question 2)."""
    import types
    import model as LM
    L = LD()
    day = 86400.0
    cfg = dict(CFG, block_idle_days=3, block_window_min=2, onboard_classes={"pipeline": "on", "game": "off", "mod": "on"},
               no_home_shape_from="2027-06-01T08:00:00Z")

    def b(kind=None, needs="offline", reason="r", lift=None):
        return types.SimpleNamespace(id="LD_ENDLESS", blocked=True, blocked_kind=kind, blocked_reason=reason,
                                     blocked_lift_at=lift, needs=needs)
    for x, has in ((b("owner"), True), (b("time", lift="2027-01-01"), True), (b("external"), True),
                   (b("live", needs="game-up"), True), (b(None), False), (b(""), False), (b("other"), False),
                   (b("item"), False), (b("judge"), False), (b("time"), False), (b("external", reason=None), False),
                   (b("live", needs="offline"), False)):
        chk(lambda x=x, has=has: bool(L.block_end(x)) == has,
            "block_end: kind %r needs %s lift %s reason %s -> %s" % (x.blocked_kind, x.needs, x.blocked_lift_at,
                                                                     x.blocked_reason, "an end" if has else "no end"))

    def ts(t):
        import datetime as dt
        return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def age(block_at, kind=None, needs="offline", system="pipeline:bridge", now=NOW, extra=()):
        evs = [{"seat": "BENCH", "ts": ts(block_at - 60), "tsn": 1, "event": "file", "id": "LD_ENDLESS", "title": "t",
                "kind": "task", "needs": needs, "for": "BENCH"},
               dict({"seat": "BENCH", "ts": ts(block_at), "tsn": 2, "event": "block", "id": "LD_ENDLESS",
                     "reason": "waits for something"}, **({"kind": kind} if kind else {}))]
        evs += [dict({"seat": "BENCH", "ts": ts(t), "tsn": 3 + n}, **k) for n, (t, k) in enumerate(extra)]
        op = L.Openings()
        w = LM.replay(evs, observe=op.observe)
        return L.block_age(w.items["LD_ENDLESS"], op, now, cfg, system=system)
    old = NOW - 5 * day
    due, why = age(old)
    chk(lambda: due and "no end" in why and "--kind" in why and "unblock" in why and "drop" in why,
        "no kind, needs offline, idle 5 d: due; the why asks to drop a stale ticket, type or lift the block (%s)" % why)
    for needs in ("offline", "deploy", "harvest", "owner", "bridge", "game-up"):
        chk(lambda needs=needs: age(old, needs=needs)[0], "needs %s: a block with no end ages all the same" % needs)
    chk(lambda: age(old, kind="other")[0], "kind other: no end, due (the ledger refuses a time block with no date)")
    chk(lambda: not age(NOW - 2 * day)[0], "idle 2 days: not due yet")
    note = (old + 4 * day, {"event": "note", "id": "LD_ENDLESS", "text": "still blocked"})
    chk(lambda: not age(old, extra=[note])[0], "a later event of its own restarts the idle clock")
    chk(lambda: not age(old, kind="owner")[0], "a block of kind owner never ages: his act lifts it")
    off, why_off = age(old, system="game:flight")
    chk(lambda: not off and "off" in why_off, "its home class is off: it waits for its class (%s)" % why_off)
    # the crossing of the two age rules: a block with no end decides before the needs window, so a window that opened
    # often enough does not take a ticket of an off class past its block
    ups = [(old + k * day, {"event": "game", "state": "UP"}) for k in (1, 2)]
    cross, why_x = age(old, needs="game-up", system="game:flight", extra=ups)
    chk(lambda: not cross and "off" in why_x and "no end" in why_x,
        "no kind, needs game-up, the window opened twice, idle 5 d, an off class: the no-end rule decides, and it "
        "waits for its class (%s)" % why_x)
    m, why_m = age(old, system="mod:FlowWorks")
    chk(lambda: not m and "mod_members" in why_m, "one mod's ticket: its mod's bundle settles it (%s)" % why_m)
    early, why_e = age(old, system="item:LD_ENDLESS")
    chk(lambda: not early and "2027-06-01" in why_e, "no home, before no_home_shape_from: waits for that date (%s)" % why_e)
    chk(lambda: age(L._epoch_of("2027-06-02T00:00:00Z") - 5 * day, system="cause:P",
                    now=L._epoch_of("2027-06-02T00:00:00Z"))[0], "no home, after that date: due")


def t_old_no_home_tickets_are_placed_then_named_for_shape():
    """The applied full tick writes the rule homes, then names for Shape at most no_home_shape_per_day in 24 h of the
    old tickets no rule places, oldest first, from no_home_shape_from (the Conductor, 2026-11-26, question 1)."""
    L = LD()
    frm = NOW - 86400
    cfg = dict(CFG, no_home_shape_from=frm, no_home_shape_per_day=2)
    cands = {"C3": 30.0, "C1": 10.0, "C2": 20.0}
    got, why = L.no_home_names(cands, cfg, {}, NOW)
    chk(lambda: got == ["C1", "C2"], "two a day, oldest first (%s: %s)" % (got, why))
    got, _ = L.no_home_names(cands, cfg, {"X": NOW - 3600}, NOW)
    chk(lambda: got == ["C1"], "a name in the last 24 h counts against the pace (%s)" % got)
    got, _ = L.no_home_names(cands, cfg, {"X": NOW - 90000, "Y": NOW - 90000}, NOW)
    chk(lambda: got == ["C1", "C2"], "names older than 24 h do not count (%s)" % got)
    got, why = L.no_home_names(cands, dict(cfg, no_home_shape_from=NOW + 60), {}, NOW)
    chk(lambda: got == [] and "from" in why, "before no_home_shape_from: none (%s)" % why)
    got, why = L.no_home_names(cands, dict(cfg, no_home_shape_from=None), {}, NOW)
    chk(lambda: got == [], "no date set: none (%s)" % why)
    import types

    def x(iid, **k):
        d = dict(id=iid, state="proposed", effect=None, shape=None, shape_named=None, created_at="2026-11-01T00:00:00Z",
                 home=None, title="t", wait_until=None, blocked=False, lease=None, owner=None)
        d.update(k)
        return types.SimpleNamespace(**d)
    items = {"OK": x("OK"), "OLDER": x("OLDER", created_at="2026-10-01T00:00:00Z"), "NAMED": x("NAMED", shape_named="2026-11-20T00:00:00Z"),
             "NEW": x("NEW", created_at="2026-11-25T00:00:00Z"), "TESTED": x("TESTED", effect="cmd:false"),
             "MOD": x("MOD"), "PARKED": x("PARKED"), "OFF": x("OFF"), "HELD": x("HELD"), "LEASED": x("LEASED"),
             "PLACED": x("PLACED"), "HOMED": x("HOMED"), "SHUT": x("SHUT", state="done")}
    c = L.no_home_cands(items, NOW, {"shape_from": "2026-11-23T14:00:00Z"},
                        system=lambda i: "pipeline:bridge" if i == "HOMED" else "mod:FlowWorks" if i == "MOD" else "item:%s" % i,
                        parked=lambda i: i == "PARKED", off=lambda i: "off" if i == "OFF" else None,
                        held=lambda i: "held" if i == "HELD" else None, leased=lambda i: i == "LEASED",
                        placed={"PLACED"})
    chk(lambda: sorted(c) == ["OK", "OLDER"] and c["OLDER"] < c["OK"],
        "the candidates: open, no test, never named, old, no home, no rule home, not parked, off, held or leased (%s)" % c)
    d = tempfile.mkdtemp(prefix="ld_nohome_")
    os.environ["RM_LIST_DISPATCH_DIR"] = d
    acts = []
    base = {"items": {}, "runs": {}, "other_live": 0,
            "old": {"homes": [("H1", {"home": "pipeline:bridge", "group": "by-rule-cause", "flag": "CANNOT TELL",
                                      "reason": "by rule"})], "cands": dict(cands)}}
    fx = {"facts": lambda st: json.loads(json.dumps(base)), "account": lambda: (True, ""),
          "home": lambda rows: acts.append(("home", [r[0] for r in rows])) or (0, "home: 1 written"),
          "name": lambda iid, why: acts.append(("name", iid)) or (0, "")}
    rd = L.tick(dict(cfg), apply=False, fx=fx, now=NOW)
    chk(lambda: acts == [] and "would" in json.dumps(rd.get("old")), "a dry tick writes no home and names none (%s)" % rd.get("old"))
    L.tick(dict(cfg), apply=True, fx=fx, now=NOW, only=["C1"])
    chk(lambda: acts == [], "a run-now tick writes no home and names none (%s)" % acts)
    rd = L.tick(dict(cfg), apply=True, fx=fx, now=NOW)
    chk(lambda: acts == [("home", ["H1"]), ("name", "C1"), ("name", "C2")] and rd["old"]["named"] == ["C1", "C2"],
        "an applied tick writes the homes, then names two, oldest first (%s, %s)" % (acts, rd.get("old")))
    st = json.load(open(os.path.join(d, "state.json")))
    chk(lambda: sorted(st.get("no_home_named") or {}) == ["C1", "C2"], "the names are kept in the state")
    del acts[:]
    L.tick(dict(cfg), apply=True, fx=fx, now=NOW + 60)
    chk(lambda: ("name", "C3") not in acts, "the next tick inside 24 h names none past the pace (%s)" % acts)
    base["old"] = {"could_not_look": "the ledger could not be read"}
    del acts[:]
    rd = L.tick(dict(cfg), apply=True, fx=fx, now=NOW + 120)
    chk(lambda: acts == [] and "could not look" in json.dumps(rd.get("old")), "could not look: nothing written, and said")
def t_a_judge_route_launches_one_fresh_judge_run():
    """A part routed to a judge: the old-work filter first, then one fresh judge run (owner by card 2026-11-26, "Ticket
    lane starts it (Recommended)"; RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX part 2). Before it, a judge route
    read `routed` and nothing ever launched (10 tickets at the 3:13 PM PST tick)."""
    jr = {"who": "judge", "ask": "rule design/x.md against design/RimMandrake/art_judge_brief.md", "resumes": "a KEEP"}
    off = {"stale": None, "live": False}
    for name, base in (("no check", it(effect=None, verdict=None, route=jr, judge=off)),
                       ("a failing check", it(route=jr, judge=off))):
        rows, launches, _ = run({"A": base})
        r = rows["A"]
        chk(lambda: r["decision"] == "judge" and launches == ["A"] and r.get("model") == "opus"
            and r.get("kind") == "judge", "a judge route with %s launches one opus judge run (%s: %s)"
            % (name, r["decision"], r.get("why")))
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=dict(jr, who="owner"))})
    chk(lambda: rows["A"]["decision"] == "routed" and launches == [], "an owner route still launches nothing")
    stale = dict(off, stale="every path the ask names is gone now: design/x.md")
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=stale)})
    chk(lambda: rows["A"]["decision"] == "stopped" and launches == [] and "stale" in rows["A"]["why"]
        and rows["A"].get("need"), "a stale judge ask is not launched and goes to the Conductor (%s)" % rows["A"].get("why"))
    live = {"stale": None, "live": True}
    held = [{"game": "ArchBig", "state": "HELD", "line": "ArchBig: HELD by BENCH"},
            {"game": "ArchSmall", "state": "HIS_HOLD", "line": "ArchSmall: HIS HOLD"}]
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=live)}, games=held)
    chk(lambda: rows["A"]["decision"] == "judge_waits_game" and launches == [] and "ArchBig: HELD" in rows["A"]["why"],
        "a judge that needs captures waits with the reason when no game is free (%s)" % rows["A"].get("why"))
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=live)}, games=None)
    chk(lambda: rows["A"]["decision"] == "blind" and launches == [], "games that could not be read launch no live judge")
    cnl = LD().PR_could_not_look("the lock folder is gone")
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=live)}, games=cnl)
    chk(lambda: rows["A"]["decision"] == "blind" and "the lock folder is gone" in rows["A"]["why"] and launches == [],
        "a could-not-look reading of the games names its cause (%s)" % rows["A"].get("why"))
    free = [dict(held[0], state="FREE", line="ArchBig: FREE"), held[1]]
    hcfg = dict(CFG, hosts={"SteveDesktop": {"max_live": 2, "min_left_pct": 5}})
    room = {"SteveDesktop": {"live": 0, "left": 50.0}}
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=live)}, games=free, cfg=hcfg, hosts=room)
    chk(lambda: rows["A"]["decision"] == "judge" and rows["A"].get("game") == "ArchBig" and not rows["A"].get("host"),
        "a live judge takes the free game, on Archmagi (%s)" % rows["A"])
    # two live judges in one tick: the second never takes the game that the first took this tick
    both = [dict(held[0], state="FREE", line="ArchBig: FREE"), dict(held[1], state="FREE", line="ArchSmall: FREE")]
    two = {"A": it(effect=None, verdict=None, route=jr, judge=live), "B": it(effect=None, verdict=None, route=jr, judge=live)}
    rows, launches, _ = run(two, games=both, cfg=dict(CFG, max_live=3))
    chk(lambda: launches == ["A", "B"] and rows["A"].get("game") == "ArchBig" and rows["B"].get("game") == "ArchSmall",
        "two live judges in one tick take two free games, not one (%s, %s)" % (rows["A"].get("game"), rows["B"].get("game")))
    rows, launches, _ = run(two, games=free, cfg=dict(CFG, max_live=3))
    chk(lambda: launches == ["A"] and rows["B"]["decision"] == "judge_waits_game" and "ArchBig" in rows["B"]["why"],
        "a second live judge waits when the one free game went to the first this tick (%s: %s)"
        % (rows["B"]["decision"], rows["B"].get("why")))
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=live, held="HELD BY OWNER: X"),
                             "B": it(effect=None, verdict=None, route=jr, judge=live)}, games=free, cfg=dict(CFG, max_live=3))
    chk(lambda: rows["A"]["decision"] == "held" and rows["B"].get("game") == "ArchBig",
        "a judge row that a gate stops takes no game (%s, %s)" % (rows["A"]["decision"], rows["B"].get("game")))
    # gather: a judge ticket with no check still reads the owner's mod hold and its chain depth (every gate of a launch)
    import contextlib
    import list_effect as LE
    import model as LM
    ld, _ids, _cfg, pats = _lag_world()
    jid = "RIMMANDRAKE_JUDGE_STILLSAND_DUNE_ART"
    evs = [{"seat": "BENCH", "ts": "2026-11-22T00:00:00Z", "tsn": 1, "event": "file", "id": jid, "for": "BENCH",
            "kind": "task", "title": "judge the Stillsand dune art"},
           {"seat": "BENCH", "ts": "2026-11-22T01:00:00Z", "tsn": 2, "event": "shape", "id": jid,
            "parts": [{"name": "rule", "route": {"who": "judge", "ask": "rule the dune art", "resumes": "a KEEP"}}]}]
    with tempfile.TemporaryDirectory(prefix="ld_judge_held_") as d, patch.dict(os.environ, RM_DISPATCHER_STATE=d), \
            contextlib.ExitStack() as es:
        for p in pats[1:]:
            es.enter_context(p)
        es.enter_context(patch.object(LE, "_world", lambda observe=None: LM.replay(evs, observe=observe)))
        es.enter_context(patch.object(ld, "_mods", return_value=["Stillsand"]))
        es.enter_context(patch.object(ld, "_held", lambda m: "HELD BY OWNER: %s" % m if m == "Stillsand" else None))
        g = ld.gather({}, NOW, load_lag_s=90)
    gi = (g.get("items") or {}).get(jid) or {}
    rows, launches, _ = run({jid: gi}, games=[])
    chk(lambda: gi.get("held") and "depth" in gi and rows[jid]["decision"] == "held" and launches == [],
        "gather reads the owner's hold and the chain depth of a judge ticket with no check, so it is not launched "
        "(held=%s, depth=%s, %s)" % (gi.get("held"), gi.get("depth"), rows[jid]["decision"]))
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=off)}, account=(False, "drain"))
    chk(lambda: rows["A"]["decision"] == "account_hold" and launches == [], "the account gate holds a judge launch")
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=off), "B": it()},
                            systems={"A": "fix:X", "B": "fix:X"})
    chk(lambda: rows["A"]["decision"] == "judge" and "A" in launches and not rows["A"].get("bundle")
        and rows["B"]["decision"] == "launch", "a judge run is never folded into a work bundle (%s)" % rows["A"])
    st = att({"unit": "j1", "failed": None, "next": None, "kind": "judge"})
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=off)},
                            runs={"A": {"live": [], "ended": ["j1"]}}, st=st)
    chk(lambda: rows["A"]["decision"] == "stopped" and launches == [],
        "a judge run that ended and left its route is not launched again (%s)" % rows["A"].get("why"))
    st = att({"unit": "w1", "failed": None, "next": None})
    rows, launches, _ = run({"A": it(effect=None, verdict=None, route=jr, judge=off)},
                            runs={"A": {"live": [], "ended": ["w1"]}}, st=st)
    chk(lambda: rows["A"]["decision"] == "judge" and launches == ["A"],
        "the Work run that routed it to a judge does not stop the first judge run (%s)" % rows["A"].get("why"))
    b = LD().judge_brief_text("A", it(effect=None, verdict=None, route=jr, judge=live, title="t"),
                              {"game": "ArchBig", "run_n": 1}, makers=["u0"])
    for need in ("stop", "polish", "You are not u0", "art_judge_brief.md", "game_lock.py claim ArchBig",
                 "not worth the touch", "STALE", "flight"):
        chk(lambda need=need: need in b, "the judge brief says %r" % need)
    sent = []
    fx = {"launch": lambda *a, **k: sent.append(a) or (0, "", "j9"), "need": lambda *a: None}
    st = {"items": {}}
    items = {"A": it(effect=None, verdict=None, route=jr, judge=off)}
    rows, launches = LD().decide(dict(CFG), st, {"items": items, "runs": {}, "other_live": 0}, NOW)
    LD().execute(dict(CFG), st, rows, launches, {"items": items}, NOW, fx=fx)
    chk(lambda: sent and "fresh judge" in sent[0][3] and st["items"]["A"]["attempts"][-1]["kind"] == "judge"
        and rows[0]["decision"] == "launched", "the tick launches the judge with the judge brief and records it")


def t_a_live_check_with_no_game_takes_a_free_game_or_waits():
    # OPS_LIST_GATE_HOLDS_READY_WORK_ON_COULD_NOT_LOOK_WTHJ, outage 5 (2026-11-27 03:16Z): DONOR_MUTATORS_MIGRATE's live
    # check exited 2 ("not in the RUNNING mod list") because no game ran its mods. The row read blind, so the alarm rang
    # and nothing launched, while a game of Archmagi could take the work (Conductor, note 16: "a live check reads as
    # waiting for a game, not blind").
    out = "exit 2 (only 0 holds and 1 fails)\nUNMEASURED: not in the RUNNING mod list: mandrake.rsw.swbestiary"
    live = lambda **kw: it(effect="cmd:python.exe src/X/live_x.py", verdict="unmeasured", needs="bridge", out=out, **kw)
    free = [{"game": "ArchBig", "state": "FREE", "line": "ArchBig: FREE"},
            {"game": "ArchSmall", "state": "HIS_HOLD", "line": "ArchSmall: HIS HOLD"}]
    held = [dict(free[0], state="HELD", line="ArchBig: HELD by BENCH"), free[1]]
    hcfg = dict(CFG, hosts={"SteveDesktop": {"max_live": 2, "min_left_pct": 5}})
    room = {"SteveDesktop": {"live": 0, "left": 50.0}}
    rows, launches, _ = run({"A": live()}, games=free, cfg=hcfg, hosts=room)
    r = rows["A"]
    chk(lambda: r["decision"] == "launch" and launches == ["A"] and r.get("game") == "ArchBig" and not r.get("host")
        and not r.get("could_not_look"), "a live check that cannot look takes the free game, on Archmagi (%s)" % r)
    rows, launches, _ = run({"A": live()}, games=held)
    r = rows["A"]
    chk(lambda: r["decision"] == "waits_game" and launches == [] and not r.get("could_not_look")
        and "ArchBig: HELD" in r["why"], "no game free: waits_game with the games' lines, not blind (%s)" % r)
    bh = LD().blind_hold({"passes": 3}, list(rows.values()), NOW)
    chk(lambda: bh["passes"] == 0, "a row that waits for a game is no could-not-look hold (%s)" % bh)
    rows, launches, _ = run({"A": live()}, games=None)
    chk(lambda: rows["A"]["decision"] == "blind" and launches == [], "games that could not be read: blind")
    two = {"A": live(), "B": live()}
    both = [free[0], dict(free[1], state="FREE", line="ArchSmall: FREE")]
    rows, launches, _ = run(two, games=both, cfg=dict(CFG, max_live=3))
    chk(lambda: launches == ["A", "B"] and rows["A"].get("game") == "ArchBig" and rows["B"].get("game") == "ArchSmall",
        "two live checks in one tick take two games (%s, %s)" % (rows["A"].get("game"), rows["B"].get("game")))
    # what stays blind: an offline item's exit 2, a live item's other exits (127: a fault of the check's form), a
    # missing file; a live item's failing check is ordinary work and takes no game
    for name, x in (("an offline item's exit 2", it(verdict="unmeasured", out=out)),
                    ("a live item's exit 127", it(verdict="unmeasured", needs="bridge",
                                                  out="exit 127 (only 0 holds and 1 fails)\npython.exe: command not found")),
                    ("a live item's deadline", it(verdict="unmeasured", needs="game-up",
                                                  out="the command ran past its 60s deadline"))):
        chk(lambda x=x: dec({"A": x}, games=free) == ("blind", []), "%s stays blind" % name)
    rows, launches, _ = run({"A": it(needs="bridge")}, games=free)
    chk(lambda: launches == ["A"] and not rows["A"].get("game"), "a live item whose check fails takes no game")
    chk(lambda: LD().waits_for_game(live()) and not LD().waits_for_game(it(verdict="unmeasured", out=out)),
        "waits_for_game reads the needs and the exit")
    chk(lambda: LD().games_wanted({"A": live()}) and not LD().games_wanted({"A": it()}),
        "the tick reads the games for a live check that cannot look, and only then (with a live judge)")
    b = LD().brief_text("A", live(), dict(rows["A"], game="ArchBig"))
    chk(lambda: "game_lock.py claim ArchBig" in b and "small_list.json" in b and "game_lock.py release ArchBig" in b,
        "the Work brief tells the run to claim, deploy and release the game it was given")
    import work_bundle as WB
    grows = [{"item": "A", "decision": "launch", "game": "ArchBig"}, {"item": "B", "decision": "launch", "host": "SteveDesktop"}]
    _, gl = WB.group(grows, ["A", "B"], {"A": "s", "B": "s"}, {})
    chk(lambda: gl == ["A", "B"] and "bundle" not in grows[0] and grows[1].get("bundle", {}).get("members") == ["B"],
        "a row that takes a game is its own run, never in a bundle that may run on a host (%s)" % grows)


def t_a_check_that_stays_blind_gets_a_repair_run():
    # RELAPSE_MATURATION_FIX_DIED_TWICE: maturation.list_gate_blind_passes rang in six episodes on 2026-11-26 and 27,
    # each a new reason why one item's check could not look (a PATH, an unlanded file, a live bundle, no game, a bridge
    # profile). The row read blind on every tick; nothing repaired the check but an Operations read bought by the alarm.
    out = "exit 127 (only 0 holds and 1 fails)\npython.exe: command not found"
    blind = lambda **kw: it(verdict="unmeasured", out=out, **kw)
    acts = []
    fx = {"account": lambda: (True, ""), "launch": lambda *a: acts.append(a) or (0, "", "u-repair"),
          "need": lambda *a: None, "close": lambda *a: (0, ""), "effect": lambda *a: (0, "")}
    os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ld_repair_")
    cfg = dict(CFG, blind_repair_passes=3)
    world = {"items": {"A": blind(), "B": blind()}, "runs": {}, "other_live": 0}

    def tick(facts, t, apply=True, **kw):
        return LD().tick(dict(cfg), apply=apply, fx=dict(fx, facts=lambda st: facts), now=t, **kw)
    rd = [tick(world, NOW)]
    dry = tick(world, NOW + 100, apply=False)
    only = tick(world, NOW + 200, only=["A"])
    rd.append(tick(world, NOW + 600))
    chk(lambda: [r["items"]["A"]["decision"] for r in rd] == ["blind", "blind"] and rd[1]["blind_hold"]["passes"] == 2
        and acts == [], "the first ticks of a check that cannot look read blind and launch nothing (%s)"
        % [r["items"]["A"] for r in rd])
    chk(lambda: dry["items"]["A"]["decision"] == "blind" and only["items"]["A"]["decision"] == "blind" and acts == [],
        "a dry tick and a run-now tick neither count nor end the streak (else the second applied tick would launch)")
    world2 = dict(world, items={"A": blind(), "B": it(verdict="holds", out="x")})      # B's check reads: its streak ends
    rd3 = tick(world2, NOW + 1200)
    a = rd3["items"]["A"]
    chk(lambda: a["decision"] == "launched" and len(acts) == 1 and acts[0][0] == "A" and acts[0][1] == "opus"
        and rd3["blind_hold"]["passes"] == 0,
        "the third blind tick launches one repair run on opus, and the alarm's streak ends (%s, %s)" % (a, rd3["blind_hold"]))
    brief = acts[0][3] if acts else ""
    chk(lambda: "could not look" in brief and "python.exe: command not found" in brief and "repair" in brief
        and "cli.py shape A" in brief, "the repair run's brief names the check's output and the repair it owes")
    world3 = dict(world, items={"A": blind(), "B": blind()})
    rd4 = tick(world3, NOW + 1800)
    chk(lambda: rd4["items"]["B"]["decision"] == "blind",
        "a streak is per item: B's check read once, so it starts again at 1 (%s)" % rd4["items"]["B"])
    ended = dict(world3, runs={"A": {"live": [], "ended": ["u-repair"]}})
    rds = [tick(ended, NOW + 2400 + 600 * k) for k in range(3)]
    chk(lambda: rd4["items"]["A"]["decision"] == "blind" and [r["items"]["A"]["decision"] for r in rds] == [
        "blind", "stopped", "stopped"] and len(acts) == 2,
        "after the repair run ended with no next act and the check still cannot look, A reads stopped, never blind "
        "for ever (%s)" % [r["items"]["A"]["decision"] for r in rds])
    chk(lambda: acts[1][0] == "B", "B, blind three ticks in a row on its own, got its own repair run (%s)"
        % [x[0] for x in acts])
    rows, launches, _ = run({"A": blind()}, st={"items": {"A": {"blind_n": 2}}}, cfg=dict(CFG, blind_repair_passes=3),
                            runs={"A": {"live": ["u9"], "ended": []}})
    chk(lambda: rows["A"]["decision"] == "live" and launches == [], "a live run on the item outranks a repair run")
    rows, launches, _ = run({"A": blind()}, st={"items": {"A": {"blind_n": 2}}}, cfg=dict(CFG, blind_repair_passes=3,
                                                                                         max_live=0))
    chk(lambda: rows["A"]["decision"] == "slots_full" and not rows["A"].get("could_not_look") and rows["A"].get("check_blind"),
        "a repair run held by a gate keeps its streak and is no could-not-look hold (%s)" % rows["A"])
    chk(lambda: isinstance(LD().load_cfg().get("blind_repair_passes"), int)
        and LD().load_cfg()["blind_repair_passes"] <= [t for t in json.load(open(os.path.join(
            REPO, "src", "RimMandrake", "Utils", "ops_watch_rules.json")))["targets"]
            if t.get("key") == "maturation.list_gate_blind_passes"][0]["value"],
        "the shipped repair line comes before the alarm's line, so one item's check never rings it")
    os.environ["RM_LIST_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="ld_selftest_")


def t_the_judge_filter_reads_the_ask_against_now():
    root = tempfile.mkdtemp(prefix="ld_judge_")
    os.makedirs(os.path.join(root, "design"))
    open(os.path.join(root, "design", "here.md"), "w").close()
    jf = LD().judge_facts
    chk(lambda: jf("rule design/gone.md and design/gone2.json", root)["stale"],
        "an ask whose every named path is gone is stale")
    chk(lambda: jf("rule design/here.md, write design/gone.json", root)["stale"] is None,
        "an ask that names one path of now is not stale")
    chk(lambda: jf("pick a or b for RM_Murrelith", root)["stale"] is None, "an ask that names no path is not stale")
    chk(lambda: jf("On in-game captures of the sea-floor view, rule", root)["live"] is True,
        "an ask on in-game captures needs a game")
    chk(lambda: jf("From a screenshot of a fresh map on this build", root)["live"] is True, "a screenshot needs a game")
    chk(lambda: jf("rule design/here.md from the brief", root)["live"] is False, "a text judge needs no game")


PAUSE_RX = [r"^RIMMANDRAKE_READ_FIX_[0-9A-F]+(_[0-9A-F]{6})?_WITH_FRESH_EYES$"]
PAUSE_WHY = "the owner's order (test): the pipeline works before hardening"


def _pause_world(setting, extra_runs=()):
    """The code review pause fixture: a fresh-reader ticket (a made-up sha) and a fix ticket, both ready, the real `_off`
    over a settings file written from `setting` (a dict, a raw text, or None for no such file). -> (rd, tick)."""
    import contextlib
    import control
    import detached_helper as DH
    import list_effect as LE
    import model as LM
    import probe_result as PR
    ld = LD()
    ids = ["RIMMANDRAKE_READ_FIX_ABCDEF1234_WITH_FRESH_EYES", "RIMMANDRAKE_FIX_SOME_OTHER_THING_ENTIRELY"]
    world = LM.replay([{"id": iid, "event": "file", "for": "BENCH", "seat": "BENCH", "kind": "task", "title": iid,
                        "effect": "cmd:false", "ts": "2026-11-22T00:00:00Z"} for iid in ids])
    d = tempfile.mkdtemp(prefix="ld_pause_")
    cfgp = os.path.join(d, "list_dispatch.json")
    if setting is not None:
        with open(cfgp, "w", encoding="utf-8") as f:
            f.write(setting if isinstance(setting, str) else json.dumps({"code_review_pause": setting}))
    cfg = dict(CFG, load_line=28, load_per_run=2, load_lag_s=90)
    fx = {"account": lambda: (True, "")}

    def tick(only=None):
        with patch.dict(os.environ, RM_DISPATCHER_STATE=d), contextlib.ExitStack() as es:
            for p in (patch.object(LE, "_world", return_value=world), patch.object(ld, "_mods", return_value=[]),
                      patch.object(ld, "CFG_PATH", cfgp), patch.object(control, "blocked", return_value=None),
                      patch.object(ld, "_paused", return_value=None), patch.object(ld, "_held", return_value=None),
                      patch.object(ld, "_pool", return_value=None), patch.object(ld, "_clone_exists", return_value=False),
                      patch.object(DH, "live_status", lambda rec, *a: rec["status"]),
                      patch.object(ld, "load_now", return_value=PR.value(1))):
                es.enter_context(p)
            for n, iid in enumerate(extra_runs):
                DH.write_record({"unit": "u%d" % n, "item": iid, "at": NOW - 5, "status": "running",
                                 "next_act_owner": "list_dispatch"})
            return ld.tick(cfg, apply=False, fx=fx, now=NOW, only=only)
    return ids, tick


def t_the_code_review_pause_holds_every_review_ticket():
    """RIMMANDRAKE_PAUSE_CODE_REVIEW_PIPELINE_WORKS_BEFORE_HARDENING (his order 2026-11-27): while list_dispatch.json's
    code_review_pause is on, the lane starts no run on a code review ticket, however late it was filed."""
    import io
    import contextlib
    on = {"on": True, "reason": PAUSE_WHY, "id_patterns": PAUSE_RX}
    ids, tick = _pause_world(on)
    rd = tick()
    rdr, fix = ids
    chk(lambda: rd["items"][rdr]["decision"] == "off" and "code review is paused" in rd["items"][rdr]["why"]
        and PAUSE_WHY in rd["items"][rdr]["why"] and not rd["launched"],
        "pause on: a ready fresh-reader ticket reads off, 'code review is paused' with the reason, and starts no run (%s)"
        % rd["items"][rdr])
    chk(lambda: rd["items"][fix]["decision"] == "would_launch",
        "pause on: a ready ticket of another kind (a fix) is launched as before (%s)" % rd["items"][fix])
    ids2, tick2 = _pause_world(dict(on, on=False))
    chk(lambda: tick2()["items"][ids2[0]]["decision"] == "would_launch", "pause off: the same reader ticket reads ready")
    ids3, tick3 = _pause_world({"on": True, "reason": PAUSE_WHY, "id_patterns": PAUSE_RX})
    ids4, tick4 = _pause_world("{}")
    chk(lambda: tick4()["items"][ids4[0]]["decision"] == "would_launch" and tick4()["pause"]["on"] is False,
        "no code_review_pause key in a readable file: the pause is off, measured")
    ids5, tick5 = _pause_world(on, extra_runs=[ids[0]])
    rd5 = tick5()
    chk(lambda: rd5["items"][ids5[0]]["decision"] == "off" and not rd5["launched"],
        "pause on, a reader ticket with a live run: the lane stops nothing and launches nothing (%s)" % rd5["items"][ids5[0]])
    chk(lambda: rd["pause"] == {"on": True, "reason": PAUSE_WHY, "held": 1}, "the reading names the pause, its reason and the "
        "count of held tickets (%s)" % rd.get("pause"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        LD()._print(rd)
    chk(lambda: "code review is paused" in buf.getvalue() and PAUSE_WHY in buf.getvalue() and "1 ticket" in buf.getvalue(),
        "status prints that the pause is on, the reason and the count (%r)" % buf.getvalue()[-300:])
    for what, setting in (("a settings file that is not JSON", "{not json"), ("no settings file", None),
                          ("a pause whose id_patterns is not a list", {"on": True, "reason": "r", "id_patterns": 7})):
        ids6, tick6 = _pause_world(setting)
        rd6 = tick6()
        chk(lambda rd6=rd6, ids6=ids6: rd6["items"][ids6[0]]["decision"] == "blind"
            and "could not look" in rd6["items"][ids6[0]]["why"] and not rd6["launched"]
            and "could not look" in str((rd6.get("pause") or {}).get("could_not_look", "")),
            "%s: the lane says could not look for the pause and reads no 'pause off' (%s)" % (what, rd6["items"][ids6[0]]))


def t_the_shipped_pause_names_the_three_kinds_and_only_them():
    ld = LD()
    s = ld.load_cfg().get("code_review_pause") or {}
    chk(lambda: s.get("on") is True and s.get("reason"), "the shipped lane carries the pause, on, with its reason")
    import re
    held = ["RIMMANDRAKE_READ_FIX_1ECCD06DB0_WITH_FRESH_EYES", "RIMMANDRAKE_READ_FIX_5E0A5DB3_WITH_FRESH_EYES",
            "RIMMANDRAKE_READ_FIX_A01DAF8197_9F3C2B_WITH_FRESH_EYES",
            "RIMMANDRAKE_FILE_NEW_MACHINERY_REVIEW_LIKE_FRESH_READER",
            "RIMMANDRAKE_REVIEW_NEW_SCRIPTS_THROUGH_CODEX_EIGHTY_THREE_UNREAD"]
    free = ["RIMMANDRAKE_FIX_RETURN_STEP_SAYS_FAILED", "RIMMANDRAKE_PAUSE_CODE_REVIEW_PIPELINE_WORKS_BEFORE_HARDENING",
            "RIMMANDRAKE_BUILD_LIST_LANE_ON_RED_DISPATCH_GOALS_FIRST", "RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE"]
    rx = [re.compile(p) for p in s.get("id_patterns") or []]
    chk(lambda: all(any(r.search(i) for r in rx) for i in held), "the shipped patterns match the three kinds of review ticket")
    chk(lambda: not any(r.search(i) for r in rx for i in free), "and no fix, no build and no blind challenge")


def t_the_pause_command_edits_one_line_and_nothing_else():
    ld = LD()
    with open(ld.CFG_PATH, encoding="utf-8") as f:
        text = f.read()
    off = ld.set_pause(text, False, None)
    on = ld.set_pause(off, True, "a new reason")
    chk(lambda: json.loads(off)["code_review_pause"]["on"] is False and json.loads(on)["code_review_pause"]["on"] is True
        and json.loads(on)["code_review_pause"]["reason"] == "a new reason", "pause off, then on with a new reason: the key follows")
    keep = lambda t: {k: v for k, v in json.loads(t).items() if k != "code_review_pause"}  # noqa: E731
    chk(lambda: keep(off) == keep(text) == keep(on), "every other key is untouched")
    chk(lambda: sum(1 for a, b in zip(text.splitlines(), off.splitlines()) if a != b) == 1
        and len(text.splitlines()) == len(off.splitlines()), "exactly one line of the file changes")
    try:
        ld.set_pause("{}", True, None)
        chk(lambda: False, "a file with no pause line is refused, naming the line to add")
    except ValueError as e:
        chk(lambda: "code_review_pause" in str(e), "a file with no pause line is refused, naming the line to add")


# ---- the game work pause (item RIMMANDRAKE_SWITCH_OFF_LANE_GAME_TICKETS_CROWN_SHADOW_RAN; his order 2026-11-27) ---------

GAME_WHY = "the owner's order (test): one advancing mod, pipeline ticket cleanup first"
GAME_ON = {"on": True, "reason": GAME_WHY, "advancing_mods": ["FlowWorks"]}
CB = "src/RimMandrake/CreatureBehaviors/Source/CrownShadow.cs"      # a mod that does not advance
FW = "src/RimMandrake/FlowWorks/Source/Flow.cs"                     # the advancing mod
TOOL = "src/RimMandrake/rimflow/list_dispatch.py"                   # pipeline machinery
# id: (home, title, effect, filed)
GAME_TICKETS = {
    "RIMMANDRAKE_TRY_CROWN_SHADOW_GAME_HOME": ("game:direct-sun", "draw a crown shadow", "cmd:false", "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_SHAPE_CROWN_SHADOW_GAME_HOME": ("game:direct-sun", "shape the shade work", None, "2026-12-01T00:00:00Z"),
    "RIMMANDRAKE_JOIN_CROWN_SHADOW_GAME_HOME": ("game:direct-sun", "an old shade ticket", None, "2026-11-20T00:00:00Z"),
    "RIMMANDRAKE_FIX_SHADE_NAMES_OTHER_MOD": (None, "fix %s per %s" % (CB, TOOL), "cmd:false", "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_FIX_FLOW_NAMES_ADVANCING_MOD": (None, "fix %s per %s" % (FW, TOOL), "cmd:false", "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_FIX_LANE_PIPELINE_HOME": ("pipeline:list-dispatch", "fix %s, seen on %s" % (TOOL, CB), "cmd:false",
                                           "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_FIX_ARCHMAGI_MACHINE_HOME": ("machine:Archmagi", "fix the timer, seen on %s" % CB, "cmd:false",
                                              "2026-11-27T00:00:00Z"),
    "OPS_ALARM_DIAGNOSE_SHADE_TICK_SEEN_ON_OTHER_MOD": (None, "an alarm on %s and %s" % (CB, TOOL), "cmd:false",
                                                        "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_KEEP_TIMER_LIVE_PROMISE_BROKE": (None, "a live promise on %s and %s" % (CB, TOOL), "cmd:false",
                                                  "2026-11-27T00:00:00Z"),
    "RIMMANDRAKE_OLD_NO_HOME_NAMES_OTHER_MOD": (None, "old: %s per %s" % (CB, TOOL), None, "2026-11-20T00:00:00Z"),
    "RIMMANDRAKE_OLD_NO_HOME_PIPELINE_ONLY": (None, "old: %s only" % TOOL, None, "2026-11-20T00:00:00Z"),
    "RIMMANDRAKE_OLD_PIPELINE_HOME_NO_CHECK": ("pipeline:list-dispatch", "old: seen on %s" % CB, None,
                                               "2026-11-20T00:00:00Z"),
    "RIMMANDRAKE_FIX_SHADE_MOD_HOME_OTHER_MOD": ("mod:CreatureBehaviors", "a mod's own ticket", "cmd:false",
                                                 "2026-11-27T00:00:00Z"),
}
(G_LAUNCH, G_SHAPE, G_JOIN, G_NAMES, G_FW, G_PIPE, G_MACH, G_OPS, G_LIVE, G_OLD_CB, G_OLD_PIPE,
 G_OLD_PIPE_HOME, G_MODHOME) = list(GAME_TICKETS)


def _game_world(setting):
    """The game work pause fixture: GAME_TICKETS in a fake ledger, the real `_off` over a settings file that holds
    `game_work_pause: setting` (None: no such key, the parent's file), onboard_classes all on. -> (tick, gather)."""
    import contextlib
    import control
    import detached_helper as DH
    import list_effect as LE
    import model as LM
    import probe_result as PR
    import work_bundle as WB
    ld = LD()
    evs = []
    for iid, (home, title, effect, filed) in GAME_TICKETS.items():
        e = {"id": iid, "event": "file", "for": "BENCH", "seat": "BENCH", "kind": "task", "title": title, "ts": filed}
        if effect:
            e["effect"] = effect
        evs.append(e)
        if home:
            evs.append({"id": iid, "event": "home", "home": home, "group": "test", "flag": "CANNOT TELL",
                        "seat": "BENCH", "ts": filed})
    evs += [{"id": G_LIVE, "event": "close", "sha": "abc1234", "live": "once: test", "seat": "BENCH",
             "ts": "2026-11-27T01:00:00Z"},
            {"id": G_LIVE, "event": "live", "result": "broken", "detail": "the timer died", "seat": "RUNNER",
             "ts": "2026-11-27T02:00:00Z"}]
    world = LM.replay(evs)
    d = tempfile.mkdtemp(prefix="ld_game_")
    cfgp = os.path.join(d, "list_dispatch.json")
    with open(cfgp, "w", encoding="utf-8") as f:
        f.write(json.dumps({} if setting is None else {"game_work_pause": setting}) if not isinstance(setting, str)
                else setting)
    shipped = dict(LD()._shipped(), onboard_classes={"pipeline": "on", "machine": "on", "mod": "on", "game": "on"})
    cfg = dict(CFG, max_live=40, load_line=1000, load_per_run=0, load_lag_s=90)
    fx = {"account": lambda: (True, "")}

    @contextlib.contextmanager
    def ctx():
        with patch.dict(os.environ, RM_DISPATCHER_STATE=d), contextlib.ExitStack() as es:
            for p in (patch.object(LE, "_world", return_value=world), patch.object(ld, "_mods", return_value=[]),
                      patch.object(ld, "CFG_PATH", cfgp), patch.object(ld, "_shipped", return_value=shipped),
                      patch.object(control, "blocked", return_value=None),
                      patch.object(ld, "_paused", return_value=None), patch.object(ld, "_held", return_value=None),
                      patch.object(ld, "_pool", return_value=None), patch.object(ld, "_clone_exists", return_value=False),
                      patch.object(LM, "read", return_value=[]), patch.object(WB, "age_refusal", return_value=None),
                      patch.object(DH, "live_status", lambda rec, *a: rec["status"]),
                      patch.object(ld, "load_now", return_value=PR.value(1))):
                es.enter_context(p)
            yield

    def tick():
        with ctx():
            return ld.tick(cfg, apply=False, fx=fx, now=NOW)

    def gather():
        with ctx():
            return ld.gather({}, NOW, load_lag_s=90, run_many=lambda effects, *a, **k: (
                {e: ("fails", "red") for e in effects}, {}))
    return tick, gather


def _dec(rd, iid):
    r = rd["items"].get(iid) or {}
    return r.get("decision"), r.get("why") or ""


def _onboard_members(facts, home):
    h = ((facts.get("onboard") or {}).get("homes") or {}).get(home) or {}
    return set(h.get("members") or []), h.get("left_out") or {}


def t_the_game_work_pause_holds_every_route_of_game_work():
    """While game_work_pause is on, the lane starts no run of any route for a ticket of game work, and the row says
    why, with the reason and the command that lifts the pause."""
    import codex_lane as CL
    import re
    tick, gather = _game_world(GAME_ON)
    rd = tick()
    for iid in (G_LAUNCH, G_SHAPE, G_NAMES):
        dcs, why = _dec(rd, iid)
        chk(lambda dcs=dcs, why=why: dcs == "off" and "game work is paused" in why and GAME_WHY in why
            and "pause game off" in why, "pause on: %s reads off, 'game work is paused', the reason and the lift (%s: %s)"
            % (iid, dcs, why))
    chk(lambda: not any(x["item"] in (G_LAUNCH, G_SHAPE, G_NAMES) for x in rd["launched"]), "no launch on game work")
    n_off = sum(1 for r in rd["items"].values() if r["decision"] == "off" and "game work is paused" in r["why"])
    chk(lambda: _dec(rd, G_MODHOME)[0] == "mod_work" and (rd.get("game_pause") or {}).get("held") == n_off == 3,
        "the reading counts the rows the pause holds, never a mod's own ticket, whose row reads mod_work (%s held, %d "
        "rows, %s)" % ((rd.get("game_pause") or {}).get("held"), n_off, _dec(rd, G_MODHOME)))
    facts = gather()
    chk(lambda: G_JOIN not in (facts.get("join") or {}), "pause on: an old game ticket joins no work bundle (%s)"
        % sorted(facts.get("join") or {}))
    mem, left = _onboard_members(facts, "game:direct-sun")
    chk(lambda: not mem and all("game work is paused" in str(left.get(i)) for i in (G_SHAPE, G_JOIN)),
        "pause on: a game home's old tickets start no onboarding run, though its class is on (members %s, left %s)"
        % (sorted(mem), left))
    cands = (facts.get("old") or {}).get("cands") or {}
    chk(lambda: G_OLD_CB not in cands and G_OLD_PIPE in cands,
        "pause on: an old no-home ticket that names a non-advancing mod's files is not named for Shape; a pipeline one "
        "is (%s)" % sorted(cands))
    rx = re.compile(LD()._shipped().get("sonnet_if_check_regex") or ".")
    cx = dict((facts["items"].get(G_LAUNCH) or {}), effect="cmd:python3 src/x/selftest_x.py", verdict="fails")
    ok, why = CL.eligible(cx, rx, NOW)
    chk(lambda: not ok, "pause on: the Codex lane takes no game ticket (%s)" % why)
    st = ((facts.get("game_pause") or {}))
    chk(lambda: st.get("on") is True and st.get("reason") == GAME_WHY, "the facts name the pause and its reason (%s)" % st)
    # could not look: a malformed setting holds the game ticket as blind, never as 'not game work'
    tick2, _g = _game_world({"on": True, "reason": "r", "advancing_mods": "FlowWorks"})
    rd2 = tick2()
    dcs, why = _dec(rd2, G_LAUNCH)
    chk(lambda: dcs == "blind" and "could not look" in why, "a setting that cannot be read: the game ticket reads blind, "
        "could not look (%s: %s)" % (dcs, why))
    chk(lambda: _dec(rd2, G_PIPE)[0] == "would_launch", "and a pipeline ticket still launches (%s)" % (_dec(rd2, G_PIPE),))


def t_the_game_work_pause_never_holds_pipeline_work():
    tick, gather = _game_world(GAME_ON)
    rd = tick()
    for iid in (G_FW, G_PIPE, G_MACH, G_OPS, G_LIVE):
        chk(lambda iid=iid: _dec(rd, iid)[0] == "would_launch", "pause on: %s still launches (%s)" % (iid, _dec(rd, iid)))
    tick0, _ = _game_world(None)
    rd0 = tick0()
    chk(lambda: _dec(rd0, G_LAUNCH)[0] == "would_launch" and _dec(rd0, G_NAMES)[0] == "would_launch"
        and _dec(rd0, G_SHAPE)[0] in ("would_shape", "bundled"), "no pause key (the parent's file): the game tickets launch and "
        "shape (%s, %s, %s)" % (_dec(rd0, G_LAUNCH), _dec(rd0, G_NAMES), _dec(rd0, G_SHAPE)))
    tick_off, gather_off = _game_world(dict(GAME_ON, on=False))
    rd_off = tick_off()
    same = lambda a, b: {i: (r["decision"], r["why"]) for i, r in a["items"].items()} == {  # noqa: E731
        i: (r["decision"], r["why"]) for i, r in b["items"].items()}
    chk(lambda: same(rd_off, rd0), "pause off: every row is as with no pause key")
    f_off, f0 = gather_off(), _game_world(None)[1]()
    chk(lambda: f_off.get("join") == f0.get("join") and _onboard_members(f_off, "game:direct-sun")[0]
        == _onboard_members(f0, "game:direct-sun")[0] and (f_off.get("old") or {}).get("cands")
        == (f0.get("old") or {}).get("cands"), "pause off: the bundle joins, onboarding members and Shape names are as "
        "with no pause key")
    # the exemptions hold in both layers: the pure reading, and the pause, which never reads its setting for them
    gw = LD().game_work
    names_cb = {"mod": None, "names": ["CreatureBehaviors"]}
    for iid, work in (("RIMMANDRAKE_X", {"home": "pipeline:list-dispatch", "mod_work": names_cb}),
                      ("RIMMANDRAKE_X", {"home": "machine:Archmagi", "mod_work": names_cb}),
                      ("OPS_ALARM_X", {"home": None, "mod_work": names_cb}),
                      ("RIMMANDRAKE_X", {"home": None, "live": True, "mod_work": names_cb}),
                      ("RIMMANDRAKE_X", {"home": None, "mod_work": {"mod": "FlowWorks", "names": ["FlowWorks"]}})):
        chk(lambda iid=iid, work=work: gw(iid, work, ["FlowWorks"])[0] is False,
            "game_work: %s %s is not game work (%s)" % (iid, work.get("home") or work, gw(iid, work, ["FlowWorks"])))
    chk(lambda: gw("RIMMANDRAKE_X", {"home": "game:direct-sun", "mod_work": {"mod": None}}, ["FlowWorks"])[0] is True
        and gw("RIMMANDRAKE_X", {"home": None, "mod_work": names_cb}, ["FlowWorks"])[0] is True,
        "game_work: a game: home and a ticket that names a non-advancing mod's files are game work")
    tick_bad, _ = _game_world({"on": True, "reason": "r", "advancing_mods": "FlowWorks"})
    rd_bad = tick_bad()
    for iid in (G_PIPE, G_MACH, G_OPS, G_LIVE):
        chk(lambda iid=iid: _dec(rd_bad, iid)[0] == "would_launch", "a setting that cannot be read holds no %s (%s)"
            % (iid, _dec(rd_bad, iid)))
    facts = gather()
    mem, _left = _onboard_members(facts, "pipeline:list-dispatch")
    chk(lambda: G_OLD_PIPE_HOME in mem, "pause on: a pipeline home's old ticket still joins its onboarding run (%s)" % sorted(mem))


def t_the_game_pause_command_sets_one_line_and_counts_the_held():
    import io
    import contextlib
    ld = LD()
    with open(ld.CFG_PATH, encoding="utf-8") as f:
        text = f.read()
    s = json.loads(text).get("game_work_pause") or {}
    chk(lambda: s.get("on") is True and s.get("reason") and s.get("advancing_mods") == ["FlowWorks"],
        "the shipped lane carries the game pause, on, with its reason and FlowWorks as the one advancing mod (%s)" % s)
    off = ld.set_pause(text, False, None, key="game_work_pause")
    on = ld.set_pause(off, True, "a new reason", key="game_work_pause")
    chk(lambda: json.loads(off)["game_work_pause"]["on"] is False and json.loads(on)["game_work_pause"]["reason"]
        == "a new reason", "pause game off, then on with a new reason: the key follows")
    keep = lambda t: {k: v for k, v in json.loads(t).items() if k != "game_work_pause"}  # noqa: E731
    chk(lambda: keep(off) == keep(text) == keep(on), "every other key is untouched, the code review pause included")
    chk(lambda: sum(1 for a, b in zip(text.splitlines(), off.splitlines()) if a != b) == 1, "exactly one line changes")
    d = tempfile.mkdtemp(prefix="ld_gcmd_")
    p = os.path.join(d, "list_dispatch.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    sd = tempfile.mkdtemp(prefix="ld_gcmd_state_")

    def cli(*argv):
        buf = io.StringIO()
        with patch.object(ld, "CFG_PATH", p), patch.dict(os.environ, RM_LIST_DISPATCH_DIR=sd), \
                contextlib.redirect_stdout(buf):
            rc = ld.main(list(argv))
        return rc, buf.getvalue()
    rc, out = cli("pause", "game", "off", "--why", "lifted in a test")
    with open(p, encoding="utf-8") as f:
        after = json.load(f)
    chk(lambda: rc == 0 and after["game_work_pause"]["on"] is False and after["code_review_pause"]["on"] is True,
        "`pause game off` switches only the game pause (%s)" % out.strip())
    rc, out = cli("pause", "off")
    with open(p, encoding="utf-8") as f:
        after = json.load(f)
    chk(lambda: rc == 0 and after["code_review_pause"]["on"] is False, "`pause off` keeps its words: the code review "
        "pause (%s)" % out.strip())
    rc, out = cli("pause", "game", "status")
    chk(lambda: rc == 2 and "UNMEASURED" in out and "game work pause" in out, "status with no reading: the pause and "
        "UNMEASURED for the count (%s)" % out.strip())
    with open(os.path.join(sd, "reading.json"), "w", encoding="utf-8") as f:
        json.dump({"at": NOW, "at_pac": "then", "game_pause": {"on": True, "reason": GAME_WHY, "held": 7,
                                                               "advancing_mods": ["FlowWorks"]}}, f)
    cli("pause", "game", "on", "--why", GAME_WHY)
    rc, out = cli("pause", "game", "status")
    chk(lambda: rc == 0 and "on" in out and GAME_WHY in out and "7 ticket" in out and "FlowWorks" in out,
        "status prints the pause, its reason, its advancing mods and the held count of the last tick (%s)" % out.strip())


# ---- a lane-cause ticket whose cause was seen in two incidents gets one Work run between incidents -------------------
# (item RIMMANDRAKE_OFFER_TWICE_SEEN_LANE_CAUSE_NOTHING_WORKS_IT; page design/specs/2026-11-23-lane-cause-once/boundary.md)

def _lt():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "lane_ticket_under_test", os.path.join(REPO, "src", "RimMandrake", "Utils", "testq", "lane_ticket.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CAUSE = "STEVE_LANE_UNSTICK_IDLE_UNOWNED_IDLEEMPTY_YVBFTB"
WAITTXT = "steward: waiting for lane cause IDLEEMPTY_YVBFTB (SteveDesktop lane IDLE_EMPTY)"


def _ts(n):
    import time as _t
    return _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime(1_799_000_000 + n))


def _incident(n, t0, live_at_end=False):
    """The ledger events of incident number n starting at offset t0: its alarm, its recovery and the steward's block."""
    ev = []
    if n == 1:
        ev.append({"event": "spawn", "name": CAUSE, "title": "alarm one: lane IDLE_EMPTY since 11:56", "ts": _ts(t0)})
    else:
        ev.append({"event": "unblock", "id": CAUSE, "reason": "steward: lane cause returned", "ts": _ts(t0)})
        ev.append({"event": "note", "id": CAUSE, "text": "steward: lane IDLE_EMPTY again since 18:03 (alarm %d)" % n,
                   "ts": _ts(t0 + 5)})
    if not live_at_end:
        ev.append({"event": "note", "id": CAUSE, "text": "steward: SteveDesktop lane proven again: job J%d DONE" % n,
                   "ts": _ts(t0 + 100)})
        ev.append({"event": "block", "id": CAUSE, "reason": WAITTXT, "ts": _ts(t0 + 110)})
    return ev


def t_a_lane_cause_ticket_seen_in_two_incidents_gets_one_work_run():
    LT = _lt()
    one = _incident(1, 0)
    two = one + _incident(2, 1000)
    three = two + _incident(3, 2000)

    def verdict(events, runs=()):
        return LT.offer(LT.incidents(events), list(runs))[0]
    chk(lambda: verdict(two) == "offer", "two ended incidents and no live incident: offered to the ticket lane")
    chk(lambda: verdict(one) == "blocked" and "1 ended" in LT.offer(LT.incidents(one), [])[1],
        "one ended incident stays blocked by the steward, and says how many ended")
    chk(lambda: verdict(two + _incident(3, 2000, live_at_end=True)) == "live" and verdict(three[:-2] + _incident(4, 3000, True)) == "live",
        "a live incident stays with the steward, however many incidents ended before")
    last2 = LT.incidents(two)["ended"][-1]["at"]
    chk(lambda: verdict(two, [last2 + 30]) == "spent", "a ticket that had its one Work run is not offered again for the same two incidents")
    chk(lambda: verdict(two, [last2 - 5000]) == "offer", "a Work run before the second incident ended is no run between incidents")
    last3 = LT.incidents(three)["ended"][-1]["at"]
    chk(lambda: verdict(three, [last2 + 30]) == "offer" and verdict(three, [last2 + 30, last3 + 30]) == "spent",
        "a third ended incident makes one more offer, and its run spends it")
    chk(lambda: verdict(one + [{"event": "unblock", "id": CAUSE, "ts": _ts(500)}] ) == "live", "a return after the last block is a live incident")
    bad = two[:3] + [dict(two[3], ts="not a time")] + two[4:]
    chk(lambda: LT.offer(LT.incidents(bad), [])[0] == "could_not_look", "an incident record with an unreadable time reads could not look")
    chk(lambda: LT.offer(LT.incidents([{"event": "block", "id": CAUSE, "reason": WAITTXT}] * 2), [])[0] == "could_not_look",
        "a steward block with no time reads could not look, never ended")
    chk(lambda: LT.offer(LT.incidents(None), [])[0] == "could_not_look", "no record at all reads could not look")
    ev = LT.incidents(two)["ended"]
    chk(lambda: len(ev) == 2 and "alarm one" in ev[0]["alarm"] and "alarm 2" in ev[1]["alarm"]
        and "J1 DONE" in ev[0]["recovery"] and "J2 DONE" in ev[1]["recovery"] and ev[0]["at"] < ev[1]["at"],
        "each ended incident keeps its alarm text, its recovery and its end time")
    chk(lambda: verdict(two + [{"event": "block", "id": CAUSE, "reason": "a hand block", "ts": _ts(3000)}]) == "offer",
        "a block that is not the steward's wait ends no incident and starts none")

    # decide: the ticket has no outcome check and is blocked; the offer, and only the offer, launches it
    def row(events, runs=(), blocked=True):
        lc = LT.incidents(events)
        return dec_row({"A": it(state="ready", blocked=blocked, effect=None, verdict=None, lane_cause=lc,
                                blocked_reason=WAITTXT, title="SteveDesktop lane IDLE_EMPTY")},
                       st={"items": {"A": {"attempts": [{"at": r, "unit": "u%d" % k, "model": "opus", "cap": 12, "kind": "lane_cause"}
                                                        for k, r in enumerate(runs)]}}},
                       runs={"A": {"ended": ["u%d" % k for k in range(len(runs))]}})
    r = row(two)
    chk(lambda: r["decision"] == "launch" and r.get("kind") == "lane_cause" and r.get("model") == "opus",
        "decide: two ended incidents read launch, a lane_cause run, opus (case 1)")
    chk(lambda: row(one)["decision"] == "blocked" and "waiting for lane cause" in row(one)["why"],
        "decide: one ended incident reads blocked with the steward's reason (case 2)")
    chk(lambda: row(two + _incident(3, 2000, True))["decision"] == "blocked", "decide: a live incident reads blocked (case 3)")
    chk(lambda: row(two, runs=[last2 + 30])["decision"] == "blocked" and row(three, runs=[last2 + 30])["decision"] == "launch",
        "decide: the one run spends the offer, and a third incident offers one more (case 4)")
    chk(lambda: row(three, runs=[last2 + 30])["why"] != "" and "run 2" in row(three, runs=[last2 + 30])["why"],
        "decide: the second offer is no 'ended with no LEFT OPEN' stop, and counts its own run")
    cnl = dec_row({"A": it(state="ready", blocked=True, effect=None, verdict=None, lane_cause={"unreadable": "ts bad"},
                           blocked_reason=WAITTXT)})
    chk(lambda: cnl["decision"] == "blind" and cnl.get("could_not_look"), "decide: an unreadable incident record reads blind (could not look), never launch")
    plain = dec_row({"A": it(state="ready", blocked=True, effect=None, verdict=None, blocked_reason="owner said wait")})
    chk(lambda: plain["decision"] != "launch", "decide: a blocked ticket with no check and no lane_cause facts is not launched")
    chk(lambda: row(two)["decision"] == "launch" and dec_row({"A": it(state="ready", blocked=True, effect=None, verdict=None,
        lane_cause=LT.incidents(two), blocked_reason=WAITTXT)}, cfg=dict(CFG, enabled=False))["decision"] == "disabled",
        "decide: the lane's own gates still bind an offer")

    # the brief the offered run gets: both incidents' times, alarm text and recovery
    d = LD()
    br = d.lane_cause_brief_text("A", it(state="ready", effect=None, title="SteveDesktop lane IDLE_EMPTY"), dict(r))
    chk(lambda: "alarm one" in br and "alarm 2" in br and "J1 DONE" in br and "J2 DONE" in br and _ts(110) in br,
        "the offered run's brief carries both incidents: end time, alarm text and recovery")
    chk(lambda: "cmd:" not in br and "check holds" not in br, "the offered run's brief names no outcome check (the ticket has none)")

    # gather: the observer keeps the events of a cause ticket; the facts read from them
    op = d.Openings()
    for e in two:
        op.observe(e, None, True)
    op.observe({"event": "note", "id": "SOME_OTHER_ITEM", "text": "x", "ts": _ts(1)}, None, True)
    chk(lambda: list(op.cause_events) == [CAUSE] and len(op.cause_events[CAUSE]) == len(two),
        "the replay observer keeps the events of lane-cause tickets only")
    x = type("X", (), {"id": CAUSE, "blocked": True, "blocked_reason": WAITTXT})()
    chk(lambda: d.lane_cause_facts(x, op) == LT.incidents(two), "lane_cause_facts reads a steward-blocked cause ticket's incidents")
    x2 = type("X", (), {"id": CAUSE, "blocked": False, "blocked_reason": None})()
    x3 = type("X", (), {"id": "RIMMANDRAKE_SOME_OTHER_ITEM_X", "blocked": True, "blocked_reason": WAITTXT})()
    chk(lambda: d.lane_cause_facts(x2, op) is None and d.lane_cause_facts(x3, op) is None,
        "lane_cause_facts reads nothing for a ticket the steward does not hold blocked")
    op.cause_events[CAUSE][2]["ts"] = "garbage"      # the first incident's steward block
    chk(lambda: "unreadable" in (d.lane_cause_facts(x, op) or {}), "lane_cause_facts says could not look when an event time cannot be read")


def dec_row(items, iid="A", **kw):
    rows, _launches, _ = run(items, **kw)
    return rows[iid]


def main():
    for t in (t_decide_is_pure_and_says_why_on_every_row,
              t_the_check_runs_before_every_attempt,
              t_a_lead_takes_the_ready_tickets_of_its_home,
              t_one_work_run_then_one_more_only_on_a_named_next_act,
              t_a_launch_that_never_started_is_not_spent, t_a_list_run_that_died_spends_no_run,
              t_a_stop_names_the_outcome_the_reason_and_the_smallest_act,
              t_a_run_carries_a_mod_only_when_mod_work_reads_the_ticket_as_that_mods,
              t_waits_are_not_launched,
              t_a_block_whose_predecessor_is_done_is_not_a_block,
              t_the_gates_launch_nothing,
              t_the_lane_has_its_own_slots_and_chain_rule,
              t_a_ready_ticket_goes_to_a_host_with_room_first, t_a_ticket_of_an_archmagi_only_home_runs_on_archmagi,
              t_a_chain_counts_only_links_that_a_lane_run_filed,
              t_a_clear_grants_one_run_past_the_chain_stop, t_a_clear_keeps_the_runs_in_the_chain,
              t_a_clear_is_never_lost_to_a_tick,
              t_the_reading_says_each_machines_room,
              t_the_tick_counts_recent_lane_launches_before_taking_spare_room,
              t_an_unreadable_record_blinds_only_what_it_can_change,
              t_a_gate_held_on_could_not_look_is_told,
              t_a_raised_item_goes_first,
              t_a_lane_run_on_a_mod_takes_no_mod_slot,
              t_a_lane_run_holds_its_mod_only_on_its_files,
              t_a_passed_wait_gets_one_second_look,
              t_a_shaped_old_item_gets_its_second_look,
              t_a_claimed_item_is_not_the_lanes,
              t_oldest_blocking_item_first,
              t_the_run_owns_no_continuation,
              t_the_tick_files_nothing,
              t_a_heavy_acceptance_script_is_not_adopted,
              t_a_write_that_stands_unlanded_is_not_a_refusal, t_a_refused_close_a_run_can_repair_gets_one_run,
              t_a_dry_tick_writes_nothing,
              t_only_narrows_the_items_never_the_gates,
              t_a_mod_ticket_is_not_the_list_pipelines,
              t_each_limit_names_its_danger,
              t_blocked_idle_window_open_is_due,
              t_a_block_with_no_end_ages_whatever_its_needs,
              t_old_no_home_tickets_are_placed_then_named_for_shape,
              t_each_row_says_since_when_it_took_its_decision,
              t_a_judge_route_launches_one_fresh_judge_run,
              t_the_judge_filter_reads_the_ask_against_now,
              t_a_live_check_with_no_game_takes_a_free_game_or_waits,
              t_a_check_that_stays_blind_gets_a_repair_run,
              t_the_code_review_pause_holds_every_review_ticket,
              t_the_shipped_pause_names_the_three_kinds_and_only_them,
              t_the_pause_command_edits_one_line_and_nothing_else,
              t_the_game_work_pause_holds_every_route_of_game_work,
              t_the_game_work_pause_never_holds_pipeline_work,
              t_the_game_pause_command_sets_one_line_and_counts_the_held,
              t_a_lane_cause_ticket_seen_in_two_incidents_gets_one_work_run):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            chk(lambda: False, "%s could not run (%s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    print("selftest_list_dispatch: %s (%d fail)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
