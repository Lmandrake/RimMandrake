#!/usr/bin/env python3
"""LIVE_STAGING_BUILD_STAGEHAND_WITHOUT_TOKENS: the python stager (relentless_stage.py) driven end to end with fake
effects, its verdict fed to the real supervisor (relentless_game.step) on a fake world.

  happy path: deploy -> down -> apply -> list -> load -> game-ready, no LLM, every step's seconds recorded;
  deploy failure: a game_stage snag before the game is touched, no LLM, restaged with no worker;
  load timeout: handed back STILL LOADING (the supervisor waits the load out), recorded as not loaded;
  an unknown state (a load death whose first exception no rule names, or none) execs the LLM, briefed with the state
  and the Player.log tail, the stage prompt's guards still in it; a death a rule names is a snag, no LLM;
  the bridge is released on every one of those paths; the OWNER hold refuses the staging (no take, no launch);
  `round` (live proof A1) reads 0 only for an LLM-free loaded staging whose hold the journal measured.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                      # noqa: E402
import relentless_game as G                 # noqa: E402
import relentless_stage as S                # noqa: E402
import selftest_relentless_game as SG       # noqa: E402
import selftest_relentless_stage as SS      # noqa: E402

FAILS = SG.FAILS
ok = SG.ok

PLAN = dict(SS.PLAN, remedy_cmds=[], fallback=["claude_bounded.sh", "-p", "STAGING prompt: never a flyer's flight",
                                               "--agent", "rm-testpilot"])


def staging(x):
    """A rig whose item I0 is in the staging phase, its bridge taken and its stager unit launched."""
    SG.to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging" and x.w.events.count("take") == 1 and x.w.launches[-1][3] == G.STAGE_AGENT,
       "staging: the bridge taken once, the python stager launched")
    return st


def wired(x, st, **kw):
    """FakeOps whose report is the real relentless.py verb on the rig's store (game-ready / snag)."""
    ops = SS.FakeOps(**kw)

    def report(verb, text, klass=None):
        ops.reports.append((verb, text, klass))
        if verb == "game-ready":
            G.ready(x.s, "I0", st["gen"], text)
        else:
            R.snag(x.s, "I0", st["gen"], klass or "game_stage", text, x.r)
        return 0, "reported"
    ops.report = report
    return ops


def run_stager(x, st, plan=PLAN, execv=None, **kw):
    d = tempfile.mkdtemp(prefix="stage_machine_")
    try:
        pf = os.path.join(d, "p.stage.json")
        with open(pf, "w") as f:
            json.dump(plan, f)
        ops = wired(x, st, **kw)
        execs = []

        def ex(f, a):
            execs.append(a)
            raise SystemExit(0)         # execvp never returns: the unit is the LLM from here
        rc = None
        try:
            rc = S.main_run(pf, ops, execv=execv or ex)
        except SystemExit:
            pass
        return ops, execs, rc
    finally:
        shutil.rmtree(d, ignore_errors=True)


def end_unit(x, st):
    """The staging unit exits; the supervisor settles it (two ticks: stop, then release)."""
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()


def t_happy_path():
    x = SG.rig(1)
    st = staging(x)
    ops, execs, rc = run_stager(x, st)
    rec = ops.records[-1] if ops.records else {}
    ok(rc == 0 and not execs and ops.reports[0][0] == "game-ready", "happy path: game-ready, no LLM: %s" % ops.reports)
    ok(rec.get("verdict") == "ready" and rec.get("llm") is None and rec.get("loaded") is True,
       "one timings line: ready, LLM-free, loaded: %s" % rec)
    order = rec.get("order") or []
    ok(order[:5] == ["deploy_plan", "game_down", "deploy_apply", "modlist", "load"],
       "each step timed in the machine's order (deploy -> down -> apply -> list -> load): %s" % order)
    ok(sum(rec["stages"].values()) == rec["total_s"] and rec["stages"]["load"] >= S.LAUNCH_SETTLE_S,
       "the steps' seconds add up to the staging's total: %s" % rec)
    ok(ops.reports[0][1].startswith("stages(s): deploy_plan="), "game-ready leads with the timings (the note keeps 600)")
    ok(x.st("I0")["game"].get("ready"), "the supervisor has the stager's game-ready")
    x.w.running = True              # the stager brought the game up
    end_unit(x, st)
    ok("release" in x.w.events and x.st("I0")["game"]["phase"] in ("prove", "proving"),
       "happy path: the bridge released, then the blind round: %s %s" % (x.w.events, x.st("I0")["game"]["phase"]))
    x.done()


def t_deploy_failure():
    x = SG.rig(1)
    st = staging(x)
    ops, execs, rc = run_stager(x, st, fail={"plan": (2, "Traceback: deploy_custom_mods crashed\n")})
    ok(not execs and ops.reports and ops.reports[0][0] == "snag" and ops.reports[0][2] == "game_stage",
       "a deploy failure is a game_stage snag, no LLM: %s" % ops.reports)
    ok("launch" not in SS.tags(ops) and "kill" not in SS.tags(ops), "the game is never touched after a failed plan")
    ok(ops.records and ops.records[-1]["verdict"] == "snag" and ops.records[-1]["llm"] is None, "recorded as a snag")
    end_unit(x, st)
    st2 = x.st("I0")
    ok("release" in x.w.events and st2["game"]["phase"] == "stage" and st2["game"]["retry_at"] and not st2.get("last_fail"),
       "deploy failure: the bridge released, restaged, no worker (the routing itself: selftest_relentless_stage_reroute)")
    x.done()


def t_load_timeout():
    x = SG.rig(1)
    st = staging(x)
    ops, execs, rc = run_stager(x, st, token="slow", bound=5000)
    rec = ops.records[-1]
    ok(not execs and ops.reports[0][0] == "game-ready" and "STILL LOADING" in ops.reports[0][1],
       "a load past the run's bound is handed back still loading, no LLM")
    ok(rec["verdict"] == "ready" and rec["loaded"] is False, "and recorded as not loaded: %s" % rec)
    end_unit(x, st)
    ok("release" in x.w.events, "load timeout: the bridge released")
    x.done()


UNKNOWN_LOG = "Loading game\nInitializing\nException in OnGUI: InvalidOperationException: a modal that will not close\n"


def t_unknown_state_goes_to_the_llm():
    x = SG.rig(1)
    st = staging(x)
    ops, execs, rc = run_stager(x, st, token="gone", log=UNKNOWN_LOG)
    ok(execs and not ops.reports, "a load death whose first exception no rule names execs the LLM stager: %s %s"
       % (execs, ops.reports))
    p = execs[0][execs[0].index("-p") + 1] if execs else ""
    ok("game died loading" in p and "InvalidOperationException" in p and "Player.log tail" in p,
       "briefed with the state and the log tail: %s" % p[:200])
    ok(p.endswith("STAGING prompt: never a flyer's flight") and execs[0][-2:] == ["--agent", "rm-testpilot"],
       "the stage prompt (its guards) still follows, the agent unchanged")
    ok(ops.records and ops.records[-1]["llm"] == "game died loading", "the LLM launch is recorded: %s" % ops.records)
    end_unit(x, st)        # the LLM ends without a game-ready: the supervisor still releases
    ok("release" in x.w.events, "unknown state: the bridge released however the LLM ended")
    x.done()
    x = SG.rig(1)
    st = staging(x)
    ops, execs, _ = run_stager(x, st, token="gone", log="")
    ok(execs and "first Player.log exception none" in execs[0][2], "a death with no exception at all is no rule's either")
    x.done()
    x = SG.rig(1)
    st = staging(x)
    ops, execs, _ = run_stager(x, st, token="gone")       # SS.DIED: Could not find type named ...
    ok(not execs and ops.reports[0][0] == "snag" and "missing or stale type" in ops.reports[0][1],
       "a death a rule names is a snag naming the first exception, no tokens")
    x.done()


def t_owner_hold_refuses():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.w.idle = "NOT TAKEABLE  OWNER holds it"
    x.w.take_why = "NOT TAKEABLE  OWNER holds it (his hold, 45 min after his last act)"
    n = len(x.w.launches)
    x.tick()
    x.tick()
    ok(len(x.w.launches) == n and x.st("I0")["game"]["phase"] != "staging",
       "the OWNER hold: no staging is launched: phase %s" % x.st("I0")["game"]["phase"])
    x.done()


def t_round_reads_the_record():
    rec = {"at": "2026-11-06T20:00:00Z", "item": "I0", "verdict": "ready", "llm": None, "loaded": True,
           "stages": {"deploy_plan": 3, "load": 25}, "order": ["deploy_plan", "load"], "total_s": 28}
    t = S._epoch("2026-11-06T20:00:00Z")
    pair = [{"item": "I0", "start": t - 40, "end": t + 30, "s": 70}]
    code, line = S.round_verdict(rec, pair)
    ok(code == 0 and "bridge hold 70s" in line, "round: an LLM-free loaded staging with its hold measured is 0: %s" % line)
    ok(S.round_verdict(dict(rec, llm="game died loading"), pair)[0] == 1, "round: an LLM launch is 1")
    ok(S.round_verdict(dict(rec, loaded=False), pair)[0] == 1, "round: still loading is no completed round")
    ok(S.round_verdict(rec, [])[0] == 2 and S.round_verdict(None, pair)[0] == 2, "round: no record or no hold is UNMEASURED")
    lines = [json.dumps(dict(rec, item="I1")), "junk", json.dumps(rec), json.dumps(dict(rec, item="I1", llm="x"))]
    ok(S.last_timing(lines, "I0") == rec, "the item's own latest line")


def main():
    for t in (t_happy_path, t_deploy_failure, t_load_timeout, t_unknown_state_goes_to_the_llm, t_owner_hold_refuses,
              t_round_reads_the_record):
        print("--", t.__name__)
        t()
    print("selftest_relentless_stage_machine: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
