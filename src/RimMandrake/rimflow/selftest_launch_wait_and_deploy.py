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
    """game_instance's operations, recorded: running, hold_refusal, stop, pids, alive, launch."""

    def __init__(self, up=False, held=None, stop_rc=0, launch_rc=0):
        self.up, self.held, self.stop_rc, self.launch_rc, self.log = up, held, stop_rc, launch_rc, []

    def running(self, name=None):
        return self.up

    def hold_refusal(self, name, despite=None):
        return self.held

    def pids(self, name=None):
        return [4242] if self.up else []

    def alive(self, pids):
        return [p for p in pids if p == 4242] if self.up else []

    def stop(self, pid_=None, force=False, name=None, purpose=None, despite=None, seat=None):
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
                     "MATURATION_DEPLOY_PLAN", "FAKE_PLAN_DIR", "FAKE_APPLY_RC", M.COMPANION_ENV,
                     "MATURATION_COMPANION_BUILD", "FAKE_BUILD_RC")
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


class ExitingGame(FakeGame):
    """FakeGame whose stopped process stays in the list for `linger` reads with its command line unreadable, as Windows
    reports a RimWorld that is closing: game_instance.pids raises Blind for it, and only a read by pid sees it go."""

    def __init__(self, linger=2, **kw):
        FakeGame.__init__(self, **kw)
        self.linger, self.stopped = linger, False

    def _gone_yet(self):
        if self.stopped and self.linger:
            self.linger -= 1
            return False
        return True

    def pids(self, name=None):
        if self.stopped and not self._gone_yet():
            raise ExitingGame.Blind("cannot read the command line of game pid [4242], so it cannot be told apart")
        return FakeGame.pids(self, name)

    def alive(self, pids):
        return [] if self._gone_yet() else [p for p in pids if p == 4242]

    def stop(self, pid_=None, force=False, name=None, purpose=None, despite=None, seat=None):
        rc, txt = FakeGame.stop(self, pid_, force, name, purpose, despite, seat)
        self.stopped = True
        return rc, txt

    class Blind(RuntimeError):
        pass


def t_a_closing_game_is_waited_on_by_pid(fx):
    """RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_SIX: Pyrelands visit 5's deploy stopped game a (its Player.log
    closed 03:45:42 PST, 2026-11-22), then read the closing game's owner, got an unreadable command line for pid 15352,
    and refused "game a could not be stopped for the deploy: Blind". The wait after our own stop reads the stopped pids."""
    fx.plan(drift("~  Biomes/Pyrelands/Assemblies/FireEcologyHook.dll"), after=SYNC)
    g = ExitingGame(up=True)
    r = M.launch_mod(fx.root, P, 20, ST.ITEM, seat="BENCH", bridge=lambda p, s, game="a": (True, "free"),
                     companion=lambda game="a": (True, "fresh"), game="a", game_ops=g)
    stops = [x for x in g.log if x[0] == "stop"]
    check(r[0] == 0 and r[2] and len(fx.launched()) == 1 and stops == [("stop", "a", False)] and g.up,
          "a-closing-game-is-waited-on-by-pid: a stopped game whose command line reads empty while it closes is waited "
          "on by its pid, not refused as Blind; one plain stop, the deploy, the game up, the visit launched (stops %s, "
          "rc %s %s)" % (stops, r[0], (r[1] or "")[:200]))


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


STUB_IDLE = r"""import os, sys
a = sys.argv[1:]
seat = os.environ.get("RIMFLOW_SEAT") or (a[a.index("--seat") + 1] if "--seat" in a else None)
if not seat:
    sys.stderr.write("REFUSED: I cannot tell which seat I am, and I will not guess.\n")
    sys.exit(2)
print("TAKEABLE  free (stub, seat %s)" % seat)
"""


class SeatGame(FakeGame):
    """FakeGame whose stop records the seat it was handed."""

    def stop(self, pid_=None, force=False, name=None, purpose=None, despite=None, seat=None):
        self.log.append(("seat", seat))
        return FakeGame.stop(self, pid_, force, name, purpose, despite, seat)


def t_a_seatless_tick_stops_its_game(fx):
    """RIMMANDRAKE_REPAIR_GIMMESOMESLACK_FORM_REFUSAL_AT_THE_RUN_FIVE: the systemd tick names no seat in its env, so the
    deploy's game stop ran `rimflow bridge idle` seatless and got "I cannot tell which seat I am" (exit 2)."""
    fx.plan(drift("~  Biomes/Pyrelands/Assemblies/FireEcologyHook.dll"), after=SYNC)
    g = SeatGame(up=True)
    r = M.launch_mod(fx.root, P, 20, ST.ITEM, seat="BENCH", bridge=lambda p, s, game="a": (True, "free"),
                     companion=lambda game="a": (True, "fresh"), game="a", game_ops=g)
    seats = [x[1] for x in g.log if x[0] == "seat"]
    check(r[0] == 0 and seats and all(x == "BENCH" for x in seats),
          "a-seatless-tick-stops-its-game: the deploy's game stop is handed the launch's seat (seats %s, rc %s %s)"
          % (seats, r[0], (r[1] or "")[:200]))
    utils = os.path.join(REPO, "src", "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    import game_instance as GI
    stub = os.path.join(fx.root, "stub_idle.py")
    with open(stub, "w") as f:
        f.write(STUB_IDLE)
    was = {k: os.environ.pop(k, None) for k in ("RIMFLOW_SEAT", "AGENT_SEAT")}
    cli, holder = GI.RIMFLOW_CLI, GI.live_holder
    GI.RIMFLOW_CLI, GI.live_holder = stub, (lambda name, new_run=False: None)
    try:
        bare = GI.bridge_refusal("a", "probe")
        seated = GI.bridge_refusal("a", "probe", seat="BENCH")
    finally:
        GI.RIMFLOW_CLI, GI.live_holder = cli, holder
        os.environ.update({k: v for k, v in was.items() if v})
    check(seated is None and bare and "which seat" in bare,
          "a-seatless-tick-stops-its-game: bridge_refusal with seat=BENCH reads the stub's TAKEABLE in a seatless env "
          "(seated %r; bare %r)" % (seated, (bare or "")[:120]))


FAKE_BUILD = r"""#!/usr/bin/env python3
import os, sys
d = os.environ["FAKE_PLAN_DIR"]
with open(os.path.join(d, "build.log"), "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\n")
with open(os.path.join(d, "build_env.log"), "a") as f:
    f.write("%s %s\n" % (os.environ.get("RM_HOST_GUARD_GEN", "-"), os.environ.get("RIMFLOW_SEAT", "-")))
rc = int(os.environ.get("FAKE_BUILD_RC", "0"))
if rc:
    print("CANNOT DEPLOY WHILE RIMWORLD IS RUNNING (the process list shows it). Nothing was written.")
    sys.exit(rc)
open(os.path.join(d, "built"), "w").close()
print("deployed. RESTART RIMWORLD")
"""


class Companion:
    """A companion reader: STALE until the fake build has run (its `built` marker), then FRESH; `stays` keeps it STALE."""

    def __init__(self, fx, stays=False):
        self.fx, self.stays, self.reads = fx, stays, []
        for n in ("built", "build.log", "build_env.log"):
            if os.path.exists(os.path.join(fx.pd, n)):
                os.remove(os.path.join(fx.pd, n))
        b = os.path.join(fx.root, "fake_build.py")
        with open(b, "w") as f:
            f.write(FAKE_BUILD)
        os.environ[M.COMPANION_BUILD_ENV] = "%s %s" % (sys.executable, b)

    def __call__(self, game="a"):
        self.reads.append(game)
        if os.path.exists(os.path.join(self.fx.pd, "built")) and not self.stays:
            return True, "FRESH (stand-in)"
        return False, "STALE /x/JawaBench.BridgeTools.dll (stand-in)"

    def builds(self):
        p = os.path.join(self.fx.pd, "build.log")
        return open(p).read().splitlines() if os.path.exists(p) else []


def companion_launch(fx, comp, g, game="a"):
    return M.launch_mod(fx.root, P, 20, ST.ITEM, bridge=lambda p, s, game="a": (True, "free"), companion=comp,
                        game=game, game_ops=g)


def t_a_stale_companion_rebuilds_with_the_game_down(fx):
    """RIMMANDRAKE_REPAIR_FLOWWORKS_FORM_REFUSAL_AT_THE_RUN_FOUR: FlowWorks visit 3 was refused for a STALE companion
    with the bridge free and the fix named (`build.py --gm --apply`), and the tick never sends a refused input again."""
    fx.plan(SYNC)
    comp, g = Companion(fx), FakeGame(up=True)
    r = companion_launch(fx, comp, g, game="b")
    b = comp.builds()
    check(r[0] == 0 and r[2] and len(fx.launched()) == 1 and len(b) == 1
          and all(x in b[0].split() for x in ("--gm", "--apply")) and "--instance b" in b[0]
          and [x[0] for x in g.log] == ["stop", "launch"] and g.up and len(comp.reads) >= 2,
          "a-stale-companion-rebuilds-with-the-game-down: a STALE companion with the bridge free: game b stopped, "
          "`build.py --gm --apply --instance b` once, game b started, the companion read again, the visit launches "
          "(builds %s, game ops %s, reads %s, rc %s %s)" % (b, g.log, comp.reads, r[0], (r[1] or "")[:200]))


def t_a_stale_companion_and_drift_share_one_restart(fx):
    fx.plan(drift("~  Biomes/Pyrelands/Assemblies/FireEcologyHook.dll"), after=SYNC)
    comp, g = Companion(fx), FakeGame(up=True)
    r = companion_launch(fx, comp, g)
    calls = fx.plan_calls()
    check(r[0] == 0 and r[2] and len(comp.builds()) == 1 and sum("--apply" in c for c in calls) == 1
          and [x[0] for x in g.log] == ["stop", "launch"],
          "a-stale-companion-and-drift-share-one-restart: a STALE companion and a drifting DLL: one stop, the rebuild "
          "and the deploy, one start, then the visit (builds %s, plan calls %s, game ops %s, rc %s %s)" % (
              comp.builds(), calls, g.log, r[0], (r[1] or "")[:200]))


def t_a_failed_companion_build_is_a_fault(fx):
    fx.plan(SYNC)
    comp, g = Companion(fx), FakeGame(up=False)
    os.environ["FAKE_BUILD_RC"] = "1"
    try:
        r = companion_launch(fx, comp, g)
    finally:
        os.environ.pop("FAKE_BUILD_RC", None)
    check(r[0] == 2 and r[1].startswith("REFUSED") and "companion" in r[1] and "CANNOT DEPLOY" in r[1]
          and not fx.launched(),
          "a-failed-companion-build-is-a-fault: a rebuild that exits non-zero: REFUSED, naming the rebuild and its "
          "line, not a wait, nothing launched (rc %s %s)" % (r[0], (r[1] or "")[:240]))
    fx.plan(SYNC)
    comp, g = Companion(fx, stays=True), FakeGame(up=False)
    r = companion_launch(fx, comp, g)
    check(r[0] == 2 and r[1].startswith("REFUSED") and "STALE" in r[1] and not fx.launched(),
          "a-failed-companion-build-is-a-fault: a companion still STALE after the rebuild: REFUSED, naming it "
          "(rc %s %s)" % (r[0], (r[1] or "")[:240]))


def t_a_stale_companion_on_a_held_game_waits(fx):
    fx.plan(SYNC)
    comp, g = Companion(fx), FakeGame(up=True, held="game a is held: pipe off game:a")
    r = companion_launch(fx, comp, g)
    check(r[0] == 2 and r[1].startswith(M.WAIT_MARK) and not comp.builds() and g.log == [] and not fx.launched(),
          "a-stale-companion-on-a-held-game-waits: his hold on the game: no rebuild, no stop, the refusal starts with "
          "WAIT_MARK (rc %s %s)" % (r[0], (r[1] or "")[:200]))


class Lock:
    """A _repair_lock stand-in: records claim and release beside the game's operations (one shared log)."""

    def __init__(self, g, state="ok", gen=7):
        self.g, self.state, self.gen = g, state, gen

    def __call__(self, game, purpose, seat):
        self.g.log.append(("claim", game, seat))
        if self.state != "ok":
            return self.state, "ArchBig: HELD by BENCH (pid 4009276), for: another run's staging", lambda: None
        was = os.environ.get("RM_HOST_GUARD_GEN")
        os.environ["RM_HOST_GUARD_GEN"] = str(self.gen)

        def release():
            if was is None:
                os.environ.pop("RM_HOST_GUARD_GEN", None)
            else:
                os.environ["RM_HOST_GUARD_GEN"] = was
            self.g.log.append(("release", game))
        return "ok", "CLAIMED", release


def t_a_repair_holds_the_game_for_its_whole_window(fx):
    """RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_EIGHT: on 2026-11-22 at 21:07 PST the tick stopped ArchBig
    for Pyrelands visit 6's companion rebuild without holding its lock; another run claimed the free lock mid-rebuild,
    and build.py refused (`the bridge is held by BENCH (this seat: unset)`). The repair takes the lock before the stop,
    its build runs under that take, and it frees the lock only after the game is up again."""
    fx.plan(SYNC)
    comp, g = Companion(fx), FakeGame(up=True)
    st, txt = M.deploy_repair(fx.root, P, "a", None, g, "selftest repair", seat="BENCH", companion=comp, lock=Lock(g))
    envp = os.path.join(fx.pd, "build_env.log")
    benv = open(envp).read().split() if os.path.exists(envp) else []
    check(st == "ok" and [x[0] for x in g.log] == ["claim", "stop", "launch", "release"] and benv[:1] == ["7"]
          and os.environ.get("RM_HOST_GUARD_GEN") is None,
          "a-repair-holds-the-game-for-its-whole-window: claim, stop, rebuild under the take (RM_HOST_GUARD_GEN), "
          "start, release (state %s, ops %s, build env %s, %s)" % (st, g.log, benv, (txt or "")[:160]))


def t_a_repair_on_a_game_another_run_holds_waits(fx):
    fx.plan(SYNC)
    comp, g = Companion(fx), FakeGame(up=True)
    st, txt = M.deploy_repair(fx.root, P, "a", None, g, "selftest repair", seat="BENCH", companion=comp,
                              lock=Lock(g, state="held"))
    check(st == "wait" and txt.startswith(M.WAIT_MARK) and [x[0] for x in g.log] == ["claim"] and not comp.builds()
          and g.up,
          "a-repair-on-a-game-another-run-holds-waits: another run's live lock: a wait, the game left up, no rebuild "
          "(state %s, ops %s, %s)" % (st, g.log, (txt or "")[:200]))
    g2 = FakeGame(up=True)
    st, txt = M.deploy_repair(fx.root, P, "a", None, g2, "selftest repair", seat="BENCH", companion=comp,
                              lock=Lock(g2, state="blind"))
    check(st == "fail" and not txt.startswith(M.WAIT_MARK) and [x[0] for x in g2.log] == ["claim"],
          "a-repair-on-an-unreadable-lock-is-a-fault: a lock that could not be looked at: a fault named, nothing done "
          "(state %s, ops %s, %s)" % (st, g2.log, (txt or "")[:200]))


def t_the_real_repair_lock_takes_and_frees_this_process(fx):
    """M._repair_lock on a temp lock file: free -> held by THIS process (not its parent, which for the systemd tick
    never exits), RM_HOST_GUARD_GEN set while held; release -> FREE and the env restored; another live process's
    lock -> held, nothing taken."""
    import subprocess
    import game_lock as GL
    import driver_lock as DL
    path = os.path.join(fx.root, "lock_a", "DRIVER_LOCK.json")
    os.makedirs(os.path.dirname(path))
    keys = ("RIMFLOW_DRIVER_LOCK", "RM_GAME_INSTANCE", "RM_HOST_GUARD_GEN", "RM_DRIVER_PID")
    was = {k: os.environ.get(k) for k in keys}
    os.environ["RIMFLOW_DRIVER_LOCK"] = path
    os.environ.pop("RM_GAME_INSTANCE", None)
    os.environ.pop("RM_HOST_GUARD_GEN", None)
    sleeper = None
    try:
        st, txt, release = M._repair_lock("a", "selftest repair", "BENCH")
        q = GL.query("a", pipe=False, path=path)
        held_ok = (st == "ok" and q["state"] == "HELD" and (q.get("holder") or {}).get("pid") == os.getpid()
                   and os.environ.get("RM_HOST_GUARD_GEN") == str(q.get("generation"))
                   and os.environ.get("RM_DRIVER_PID") == str(os.getpid()))
        utils = os.path.join(os.path.dirname(HERE), "Utils")
        if utils not in sys.path:
            sys.path.insert(0, utils)
        import game_instance as GI
        stop_gate = GI.bridge_refusal("a", "selftest stop", seat="BENCH")    # the stop's gate: our own take passes
        release()
        q2 = GL.query("a", pipe=False, path=path)
        freed = (q2["state"] == "FREE" and os.environ.get("RM_HOST_GUARD_GEN") is None
                 and os.environ.get("RM_DRIVER_PID") is None)
        sleeper = subprocess.Popen(["sleep", "60"])
        other = dict(DL.my_identity(), pid=sleeper.pid, start=DL._proc_start(sleeper.pid))
        GL.claim("a", "another run", seat="BENCH", identity=other, path=path)
        st3, txt3, _ = M._repair_lock("a", "selftest repair", "BENCH")
        q3 = GL.query("a", pipe=False, path=path)
        check(held_ok and stop_gate is None and freed and st3 == "held" and (q3.get("holder") or {}).get("pid") == sleeper.pid,
              "the-real-repair-lock-takes-and-frees-this-process: held by pid %s with its generation exported, freed "
              "on release, the stop's gate passes its own take, another live run's lock read as held (%s / %s / %s / %s %s)" % (
                  os.getpid(), q.get("line"), stop_gate, q2.get("line"), st3, txt3[:120]))
    finally:
        if sleeper:
            sleeper.kill()
            sleeper.wait()
        for k, v in was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


STALE = "the walk build is not the current source: the deployed walk folder X is not the source at abc (its .srchash differs)"


def stale_tick(st, why, owed="exit not met", dec="exit_not_met"):
    """One tick's resolve on an in-game visit that ended not met for `why` (its exit's reasons)."""
    root = tempfile.mkdtemp(prefix="walkdeploy_")
    os.makedirs(os.path.join(root, "design", "concepts"))
    facts = {P: {"version": "0.1.0", "visit": 6, "live_units": [], "owed": owed, "exit": {"state": "not_met", "why": why}}}
    rows = [{"mod": P, "stage": "in_game", "decision": dec, "visit": 6, "why": "; ".join(why[:3]), "need": "n"}]
    rows, launches = AUT.resolve(root, {"seat": "BENCH", "max_live": 4, "steward_cap_tokens": 1_250_000}, st, facts, rows, [], 1000.0, {
        "designer_state": lambda m: {}, "version_locked": lambda m: True, "open_items": lambda ids, **kw: [],
        "version_evidence": lambda m: [], "designer_unit": lambda m: None, "designer_chain": lambda m: None,
        "live_endings": lambda ids: {}, "version_bugs": lambda *a, **k: [], "ticket_runs": lambda i: []})
    return rows[0], launches


def t_a_stale_walk_build_is_the_ticks_deploy():
    cfg = {"seat": "BENCH"}
    known = {"known": lambda: set(), "file": lambda *a, **k: (False, "no filing in a test")}
    st = {"mods": {}}
    r, la = stale_tick(st, [STALE])
    check(r.get("aut") == "autodeploy" and la == [P] and "autodeploy" in MD.NO_SLOT_AUT and not r.get("need"),
          "a-stale-walk-build-is-the-ticks-deploy: an exit whose one reason is the stale walk folder is the tick's act, no "
          "steward (read %s / %s)" % (r.get("decision"), la))
    r2, _ = stale_tick({"mods": {}}, [STALE, "in-game check sc_x: its last row reads FAIL"])
    check(r2.get("aut") == "steward", "...with any other reason beside it, the steward reads the visit (%s)" % r2.get("aut"))
    key = r["steward_key"]

    def ended(state, text, **kw):
        """The deploy unit's end, as the tick's game_deploy_sync books it."""
        st["mods"].setdefault(P, {})["game_deploy"] = dict({
            "unit": "rm-game-deploy-x", "game": "a", "kind": "walk", "key": key, "at": 900.0, "tries": 1, "ended": 990.0,
            "result": {"state": state, "text": text}}, **kw)
    units = []
    fx = dict(known, walk_letter=lambda r_, m: "a", game_deploy=lambda mod, game, kind, purpose, seat="BENCH": (
        units.append((mod, game, kind)) or (0, "STARTED", "rm-game-deploy-%d" % len(units))))
    ended("wait", "%s ArchBig is held by another run" % M.WAIT_MARK)
    AUT.execute("/nonexistent", dict(cfg), st, [r], la, 1000.0, fx)
    check(r["decision"] == "live" and units == [(P, "a", "walk")] and not (st["mods"][P].get("steward") or {}),
          "...a game another run holds is a wait that spends no try: the deploy starts again (%s)" % r["decision"])
    r, la = stale_tick(st, [STALE])
    check(r.get("aut") == "autodeploy" and la == [P], "...and the next tick tries it again (%s)" % r.get("decision"))
    ended("ok", "ArchBig stopped; deployed; ArchBig started")
    AUT.execute("/nonexistent", dict(cfg), st, [r], la, 1000.0, fx)
    check(r["decision"] == "launched" and "ArchBig stopped" in r["why"], "...a deploy that lands says what it did (%s)" % r["why"])
    r, la = stale_tick(st, [STALE])
    check(r.get("decision") == "launch_failed" and la == [], "...a reading still stale after it pauses, never loops (%s)"
          % r.get("decision"))
    st = {"mods": {}}
    r, la = stale_tick(st, [STALE])
    ended("fail", "the deploy exited 1")
    AUT.execute("/nonexistent", dict(cfg), st, [r], la, 1000.0, fx)
    check(r["decision"] == "launch_failed" and "exited 1" in r["why"], "...a failed deploy names its cause (%s)" % r["why"])
    st = {"mods": {}}
    r, la = stale_tick(st, [STALE])
    ended("ok", "an earlier stale reading's", key="another")
    AUT.execute("/nonexistent", dict(cfg), st, [r], la, 1000.0, fx)
    check(r["decision"] == "live" and len(units) == 2, "...another reading's deploy is not this one's (%s)" % r["decision"])


def t_a_build_match_that_could_not_look_is_a_wait():
    blind = "the build match could not look (AboutUnreadable: ENOMEM): no in-game check counts until it does"
    for why in ([blind], [blind, "in-game check sc_x: its last row reads FAIL"]):
        st = {"mods": {}}
        r, la = stale_tick(st, why)
        check(r.get("decision") == "launch_wait" and not r.get("aut") and not r.get("need") and la == [],
              "a-build-match-that-could-not-look-is-a-wait: no steward, no launch (read %s / %s / %s)" % (
                  r.get("decision"), r.get("aut"), la))
    r, _ = stale_tick({"mods": {}}, ["the build match could not run (ValueError: x): no in-game check counts until it does"])
    check(r.get("aut") == "steward", "...a build match that cannot run for another cause still brings the steward (%s)"
          % r.get("aut"))


def t_about_read_waits_out_enomem():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "..", "Utils", "selftest_modset_about_enomem.py")],
                       capture_output=True, text=True, timeout=300)     # a hang guard
    check(r.returncode == 0, "about-read-waits-out-enomem: selftest_modset_about_enomem.py (rc %d, %s)" % (
        r.returncode, r.stdout[-300:]))


def main():
    fx = Fixture()
    try:
        for t in (t_non_game_drift_launches, t_loaded_drift_deploys_then_launches, t_a_dll_deploys_with_the_game_down,
                  t_a_closing_game_is_waited_on_by_pid,
                  t_a_failed_deploy_is_a_fault, t_a_blind_plan_is_could_not_look, t_a_held_bridge_or_game_waits,
                  t_a_game_only_def_refuses, t_an_empty_or_add_only_plan, t_a_seatless_tick_stops_its_game,
                  t_a_stale_companion_rebuilds_with_the_game_down, t_a_stale_companion_and_drift_share_one_restart,
                  t_a_failed_companion_build_is_a_fault, t_a_stale_companion_on_a_held_game_waits,
                  t_a_repair_holds_the_game_for_its_whole_window, t_a_repair_on_a_game_another_run_holds_waits,
                  t_the_real_repair_lock_takes_and_frees_this_process):
            safe(lambda: t(fx) is None, t.__name__[2:] + " ran")
    finally:
        fx.close()
    for t in (t_drain_refusals_count_no_fault, t_a_never_started_launch_owes_a_repair, t_the_tick_waits_on_a_drain,
              t_a_visit_item_name_passes_the_spawn_guard, t_a_stale_walk_build_is_the_ticks_deploy,
              t_a_build_match_that_could_not_look_is_a_wait,
              t_about_read_waits_out_enomem):
        safe(lambda: t() is None, t.__name__[2:] + " ran")
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
