#!/usr/bin/env python3
"""Acceptance for plan.md step 2 (the Ready and Work stages of the Workshop Pipeline): the tick's decisions, over fake
facts. Nothing is launched.

Contract: a new module src/RimMandrake/rimflow/list_dispatch.py with its settings list_dispatch.json beside it.
  decide(cfg, st, facts, now, account=(True, "")) -> (rows, launches)      pure over its inputs; may mutate st
    cfg   {"enabled": bool, "max_live": int, "max_chain_depth": int, "max_runs_per_item": int, ...}
    st    {"items": {id: {"attempts": [{"unit": str, "failed": str or None, "next": str or None}], ...}}}
          "next" is the next act that the ended run named as its own to do, or None
    facts {"items": {id: {"state", "blocked", "effect", "verdict", "depth", "waits_on": [open item ids]}} or None
           (the ledger could not be read),
           "runs": {id: {"live": [unit], "ended": [unit]}}, "other_live": int (mod and nightly-test runs)}
    each row {"item", "decision", "why"}; a "stopped" row also has "need": {"outcome", "why_not_recovered",
    "smallest_act"}, all three non-empty.
  load_cfg() -> the shipped settings; every numeric limit NAME has a "_NAME_doc" that names the danger it guards.
Expected: PASS 20/20. Watched failing 0/20 on 5a64425b3ae8 (list_dispatch.py absent); moved here green."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

LD, why = H.load("list_dispatch")
CFG = {"enabled": True, "max_live": 2, "max_chain_depth": 2, "max_runs_per_item": 2}
NOW = 1_800_000_000.0


def it(state="open", blocked=False, effect="cmd:false", verdict="fails", depth=0, waits_on=()):
    return {"state": state, "blocked": blocked, "effect": effect, "verdict": verdict, "depth": depth,
            "waits_on": list(waits_on)}


def run(items, runs=None, st=None, cfg=None, account=(True, ""), other_live=0):
    if LD is None:
        raise RuntimeError(why)
    rows, launches = LD.decide(dict(cfg or CFG), st if st is not None else {"items": {}},
                               {"items": items, "runs": runs or {}, "other_live": other_live}, NOW, account=account)
    return {r["item"]: r for r in rows}, launches


def dec(items, iid="A", **kw):
    rows, launches = run(items, **kw)
    return rows[iid]["decision"], launches


ENDED = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None, "next": None}]}}}
NEXT1 = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None, "next": "apply the 103 commands"}]}}}
NEXT2 = {"items": {"A": {"attempts": [{"unit": "u1", "failed": None, "next": "apply"}, {"unit": "u2", "failed": None, "next": "verify"}]}}}
BOTH = {"live": [], "ended": ["u1", "u2"]}
NEVER = {"items": {"A": {"attempts": [{"unit": "u1", "failed": "never started: transient"}]}}}

H.check("a failing check and nothing live: launch", lambda: dec({"A": it()}) == ("launch", ["A"]))
H.check("a check that already holds: close, no launch", lambda: dec({"A": it(verdict="holds")}) == ("close", []))
H.check("an unmeasured check: blind, no launch", lambda: dec({"A": it(verdict="unmeasured")}) == ("blind", []))
H.check("an item with no check is not the lane's: no launch",
        lambda: dec({"A": it(effect=None, verdict=None)}) == ("no_effect", []))
H.check("a closed item and a blocked item: nothing",
        lambda: dec({"A": it(state="done")})[1] == [] and dec({"A": it(blocked=True)}) == ("blocked", []))
H.check("a live run on the item: nothing", lambda: dec({"A": it()}, runs={"A": {"live": ["u1"], "ended": []}}) == ("live", []))
H.check("a run ended, the check fails, and the run named its next act: one more Work run",
        lambda: dec({"A": it()}, runs={"A": {"live": [], "ended": ["u1"]}}, st=dict(NEXT1)) == ("launch", ["A"]))
H.check("two Work runs is the most: after the second, stopped",
        lambda: dec({"A": it()}, runs={"A": BOTH}, st=dict(NEXT2)) == ("stopped", []))
H.check("a run ended with no next act and the check still fails: stopped",
        lambda: dec({"A": it()}, runs={"A": {"live": [], "ended": ["u1"]}}, st=dict(ENDED)) == ("stopped", []))
H.check("a stopped row names the outcome at risk, why recovery was not enough, and the smallest act",
        lambda: all(run({"A": it()}, runs={"A": {"live": [], "ended": ["u1"]}}, st=dict(ENDED))[0]["A"]["need"].get(k)
                    for k in ("outcome", "why_not_recovered", "smallest_act")))
H.check("the helper died after it did the work: the check holds, so close (no stop, no rerun)",
        lambda: dec({"A": it(verdict="holds")}, runs={"A": {"live": [], "ended": ["u1"]}}, st=dict(ENDED)) == ("close", []))
H.check("a launch that never started is not a spent attempt: launch again",
        lambda: dec({"A": it()}, st=dict(NEVER)) == ("launch", ["A"]))
H.check("max_live live list runs: slots_full for the next item",
        lambda: dec({"A": it(), "B": it(), "C": it()}, iid="C",
                    runs={"A": {"live": ["u1"], "ended": []}, "B": {"live": ["u2"], "ended": []}}) == ("slots_full", []))
H.check("mod and nightly-test runs do not use the Workshop Pipeline's slots",
        lambda: dec({"A": it()}, other_live=5) == ("launch", ["A"]))
H.check("an account hold launches nothing", lambda: dec({"A": it()}, account=(False, "drain")) == ("account_hold", []))
H.check("a chain that already holds max_chain_depth lane runs is not launched",
        lambda: dec({"A": it(depth=2)}) == ("chain_stop", []))
H.check("Ready: an item that depends on an open item is not launched, and its row names that item",
        lambda: (lambda rl: rl[0]["A"]["decision"] == "waits_on" and "B_OPEN" in rl[0]["A"]["why"] and rl[1] == [])(
            run({"A": it(waits_on=["B_OPEN"])})))
H.check("Ready: every row that is not launched says why in words",
        lambda: all(str(r.get("why") or "").strip() for r in run(
            {"A": it(waits_on=["B_OPEN"]), "B": it(depth=2), "C": it(blocked=True)})[0].values()))
H.check("an unreadable ledger is one blind row and no launch",
        lambda: (lambda rl: len(rl[0]) == 1 and next(iter(rl[0].values()))["decision"] == "blind" and rl[1] == [])(
            (lambda rows, launches: ({r["item"]: r for r in rows}, launches))(
                *LD.decide(dict(CFG), {"items": {}}, {"items": None, "runs": {}, "other_live": 0}, NOW))) if LD else (_ for _ in ()).throw(RuntimeError(why)))
H.check("each shipped numeric limit names the danger it guards",
        lambda: (lambda c: all(str(c.get("_%s_doc" % k) or "").strip() for k, v in c.items()
                               if isinstance(v, (int, float)) and not isinstance(v, bool) and not k.startswith("_"))
                 and "max_live" in c and "max_chain_depth" in c)(LD.load_cfg() if LD else (_ for _ in ()).throw(RuntimeError(why))))
H.done(20)
