#!/usr/bin/env python3
"""selftest_launch_wait_and_deploy.py -- the promises of
design/specs/2026-11-20-launch-refusal-wait-and-deploy/boundary.md, one check each, by name.

Items RIMMANDRAKE_DEPLOY_BEFORE_GAME_VISIT_PYRELANDS_REFUSED_THRICE and
RIMMANDRAKE_STOP_COUNTING_DRAIN_REFUSALS_AS_SYSTEM_FAULTS. On 2026-11-20 the tick counted three account-drain refusals
(FlowWorks) and three in-game refusals on non-game drift (Pyrelands) as system faults, and the fault loop paused both.
Fixtures only: a fake deploy plan (MATURATION_DEPLOY_PLAN), a fake detached_helper, fake game operations, a temp
dispatch state; the real game, bridge, ledger and state.json are never touched.

    python3 src/RimMandrake/rimflow/selftest_launch_wait_and_deploy.py      exit 0: every check passes
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_maturation as ST    # noqa: E402  the in-game fixture (concept tree, fake detached_helper)
import maturation as M              # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402
import run_void as RV               # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REAL_PLAN = os.path.join(REPO, "design", "specs", "2026-11-20-launch-refusal-wait-and-deploy", "plan_2026-11-20.txt")
FAILS = []
P = "Pyrelands"

FAKE_PLAN = r'''#!/usr/bin/env python3
import os, sys
d = os.environ["FAKE_PLAN_DIR"]
with open(os.path.join(d, "calls.log"), "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\n")
applied = os.path.join(d, "applied")
if "--apply" in sys.argv:
    rc = int(os.environ.get("FAKE_APPLY_RC", "0"))
    if rc:
        print("  ! FAILED to write Assemblies/X.dll: [Errno 13] Permission denied")
        sys.exit(rc)
    open(applied, "w").close()
    print("Deployed 1 file(s). RESTART RIMWORLD")
    sys.exit(0)
name = "after.txt" if os.path.exists(applied) and os.path.exists(os.path.join(d, "after.txt")) else "plan.txt"
p = os.path.join(d, name)
if not os.path.exists(p):
    sys.exit("deploy_custom_mods.py: no such mod in the repo")
text = open(p).read()
print(text)
sys.exit(1 if "Drift found." in text else 0)
'''
SYNC = "RimMandrake.Biomes mandrake.rm.biomes\n    in sync (12 files)\n\nEverything in sync."


def drift(*lines):
    return "RimMandrake.Biomes mandrake.rm.biomes\n%s\n\nDrift found. Re-run with --apply to deploy." % "\n".join(
        "    " + x for x in lines)


KEPT = "   (in game, not in repo; kept — use --prune to delete, or --pull to rescue)"


class FakeGame:
    """game_instance's operations, recorded: running, hold_refusal, stop, pids, launch."""

    def __init__(self, up=False, held=None, stop_rc=0, launch_rc=0):
        self.up, self.held, self.stop_rc, self.launch_rc, self.log = up, held, stop_rc, launch_rc, []

    def running(self, name=None):
        return self.up

    def hold_refusal(self, name, despite=None):
        return self.held

    def pids(self, name=None):
        return [4242] if self.up else []

    def stop(self, pid_=None, force=False, name=None, purpose=None, despite=None):
        self.log.append(("stop", name, force))
        if not self.stop_rc:
            self.up = False
        return self.stop_rc, "taskkill /PID 4242"

    def launch(self, name=None, wait=False, despite=None, **kw):
        self.log.append(("launch", name, wait))
        if not self.launch_rc:
            self.up = True
        return self.launch_rc, "started game %s, pid 4243" % name


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def safe(fn, what):
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001  on the base a missing name is a FAIL, never a crash
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:160])
    check(bool(cond), what)


class Fixture:
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="launch_wait_deploy_")
        self.keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
                     "MATURATION_DEPLOY_PLAN", "FAKE_PLAN_DIR", "FAKE_APPLY_RC", M.COMPANION_ENV)
        self.was = {k: os.environ.get(k) for k in self.keys}
        self.was.update(ST.isolate(self.root))
        ST.copy_ingame(self.root)
        ST.write_ledger(self.root)
        self.dh, self.dhlog = os.path.join(self.root, "fake_dh.py"), os.path.join(self.root, "fake_dh.log")
        with open(self.dh, "w") as f:
            f.write(ST.FAKE_DH)
        self.pd = os.path.join(self.root, "plan")
        os.makedirs(self.pd)
        plan = os.path.join(self.root, "fake_plan.py")
        with open(plan, "w") as f:
            f.write(FAKE_PLAN)
        os.environ.update(MATURATION_DETACHED_HELPER=self.dh, FAKE_DH_LOG=self.dhlog,
                          MATURATION_CLOCK=str(ST.INGAME_CLOCK), MATURATION_BRIEF_DIR=os.path.join(self.root, "briefs"),
                          MATURATION_DEPLOY_PLAN="%s %s" % (sys.executable, plan), FAKE_PLAN_DIR=self.pd)
        os.environ.pop("FAKE_APPLY_RC", None)

    def plan(self, text, after=None, apply_rc=0):
        for n in ("calls.log", "applied", "after.txt", "plan.txt"):
            p = os.path.join(self.pd, n)
            if os.path.exists(p):
                os.remove(p)
        if text is not None:
            with open(os.path.join(self.pd, "plan.txt"), "w") as f:
                f.write(text)
        if after is not None:
            with open(os.path.join(self.pd, "after.txt"), "w") as f:
                f.write(after)
        os.environ["FAKE_APPLY_RC"] = str(apply_rc)
        open(self.dhlog, "w").close()

    def plan_calls(self):
        p = os.path.join(self.pd, "calls.log")
        return [x for x in open(p).read().splitlines()] if os.path.exists(p) else []

    def launched(self):
        return [x for x in open(self.dhlog).read().splitlines() if x.strip()]

    def launch(self, game_ops, bridge=(True, "free"), game="a"):
        return M.launch_mod(self.root, P, 20, ST.ITEM, bridge=lambda p, s, game="a": bridge,
                            companion=lambda game="a": (True, "fresh"), game=game, game_ops=game_ops)

    def close(self):
        ST.restore(self.was)


def t_non_game_drift_launches(fx):
    with open(REAL_PLAN) as f:
        real = f.read()
    fx.plan(real)
    g = FakeGame(up=True)
    r = fx.launch(g)
    check(r[0] == 0 and r[2] and len(fx.launched()) == 1 and g.log == []
          and not any("--apply" in c for c in fx.plan_calls()),
          "non-game-drift-launches: this evening's real plan (a Cauldron .sh, nine game-only textures no repo file "
          "names) launches the visit, no deploy, no restart (rc %s, launched %d, game ops %s, %s)" % (
              r[0], len(fx.launched()), g.log, r[1].splitlines()[0][:160] if r[1] else ""))


def t_loaded_drift_deploys_then_launches(fx):
    fx.plan(drift("~  Biomes/Pyrelands/Defs/ThingDefs/RM_FE_Ash.xml"), after=SYNC)
    g = FakeGame(up=False)
    r = fx.launch(g, game="b")
    calls = fx.plan_calls()
    check(r[0] == 0 and r[2] and len(fx.launched()) == 1 and g.log == []
          and sum("--apply" in c for c in calls) == 1 and all("--instance b" in c for c in calls) and len(calls) == 3,
          "loaded-drift-deploys-then-launches: a ~ on a def with the game down deploys once for the visit's game "
          "(--instance b), reads the plan again, launches (calls %s, game ops %s, rc %s %s)" % (
              calls, g.log, r[0], (r[1] or "")[:200]))


def t_a_dll_deploys_with_the_game_down(fx):
    fx.plan(drift("~  Biomes/Pyrelands/Assemblies/FireEcologyHook.dll"), after=SYNC)
    g = FakeGame(up=True)
    order = []
    stop, launch = g.stop, g.launch

    def stop_(*a, **k):
        order.append("stop:%d" % len(fx.plan_calls()))
        return stop(*a, **k)

    def launch_(*a, **k):
        order.append("up:%d" % len(fx.plan_calls()))
        return launch(*a, **k)
    g.stop, g.launch = stop_, launch_
    r = fx.launch(g)
    calls = fx.plan_calls()
    # stop after the first plan read (1 call), up after the apply (2 calls), then the re-read (3)
    check(r[0] == 0 and r[2] and order == ["stop:1", "up:2"] and len(calls) == 3 and "--apply" in calls[1]
          and g.up, "a-dll-deploys-with-the-game-down: the game is stopped before the deploy and started after it, "
          "then re-read, then launched (order %s, calls %s, rc %s %s)" % (order, calls, r[0], (r[1] or "")[:200]))


def t_a_failed_deploy_is_a_fault(fx):
    fx.plan(drift("~  Biomes/Pyrelands/Defs/ThingDefs/RM_FE_Ash.xml"), after=SYNC, apply_rc=1)
    r = fx.launch(FakeGame(up=False))
    check(r[0] == 2 and not r[2] and "deploy" in r[1] and "Permission denied" in r[1]
          and not r[1].startswith(M.WAIT_MARK) and not AUT.wait_refusal(r[1]) and not fx.launched(),
          "a-failed-deploy-is-a-fault: the deploy exits 1: REFUSED, naming the deploy failure, not a wait (%s)" %
          (r[1] or "")[:220])


def t_a_blind_plan_is_could_not_look(fx):
    fx.plan(None)
    r = fx.launch(FakeGame(up=True))
    calls = fx.plan_calls()
    check(r[0] == 2 and "could not" in r[1] and not fx.launched() and not any("--apply" in c for c in calls),
          "a-blind-plan-is-could-not-look: a plan that cannot run refuses as could-not-look, no deploy (%s)" %
          (r[1] or "")[:200])
    fx.plan("RimMandrake.Biomes mandrake.rm.biomes\n    ~  Biomes/Pyrelands/Defs/X.xml\n")
    st = M.deploy_state(fx.root, P)
    check(st.get("state") == "could_not_look",
          "a-blind-plan-is-could-not-look: a plan printing neither last line is could-not-look (read %s)" % st.get("state"))


def t_a_held_bridge_or_game_waits(fx):
    fx.plan(drift("~  Biomes/Pyrelands/Defs/ThingDefs/RM_FE_Ash.xml"), after=SYNC)
    r = fx.launch(FakeGame(up=True), bridge=(False, "NOT TAKEABLE  held by CONDUCTOR for a look"))
    check(r[0] == 2 and r[1].startswith(M.WAIT_MARK) and not fx.launched()
          and not any("--apply" in c for c in fx.plan_calls()),
          "a-held-bridge-or-game-waits: the bridge held: a wait refusal, no deploy (%s)" % (r[1] or "")[:160])
    fx.plan(drift("~  Biomes/Pyrelands/Defs/ThingDefs/RM_FE_Ash.xml"), after=SYNC)
    g = FakeGame(up=True, held="game a is held: his look")
    r2 = fx.launch(g)
    check(r2[0] == 2 and r2[1].startswith(M.WAIT_MARK) and g.log == [] and not fx.launched()
          and not any("--apply" in c for c in fx.plan_calls()),
          "a-held-bridge-or-game-waits: game a under his hold: a wait refusal, no stop, no deploy (%s)" %
          (r2[1] or "")[:160])
    # the tick's bookkeeping of that refusal: three in a row, no fault and no try spent
    cfg = {"launch_tries": 3, "_code": "c1"}
    st = {"mods": {P: {}}}
    s = st["mods"][P]
    row = {"mod": P, "visit": 2, "visit_id": "0.1.0#2", "cap": 30}
    for _ in range(3):
        entry = (s.get("ingame_auto") or [None])[-1]
        row["retry_of"] = entry if entry and MD.retriable(cfg, entry, mod=P) else None
        MD.launch_counted(cfg, s, row, ST.INGAME_CLOCK, "ingame_auto", {"visit_id": "0.1.0#2", "visit": 2},
                          lambda: "RIMMANDRAKE_DRIVE_X_IN_GAME_VISIT_TWO", lambda it: (True, "filed %s" % it),
                          lambda it: (True, "publish: pushed"), lambda it: (2, r[1], None))
        RV.sync_system(st, lambda u: None, keep_failed=lambda b, x: MD.still_retried(cfg, b, x, P),
                       now=ST.INGAME_CLOCK)
    e = (s.get("ingame_auto") or [{}])[-1]
    check(RV.faults(s) == 0 and len(s.get("ingame_auto") or []) == 1 and int(e.get("tries") or 0) <= 1,
          "a-held-bridge-or-game-waits: three such refusals count 0 faults and spend no try (faults %d, entries %d, "
          "tries %s)" % (RV.faults(s), len(s.get("ingame_auto") or []), e.get("tries")))


def t_a_game_only_def_refuses(fx):
    fx.plan(drift("-  Biomes/Pyrelands/Defs/ThingDefs_Ash/Filth_Stray.xml" + KEPT))
    g = FakeGame(up=True)
    r = fx.launch(g)
    check(r[0] == 2 and "Filth_Stray.xml" in r[1] and "--pull" in r[1] and "--prune" in r[1] and g.log == []
          and not any("--apply" in c for c in fx.plan_calls()) and not fx.launched(),
          "a-game-only-def-refuses: a kept game-only def refuses, naming the file and --pull/--prune, no deploy (%s)"
          % (r[1] or "")[:220])
    # a game-only texture a repo file names (PyrelandsAshCover.cs names Things/Filth/RM_FE_AshCover) is drift too
    fx.plan(drift("-  Biomes/Pyrelands/Textures/Things/Filth/RM_FE_AshCover.png" + KEPT))
    st = M.deploy_state(fx.root, P)
    check(st.get("state") == "stuck" and any("RM_FE_AshCover.png" in x for x in st.get("loaded") or []),
          "a-game-only-def-refuses: a game-only texture a repo file names is loaded drift (read %s, %s)" % (
              st.get("state"), st.get("loaded")))


def t_an_empty_or_add_only_plan(fx):
    fx.plan(SYNC)
    st = M.deploy_state(fx.root, P)
    check(st.get("state") == "current" and not st.get("loaded") and not st.get("ignored"),
          "an-empty-or-add-only-plan: Everything in sync reads current (read %s)" % st.get("state"))
    fx.plan(drift("+  Biomes/Pyrelands/Textures/Things/Plant/RM_FE_New.png", "+  Biomes/Pyrelands/Defs/New.xml"),
            after=SYNC)
    g = FakeGame(up=False)
    r = fx.launch(g)
    check(r[0] == 0 and sum("--apply" in c for c in fx.plan_calls()) == 1 and len(fx.launched()) == 1,
          "an-empty-or-add-only-plan: only + lines on loaded files deploy, then launch (calls %s, %s)" % (
              fx.plan_calls(), (r[1] or "")[:160]))
    fx.plan(drift("~  Biomes/Pyrelands/Defs/ThingDefs/RM_FE_Ash.xml"), after=drift("~  Biomes/Pyrelands/Defs/X.xml"))
    r = fx.launch(FakeGame(up=False))
    check(r[0] == 2 and "still differs" in r[1] and not fx.launched(),
          "an-empty-or-add-only-plan: a plan still differing after the deploy refuses (%s)" % (r[1] or "")[:160])


DRAIN = ("refused: the account system is draining (switching plan notice since 2026-11-20T18:00:00-08:00): live runs "
         "finish on it and no new run starts until the switch. Launch again after it (`python3 "
         "src/RimMandrake/Utils/switching_plan.py status` shows it). Why: system at 3.0% is at or under its 3% line")
FIX = "RIMMANDRAKE_MOCK_FLOWWORKS_WATER_BY_DEPTH_ON_REAL_GROUND"


def fixer_ticks(reply, n=3):
    """n ticks of one fixer launch on mod FakeFlow, each refused with `reply`, the tick's sync_system after each."""
    cfg = {"launch_tries": 3, "_code": "c1", "seat": "BENCH"}
    st = {"mods": {"FakeFlow": {}}}
    s = st["mods"]["FakeFlow"]
    rows = []
    for i in range(n):
        x = (s.get("fixers") or {}).get(FIX)
        row = {"mod": "FakeFlow", "aut": "fixer", "fix_item": FIX, "fix_key": FIX, "stage": "blind_challenge",
               "cap": 10, "fix_for": "visit", **({"retry_of": x} if x else {})}
        AUT.execute("/nonexistent", cfg, st, [row], ["FakeFlow"], ST.INGAME_CLOCK + i * 60,
                    {"known": lambda: set(), "launch_brief": lambda *a, **k: (1, reply, None)})
        RV.sync_system(st, lambda u: None, keep_failed=lambda b, x: MD.still_retried(cfg, b, x, "FakeFlow"),
                       now=ST.INGAME_CLOCK + i * 60 + 1)
        rows.append(row)
    return s, rows


def t_drain_refusals_count_no_fault():
    s, rows = fixer_ticks(DRAIN)
    x = (s.get("fixers") or {}).get(FIX) or {}
    check(RV.faults(s) == 0 and rows[-1].get("decision") in AUT.WAIT and int(x.get("tries") or 0) <= 1,
          "drain-refusals-count-no-fault: three drain refusals in a row: fault count 0, no try spent, the row a wait "
          "(faults %d, decision %s, tries %s)" % (RV.faults(s), rows[-1].get("decision"), x.get("tries")))


def t_a_never_started_launch_owes_a_repair():
    # a launch that never started, for any reason, is a fault of form: no fault, one repair owed (form_fault;
    # selftest_repair_at_refusal.py). Before 2026-11-21 this check read "a real launch fault still counts".
    s, rows = fixer_ticks("LAUNCH FAILED rm-detached-x: Failed to start transient service unit", n=1)
    owed = [r for r in s.get("form_repairs") or [] if r.get("state") == "owed"]
    check(RV.faults(s) == 0 and len(owed) == 1,
          "a-never-started-launch-owes-a-repair: faults %d, repairs owed %d" % (RV.faults(s), len(owed)))


def t_the_tick_waits_on_a_drain():
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "fixer owed"}, {"mod": "Other", "decision": "live"}]
    la = MD.drain_gate(rows, ["FakeFlow"], DRAIN)
    check(la == [] and rows[0]["decision"] == "account_hold" and "waiting: account switch" in rows[0]["why"]
          and rows[1]["decision"] == "live",
          "the-tick-waits-on-a-drain: while the drain stands nothing launches and the row reads account_hold, "
          "waiting: account switch (read %s: %s)" % (rows[0]["decision"], rows[0].get("why", "")[:80]))
    rows = [{"mod": "FakeFlow", "decision": "launch", "why": "fixer owed"}]
    check(MD.drain_gate(rows, ["FakeFlow"], None) == ["FakeFlow"] and rows[0]["decision"] == "launch",
          "the-tick-waits-on-a-drain: no drain notice holds nothing")


def t_a_visit_item_name_passes_the_spawn_guard():
    import model
    known = {"RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_TWO", "RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO"}
    names = [MD.ingame_item_id("Pyrelands", 2, set()), MD.ingame_item_id("Pyrelands", 2, known),
             MD.ingame_item_id("GimmeSomeSlack", 3, {"RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_VISIT_THREE"})]
    check(all(n and model.RUNNER_INGAME_NAME.match(n) for n in names) and names[1] not in known,
          "a-visit-item-name-passes-the-spawn-guard: with both visit names taken (2026-11-20 7:11 PM, after a clear) "
          "the next name still passes the RUNNER spawn guard (%s)" % names)


def main():
    fx = Fixture()
    try:
        for t in (t_non_game_drift_launches, t_loaded_drift_deploys_then_launches, t_a_dll_deploys_with_the_game_down,
                  t_a_failed_deploy_is_a_fault, t_a_blind_plan_is_could_not_look, t_a_held_bridge_or_game_waits,
                  t_a_game_only_def_refuses, t_an_empty_or_add_only_plan):
            safe(lambda: t(fx) is None, t.__name__[2:] + " ran")
    finally:
        fx.close()
    for t in (t_drain_refusals_count_no_fault, t_a_never_started_launch_owes_a_repair, t_the_tick_waits_on_a_drain,
              t_a_visit_item_name_passes_the_spawn_guard):
        safe(lambda: t() is None, t.__name__[2:] + " ran")
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
