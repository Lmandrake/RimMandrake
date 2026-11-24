#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED (rank 5 of one_page.md).

Contract: src/RimMandrake/rimflow/run_end_wake.py gains
  report_of(rec) -> {"status": "value"|"empty"|"failed"|"could_not_look", "text": str, "why": str}
      rec is a pending record {"unit", "state", "result": path of the .out.json, "item", "at"}. The text is the run's
      whole last message (detached_helper.run_report's rule). An is_error result is "failed" and keeps its text.
  render(recs, state_block=None) -> str       each record's whole text; a record whose state is not success, whose
      status is not "value", or whose text holds LEFT OPEN: or OWED, stands before the routine ones; state_block is
      appended when it is given.
  state_block(readers=None, now=None, deadline_s=20) -> str     readers {"locks": fn, "pipe": fn, "accounts": fn}; each
      line carries the local Pacific time of its reading; a reader that raises or outlives the deadline reads
      COULD NOT LOOK with its name and cause; an empty answer reads "none (looked)".
Expected when built: PASS 15/15."""
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

RW = H.load("run_end_wake")
T = tempfile.mkdtemp()
N = [0]


def rec(result="the answer", raw=None, missing=False, state="success (0)", is_error=False):
    N[0] += 1
    p = os.path.join(T, "u%d.out.json" % N[0])
    if not missing:
        with open(p, "w") as f:
            f.write(raw if raw is not None else json.dumps({"type": "result", "result": result, "is_error": is_error,
                                                            "total_cost_usd": 12.34, "session_id": "s", "num_turns": 3}))
    return {"unit": "u%d" % N[0], "state": state, "result": p, "item": "ITEM_%d" % N[0], "at": N[0]}


def rp(r):
    return H.need(RW).report_of(r)


def rd(*a, **k):
    return H.need(RW).render(*a, **k)


LONG = "HEAD " + "x" * 40000 + " MIDDLE-FACT " + "y" * 40000 + " TAIL"
H.check("a result is a value and its whole text", lambda: rp(rec("hello"))["status"] == "value"
        and rp(rec("hello"))["text"] == "hello")
H.check("the rendered wake holds the text", lambda: "the answer" in rd([rec()]))
H.check("a long result is not cut: head, middle and tail are there",
        lambda: all(s in rd([rec(LONG)]) for s in ("HEAD", "MIDDLE-FACT", "TAIL")))
H.check("empty: an empty last message reads empty, not value and not could not look",
        lambda: rp(rec(""))["status"] == "empty" and "EMPTY" in rd([rec("")]))
H.check("missing: no result file reads could not look and names the path", lambda: (
    lambda r: rp(r)["status"] == "could_not_look" and r["result"] in rd([r]) and "COULD NOT LOOK" in rd([r]))(
        rec(missing=True)))
H.check("torn: a half-written file reads could not look", lambda: rp(rec(raw='{"result": "ab'))["status"] == "could_not_look")
H.check("failed: an error result reads failed and keeps its text", lambda: (
    lambda r: rp(r)["status"] == "failed" and "boom" in rp(r)["text"] and "FAILED" in rd([r]))(
        rec("boom", is_error=True, state="failed (1)")))
H.check("a run that needs him or is left open stands before a routine run", lambda: (
    lambda t: t.index("pick one") < t.index("routine words"))(
        rd([rec("routine words"), rec("LEFT OPEN: pick one of two")])))
H.check("no spend figure of the result file reaches the wake", lambda: "12.34" not in rd([rec()])
        and H.no_spend(rd([rec()])))
H.check("the state block names each reader's answer and a time", lambda: (
    lambda b: "free" in b and "running" in b and "PST" in b)(H.need(RW).state_block(
        {"locks": lambda: "free", "pipe": lambda: "running", "accounts": lambda: "x"}, now=1795492604)))


def boom():
    raise OSError("store unreadable")


H.check("a reader that fails reads COULD NOT LOOK with its name, and the others still answer", lambda: (
    lambda b: "COULD NOT LOOK" in b and "pipe" in b and "unreadable" in b and "free" in b)(H.need(RW).state_block(
        {"locks": lambda: "free", "pipe": boom})))


def hung():
    f = H.need(RW).state_block      # absent: fail at once, with no sleeping reader left behind
    t0 = time.time()
    b = f({"locks": lambda: time.sleep(8), "pipe": lambda: "running"}, deadline_s=1)
    return "COULD NOT LOOK" in b and "running" in b and time.time() - t0 < 6


H.check("a reader that hangs reads COULD NOT LOOK inside its deadline", hung)
H.check("an empty answer reads none (looked), not could not look", lambda: (
    lambda b: "none (looked)" in b and "COULD NOT LOOK" not in b)(H.need(RW).state_block({"locks": lambda: ""})))
H.check("the page names its promises", lambda: H.page(
    "design/specs/2026-11-23-wake-carries-result/boundary.md", "the-whole-last-message", "could-not-look-is-said",
    "the-window-reads-it-whole"))
H.check("its selftest runs at ./publish", lambda: H.listed("src/RimMandrake/rimflow/selftest_run_end_wake_result.py"))
H.done(15)
