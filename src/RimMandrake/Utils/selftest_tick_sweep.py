#!/usr/bin/env python3
"""selftest: the sweep of the Maturation Pipeline tick (RIMMANDRAKE_BUILD_TICK_SWEEP_SLACK_KEPT_TICKETS_45_HOURS; page
design/specs/2026-11-27-tick-sweep/boundary.md). One check per promise, by its name. Each measured fault is planted
again (a monkeypatched reversal of its fix, tick_sweep.PLANTS) and the sweep must name it; the shipped code must sweep
clean over the quick grid.

    python3 src/RimMandrake/Utils/selftest_tick_sweep.py          the checks (what ./publish runs)
    python3 src/RimMandrake/Utils/selftest_tick_sweep.py --red    each check against a sweep that cannot see its
                                                                  fault: every one must FAIL (exit 0 when all do)
"""
import contextlib
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tick_sweep as TS  # noqa: E402

FAILS = []
PLANT_HOURS = 3     # every planted fault reads STUCK by +80 min (its limit, 1 h, past its start); 3 h is room to spare


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (": " + str(detail)[:600]) if detail else ""))
    if not ok:
        FAILS.append("%s: %s" % (name, str(detail)[:600]))


def run(reg_name, plant, hours=PLANT_HOURS, fx=None):
    base, window, offset = reg_name.split(".")
    reg = TS.regime(base, window, int(offset), hours=hours)
    if fx:
        reg["fx"] = fx
    return TS.sweep([reg], plant)


def stuck_of(out, kind):
    return [c for r in out["results"] for c in r["stuck"] if c["kind"] == kind]


def line(out):
    return " | ".join(TS.report(out).splitlines()[:5])


# ---------------------------------------------------------------- the four measured faults, and the road-back hold

def t_mod_resting_after_pass_keeps_open_tickets_found():
    # Gimme Some Slack, 2026-11-24: passed, resting, two mod_work tickets on no owed list for 45 h (fixed 07441d68f4)
    out = run("rest.calm.0", "rest")
    got = sorted(c["what"].split()[0] for c in stuck_of(out, "ticket"))
    check("mod_resting_after_pass_keeps_open_tickets_found: both open tickets STUCK off the owed list",
          got == ["RIMMANDRAKE_A", "RIMMANDRAKE_B"], "%s; %s" % (got, line(out)))


def t_refused_load_counted_as_visit_failure_found():
    # RIMMANDRAKE_ROUTE_VISIT_TESTQ_CHECKS_AHEAD_OF_FILLER: a lane refusal (LOAD) spent the check (fixed 5d09ae880d)
    out = run("visit.lane_refuses_1h.0", "refused")
    got = sorted(c["what"] for c in stuck_of(out, "chain"))
    check("refused_load_counted_as_visit_failure_found: each check spent by lane refusals alone, never run, STUCK",
          got == ["Fw x1", "Fw x2", "Fw x3"], "%s; %s" % (got, line(out)))


def t_deploy_given_to_a_steward_that_may_not_stop_the_game_found():
    # RIMMANDRAKE_LET_TICK_DEPLOY_STALE_WALK_BUILD_STEWARD_MAY_NOT_STOP_GAME: Explosive Knockback, 2026-11-24 (9f802d6866)
    out = run("stale.calm.0", "steward_deploy")
    got = [c for c in stuck_of(out, "mod") if c["what"] == "Ek"]
    check("deploy_given_to_a_steward_that_may_not_stop_the_game_found: Ek STUCK on a live steward that nothing ends",
          bool(got) and "steward" in str(got[0].get("why")), "%s; %s" % (got[:1], line(out)))


def t_road_back_hold_read_blocked_with_games_free_found():
    # design/specs/2026-11-25-tick-launches-road-back-hold/boundary.md: offline_build read `blocked` on road_back_items
    out = run("road.calm.0", "road_back")
    got = [c for c in stuck_of(out, "mod") if c["what"] == "Ekb"]
    check("road_back_hold_read_blocked_with_games_free_found: Ekb STUCK on `blocked` with both games free",
          bool(got) and got[0].get("decision") == "blocked", "%s; %s" % (got[:1], line(out)))


# ---------------------------------------------------------------- the sweep's own nets, each seen to catch

def t_relaunch_loop_that_never_leaves_found():
    # no measured fault: the day-end net. Each steward gives up after 2 h and is launched again, so the mod moves every
    # step but never leaves in_game; only the day's end reads it
    out = run("stale.steward_gives_up.0", "relaunch_loop", hours=TS.QUICK_HOURS)
    got = [c for c in stuck_of(out, "day") if c["what"] == "Ek"]
    check("relaunch_loop_that_never_leaves_found: Ek STUCK at the day's end, never left in_game",
          bool(got) and not stuck_of(out, "mod"), "%s; %s" % (got[:1], line(out)))


def t_swallowed_exception_found():
    # a stand-in that breaks the real contract (publish_filed -> (ok, text)) makes the tick catch a TypeError into a
    # row's why; the sweep names it, never reads it as a pass
    out = run("stale.steward_gives_up.0", "relaunch_loop", fx={"publish": lambda item: None})
    got = stuck_of(out, "error")
    check("swallowed_exception_found: a TypeError the tick caught is an error case",
          bool(got) and "TypeError" in str(got[0].get("why")), "%s; %s" % (got[:1], line(out)))


def t_world_calls_are_refused_and_counted():
    del TS.TOUCHED[:]
    errs = []
    for f in (lambda: subprocess.run(["true"], timeout=5),     # budget: fixture (refused before it starts)
              lambda: socket.create_connection(("127.0.0.1", 9), timeout=1)):  # budget: fixture (refused, never sent)
        try:
            f()
        except OSError as e:
            errs.append(str(e))
    check("world_calls_are_refused_and_counted: a process and a socket are each refused and counted",
          len(errs) == 2 and len(TS.TOUCHED) == 2, "%s %s" % (errs, TS.TOUCHED))
    del TS.TOUCHED[:]


def t_sweep_is_deterministic():
    a, b = run("mixed.lane_refuses_1h.0", None), run("mixed.lane_refuses_1h.0", None)
    ea, eb = a["results"][0]["events"], b["results"][0]["events"]
    check("sweep_is_deterministic: the same regime twice gives the same events and cases",
          ea == eb and a["cases"] == b["cases"] and len(ea) > 0, "%d/%d events, %d/%d cases" % (
              len(ea), len(eb), a["cases"], b["cases"]))


def t_shipped_tick_sweeps_clean():
    out = TS.sweep(TS.grid(quick=True))
    print(TS.report(out))
    check("shipped_tick_sweeps_clean: the quick grid reads no STUCK case and touches nothing of the world",
          out["stuck"] == 0 and out["touched"] == 0 and out["cases"] > 0,
          "%d stuck, %d touched, %d cases in %d regimes" % (out["stuck"], out["touched"], out["cases"],
                                                            len(out["results"])))


# ---------------------------------------------------------------- red: each check against a sweep blind to its fault

@contextlib.contextmanager
def _unplanted(name):
    """The plant `name` puts nothing back: the _found check then reads the shipped code, which has no such fault."""
    old = TS.PLANTS[name]
    TS.PLANTS[name] = TS.Plant(name, "unplanted (red run)", lambda: [])
    try:
        yield
    finally:
        TS.PLANTS[name] = old


@contextlib.contextmanager
def _old_told():
    """The sweep's first told(): any paused row counted as told. Blind to the road-back fault (a `blocked` row is
    klass paused with no need line)."""
    old = TS.told
    TS.told = lambda row: bool(row.get("need")) or row.get("klass") in ("held", "planned", "paused")
    try:
        yield
    finally:
        TS.told = old


@contextlib.contextmanager
def _planted_globally(name):
    """The shipped-clean check with a fault planted in every regime: it must go red."""
    old = TS.sweep

    def planted(regs, plant=None, rows=False):
        return old(regs, plant or name, rows)
    TS.sweep = planted
    try:
        yield
    finally:
        TS.sweep = old


@contextlib.contextmanager
def _blind_world():
    """The guard that refuses world calls is taken off: nothing is refused, nothing counted."""
    TS.subprocess.Popen.__init__ = TS._POPEN_INIT
    conn = TS.socket.socket.connect
    TS.socket.socket.connect = lambda self, addr: (_ for _ in ()).throw(OSError("refused, not counted (red run)"))
    try:
        yield
    finally:
        TS.subprocess.Popen.__init__ = TS._refuse_popen
        TS.socket.socket.connect = conn


@contextlib.contextmanager
def _good_stub():
    old = run

    def fixed(reg_name, plant, hours=PLANT_HOURS, fx=None):
        return old(reg_name, plant, hours=hours, fx=None)
    globals()["run"] = fixed
    try:
        yield
    finally:
        globals()["run"] = old


RED = [
    (t_world_calls_are_refused_and_counted, "the world guard off", _blind_world),
    (t_mod_resting_after_pass_keeps_open_tickets_found, "unplanted", lambda: _unplanted("rest")),
    (t_refused_load_counted_as_visit_failure_found, "unplanted", lambda: _unplanted("refused")),
    (t_deploy_given_to_a_steward_that_may_not_stop_the_game_found, "unplanted", lambda: _unplanted("steward_deploy")),
    (t_road_back_hold_read_blocked_with_games_free_found, "unplanted", lambda: _unplanted("road_back")),
    (t_road_back_hold_read_blocked_with_games_free_found, "planted, the first told() (paused = told)", _old_told),
    (t_relaunch_loop_that_never_leaves_found, "unplanted", lambda: _unplanted("relaunch_loop")),
    (t_swallowed_exception_found, "the stand-in keeps its contract", _good_stub),
    (t_shipped_tick_sweeps_clean, "the rest fault planted in every regime", lambda: _planted_globally("rest")),
]


def main(argv):
    t0 = time.time()
    try:
        if "--red" in argv:
            missed = []
            for t, label, blind in RED:
                del FAILS[:]
                with blind():
                    t()
                if FAILS:
                    print("RED as expected: %s (%s)" % (t.__name__, label))
                else:
                    missed.append(t.__name__)
            del FAILS[:]
            print("\nselftest_tick_sweep --red: %d of %d checks went red; %.1f s" % (len(RED) - len(missed), len(RED),
                                                                                    time.time() - t0))
            for m in missed:
                print("  STAYED GREEN " + m)
            return 1 if missed else 0
        # named here, not in a list: boundary_check.tests_in reads which tests main() runs from main's own names
        for t in (t_world_calls_are_refused_and_counted, t_mod_resting_after_pass_keeps_open_tickets_found,
                  t_refused_load_counted_as_visit_failure_found,
                  t_deploy_given_to_a_steward_that_may_not_stop_the_game_found,
                  t_road_back_hold_read_blocked_with_games_free_found, t_relaunch_loop_that_never_leaves_found,
                  t_swallowed_exception_found, t_sweep_is_deterministic, t_shipped_tick_sweeps_clean):
            try:
                t()
            except Exception as e:  # noqa: BLE001  a check that broke is a FAIL of its promise, by name
                import traceback
                check(t.__name__[2:] + ": the check itself broke", False, "%s: %s | %s" % (
                    type(e).__name__, e, traceback.format_exc().strip().splitlines()[-3:]))
    finally:
        shutil.rmtree(TS.ROOT, ignore_errors=True)
    print("\n%s: %d FAIL; %.1f s" % ("selftest_tick_sweep", len(FAILS), time.time() - t0))
    for f in FAILS:
        print("  FAIL " + f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
