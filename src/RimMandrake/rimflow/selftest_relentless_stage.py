#!/usr/bin/env python3
"""STAGING_REWIRE_PYTHON_NOT_AN_LLM: Relentless's game staging is relentless_stage.py, not an LLM session.

  the step order: deploy plan -> (stop on a hand-edited game copy) -> game down -> apply -> modlist_swap (restore for a
  final, --enable) -> Steam launch -> wait for the bridge token, bounded -> up -> remedies -> game-ready; each known
  stop is a game_stage snag; an unhandled exception, and only that, execs the LLM fallback; the supervisor's unit runs
  this file with the plan beside its output; stage_plan never deploys a packageId; `holds` pairs game_stage with
  game_staged in the journal.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless  # noqa: E402
import relentless_game as G  # noqa: E402
import relentless_stage as S  # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


CLEAN = "Armoury          mandrake.rm.armoury\n    ~  Defs/A.xml\n\nDrift found. Re-run with --apply to deploy.\n"
HAND = ("Armoury          mandrake.rm.armoury\n    -  Defs/Theirs.xml   (in game, not in repo; kept — use --prune to delete,"
        " or --pull to rescue)\n\nDrift found. Re-run with --apply to deploy.\n")
PRUNED = ("Armoury          mandrake.rm.armoury\n    -  Defs/Old.xml   (in game, not in repo; deleted in repo -- --apply "
          "prunes it)\n\nDrift found. Re-run with --apply to deploy.\n")


DIED = ("Mono path[0] = ...\nLoading game\nCould not find type named RimMandrake.Armoury.CompFoo from node <li>\n"
        "Exception in BuildDefs: NullReferenceException\n")


class Cursor(object):
    def __init__(self, ops):
        self.ops = ops

    def wait(self, token, budget, abort=None):
        self.ops.calls.append(("wait", token, budget))
        if self.ops.token == "gone":      # polled as logwait does: abort() each 3 s until it answers or the bound
            self.ops.up = False
            t0 = self.ops.t
            while self.ops.t - t0 < budget:
                why = abort()
                if why:
                    return {"ok": False, "why": why, "waited_s": self.ops.t - t0}
                self.ops.t += 3
            return {"ok": False, "why": "timeout", "waited_s": budget}
        if self.ops.token == "slow":
            return {"ok": False, "why": "timeout after %d s" % budget, "waited_s": budget}
        self.ops.up = True
        return {"ok": True, "waited_s": 22}


class FakeOps(object):
    def __init__(self, up=True, plan_out=CLEAN, token="ok", bound=400, stubborn=0, fail=None, blind=False, log=DIED):
        self.up, self.plan_out, self.token, self.bound, self.log, self.records = up, plan_out, token, bound, log, []
        self.stubborn, self.fail, self.blind = stubborn, fail or {}, blind
        self.calls, self.t, self.reports = [], 1000.0, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def sh(self, argv, timeout=480):
        tag = ("apply" if "--apply" in argv and argv[1:2] == [S.DEPLOY] else "plan" if argv[1:2] == [S.DEPLOY]
               else "restore" if "--restore" in argv else "minimal" if "--minimal" in argv else "enable" if "--enable" in argv else argv[0])
        self.calls.append((tag, argv))
        if tag in self.fail:
            return self.fail[tag]
        return (1, self.plan_out) if tag == "plan" else (0, "done")

    def running(self):
        if self.blind:
            raise RuntimeError("tasklist.exe exit 1: blind")
        return self.up

    def kill(self, force=False):
        self.calls.append(("kill", force))
        if self.stubborn and not force:
            return 0, ""
        self.up = False
        return 0, ""

    def stamp(self, state):
        self.calls.append(("stamp", state))
        return 0, ""

    def cursor(self):
        self.calls.append(("cursor",))
        return Cursor(self)

    def launch(self):
        self.calls.append(("launch",))
        return 0, ""

    def load_bound(self):
        return self.bound

    def log_text(self):
        return self.log

    def record(self, rec):
        self.records.append(rec)

    def report(self, verb, text, klass=None):
        self.reports.append((verb, text, klass))
        return 0, "reported"


PLAN = {"item": "I0", "gen": 2, "sha": "abc", "full": False, "enable": ["Armoury", "ferny.worldbuilder"],
        "deploy": ["--mod Armoury"], "riders": [], "remedy_cmds": ["python.exe m.py run Armoury"], "max_s": 3600}


def tags(ops):
    return [c[0] if c[0] != "stamp" else "stamp:" + c[1] for c in ops.calls]


def t_hazards():
    ok(S.plan_hazards(CLEAN) is None, "a clean plan has no hazard")
    ok("Defs/Theirs.xml" in (S.plan_hazards(HAND) or ""), "a kept `-` line (another seat's file) is a hazard, named")
    ok(S.plan_hazards(PRUNED) is None, "a repo-deleted `-` line is a prune, not a hazard")
    ok("refuses" in (S.plan_hazards("  ! REFUSING TO DEPLOY: malformed XML\nDrift found.\n") or ""), "a refusal stops")
    ok("did not finish" in (S.plan_hazards("Armoury  x\n    ~  Defs/A.xml\n") or ""), "a plan cut short stops")


def t_order():
    ops = FakeOps(up=True)
    v, text = S.run(PLAN, ops)
    seq = tags(ops)
    want = ["plan", "stamp:going-down", "kill", "stamp:down", "apply", "minimal", "enable", "stamp:loading", "cursor", "launch",
            "wait", "stamp:up", "bash"]
    ok(v == "ready" and seq == want, "the steps run in the item's order: %s" % seq)
    ok(seq.index("kill") < seq.index("apply"), "the apply (stale DLLs with it) runs in the shutdown window")
    ok(seq.index("cursor") < seq.index("launch"), "the log cursor opens before the launch: no old session's token")
    en = [c[1] for c in ops.calls if c[0] == "enable"][0]
    ok(en[-1] == "--apply" and "ferny.worldbuilder" in en, "modlist_swap --enable --apply names every mod, packageIds too")
    ok("bridge up" in text and "remedy" in text, "game-ready says what was deployed, the list and the remedy: %s" % text)
    w = [c for c in ops.calls if c[0] == "wait"][0]
    ok(w[1] == "Bridge token:" and w[2] == 400 - S.LAUNCH_SETTLE_S, "the wait is load_policy's bound: %s" % (w,))


def t_full_and_down():
    ops = FakeOps(up=False)
    v, _ = S.run(dict(PLAN, full=True, remedy_cmds=[]), ops)
    seq = tags(ops)
    ok(v == "ready" and "kill" not in seq and "minimal" not in seq and seq.index("restore") < seq.index("enable"),
       "a final restores FULL.LATEST, then enables on top; a down game is not killed: %s" % seq)


def t_stops():
    ops = FakeOps(plan_out=HAND)
    v, text = S.run(PLAN, ops)
    ok(v == "snag" and "Theirs.xml" in text and "kill" not in tags(ops) and "apply" not in tags(ops),
       "another seat's file stops it before the game is touched or anything written")
    ops = FakeOps(fail={"apply": (1, "NOTHING WAS WRITTEN")})
    v, text = S.run(PLAN, ops)
    ok(v == "snag" and "launch" not in tags(ops), "a failed apply stops it unlaunched: %s" % text[:80])
    ops = FakeOps(fail={"enable": (2, "cannot resolve Foo")})
    v, text = S.run(PLAN, ops)
    ok(v == "snag" and "cannot resolve Foo" in text and "launch" not in tags(ops), "an unresolvable list stops it")
    ops = FakeOps(token="gone")
    v, text = S.run(PLAN, ops)
    ok(v == "snag" and "died during the load" in text and "missing or stale type" in text and "CompFoo" in text,
       "a game that dies loading on a first exception a rule names is a snag naming it, no LLM: %s" % text[:160])
    ops = FakeOps(stubborn=1)
    v, _ = S.run(PLAN, ops)
    ok(v == "ready" and ("kill", True) in ops.calls, "a game that ignores taskkill is forced after the grace")
    ops = FakeOps(token="slow", bound=5000)
    v, text = S.run(PLAN, ops)
    w = [c for c in ops.calls if c[0] == "wait"][0]
    ok(v == "ready" and "STILL LOADING" in text and w[2] < 3600,
       "a load past what the run may spend is handed back still loading, the wait inside stage_max_s: %s" % (w,))
    ops = FakeOps(token="gone")
    ops.running = lambda: False         # Steam cold: no process at all yet
    v, text = S.run(PLAN, ops)
    ok(v == "snag", "no process past the start grace is a snag")
    ops = FakeOps(token="gone")
    real = ops.running
    ops.running = lambda: ops.now() - 1000 > 60 and real()      # not up for the first poll, inside the grace
    c = Cursor(ops)
    ops.cursor = lambda: c
    hit = []
    orig = c.wait
    c.wait = lambda tok, b, abort=None: hit.append(abort()) or orig(tok, b, abort)
    ops.t = 1000.0
    S.run(PLAN, ops)
    ok(hit and hit[0] is None, "a game process not there yet inside the start grace is not 'died'")
    ops = FakeOps()
    slow = ops.sh

    def sh(argv, timeout=480):
        if argv[0] == "bash":
            ops.t += 300
        return slow(argv, timeout)
    ops.sh = sh
    v, text = S.run(dict(PLAN, remedy_cmds=["a", "b", "c"]), ops)
    ok(text.count("NOT RUN") == 1, "the producers share one budget inside stage_idle_s: %s" % text[-160:])
    ops = FakeOps()
    v, _ = S.run(dict(PLAN, riders=["I1"]), ops)
    ok(tags(ops)[0] == "./sync", "riders: the clone is levelled first so their builds are in the tree")


def t_main_run():
    d = tempfile.mkdtemp(prefix="stage_st_")
    try:
        pf = os.path.join(d, "p.stage.json")
        with open(pf, "w") as f:
            json.dump(dict(PLAN, fallback=["claude_bounded.sh", "-p", "STAGING prompt"]), f)
        ops = FakeOps()
        rc = S.main_run(pf, ops, execv=lambda *a: ok(False, "no exec on a handled run"))
        ok(rc == 0 and ops.reports[0][0] == "game-ready", "a staged game reports game-ready")
        ops = FakeOps(plan_out=HAND)
        S.main_run(pf, ops, execv=lambda *a: ok(False, "no exec on a known stop"))
        ok(ops.reports[0][0] == "snag" and ops.reports[0][2] == "game_stage", "a known stop is a game_stage snag, no LLM")
        got = []
        ops = FakeOps(blind=True)

        def execs(f, a):                # execvp never returns
            got.append(a)
            raise SystemExit(0)
        try:
            S.main_run(pf, ops, execv=execs)
        except SystemExit:
            pass
        ok(got and got[0][-1].endswith("STAGING prompt") and "unhandled exception" in got[0][-1] and not ops.reports,
           "an unhandled exception (a blind tasklist) execs the LLM stager, and reports nothing itself")
        ops = FakeOps(blind=True)

        def broken(f, a):
            raise OSError("EACCES")
        rc = S.main_run(pf, ops, execv=broken)
        ok(rc == 1 and ops.reports and ops.reports[0][0] == "snag" and "EACCES" in ops.reports[0][1],
           "a fallback that will not start is told as a snag, never a silent exit: %s" % ops.reports)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_stage_plan():
    st = {"item": "I0", "gen": 3, "game": {"full": None}}
    p = G.stage_plan(st, {"stage_max_s": 3600}, "abc", [{"item": "I1"}], ["Armoury", "ferny.worldbuilder"], ["FlowWorks"],
                     (["Graffiti"], "--mod Graffiti"), {"mods": ["Cuisine"], "cmds": ["x"]})
    ok(p["deploy"] == ["--mod Armoury --mod Cuisine --mod FlowWorks", "--mod Graffiti"],
       "deploy: the build's folders, stale-DLL and lane-fix mods, then the live-deploy trees; never a packageId: %s"
       % p["deploy"])
    ok(p["riders"] == ["I1"] and p["remedy_cmds"] == ["x"] and p["full"] is False and p["gen"] == 3, "and the rest")
    ok(G.cfg({"game": {}})["stage_python"] is True, "the python stager is the default")


def t_effects_launch():
    rl = types.SimpleNamespace(launch_argv=lambda *a: ["systemd-run", "--setenv", "A=1", "--", "claude_bounded.sh", "-p",
                                                       "PROMPT", "--output-format", "json"])
    d = tempfile.mkdtemp(prefix="stage_fx_")
    done = types.SimpleNamespace(returncode=0, stdout="", stderr="")
    try:
        fx = types.SimpleNamespace(RL=rl, r={"seat": "BENCH", "model": "opus", "pilot_agent": "rm-testpilot"})
        run_ = {"unit": "u", "out": os.path.join(d, "o.json"), "err": os.path.join(d, "o.err")}
        with mock.patch.object(subprocess, "run", return_value=done) as run, \
                mock.patch.object(relentless.run_tmp, "prepare", return_value=d), \
                mock.patch.object(relentless.run_tmp, "env", return_value={"TMPDIR": d}), \
                mock.patch.object(relentless.relentless_usage, "note_clone"):
            why = relentless.Effects.launch(fx, {"item": "I0", "_stage_plan": dict(PLAN)}, run_, "PROMPT", G.STAGE_AGENT,
                                            "/clone", 3600, {"RELENTLESS_ROOT": "/r"})
        argv = run.call_args.args[0]
        tail = argv[argv.index("--") + 1:]
        ok(why is None and tail[1:] == ["/clone/src/RimMandrake/rimflow/relentless_stage.py", "run", "--plan",
                                        os.path.join(d, "o.stage.json")], "the unit's body is the python stager: %s" % tail)
        ok("RELENTLESS_ROOT=/r" in argv[:argv.index("--")] and "RIMFLOW_BRIDGE_SEAT=RELENTLESS" in argv,
           "with the store root and the RELENTLESS bridge name")
        plan = json.load(open(os.path.join(d, "o.stage.json")))
        ok(plan["clone"] == "/clone" and plan["fallback"] == ["claude_bounded.sh", "-p", "PROMPT", "--agent",
                                                              "rm-testpilot", "--output-format", "json"],
           "the plan carries the LLM fallback: the stage prompt for the pilot agent: %s" % plan.get("fallback"))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_holds():
    lines = [json.dumps({"do": "tick", "at": "2026-11-06T00:00:00Z", "acts": [{"do": "game_stage", "item": "A"}]}),
             json.dumps({"do": "tick", "at": "2026-11-06T00:01:00Z", "acts": [{"do": "game_stage", "item": "B"}]}),
             "torn{",
             json.dumps({"do": "tick", "at": "2026-11-06T00:02:00Z", "acts": [{"do": "game_staged", "item": "A"}]}),
             json.dumps({"do": "tick", "at": "2026-11-06T00:11:00Z", "acts": [{"do": "game_staged", "item": "B"}]}),
             json.dumps({"do": "tick", "at": "2026-11-06T00:12:00Z", "acts": [{"do": "game_stage", "item": "C"}]})]
    rows = S.holds(lines)
    ok([(r["item"], r["s"]) for r in rows] == [("A", 120), ("B", 600)], "holds pair each stage with its end: %s" % rows)
    ok("median=360s" in S.holds_report(rows), "the median of the window: %s" % S.holds_report(rows))
    ok("UNMEASURED" in S.holds_report([]), "an empty window is UNMEASURED, never a zero hold")
    ok(S.holds(lines, since=S._epoch("2026-11-06T00:01:30Z")) == [], "--since drops stagings begun before it")


if __name__ == "__main__":
    for t in (t_hazards, t_order, t_full_and_down, t_stops, t_main_run, t_stage_plan, t_effects_launch, t_holds):
        print("-- " + t.__name__)
        t()
    print("selftest_relentless_stage: %s" % ("FAIL (%d)" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
