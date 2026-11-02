#!/usr/bin/env python3
"""selftest_relentless_live_round.py -- RA_S09_LIVE_WIRE_ONE_REAL_LEAF: the supervisor's live round and its pacing.

Covers relentless_live_round.py (proof lines, candidates, history, deploy args, the round's batching and early stops),
relentless.live_tick (the tick starts at most one round, paced) and live_log_check.judge. No game, no bridge, no ledger:
the run itself (relentless_live.run) has its own selftest and is swapped here.

    python3 src/RimMandrake/rimflow/selftest_relentless_live_round.py
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live_round as R      # noqa: E402
import live_log_check as G             # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def item(iid="EG_X", state="built", sha="abc123", owed=("A1", "A2"), levels=None):
    levels = levels or {"A1": "L1", "A2": "L1", "A3": "L3"}
    return {"id": iid, "state": state, "built_sha": sha, "title": "t",
            "criteria": [{"id": c, "level": lv, "text": "x"} for c, lv in sorted(levels.items())],
            "outstanding": list(owed)}


PROSE = "# EG_X\n\n- live-proof A1: python3 live_log_check.py --absent RUT_A\nlive-proof A3: echo judge\n"


def t_proof_lines():
    got = R.proof_lines(PROSE + "live-proof A1: second wins nothing\n`live-proof B12: echo b`\n")
    check("proof lines: bullet and bare lines read, first line per criterion wins",
          got == {"A1": "python3 live_log_check.py --absent RUT_A", "A3": "echo judge", "B12": "echo b"}, got)
    check("proof lines: prose that only mentions live-proof is not a line",
          R.proof_lines("we owe a live-proof for A1 someday") == {})


def t_candidates():
    now = 1_800_000_000
    its = [item(), item("FLOWWORKS_Y"), item("EG_Z", state="claimed"), item("EG_W", sha=None)]
    todo, counts = R.candidates(its, lambda i: PROSE, lambda i: "FOUNDRY" if i.startswith("FLOWWORKS") else None,
                                {}, now, 3600)
    check("candidates: only a live-level owed criterion with a proof runs (A3 is L3, A2 has no proof)",
          todo == [("EG_X", "A1", "python3 live_log_check.py --absent RUT_A", "abc123")], todo)
    check("candidates: FOUNDRY's lane and missing proofs are counted, not run",
          counts == {"FOUNDRY's lane": 1, "no proof": 1}, counts)
    at = lambda t: R.L.iso(t)    # noqa: E731
    for outcome, when, sha, runs in (("FAIL", now - 10 ** 6, "abc123", False), ("PASS", now, "abc123", False),
                                      ("REFUSED", now, "abc123", False), ("FAIL", now, "def456", True),
                                      ("UNMEASURED", now - 60, "abc123", False),
                                      ("UNMEASURED", now - 7200, "abc123", True)):
        hist = {("EG_X", "A1"): {"item": "EG_X", "criterion": "A1", "sha": sha, "outcome": outcome, "at": at(when)}}
        todo, _ = R.candidates([item()], lambda i: PROSE, lambda i: None, hist, now, 3600)
        check("history: %s on %s %ds ago -> %s" % (outcome, sha, now - when, "runs" if runs else "waits"),
              bool(todo) == runs, todo)


def t_deploy_args():
    check("deploy args: plain mods", R.deploy_args(["B", "A", "A"], {}) == "--mod A --mod B")
    check("deploy args: a folded mod plans through the composed mod, the rest beside it",
          R.deploy_args(["TerminalBiomes", "UtinniPatches"], {"TerminalBiomes": ("x", "y")})
          == "--compose biomes --with UtinniPatches")


class FakeFx(object):
    def __init__(self, game=True, mods=None):
        self.game, self.mods = game, mods or {}
        self.its = [item("EG_A"), item("EG_B"), item("EG_C"), item("EG_D")]

    def game_started(self):
        return 1.0 if self.game else None

    def items(self):
        return self.its

    def prose(self, i):
        return PROSE

    def foundry_seat(self, i):
        return None

    def folded(self):
        return {}

    def mods_of(self, sha):
        return self.mods.get(sha, ["UtinniPatches"])


def fake_run(outcomes):
    calls = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None):
        calls.append((item_id, cid, deploy))
        o, why = outcomes.get(item_id, ("PASS", "proof exit 0"))
        return {"item": item_id, "criterion": cid, "outcome": o, "why": why, "sha": "abc123"}
    return run, calls


def t_round():
    with tempfile.TemporaryDirectory() as root:
        run, calls = fake_run({})
        s = R.run_round(FakeFx(game=False), root, {}, now=1_800_000_000, run=run)
        check("round: no running game -> no run at all", calls == [] and s["why"] == "no running game", s)
        run, calls = fake_run({"EG_B": ("FAIL", "proof exit 1")})
        s = R.run_round(FakeFx(), root, {"live": {"round_max": 3}}, now=1_800_000_000, run=run)
        check("round: batches up to round_max in one sitting, a FAIL does not stop it",
              [c[0] for c in calls] == ["EG_A", "EG_B", "EG_C"] and s["eligible"] == 4, (calls, s))
        check("round: deploy args come from the item's own mods", calls[0][2] == "--mod UtinniPatches", calls)
        run, calls = fake_run({"EG_A": ("UNMEASURED", "bridge not taken: held by FOUNDRY")})
        s = R.run_round(FakeFx(), root, {}, now=1_800_000_000, run=run)
        check("round: a busy bridge ends the sitting at once", len(calls) == 1 and s["why"].startswith("stopped"), s)
        run, calls = fake_run({})
        s = R.run_round(FakeFx(mods={"abc123": ["FlowWorks"]}), root, {}, now=1_800_000_000, run=run)
        check("round: a FlowWorks game file is FOUNDRY's, never run here",
              calls == [] and all(x["outcome"] == "SKIPPED" for x in s["runs"]), s)
        rows = R.read_rows(os.path.join(root, "live", "rounds.jsonl"))
        check("round: every sitting is a rounds.jsonl row", len(rows) == 4, len(rows))


class TickFx(object):
    def __init__(self, alive=False):
        self.launched, self._alive = 0, alive

    def live_round_alive(self, pid):
        return self._alive

    def live_round_launch(self):
        self.launched += 1
        return 4242


class TickStore(object):
    def __init__(self, d):
        self.dir = d

    def p(self, *a):
        return os.path.join(self.dir, *a)

    def _write(self, path, text):
        with open(path, "w") as f:
            f.write(text)


def t_live_tick():
    import relentless as RL
    with tempfile.TemporaryDirectory() as d:
        st, fx, acts = TickStore(d), TickFx(), []
        RL.live_tick(st, fx, {"live": {}}, 1000.0, acts)
        check("tick: live.auto off starts nothing", fx.launched == 0 and acts == [])
        r = {"live": {"auto": True, "round_every_s": 600}}
        RL.live_tick(st, fx, r, 1000.0, acts)
        check("tick: auto on starts one round and records it", fx.launched == 1 and acts[-1]["do"] == "live_round")
        RL.live_tick(st, fx, r, 1100.0, acts)
        check("tick: paced, no second round inside round_every_s", fx.launched == 1)
        fx._alive = True
        RL.live_tick(st, fx, r, 5000.0, acts)
        check("tick: a round still running is never doubled", fx.launched == 1)
        fx._alive = False
        RL.live_tick(st, fx, r, 5000.0, acts)
        check("tick: after the pace and the round's end, the next one starts", fx.launched == 2)


def t_log_judge():
    log = "Mono path\nConfig error in RUT_A: bad\nRUT_B loaded fine\nwarning: RUT_C odd\n[RimBridge] Bridge token: x\n"
    code, lines = G.judge(log, ["RUT_A"])
    check("log: an error line naming the token is a FAIL", code == G.FAIL and "line 2" in lines[0], lines)
    check("log: a token only on a plain line passes", G.judge(log, ["RUT_B"])[0] == G.PASS)
    check("log: a warning line passes unless --warnings", G.judge(log, ["RUT_C"])[0] == G.PASS
          and G.judge(log, ["RUT_C"], warnings=True)[0] == G.FAIL)
    check("log: no anchor (load not finished) is UNMEASURED, never a pass",
          G.judge("Config error in nothing\n", ["RUT_Z"])[0] == G.UNMEASURED)


def main():
    for t in (t_proof_lines, t_candidates, t_deploy_args, t_round, t_live_tick, t_log_judge):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
