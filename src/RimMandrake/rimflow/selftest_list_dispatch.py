#!/usr/bin/env python3
"""selftest_list_dispatch.py - the List Pipeline's Waiting, Ready and Work stages (list_dispatch.py).

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
    import control
    chk(lambda: "list_dispatch" in control.FAMILIES, "list_dispatch is a control family (pipe off family:list_dispatch)")


def t_the_lane_has_its_own_slots_and_chain_rule():
    runs = {"A": {"live": ["u1"], "ended": []}, "B": {"live": ["u2"], "ended": []}}
    chk(lambda: dec({"A": it(), "B": it(), "C": it()}, iid="C", runs=runs) == ("slots_full", []), "max_live")
    chk(lambda: dec({"A": it()}, other_live=9) == ("launch", ["A"]), "other runs do not count")
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
        record(3, 91)
        r = row()
        chk(lambda: r["decision"] == "slots_full" and "could not be read" in r["why"],
            "unreadable detached records are no spare room (got %s)" % r["decision"])


def t_a_lane_run_on_a_mod_takes_no_mod_slot():
    import maturation_dispatch as MD
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import maturation_now as MN
    v = MN.run_view({"unit": "u-lane", "item": "X", "status": "running", "at": NOW, "next_act_owner": "list_dispatch"}, NOW)
    chk(lambda: v.get("lane") == "list_dispatch", "a run's view carries the lane that launched it (%s)" % v.get("lane"))
    f = {"FlowWorks": {"live_units": ["u-drive", "u-lane"], "lane_units": ["u-lane"]},
         "Pyrelands": {"live_units": ["u-pyre"], "lane_units": []}, "ExplosiveKnockback": {"live_units": []}}
    chk(lambda: MD.occupancy(f) == 2, "the mod tick's slots count mod runs, not the list lane's (%s)" % MD.occupancy(f))
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


def t_each_limit_names_its_danger():
    c = LD().load_cfg()
    nums = [k for k, v in c.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_")]
    chk(lambda: nums and all(str(c.get("_%s_doc" % k) or "").strip() for k in nums),
        "every numeric setting has its _doc (%s)" % ", ".join(k for k in nums if not c.get("_%s_doc" % k)))


def main():
    for t in (t_decide_is_pure_and_says_why_on_every_row,
              t_the_check_runs_before_every_attempt,
              t_one_work_run_then_one_more_only_on_a_named_next_act,
              t_a_launch_that_never_started_is_not_spent, t_a_list_run_that_died_spends_no_run,
              t_a_stop_names_the_outcome_the_reason_and_the_smallest_act,
              t_waits_are_not_launched,
              t_a_block_whose_predecessor_is_done_is_not_a_block,
              t_the_gates_launch_nothing,
              t_the_lane_has_its_own_slots_and_chain_rule,
              t_the_tick_counts_recent_lane_launches_before_taking_spare_room,
              t_a_raised_item_goes_first,
              t_a_lane_run_on_a_mod_takes_no_mod_slot,
              t_a_passed_wait_gets_one_second_look,
              t_a_claimed_item_is_not_the_lanes,
              t_oldest_blocking_item_first,
              t_the_run_owns_no_continuation,
              t_the_tick_files_nothing,
              t_a_heavy_acceptance_script_is_not_adopted,
              t_a_write_that_stands_unlanded_is_not_a_refusal,
              t_a_dry_tick_writes_nothing,
              t_only_narrows_the_items_never_the_gates,
              t_a_mod_ticket_is_not_the_list_pipelines,
              t_each_limit_names_its_danger):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            chk(lambda: False, "%s could not run (%s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    print("selftest_list_dispatch: %s (%d fail)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
