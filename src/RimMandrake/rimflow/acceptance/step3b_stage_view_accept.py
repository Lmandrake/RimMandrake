#!/usr/bin/env python3
"""Acceptance for plan.md step 3 (the stage view of the Workshop Pipeline): one stage function, and the six answers.

Contract: a new module src/RimMandrake/rimflow/list_pipeline.py
  stage_of(item, now) -> {"stage": one of STAGES, "why": str, "resumes": str or None, "promise": None|"kept"|"dead"}
      item = {"state", "effect", "verdict", "route": None or {"who", "ask", "resumes"}, "waits": None or
              {"on": str, "resumes": str, "until": epoch or None}, "run": None|"live_shape"|"live_work"|"ended",
              "stopped": bool, "promise": None|"kept"|"dead"}
      STAGES = ("shape", "waiting", "ready", "work", "verify", "closed", "trouble", "review", "conflict", "unmeasured")
  six(items, now) -> {"doing", "next", "closed", "open_why", "escalated", "review"}
      items = {id: item (as above, plus "age_h")}; "open_why" = {reason: {"count", "oldest", "age_h", "items"}}
  The tick and the page use this one function: list_dispatch.py and maturation_now.py both call stage_of.
Expected when built: PASS 17/17.  Today: FAIL 0/17, because list_pipeline.py does not exist."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

LP, why = H.load("list_pipeline")
NOW = 1_800_000_000.0


def it(**kw):
    d = {"state": "open", "effect": "cmd:false", "verdict": "fails", "route": None, "waits": None, "run": None,
         "stopped": False, "promise": None, "age_h": 1}
    d.update(kw)
    return d


def st(**kw):
    if LP is None:
        raise RuntimeError(why)
    return LP.stage_of(it(**kw), NOW)


def six(items):
    if LP is None:
        raise RuntimeError(why)
    return LP.six(items, NOW)


def src(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


ROUTE = {"who": "owner", "ask": "pick the bridge art", "resumes": "his card answer"}
ITEMS = {"A": it(run="live_work"), "B": it(), "C": it(state="done", verdict="holds"),
         "D": it(waits={"on": "X_OPEN", "resumes": "X_OPEN closes", "until": None}, age_h=50),
         "E": it(waits={"on": "X_OPEN", "resumes": "X_OPEN closes", "until": None}, age_h=5),
         "F": it(stopped=True, run="ended"), "G": it(effect=None, verdict=None, route=ROUTE)}

H.check("no check and no route: shape", lambda: st(effect=None, verdict=None)["stage"] == "shape")
H.check("a live Shape run: shape; a live Work run: work",
        lambda: st(effect=None, verdict=None, run="live_shape")["stage"] == "shape" and st(run="live_work")["stage"] == "work")
H.check("a failing check and nothing waited on: ready", lambda: st()["stage"] == "ready")
H.check("a wait names what resumes it",
        lambda: (lambda r: r["stage"] == "waiting" and r["resumes"] == "X closes")(
            st(waits={"on": "X", "resumes": "X closes", "until": None})))
H.check("a wait whose date has come is not still waiting",
        lambda: st(waits={"on": "date", "resumes": "the date", "until": NOW - 60})["stage"] != "waiting")
H.check("a run that ended and a check not yet run: verify", lambda: st(run="ended", verdict=None)["stage"] == "verify")
H.check("a check that holds: closed", lambda: st(verdict="holds", state="done")["stage"] == "closed")
H.check("a stopped item: trouble", lambda: st(stopped=True, run="ended")["stage"] == "trouble")
H.check("an item routed to the owner: review, and it names what resumes it",
        lambda: (lambda r: r["stage"] == "review" and r["resumes"] == "his card answer")(st(effect=None, verdict=None, route=ROUTE)))
H.check("a closed operational item carries its promise apart from its stage",
        lambda: (lambda r: r["stage"] == "closed" and r["promise"] == "dead")(st(verdict="holds", state="done", promise="dead")))
H.check("facts that disagree (closed, and the check fails) are shown as a conflict, never picked silently",
        lambda: st(state="done", verdict="fails")["stage"] == "conflict")
H.check("a check that could not be run is unmeasured, never closed or ready",
        lambda: st(verdict="unmeasured")["stage"] == "unmeasured")
H.check("every stage answer says why in words",
        lambda: all(str(st(**k)["why"]).strip() for k in ({}, {"stopped": True}, {"verdict": "unmeasured"})))
H.check("six: doing now is the live run; next is the ready item",
        lambda: (lambda s: [r["item"] for r in s["doing"]] == ["A"] and [r["item"] for r in s["next"]] == ["B"])(six(ITEMS)))
H.check("six: open-and-why groups open items by their reason, each group with its oldest item and age",
        lambda: (lambda g: g["count"] == 2 and g["oldest"] == "D" and g["age_h"] == 50)(
            next(v for k, v in six(ITEMS)["open_why"].items() if "X_OPEN" in k)))
H.check("six: escalated holds the trouble item, review holds the routed item, closed holds the closed one",
        lambda: (lambda s: [r["item"] for r in s["escalated"]] == ["F"] and [r["item"] for r in s["review"]] == ["G"]
                 and [r["item"] for r in s["closed"]] == ["C"])(six(ITEMS)))
H.check("the tick and the page call the one stage function",
        lambda: "stage_of(" in src(os.path.join(H.RIMFLOW, "list_dispatch.py"))
        and "stage_of(" in src(os.path.join(H.UTILS, "maturation_now.py")))
H.done(17)
