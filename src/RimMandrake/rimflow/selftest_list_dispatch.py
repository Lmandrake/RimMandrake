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
    never = {"unit": None, "failed": "never started: pool full"}
    chk(lambda: dec({"A": it()}, st=att(never)) == ("launch", ["A"]), "one never-started launch: launch again")
    chk(lambda: dec({"A": it()}, st=att(never, dict(never))) == ("stopped", []),
        "max_never_started never-started launches in a row: stopped")
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


def t_the_gates_launch_nothing():
    chk(lambda: dec({"A": it()}, cfg=dict(CFG, enabled=False)) == ("disabled", []), "disabled")
    chk(lambda: dec({"A": it()}, paused="paused by the Conductor") == ("pipeline_paused", []), "the pause")
    chk(lambda: dec({"A": it(off="pipe off family:list_dispatch")}) == ("off", []), "pipe off")
    chk(lambda: dec({"A": it(held="HELD BY OWNER: FeverWood")}) == ("held", []), "a held mod")
    chk(lambda: dec({"A": it(off_unreadable="control store unreadable")}) == ("blind", []), "an unreadable store")
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
    w = {"A": {"caused_by": None}, "B": {"caused_by": "A"}, "C": {"caused_by": "B"}}
    st = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None}]},
                    "B": {"attempts": [{"unit": "u2", "failed": None}, {"unit": None, "failed": "never started"}]}}}
    chk(lambda: LD().chain_depth("C", lambda i: w.get(i, {}).get("caused_by"), st) == 2,
        "chain depth counts spent lane runs on the ancestors only")


def t_a_claimed_item_is_not_the_lanes():
    chk(lambda: dec({"A": it(claimed="BENCH holds a live lease")}) == ("claimed", []), "a claimed item: no launch")
    chk(lambda: dec({"A": it(effect=None, verdict=None, accept="a/b_accept.py", claimed="BENCH holds a live lease")})
        == ("claimed", []), "a claimed item is not adopted")
    chk(lambda: dec({"A": it(claimed="BENCH")}, st=att({"unit": "u1", "failed": None, "next": "x"}),
                    runs={"A": {"live": [], "ended": ["u1"]}}) == ("launch", ["A"]),
        "the lane's own run's lease does not stop its second run")


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


def t_each_limit_names_its_danger():
    c = LD().load_cfg()
    nums = [k for k, v in c.items() if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_")]
    chk(lambda: nums and all(str(c.get("_%s_doc" % k) or "").strip() for k in nums),
        "every numeric setting has its _doc (%s)" % ", ".join(k for k in nums if not c.get("_%s_doc" % k)))


def main():
    for t in (t_decide_is_pure_and_says_why_on_every_row,
              t_the_check_runs_before_every_attempt,
              t_one_work_run_then_one_more_only_on_a_named_next_act,
              t_a_launch_that_never_started_is_not_spent,
              t_a_stop_names_the_outcome_the_reason_and_the_smallest_act,
              t_waits_are_not_launched,
              t_the_gates_launch_nothing,
              t_the_lane_has_its_own_slots_and_chain_rule,
              t_a_claimed_item_is_not_the_lanes,
              t_oldest_blocking_item_first,
              t_the_run_owns_no_continuation,
              t_the_tick_files_nothing,
              t_a_heavy_acceptance_script_is_not_adopted,
              t_a_dry_tick_writes_nothing,
              t_only_narrows_the_items_never_the_gates,
              t_each_limit_names_its_danger):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a promise whose test cannot run is a FAIL, never a crash
            chk(lambda: False, "%s could not run (%s: %s)" % (t.__name__, type(e).__name__, str(e)[:300]))
    print("selftest_list_dispatch: %s (%d fail)" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
