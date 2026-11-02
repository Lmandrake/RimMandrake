#!/usr/bin/env python3
"""selftest_relentless_live_round.py -- RA_S09_LIVE_WIRE_ONE_REAL_LEAF: the supervisor's live round and its pacing.

Covers relentless_live_round.py (proof lines, candidates, history, deploy args, the round's batching and early stops),
relentless.live_tick (the tick starts at most one round, paced) and live_log_check.judge. No game, no bridge, no ledger:
the run itself (relentless_live.run) has its own selftest and is swapped here.

    python3 src/RimMandrake/rimflow/selftest_relentless_live_round.py
"""
import json
import os
import re
import subprocess
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
        hist = R.history([{"item": "EG_X", "criterion": "A1", "sha": sha, "outcome": outcome, "at": at(when)}])
        todo, _ = R.candidates([item()], lambda i: PROSE, lambda i: None, hist, now, 3600)
        check("history: %s on %s %ds ago -> %s" % (outcome, sha, now - when, "runs" if runs else "waits"),
              bool(todo) == runs, todo)


def t_history_review():
    """GPT review 2026-11-01 counterexamples: per-sha terminal judgments, UTC parsing, bare backticks."""
    now = 1_800_000_000
    rows = [{"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "FAIL", "at": R.L.iso(now - 10 ** 6)},
            {"item": "EG_X", "criterion": "A1", "sha": "def456", "outcome": "PASS", "at": R.L.iso(now - 10 ** 5)},
            {"item": "EG_X", "criterion": "A1", "sha": "abc123", "outcome": "UNMEASURED", "at": R.L.iso(now - 10 ** 5)}]
    todo, _ = R.candidates([item()], lambda i: PROSE, lambda i: None, R.history(rows), now, 3600)
    check("history: a FAIL on this build stands after a later build's PASS and a later UNMEASURED", todo == [], todo)
    old = os.environ.get("TZ")
    try:
        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()
        summer = 1_782_932_400      # 2026-07-01T19:00:00Z, daylight time
        why = R.due({"sha": "s", "outcome": "UNMEASURED", "at": "2026-07-01T19:00:00Z"}, "s", summer + 60, 3600)
    finally:
        if old is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old
        time.tzset()
    check("history: an UNMEASURED a minute old in daylight time still waits (UTC parse)", why == "unmeasured lately", why)
    check("proof lines: a bare command keeps its own backticks",
          R.proof_lines("live-proof A1: echo `date`") == {"A1": "echo `date`"}, R.proof_lines("live-proof A1: echo `date`"))
    check("proof lines: a wrapped line loses only the wrapping pair",
          R.proof_lines("- `live-proof A1: echo x`") == {"A1": "echo x"}, R.proof_lines("- `live-proof A1: echo x`"))


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

    def proofs(self, i):
        return PROSE

    def foundry_seat(self, i):
        return None

    def folded(self):
        return {}

    def mods_of(self, sha):
        return self.mods.get(sha, ["UtinniPatches"])


def fake_run(outcomes):
    calls = []

    def run(fx, root, item_id, cid, proof, deploy, r, now=None, needs=()):
        calls.append((item_id, cid, deploy))
        NEEDS.append((item_id, tuple(needs)))
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
        run, calls = fake_run({})
        fx = FakeFx(mods={"abc123": ["FlowWorks"]})
        fx.its[3] = item("EG_D", sha="b2")
        s = R.run_round(fx, root, {"live": {"round_max": 1}}, now=1_800_000_000, run=run)
        check("round: FOUNDRY skips do not count toward round_max, so the item behind them runs",
              [c[0] for c in calls] == ["EG_D"], (calls, s))
        rows = R.read_rows(os.path.join(root, "live", "rounds.jsonl"))
        check("round: every sitting is a rounds.jsonl row", len(rows) == 5, len(rows))


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


def t_tick_env():
    import relentless as RL
    fx = RL.Effects.__new__(RL.Effects)
    with tempfile.TemporaryDirectory() as d:
        procs = []
        for root in ("ours", "other"):
            sp = os.path.join(d, root, "src/RimMandrake/rimflow/relentless_live_round.py")
            os.makedirs(os.path.dirname(sp))
            with open(sp, "w") as f:
                f.write("import time\ntime.sleep(30)\n")
            procs.append(subprocess.Popen([sys.executable, sp, "round"]))
        try:
            fx.books = os.path.join(d, "ours")
            check("tick: our checkout's round is alive", fx.live_round_alive(procs[0].pid))
            check("tick: another checkout's round (pid reuse) is not ours", not fx.live_round_alive(procs[1].pid))
        finally:
            for pr in procs:
                pr.kill()
                pr.wait()
    check("tick: our own pid's argv is not a round", not fx.live_round_alive(os.getpid()))
    check("tick: a dead pid is not a round", not fx.live_round_alive(2 ** 22 + 7))
    got = RL.windows_path("/usr/bin:/bin")
    want = [d for d in RL.WINDOWS_DIRS if os.path.isdir(d)]
    check("tick: the round's PATH gains the Windows dirs the systemd unit lacks (powershell.exe finds the game)",
          got.startswith("/usr/bin:/bin") and all(d in got.split(os.pathsep) for d in want), got)
    check("tick: a PATH that already has them is not doubled", RL.windows_path(got) == got)


def t_log_judge():
    log = "Mono path\nConfig error in RUT_A: bad\nRUT_B loaded fine\nwarning: RUT_C odd\n[RimBridge] Bridge token: x\n"
    code, lines = G.judge(log, ["RUT_A"])
    check("log: an error line naming the token is a FAIL", code == G.FAIL and "line 2" in lines[0], lines)
    check("log: a token only on a plain line passes", G.judge(log, ["RUT_B"])[0] == G.PASS)
    check("log: a warning line passes unless --warnings", G.judge(log, ["RUT_C"])[0] == G.PASS
          and G.judge(log, ["RUT_C"], warnings=True)[0] == G.FAIL)
    check("log: no anchor (load not finished) is UNMEASURED, never a pass",
          G.judge("Config error in nothing\n", ["RUT_Z"])[0] == G.UNMEASURED)
    a = "\n[RimBridge] Bridge token: x\n"
    check("log: an exception whose stack trace names the token on a later line is a FAIL",
          G.judge("Exception loading def:\n  defName: RUT_PaleMoss\n  at Verse.X()\n" + a, ["RUT_PaleMoss"])[0] == G.FAIL)
    check("log: a token that contains 'Error' is not itself an error line",
          G.judge("Loaded RUT_ErrorPlant successfully" + a, ["RUT_ErrorPlant"])[0] == G.PASS)
    check("log: '2 errors' and 'Exceptions' naming a token fail (GPT r2)",
          G.judge("2 errors while loading RUT_A" + a, ["RUT_A"])[0] == G.FAIL
          and G.judge("Exceptions encountered while loading RUT_A" + a, ["RUT_A"])[0] == G.FAIL)
    check("log: a blank line or a [Ref] stub does not split an error from its token (GPT r2)",
          G.judge("Exception loading def:\n\n  defName: RUT_A" + a, ["RUT_A"])[0] == G.FAIL
          and G.judge("Exception loading def:\n[Ref C0FFEE]\n  defName: RUT_A" + a, ["RUT_A"])[0] == G.FAIL)
    check("log: another identifier ending in Error is not an error word (GPT r2)",
          G.judge("Loaded RUT_A; fallback=RUT_NoError" + a, ["RUT_A"])[0] == G.PASS
          and G.judge("Loaded RUT_AError" + a, ["RUT_A", "RUT_AError"])[0] == G.PASS)
    check("log: '0 errors' is not an error line", G.judge("RUT_PaleMoss: 0 errors" + a, ["RUT_PaleMoss"])[0] == G.PASS)
    check("log: NullReferenceException naming the token is a FAIL",
          G.judge("NullReferenceException in RUT_PaleMoss tick" + a, ["RUT_PaleMoss"])[0] == G.FAIL)
    check("log: the next message after an error is its own record",
          G.judge("Config error in RUT_A: bad\nRUT_PaleMoss loaded" + a, ["RUT_PaleMoss"])[0] == G.PASS)
    check("log: a failed patch's unindented `file:` line belongs to its record (Player.log, 2026-11-01)",
          G.judge("[M] Patch operation Verse.PatchOperationAdd(Defs/X) failed\nfile: C:\\M\\Patches\\RUT_Loot.xml" + a,
                  ["RUT_Loot"])[0] == G.FAIL)


def t_log_never():
    """LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST: a Log.Warning reaches Player.log as bare text, so --never names it."""
    a = "\n[RimBridge] Bridge token: x\n"
    warn = "[RM Minerals] quarry: no OreDictionary; quarries keep the Quarry mod's own draw" + a
    check("never: bare warning text is invisible to --warnings", G.judge(warn, ["[RM Minerals] quarry"], True)[0] == G.PASS)
    check("never: --never sees it", G.judge(warn, [], never=["[RM Minerals] quarry"])[0] == G.FAIL)
    check("never: absent text passes", G.judge("RUT_A loaded" + a, [], never=["[RM Minerals] quarry"])[0] == G.PASS)
    check("never: no anchor is UNMEASURED", G.judge(warn.split("\n")[0], [], never=["x"])[0] == G.UNMEASURED)
    check("never: a stack-trace line naming it fails", G.judge("Exception x\n  at RM_MineralQuarry.PlanFor()" + a, [],
                                                            never=["RM_MineralQuarry.PlanFor"])[0] == G.FAIL)
    import io, contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = G.safe_main(["--never", "x", "--log", "/nonexistent/dir/Player.log"])
    check("never: an unreadable log is UNMEASURED", code == G.UNMEASURED, out.getvalue())
    real_main = G.main
    G.main = lambda argv=None: (_ for _ in ()).throw(UnicodeEncodeError("ascii", "é", 0, 1, "x"))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            check("log: a crash inside main is UNMEASURED, never exit 1 (GPT r1)", G.safe_main([]) == G.UNMEASURED)
    finally:
        G.main = real_main
    check("never and absent combine", G.judge("Config error in RUT_A" + a, ["RUT_A"], never=["zzz"])[0] == G.FAIL)


def t_proofs_file():
    """LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST: proofs live in live_proofs/<ID>.txt, never the item's prose (the
    Marker's box drops infrastructure/state/items, so a proof there could never be checked blind)."""
    fx = R.RoundFx.__new__(R.RoundFx)
    with tempfile.TemporaryDirectory() as d:
        fx.books = d
        os.makedirs(os.path.join(d, R.PROOFS_DIR))
        os.makedirs(os.path.join(d, "infrastructure/state/items"))
        with open(os.path.join(d, R.PROOFS_DIR, "EG_A.txt"), "w") as f:
            f.write("live-proof A1: echo a\n")
        with open(os.path.join(d, "infrastructure/state/items/EG_B.md"), "w") as f:
            f.write("live-proof A1: echo b\n")
        check("proofs: read from live_proofs/<ID>.txt", R.proof_lines(fx.proofs("EG_A")) == {"A1": "echo a"})
        check("proofs: an item's prose is not a source", fx.proofs("EG_B") == "")
    real = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), R.PROOFS_DIR)
    names = sorted(os.listdir(real)) if os.path.isdir(real) else []
    bad = []
    crit_line = re.compile(r"^[A-Z]+\d+ [A-Z0-9-]+: \S")     # <ID>.criteria: `A2 L1: what is observed` (worker brief)
    for n in names:
        with open(os.path.join(real, n), encoding="utf-8") as f:
            for line in f:
                ok = crit_line.match(line) if n.endswith(".criteria") else (R.PROOF_LINE.match(line.rstrip("\n"))
                                                                             or R.LIVE_MODS.match(line.rstrip("\n")))
                if line.strip() and not line.startswith("#") and not ok:
                    bad.append("%s: %s" % (n, line[:60]))
    check("proofs: every real live_proofs file is .txt (or .criteria) and every line parses", names and all(
        n.endswith((".txt", ".criteria")) for n in names) and not bad, "%s %s" % (names[:3], bad[:3]))


NEEDS = []


def t_live_mods():
    """PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS: a proof file names the mods its proofs need (`live-mods:`), and the
    round hands them to the gate, so a small list that holds them is enough and a list that lacks them is UNMEASURED."""
    text = "live-mods: Graffiti, SacredGraffiti\n- `live-mods: Graffiti EGrowth`\nlive-proof A1: echo a\n"
    check("live-mods: every line, in order, no repeats", R.live_mods(text) == ["Graffiti", "SacredGraffiti", "EGrowth"],
          R.live_mods(text))
    check("live-mods: none named -> none", R.live_mods("live-proof A1: echo a\n") == [])
    check("live-mods: a live-mods line is not a proof line", R.proof_lines(text) == {"A1": "echo a"})
    del NEEDS[:]
    fx = FakeFx()
    fx.proofs = lambda i: "live-mods: Graffiti\n" + PROSE
    with tempfile.TemporaryDirectory() as root:
        R.run_round(fx, root, {"live": {"round_max": 1}}, now=1_800_000_000, run=fake_run({})[0])
    check("live-mods: the round passes them to the gate", NEEDS[:1] == [("EG_A", ("Graffiti",))], NEEDS)


def t_real_lane():
    """The real lane lookup imports priority as the package does (a plain `import priority` fails on its relative
    imports, and the fakes above never reach it)."""
    fx = R.RoundFx.__new__(R.RoundFx)
    try:
        got = (fx.foundry_seat("FLOWWORKS_SELFTEST_PROBE"), fx.foundry_seat("EGROSTER_SELFTEST_PROBE"))
    except Exception as e:     # noqa: BLE001
        got = e
    check("lane: the real FlowWorks lane loads and names a seat for a FlowWorks id only",
          isinstance(got, tuple) and got[0] and got[1] is None, got)


def main():
    for t in (t_proof_lines, t_proofs_file, t_candidates, t_deploy_args, t_round, t_live_mods, t_live_tick, t_log_judge, t_log_never, t_real_lane,
              t_history_review, t_tick_env):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
