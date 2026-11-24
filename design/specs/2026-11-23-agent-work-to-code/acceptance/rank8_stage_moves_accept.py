#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_MOVE_STAGES_BY_PROGRAM_REVERSES_A_WRITTEN_NEVER (rank 8 of one_page.md).

Contract: a new module src/RimMandrake/rimflow/stage_confirm.py
  decide(f) -> {"act": "advance"|"road_back"|"steward"|"wait"|"blind"|"off", "why", "skeletons": [dict], "asks": [str]}
      f = {"exit": "met"|"not met"|None, "rows": [row] or None, "build_match": bool|None, "read_after_end": bool,
           "off": text or None, "checks_edited": [check ids whose test or scene changed in this visit]}
      row = {"check", "row", "verdict": "PASS"|"FAIL"|"COULD NOT LOOK", "class": None|"MOD"|"CHECK"|"SCENE"|"ENVIRONMENT",
             "look": bool, "evidence": path, "family": str}
      advance: exit met, build match, every row PASS with no look owed, and no check edited in this visit.
      road_back: every row that is not PASS is FAIL of class MOD. One skeleton per row: check, row, evidence, class,
          family, same_cause (the other rows of its family). It joins nothing.
      steward: an unclassed row, a look, a CHECK or SCENE class, a COULD NOT LOOK row, or an edited check (`asks` says
          which). blind: rows None or empty, exit or build unreadable. wait: the rows are older than the run's end, or
          the build does not match. off: a hold or a `pipe off`.
  The boundary page holds a line `Ruling: <ledger event or item>` for the ruling that allows it.
Expected when built: PASS 16/16."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

SC = H.load("stage_confirm")


def r(check="c1", **k):
    d = {"check": check, "row": check + ":1", "verdict": "PASS", "class": None, "look": False, "evidence": "e.json", "family": "fam"}
    d.update(k)
    return d


def dec(**k):
    f = {"exit": "met", "rows": [r(), r("c2")], "build_match": True, "read_after_end": True, "off": None, "checks_edited": []}
    f.update(k)
    return H.need(SC).decide(f)


BAD = dict(verdict="FAIL", **{"class": "MOD"})
H.check("every row counts: advance", lambda: dec()["act"] == "advance")
H.check("an unclassed failure: steward, never advance", lambda: dec(exit="not met", rows=[r(), r("c2", verdict="FAIL")])["act"] == "steward")
H.check("a look is owed: steward", lambda: dec(rows=[r(look=True)])["act"] == "steward")
H.check("a wrong check: steward", lambda: dec(exit="not met", rows=[r(verdict="FAIL", **{"class": "CHECK"})])["act"] == "steward")
H.check("a wrong scene: steward", lambda: dec(exit="not met", rows=[r(verdict="FAIL", **{"class": "SCENE"})])["act"] == "steward")
H.check("a COULD NOT LOOK row: steward, never advance and never road back", lambda: dec(
    exit="not met", rows=[r(), r("c2", verdict="COULD NOT LOOK")])["act"] == "steward")
H.check("checks that were edited in this visit and all pass together: steward reads them", lambda: (
    lambda d: d["act"] == "steward" and any("c2" in a for a in d["asks"]))(dec(checks_edited=["c2"])))
H.check("mod failures: road back, one skeleton for each row", lambda: (
    lambda d: d["act"] == "road_back" and [s["check"] for s in d["skeletons"]] == ["c1", "c2"])(
        dec(exit="not met", rows=[r(**BAD), r("c2", **BAD), r("c3")])))
H.check("a skeleton holds check, row, evidence, class; same-cause rows are listed, not joined", lambda: (
    lambda s: s["row"] == "c1:1" and s["evidence"] == "e.json" and s["class"] == "MOD" and s["same_cause"] == ["c2"])(
        dec(exit="not met", rows=[r(**BAD), r("c2", **BAD)])["skeletons"][0]))
H.check("a mod failure beside an unclassed one: steward", lambda: dec(
    exit="not met", rows=[r(**BAD), r("c2", verdict="FAIL")])["act"] == "steward")
H.check("unreadable: rows None is blind", lambda: dec(rows=None)["act"] == "blind")
H.check("empty: no rows is blind, never every row counts", lambda: dec(rows=[])["act"] == "blind")
H.check("exit or build unreadable is blind", lambda: dec(exit=None)["act"] == "blind" and dec(build_match=None)["act"] == "blind")
H.check("stale: rows from before the run's end, or a build that does not match, wait", lambda: dec(
    read_after_end=False)["act"] == "wait" and dec(build_match=False)["act"] == "wait")
H.check("a hold or pipe off launches and moves nothing", lambda: dec(off="held by the owner")["act"] == "off")


def ruled():
    rel = "design/specs/2026-11-23-stage-confirm/boundary.md"
    ok = H.page(rel, "a-look-goes-to-a-steward", "could-not-look-never-advances", "edited-checks-are-read")
    with open(os.path.join(H.REPO, rel), encoding="utf-8") as f:
        t = f.read()
    return ok and re.search(r"^Ruling: \S+", t, re.M) and H.listed("src/RimMandrake/rimflow/selftest_stage_confirm.py")


H.check("the page names the ruling that allows it and its promises; the selftest runs at ./publish", ruled)
H.done(16)
