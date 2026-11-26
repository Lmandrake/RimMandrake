#!/usr/bin/env python3
"""selftest_game_deploy_unit.py -- the promises of design/specs/2026-11-24-game-deploy-own-unit/boundary.md, by name.

Item RIMMANDRAKE_RUN_VISIT_DEPLOY_OUTSIDE_TICK_HELD_IT_FOURTEEN_MIN. On 2026-11-24, 7:25 to 7:39 AM PST, the Dispatch
tick ran a visit's deploy (a plan, an --apply, a plan) inside itself: 998 s in which no other mod could start.
Fixtures only: a fake deploy plan, a fake detached_helper, stand-in units; no real unit, game, lock or state.json.

    python3 src/RimMandrake/rimflow/selftest_game_deploy_unit.py      exit 0: every check passes
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import selftest_launch_wait_and_deploy as LW    # noqa: E402  the fake game, plan text and stale-walk tick
import selftest_maturation as SM                # noqa: E402
import selftest_maturation_dispatch as SD       # noqa: E402
import maturation as M                          # noqa: E402
import maturation_autonomy as AUT               # noqa: E402
import maturation_dispatch as MD                # noqa: E402

FAILS, P, F = [], "Pyrelands", "FlowWorks"
SLOW = 60       # the stand-in deploy's seconds (the item's acceptance test)
FAST = 10       # the tick must return under this
PLAN = r'''import os, sys, time
time.sleep(float(os.environ.get("FAKE_PLAN_SLEEP", "0")))
print("RimMandrake.Pyrelands mandrake.rm.pyrelands\n    in sync (12 files)\n\nEverything in sync.")
'''


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def need(name):
    if not hasattr(MD, name):
        raise AssertionError("maturation_dispatch has no %s: the deploy runs inside the tick" % name)
    return getattr(MD, name)


class World:
    """Two mods: Pyrelands owes an in-game visit, FlowWorks an offline build."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="game_deploy_unit_")
        keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
                "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL", "MATURATION_DEPLOY_PLAN", "FAKE_PLAN_SLEEP", M.COMPANION_ENV)
        self.was = {k: os.environ.get(k) for k in keys}
        self.was.update(SM.isolate(self.root))
        SM.copy_ingame(self.root)
        for rel in SD.COPY:
            data = SD.fixture(F, rel)
            if data is not None:
                dst = os.path.join(self.root, "design", "concepts", F, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(data)
        SM.certify_fixture(self.root, [F])
        dh, self.log = os.path.join(self.root, "fake_dh.py"), os.path.join(self.root, "fake_dh.log")
        plan = os.path.join(self.root, "fake_plan.py")
        for path, text in ((dh, SD.FAKE_DH), (plan, PLAN), (self.log, "")):
            with open(path, "w") as f:
                f.write(text)
        self.sd = os.path.join(self.root, "state")
        os.environ.update(MATURATION_DETACHED_HELPER=dh, FAKE_DH_LOG=self.log, MATURATION_CLOCK=str(SM.INGAME_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(self.root, "briefs"), RM_MATURATION_DISPATCH_DIR=self.sd,
                          MATURATION_DEPLOY_PLAN="%s %s" % (sys.executable, plan), FAKE_PLAN_SLEEP="0")
        os.environ.pop("FAKE_DH_FAIL", None)
        self.cfg = dict(SD.load_cfg(), advancing=[P, F], ingame_enabled=True, max_live=5, game_instances=["a", "b"])
        self.started, self.active, self.stale, self.held = [], {}, None, {}
        self.rec, MD.DH.read_record = MD.DH.read_record, lambda unit, root=None: None
        self.procs, self.live = [], {}

    def close(self):
        MD.DH.read_record = self.rec
        for p in self.procs:
            p.kill()
            p.wait()
        SM.restore(self.was)
        shutil.rmtree(self.root, ignore_errors=True)

    def starter(self, mod, game, kind, purpose, seat="BENCH"):
        """The stand-in unit: a real process that runs the slow deploy plan."""
        unit = "rm-game-deploy-fake-%d" % (len(self.started) + 1)
        self.procs.append(subprocess.Popen([sys.executable, os.path.join(self.root, "fake_plan.py")],
                                           stdout=subprocess.DEVNULL))
        self.started.append({"mod": mod, "game": game, "kind": kind, "unit": unit})
        self.active[unit] = True
        return 0, "STARTED %s" % unit, unit

    def finish(self, state="ok", text="deployed", **kw):
        """The unit's end: its result file, as game_deploy_worker writes it."""
        x = self.started[-1]
        self.active[x["unit"]] = False
        res = dict({"mod": x["mod"], "unit": x["unit"], "game": x["game"], "kind": x["kind"], "state": state,
                    "text": text, "sha": "abc1234", "generation": 7, "paths": []}, **kw)
        MD._write(os.path.join(MD.game_deploy_dir(), "%s.json" % x["mod"]), res)

    def facts(self, c):
        out = {}
        for mod in c["advancing"]:
            f = M.build_facts(self.root, mod)
            f.update(live_units=list(self.live.get(mod, [])), last_end=None, stage_runs={}, run_tokens={})
            out[mod] = MD.add_ingame(self.root, mod, MD.add_blind(self.root, mod, f, []), [])
        return out

    def bridge(self, p, game="a"):
        why = self.held.get(game)
        return (False, "NOT TAKEABLE %s" % why) if why else (True, "TAKEABLE")

    def tick(self, at, **cfg):
        c = dict(self.cfg, **cfg)
        fx = {"autonomy": False, "convergence": SD.no_convergence, "account": lambda: (True, "KEEP"), "known": lambda: set(),
              "bridge": self.bridge, "repair_launch": SD.REPAIRED_IN_PLACE, "facts": lambda: self.facts(c),
              "file": lambda item, title, why, **kw: (True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(
                  self.root, mod, cap, item, model="opus", seat="BENCH",
                  bridge=lambda p, s, game="a": self.bridge(p, game=game), companion=lambda game="a": (True, "fresh"), **kw),
              "game_deploy": self.starter, "unit_active": lambda u: self.active.get(u),
              "deploy_stale": lambda root, res: self.stale}
        t0 = time.time()
        rd = MD.tick(self.root, c, True, fx=fx, now=SM.INGAME_CLOCK + at, page=False)
        return rd, time.time() - t0

    def launches(self, mod=P):
        with open(self.log) as f:
            rows = [json.loads(x) for x in f if x.strip()]
        return [r for r in rows if "RM_CONTROL_MOD=%s" % mod in r]


def dec(rd, mod=P):
    return rd["mods"][mod]["decision"]


def t_the_tick_never_waits_on_a_deploy(w):
    os.environ["FAKE_PLAN_SLEEP"] = str(SLOW)
    rd, took = w.tick(0)
    check(took < FAST and len(w.started) == 1 and not w.launches() and len(w.launches(F)) == 1 and dec(rd) == "live"
          and dec(rd, F) == "launched",
          "the-tick-never-waits-on-a-deploy: a %d s deploy, the tick back in %.1f s, the second mod launched in it "
          "(%s, %s; units %s)" % (SLOW, took, dec(rd), dec(rd, F), w.started))


def t_the_mod_reads_live_until_the_deploy_ends(w):
    os.environ["FAKE_PLAN_SLEEP"] = str(SLOW)
    w.tick(0)
    rd, took = w.tick(60)
    check(took < FAST and dec(rd) == "live" and len(w.started) == 1 and not w.launches()
          and "rm-game-deploy-fake-1" in str(rd["mods"][P].get("status")),
          "the-mod-reads-live-until-the-deploy-ends: %s" % rd["mods"][P].get("status"))


def t_the_visit_launches_on_the_tick_after(w):
    os.environ["FAKE_PLAN_SLEEP"] = str(SLOW)      # a tick that reads the plan itself is late
    w.tick(0)
    w.finish()
    rd, took = w.tick(120)
    L = w.launches()
    check(took < FAST and dec(rd) == "launched" and len(L) == 1 and len(w.started) == 1
          and "RM_GAME_INSTANCE=%s" % w.started[0]["game"] in L[0],
          "the-visit-launches-on-the-tick-after: %s in %.1f s on game %s" % (dec(rd), took, w.started[0]["game"]))


def t_a_deploy_takes_no_run_slot(w):
    rd, _ = w.tick(0, max_live=1)
    check(dec(rd) == "live" and dec(rd, F) == "launched",
          "a-deploy-takes-no-run-slot: one slot, the second mod still launched (%s, %s)" % (dec(rd), dec(rd, F)))


def t_the_deploying_game_is_driven(w):
    w.tick(0)
    st = MD.read_state(os.path.join(w.sd, "state.json"))
    rows = MD.game_deploy_drivers(st)
    u = w.started[0]["unit"]
    check(rows == {u: w.started[0]["game"]}, "the-deploying-game-is-driven: another mod's pick skips it (%s)" % rows)
    w.finish()
    st2 = MD.read_state(os.path.join(w.sd, "state.json"))
    MD.game_deploy_sync(w.root, st2, 1.0, {"unit_active": lambda x: False, "deploy_stale": lambda r, x: None})
    check(MD.game_deploy_drivers(st2) == {}, "...and is free once the deploy ended")


def t_the_visit_goes_to_the_deployed_game(w):
    w.held["a"] = "held by another run"
    w.tick(0)
    w.held.clear()
    w.finish()
    rd, _ = w.tick(60)
    L = w.launches()
    check(w.started[0]["game"] == "b" and len(w.started) == 1 and len(L) == 1 and "RM_GAME_INSTANCE=b" in L[0],
          "the-visit-goes-to-the-deployed-game: deployed to b, a free again, launched on b (%s)" % dec(rd))


def t_a_failed_deploy_is_the_launch_refusal(w):
    w.tick(0)
    w.finish("fail", "the deploy failed (exit 1: ! FAILED to write Assemblies/X.dll)")
    rd, _ = w.tick(60)
    st = MD.read_state(os.path.join(w.sd, "state.json"))["mods"][P]
    book = st.get("ingame_auto") or []
    check(not w.launches() and len(book) == 1 and "FAILED to write" in str(book[0].get("failed")) and not st.get("game_deploy"),
          "a-failed-deploy-is-the-launch-refusal: booked with its cause, the result used once (%s / %s)" % (
              dec(rd), book[:1]))


def t_a_waiting_or_killed_deploy_starts_again(w):
    w.tick(0)
    w.finish("wait", M.WAIT_MARK + " ArchBig is held by another run")
    w.tick(60)
    st = MD.read_state(os.path.join(w.sd, "state.json"))["mods"][P]
    check(len(w.started) == 2 and not w.launches() and not st.get("ingame_auto") and st["game_deploy"]["tries"] == 1,
          "a-waiting-or-killed-deploy-starts-again: a wait spends no try (%d units)" % len(w.started))
    w.active[w.started[-1]["unit"]] = None
    rd, _ = w.tick(120)
    check(len(w.started) == 2 and dec(rd) == "live", "...a unit that could not be looked at is still running (%s)" % dec(rd))
    w.active[w.started[-1]["unit"]] = False         # gone, no result of its own
    w.tick(180)
    st = MD.read_state(os.path.join(w.sd, "state.json"))["mods"][P]
    check(len(w.started) == 3 and not w.launches() and st["game_deploy"]["tries"] == 2 and not st.get("ingame_auto"),
          "...a unit gone with no result starts again and spends a try (%d units)" % len(w.started))
    for at in range(240, 900, 60):
        w.active[w.started[-1]["unit"]] = False
        w.tick(at)
        st = MD.read_state(os.path.join(w.sd, "state.json"))["mods"][P]
        if st.get("ingame_auto"):
            break
    n = len(w.started)      # the waiting unit, then one per try
    check(n == AUT.tries_most(w.cfg, P) + 1 and "left no result" in str((st.get("ingame_auto") or [{}])[0].get("failed")),
          "...and past launch_tries it is the launch's refusal, never a loop (%d units)" % n)


def t_a_stale_result_deploys_again(w):
    w.tick(0)
    w.finish()
    w.stale = "src/RimMandrake/Pyrelands changed since abc1234"
    rd, _ = w.tick(60)
    check(len(w.started) == 2 and not w.launches() and dec(rd) == "live",
          "a-stale-result-deploys-again: never a visit on a copy older than the source (%s)" % dec(rd))


def t_the_stale_reading(w):
    """deploy_stale on a real small git tree: changed source, another hold of the game, a tree behind the deploy."""
    d = os.path.join(w.root, "g")
    git = lambda *a: subprocess.run(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),  # noqa: E731
                                    capture_output=True, text=True, check=True).stdout.strip()
    os.makedirs(os.path.join(d, "src", "M"))
    subprocess.run(["git", "init", "-q", d], check=True)

    def commit(path, text):
        with open(os.path.join(d, path), "w") as f:
            f.write(text)
        git("add", "-A")
        git("commit", "-q", "-m", path)
        return git("rev-parse", "HEAD")
    sha = commit("src/M/a.xml", "1")
    res = {"sha": sha, "paths": ["src/M"], "game": "a", "generation": 7}
    commit("other.txt", "x")
    gen = lambda g: 7       # noqa: E731
    same = MD.deploy_stale(d, res, generation=gen)
    other = MD.deploy_stale(d, res, generation=lambda g: 8)
    new = commit("src/M/a.xml", "2")
    changed = MD.deploy_stale(d, res, generation=gen)
    git("reset", "-q", "--hard", sha)
    behind = MD.deploy_stale(d, dict(res, sha=new), generation=gen)
    absent = MD.deploy_stale(d, dict(res, sha="f" * 40), generation=gen)
    blind = MD.deploy_stale(os.path.join(w.root, "no_such_tree"), res, generation=gen)
    check(same is None and "hold" in str(other) and "src/M" in str(changed) and behind is None and absent is None and blind,
          "the-stale-reading: an unrelated commit is fresh, a source change and another hold of the game are stale, a tree "
          "behind the deploy is fresh, a tree git cannot read is stale (%s)" % [same, other, changed, behind, absent, blind])


def t_a_stale_walk_build_deploys_in_the_unit(w):
    need("game_deploy_launch")
    cfg, st, units, active = {"seat": "BENCH"}, {"mods": {}}, [], {}

    def start(mod, game, kind, purpose, seat="BENCH"):
        units.append((mod, kind))
        return 0, "STARTED", "rm-game-deploy-w%d" % len(units)
    fx = {"known": lambda: set(), "file": lambda *a, **k: (False, "no filing in a test"), "game_deploy": start,
          "unit_active": lambda u: active.get(u, True), "deploy_stale": lambda r, x: None, "walk_letter": lambda r, m: "a"}
    r, la = LW.stale_tick(st, [LW.STALE])
    AUT.execute(w.root, cfg, st, [r], la, 1000.0, fx)
    check(units == [(P, "walk")] and r["decision"] == "live" and not (st["mods"][P].get("steward") or {}),
          "a-stale-walk-build-deploys-in-the-unit: started, the mod live, no try spent (%s)" % r["decision"])
    unit = st["mods"][P]["game_deploy"]["unit"]
    puts = []
    f = {"mod": P, "version": "0.1.0", "visit": 6, "live_units": [], "owed": "exit not met",
         "exit": {"state": "not_met", "why": ["half-written copy"]}}
    MD.decide_ingame(cfg, st["mods"][P], f, {"mod": P}, lambda d, *a, **k: puts.append(d), 1060.0, (True, ""), 0, [], None)
    check(puts == ["live"], "...while it runs no half-written copy is read as an exit (%s)" % puts)
    active[unit] = False
    MD._write(os.path.join(MD.game_deploy_dir(), P + ".json"), {"unit": unit, "state": "fail", "text": "the deploy exited 1",
                                                                "game": "a", "kind": "walk"})
    MD.game_deploy_sync(w.root, st, 1100.0, fx)
    r, la = LW.stale_tick(st, [LW.STALE])
    AUT.execute(w.root, cfg, st, [r], la, 1100.0, fx)
    check(r["decision"] == "launch_failed" and "exited 1" in r["why"] and len(units) == 1,
          "...a failed one names its cause and pauses the mod (%s)" % r["why"])


def t_the_unit_is_its_own(w):
    seen = []

    class R:
        returncode, stdout, stderr = 0, "", ""

        def __init__(self, argv, **k):
            seen.append(argv)
    import control as C
    was = C.launch_unit
    C.launch_unit = lambda argv, spec, runner=None, **k: (seen.append((list(argv), spec)), R([]))[1]
    try:
        rc, text, unit = need("game_deploy_unit")(P, "b", "visit", "deploy Pyrelands", now=5)
    finally:
        C.launch_unit = was
    argv, spec = seen[0]
    tail = argv[argv.index("--") + 1:]
    check(rc == 0 and spec["family"] == "game_deploy" and "game_deploy" in C.FAMILIES and spec["unit"] == unit
          and re.match(r"rm-game-deploy-pyrelands-5$", unit) and tail[2] == "game-deploy"
          and "RM_MATURATION_DISPATCH_DIR=" + w.sd in argv and any("RuntimeMaxSec=%d" % MD.DEPLOY_MAX_S in x for x in argv),
          "the-unit-is-its-own: control admits it under its own family, with its hang guard (%s %s)" % (unit, tail[2:5]))


def t_the_worker_writes_the_result(w):
    worker = need("game_deploy_worker")
    calls = []

    class R:
        def __init__(self, rc, out, err=""):
            self.returncode, self.stdout, self.stderr = rc, out, err
    out = [R(0, "noise\n" + json.dumps({"state": "ok", "text": "deployed", "game": "b", "generation": 9, "sha": "abc", "paths": ["p"]}))]

    def runner(argv, **k):
        calls.append((argv, k.get("cwd")))
        return out[0]
    d = os.path.join(w.root, "clone")
    res = worker(P, "b", "visit", "deploy", "rm-u", runner=runner, take=lambda item: (d, "made"))
    disk = MD.game_deploy_result(P)
    check(res["state"] == "ok" and disk["unit"] == "rm-u" and disk["generation"] == 9 and calls[0][1] == d
          and "game-repair" in calls[0][0] and "--kind" in calls[0][0],
          "the-worker-writes-the-result: game-repair ran in its own pool clone (%s)" % calls[0][0][1:4])
    out[0] = R(1, "Traceback: boom")
    res = worker(P, "b", "visit", "deploy", "rm-u2", runner=runner, take=lambda item: (d, "made"))
    check(res["state"] == "fail" and "boom" in res["text"], "...a repair that printed no verdict is a fault named (%s)" % res["text"])

    def full(item):
        raise RuntimeError("POOL REFUSED: pool full (16 of 16 clones)")
    res = worker(P, "b", "visit", "deploy", "rm-u3", runner=runner, take=full)
    check(res["state"] == "wait", "...a full pool is a wait (%s)" % res["state"])


def t_the_lock_covers_the_plan_too(w):
    """game_repair: the game's driver lock is held from before the first plan until the game is up again."""
    if not hasattr(M, "game_repair"):
        raise AssertionError("maturation has no game_repair")
    log, g = [], LW.FakeGame(up=True)
    real = (M.deploy_state, M._deploy_repair_held)
    reads = [{"state": "drift", "why": "w", "args": [], "fix": "x"}]
    g.log = log

    class Lock(LW.Lock):
        pass
    try:
        M.deploy_state = lambda root, mod, game="a", **k: (log.append("plan") or reads[0])
        M._deploy_repair_held = lambda *a, **k: (log.append("repair") or ("ok", "done"))
        comp = lambda game="a": (True, "fresh")     # noqa: E731
        r = M.game_repair(w.root, P, "a", "visit", "p", game_ops=g, companion=comp, lock=Lock(g))
        order = [x[0] if isinstance(x, tuple) else x for x in log]
        check(r["state"] == "ok" and order == ["claim", "plan", "repair", "release"] and r["generation"] == 7 and r["sha"]
              and any("Pyrelands" in x or "Biomes" in x for x in r["paths"]),
              "the-lock-covers-the-plan-too: claim, plan, repair, release (%s, generation %s)" % (order, r["generation"]))
        del log[:]
        reads[0] = {"state": "current", "why": "matches"}
        r = M.game_repair(w.root, P, "a", "visit", "p", game_ops=g, companion=comp, lock=Lock(g))
        check(r["state"] == "ok" and "repair" not in log, "...a copy already current needs no repair (%s)" % r["state"])
        reads[0] = {"state": "stuck", "why": "game-only def X"}
        r = M.game_repair(w.root, P, "a", "visit", "p", game_ops=g, companion=comp, lock=Lock(g))
        check(r["state"] == "fail" and "game-only def X" in r["text"], "...a stuck copy is a fault named (%s)" % r["text"])
        del log[:]
        r = M.game_repair(w.root, P, "a", "visit", "p", game_ops=g, companion=comp, lock=Lock(g, state="held"))
        check(r["state"] == "wait" and r["text"].startswith(M.WAIT_MARK) and "plan" not in log,
              "...a game another run holds is a wait, nothing read (%s)" % r["text"])
        reads[0] = {"state": "current", "why": "matches"}
        r = M.game_repair(w.root, P, "a", "walk", "p", game_ops=g, lock=Lock(g))
        check(r["state"] == "fail" and "matches" in r["text"], "...a walk deploy with no drift to cure is a fault named (%s)" % r["text"])
    finally:
        M.deploy_state, M._deploy_repair_held = real


def main():
    for t in (t_the_tick_never_waits_on_a_deploy, t_the_mod_reads_live_until_the_deploy_ends,
              t_the_visit_launches_on_the_tick_after, t_a_deploy_takes_no_run_slot, t_the_deploying_game_is_driven,
              t_the_visit_goes_to_the_deployed_game, t_a_failed_deploy_is_the_launch_refusal,
              t_a_waiting_or_killed_deploy_starts_again, t_a_stale_result_deploys_again, t_the_stale_reading,
              t_a_stale_walk_build_deploys_in_the_unit, t_the_unit_is_its_own, t_the_worker_writes_the_result,
              t_the_lock_covers_the_plan_too):
        if FAILS and t is not t_the_tick_never_waits_on_a_deploy and not hasattr(MD, "game_deploy_unit"):
            break       # the base: the deploy is inside the tick, nothing below exists
        w = World()
        try:
            t(w)
        except Exception as e:  # noqa: BLE001
            check(False, "%s (raised %s: %s)" % (t.__name__[2:], type(e).__name__, str(e)[:200]))
        finally:
            w.close()
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
