#!/usr/bin/env python3
"""selftest_live_round_item_gate.py -- OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU class guard.

An ITEM-level gate in relentless_live.run -- "not deployed: ..." (deploy_gap on the build's mods) or "not in the running
load: ..." (running_load_gap on the item's mods and live-mods) -- depends on the item and its build, never on the
clause. The round ran it once per owed clause, so one cause wrote N runs.jsonl rows and weighed N times in ops_watch's
relentless.live_measured_pct (2026-11-05 window, 25 of 40 rows never started a proof): TAOZIN_SPLIT L1/L2/L3 wrote
"EnvironmentalHazards has no readable packageId" three times in 17 s; GRAFFITI A2/F2 and MenuShell's two clauses the same
in seconds; WARSCAR A1 then A2 "does not cover Scarlands" on one game in two rounds.

Pinned here:
  1. in one round, once a clause of (item, build) stops at an item-level gate, the item's other clauses are skipped;
  2. across rounds, on the same game, a clause whose sibling already stopped at an item-level gate on this build is not
     due ("not deployed on this game"), as the clause itself would not be;
  3. a CLAUSE-level stop (a proof that ran and measured nothing) skips no sibling; another game or build runs them all.

    python3 src/RimMandrake/rimflow/selftest_live_round_item_gate.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live_round as R      # noqa: E402

FAILS = []
NOW = 1_800_000_000
GAME = R.L.iso(NOW - 3600)
TAOZIN_WHY = "not in the running load: EnvironmentalHazards has no readable packageId in its deployed About.xml"
SCAR_WHY = "not deployed: the deploy plan does not cover Scarlands: name it in --deploy"
PROSE = "live-proof L1: echo a\nlive-proof L2: echo b\nlive-proof L3: echo c\n"


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % (detail,)) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def item(iid, sha="1289808429"):
    return {"id": iid, "state": "built", "built_sha": sha, "title": "t",
            "criteria": [{"id": c, "level": "L1", "text": "x"} for c in ("L1", "L2", "L3")],
            "outstanding": ["L1", "L2", "L3"]}


class Fx(object):
    def __init__(self, its):
        self.its = its

    def game_started(self):
        return NOW - 3600

    def items(self):
        return self.its

    def proofs(self, i):
        return PROSE

    def folded(self):
        return {}

    def mods_of(self, sha):
        return ["EnvironmentalHazards"]


def runner(whys):
    calls = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=(), site=None, trees=()):
        calls.append((item_id, cid))
        o, why = whys.get(item_id, ("PASS", "proof exit 0"))
        return {"item": item_id, "criterion": cid, "outcome": o, "why": why, "sha": "1289808429", "game": GAME}
    return run, calls


def t_one_round():
    with tempfile.TemporaryDirectory() as root:
        run, calls = runner({"TAOZIN": ("UNMEASURED", TAOZIN_WHY)})
        s = R.run_round(Fx([item("TAOZIN"), item("OTHER")]), root, {}, max_items=10, now=NOW, run=run)
        check("instance TAOZIN L1-L3: an item-level load gate runs once, not once per clause",
              [c for c in calls if c[0] == "TAOZIN"] == [("TAOZIN", "L1")], calls)
        check("the round goes on to the next item", [c for c in calls if c[0] == "OTHER"] == [
            ("OTHER", "L1"), ("OTHER", "L2"), ("OTHER", "L3")], calls)
        check("the skipped clauses are counted in the round summary",
              (s.get("skipped") or {}).get(R.ITEM_GATED) == 2, s.get("skipped"))
        run, calls = runner({"WARSCAR": ("UNMEASURED", SCAR_WHY)})
        R.run_round(Fx([item("WARSCAR")]), root, {}, max_items=10, now=NOW, run=run)
        check("a deploy-plan gate likewise stops the item's other clauses", calls == [("WARSCAR", "L1")], calls)
        run, calls = runner({"DUD": ("UNMEASURED", "the proof exited 2: it did not measure: no river tile")})
        R.run_round(Fx([item("DUD")]), root, {}, max_items=10, now=NOW, run=run)
        check("a clause-level stop (the proof ran, measured nothing) skips no sibling", len(calls) == 3, calls)


def row(cid, why, game=GAME, sha="1289808429", iid="WARSCAR"):
    return {"item": iid, "criterion": cid, "sha": sha, "outcome": "UNMEASURED", "why": why, "game": game,
            "at": R.L.iso(NOW - 7200)}


def t_across_rounds():
    hist = R.history([row("L1", SCAR_WHY)])
    todo, counts = R.candidates([item("WARSCAR")], lambda i: PROSE, hist, NOW, 3600, GAME)
    check("instance WARSCAR A1 then A2 on one game: a sibling's item-level gate on this game and build holds every "
          "clause", todo == [] and counts.get("not deployed on this game") == 3, (todo, counts))
    todo, _ = R.candidates([item("WARSCAR")], lambda i: PROSE, hist, NOW, 3600, R.L.iso(NOW - 60))
    check("another game runs them all again", len(todo) == 3, todo)
    todo, _ = R.candidates([item("WARSCAR", sha="ffff000011")], lambda i: PROSE, hist, NOW, 3600, GAME)
    check("another build runs them all again", len(todo) == 3, todo)
    hist = R.history([row("L1", "the proof exited 2: it did not measure: A1 UNMEASURED")])
    todo, _ = R.candidates([item("WARSCAR")], lambda i: PROSE, hist, NOW, 3600, GAME)
    check("a sibling's clause-level stop holds only that clause", [t[1] for t in todo] == ["L2", "L3"], todo)
    hist = R.history([row("L1", SCAR_WHY)])
    todo, _ = R.candidates([item("WARSCAR")], lambda i: PROSE, hist, NOW, 0, GAME)
    check("a game phase's own round (retry 0: it has just staged) still runs the item", len(todo) == 3, todo)


if __name__ == "__main__":
    for t in (t_one_round, t_across_rounds):
        try:
            t()
        except Exception as e:      # noqa: BLE001  a missing name is the pre-fix instance failing, not a crash to hide
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)
