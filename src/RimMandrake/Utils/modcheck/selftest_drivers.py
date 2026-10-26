#!/usr/bin/env python3
"""Selftest for modcheck/drivers.py and its wiring (TESTQ_SWEEP_WIRE_FLOWWORKS_DRIVERS, RIVER_CHAINS_WIRE_SWEEP_TO_RIVER_SITE).
Offline: no game, no bridge; every driver call goes to a fake.

Reds on: a driver running with MODCHECK_RUN_DRIVERS unset, or without UTF-8 stdio; a driver for an unselected chain running, or table order
not kept; a timeout or a raising after-hook crashing instead of being a receipt; the shared budget not skipping; a
"chain"-stage driver running up front or more than once; `modcheck run --drivers on` not setting the flag; the
SteveDesktop worker's run command not passing `--drivers on`; FlowWorks naming a driver script that does not exist, a
chain that is not in its suite, or leaving a driver-reading chain (thirst, sprinklers, drawbridges, lines,
core_live_rows, hose_live_rows, the live_session bars, trench, suspension) with no driver; T15R (needs a saved site
SteveDesktop does not have) in thirst_live's argv; the river chains (works, current, swept, placer) not settling the
river site once, before the first of them, under the flag -- or settling it with the flag off, or when the offline
declaration probe (targeting.catalogue) walks them.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(UTILS)))
FW = os.path.join(os.path.dirname(UTILS), "FlowWorks")
for _p in (os.path.join(FW, "northstar"), FW, UTILS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import drivers as D  # noqa: E402

FAILS = []


def ok(cond, msg):
    print("%s %s" % ("PASS" if cond else "FAIL", msg))
    if not cond:
        FAILS.append(msg)


class _S(object):
    pass


def _suite():
    s = _S()
    s.live_drivers = [
        {"name": "a", "script": "ns/a.py", "args": ["--x", 1], "chains": ["c1"], "timeout_s": 50},
        {"name": "b", "script": "ns/b.py", "chains": ["c2", "c3"]},
        {"name": "r", "script": "ns/r.py", "chains": ["c9"], "stage": "chain"},
    ]
    return s


def _fake(calls, rc=0):
    def f(argv, cwd, timeout_s):
        calls.append((argv, timeout_s))
        return rc, "out"
    return f


class _Null(object):
    def write(self, *_):
        pass

    def flush(self):
        pass


def t_flag_and_plan():
    os.environ.pop(D.ENV, None)
    calls = []
    ok(D.run(_suite(), "/m", ["c1", "c2"], _call_fn=_fake(calls), log=_Null()) == [] and not calls,
       "flag off: no driver runs")
    ok([d["name"] for d in D.plan(_suite(), ["c3", "c1"])] == ["a", "b"], "plan keeps table order, selects by chain")
    ok([d["name"] for d in D.plan(_suite(), ["c2"])] == ["b"], "plan leaves an unselected chain's driver out")
    ok(D.plan(_suite(), ["c9"]) == [], "a chain-stage driver is never planned up front")
    d = {"name": "l", "script": "x.py", "args": ["--a", "1", "--log", D.PLAYER_LOG_TOKEN, "--b"]}
    ok(D._argv("/m", d, "py", _log=lambda: "C:/P.log")[2:] == ["--a", "1", "--log", "C:/P.log", "--b"],
       "@player_log becomes this machine's Player.log")
    ok(D._argv("/m", d, "py", _log=lambda: None)[2:] == ["--a", "1", "--b"], "no Player.log: the --log pair is dropped")
    os.environ[D.ENV] = "1"
    try:
        calls = []
        recs = D.run(_suite(), "/m", ["c1"], _call_fn=_fake(calls), python="py", log=_Null())
        ok(len(calls) == 1 and calls[0][0] == ["py", os.path.join("/m", "ns/a.py"), "--x", "1"] and calls[0][1] == 50,
           "flag on: the selected driver runs with its argv and timeout")
        ok(recs and recs[0]["status"] == "RC0" and recs[0]["driver"] == "a", "receipt status RC0")
        recs = D.run(_suite(), "/m", ["c1"], _call_fn=lambda a, c, t: (None, "hung"), log=_Null())
        ok(recs[0]["status"] == "TIMEOUT" and recs[0]["rc"] is None, "a timeout is a TIMEOUT receipt")
        recs = D.run(_suite(), "/m", ["c1"], _call_fn=_fake([], rc=3), log=_Null())
        ok(recs[0]["status"] == "FAILED" and recs[0]["rc"] == 3, "rc 3 is a FAILED receipt")

        def boom(_r):
            raise RuntimeError("no map")
        recs = D.run(_suite(), "/m", ["c1", "c2"], after=boom, _call_fn=_fake([]), log=_Null())
        ok(len(recs) == 2 and all("no map" in r.get("after_error", "") for r in recs), "a raising after-hook is recorded")
        recs = D.run(_suite(), "/m", ["c1", "c2"], budget_s=30, _call_fn=_fake([]), log=_Null())
        ok([r["status"] for r in recs] == ["SKIPPED_BUDGET", "SKIPPED_BUDGET"], "a spent budget skips the drivers")
        calls = []
        recs = D.run(_suite(), "/m", ["c1"], budget_s=100, _call_fn=_fake(calls), log=_Null())
        ok(calls and calls[0][1] <= 100, "a driver's timeout is capped by the budget left")
        calls = []
        r1 = D.once("/m", _suite().live_drivers[2], _call_fn=_fake(calls), log=_Null())
        r2 = D.once("/m", _suite().live_drivers[2], _call_fn=_fake(calls), log=_Null())
        ok(len(calls) == 1 and r1 is r2, "a chain-stage driver runs once per process")
    finally:
        os.environ.pop(D.ENV, None)
    ok(D.once("/m2", _suite().live_drivers[2], _call_fn=_fake([]), log=_Null()) is None, "once() with the flag off: None")


def t_call_utf8():
    # a driver's stdout is a pipe: Windows python.exe then encodes print() as cp1252 and a non-ASCII char kills the
    # phase (SteveDesktop J20261026T060806Z-63c715: v2 J_jobs_scheduler_crash UnicodeEncodeError 'charmap')
    import subprocess
    seen = {}
    real = subprocess.run

    def fake(argv, **kw):
        seen.update(kw.get("env") or {})
        return subprocess.CompletedProcess(argv, 0, "", "")
    subprocess.run = fake
    try:
        D._call(["py", "x.py"], "/m", 5)
    finally:
        subprocess.run = real
    ok(seen.get("PYTHONIOENCODING") == "utf-8" and seen.get("PYTHONUTF8") == "1",
       "a driver runs with UTF-8 stdio (PYTHONIOENCODING, PYTHONUTF8)")


def t_cli_flag():
    import cli  # noqa: E402
    src = open(cli.__file__, encoding="utf-8").read()
    ok('"--drivers"' in src and "drivers.ENV" in src, "cli has --drivers and sets drivers.ENV")
    rsrc = open(os.path.join(HERE, "runner.py"), encoding="utf-8").read()
    ok("_DRV.run(" in rsrc and 'summary["drivers"]' in rsrc, "runner.run runs the drivers and records the receipts")


def t_worker_passes_flag():
    p = os.path.join(ROOT, "infrastructure", "stevedesktop", "worker.py")
    spec = importlib.util.spec_from_file_location("steve_worker_probe", p)
    w = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(w)
    ok("--drivers on" in getattr(w, "RUN_BASE", ""), "SteveDesktop worker run command passes --drivers on")
    ok("MODCHECK_DRIVERS_BUDGET_S=1350 " in w.driver_budget_export(2700)
       and "MODCHECK_DRIVERS_BUDGET_S=7200 " in w.driver_budget_export(14400),
       "the driver budget is half the job timeout, capped at 7200 s")


def _fw_suite():
    spec = importlib.util.spec_from_file_location("modcheck_validation_FlowWorks_probe", os.path.join(FW, "validation.py"))
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    return v


def t_flowworks_table():
    v = _fw_suite()
    s = v.suite
    names = {n for n, _ in s.chains}
    table = getattr(s, "live_drivers", None) or []
    ok(len(table) >= 9, "FlowWorks suite.live_drivers has the drivers (%d)" % len(table))
    for d in table:
        ok(os.path.isfile(os.path.join(FW, d["script"])), "driver script exists: %s" % d["script"])
        for c in d.get("chains") or ():
            ok(c in names, "driver %s chain %s is in the suite" % (d["name"], c))
    covered = {c for d in table for c in d.get("chains") or ()}
    for c in ("thirst", "sprinklers", "drawbridges", "lines", "core_live_rows", "hose_live_rows", "limitless_endless",
              "pit_access_gear_ladders", "pit_travel_fly_jump_float", "trench_cover_and_raiders",
              "suspension_bridges_and_covers", "player_missions", "works", "current", "swept", "placer"):
        ok(c in covered, "chain %s has a driver" % c)
    scripts = {os.path.basename(d["script"]) for d in table}
    for _bar, (_rows, script, _w) in v.DRIVER_BAR_ROWS.items():
        ok(script in scripts, "DRIVER_BAR_ROWS driver %s is in the table" % script)
    for script in set(v.DRIVER_OF.values()):
        ok(script in scripts, "DRIVER_OF driver %s is in the table" % script)
    th = [d for d in table if d["name"] == "thirst_live"]
    ok(th and "T15R" not in " ".join(str(a) for a in th[0].get("args") or []), "thirst_live leaves T15R out")
    riv = [d for d in table if d.get("stage") == "chain"]
    ok(len(riv) == 1 and os.path.basename(riv[0]["script"]) == "river_site.py", "the river site is the one chain-stage driver")
    return v, riv[0] if riv else None


def t_river_wrapper():
    v, riv = _fw_suite(), None
    riv = [d for d in v.suite.live_drivers if d.get("stage") == "chain"][0]
    fns = dict(v.suite.chains)
    calls = []
    real = D._call
    D._call = _fake(calls)
    D._DONE.clear()

    class _T(object):
        def _guard(self):
            return False      # the chain body stops at its guard: no game is touched

        def __getattr__(self, name):
            return lambda *a, **k: None
    try:
        os.environ.pop(D.ENV, None)
        for c in ("works", "current"):
            try:
                fns[c](_T())
            except Exception:   # noqa: BLE001 - the body's own reaction to a fake context is not under test
                pass
        ok(not calls, "flag off: river chains do not settle the river site")
        os.environ[D.ENV] = "1"
        import suite as _SU  # noqa: E402
        for c in ("works", "current"):     # targeting.catalogue() walks every chain with this probe, offline
            try:
                fns[c](_SU._DeclarationProbe())
            except Exception:   # noqa: BLE001
                pass
        ok(not calls, "flag on: the offline declaration probe does not settle the river site (%d calls)" % len(calls))
        for c in ("works", "current", "swept", "placer"):
            try:
                fns[c](_T())
            except Exception:   # noqa: BLE001
                pass
        ok(len(calls) == 1 and calls[0][0][1].endswith("river_site.py"),
           "flag on: the first river chain settles the river site, once (%d calls)" % len(calls))
    finally:
        D._call = real
        os.environ.pop(D.ENV, None)
        D._DONE.clear()


def t_steam_chain_on_river_site():
    """RIVER_CHAINS_WIRE_SWEEP_TO_RIVER_SITE: toggle_river_steam's biome-gate half needs a river map, so it settles the river
    site too, and runs AFTER every non-river chain (the site replaces the map for whatever follows)."""
    v = _fw_suite()
    riv = [d for d in v.suite.live_drivers if d.get("stage") == "chain"][0]
    ok("toggle_river_steam" in riv["chains"], "toggle_river_steam is a river-site chain")
    names = [n for n, _f in v.suite.chains]
    ok("toggle_river_steam" in names, "toggle_river_steam is still registered")
    if "toggle_river_steam" in names:
        non_river = [i for i, n in enumerate(names) if n not in riv["chains"]]
        ok(names.index("toggle_river_steam") > max(non_river), "toggle_river_steam runs after every non-river chain")


def main():
    for t in (t_flag_and_plan, t_call_utf8, t_cli_flag, t_worker_passes_flag, t_flowworks_table, t_river_wrapper, t_steam_chain_on_river_site):
        try:
            t()
        except Exception as ex:     # noqa: BLE001 - one broken test must not hide the others
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(ex).__name__, ex))
    print("\nSELFTEST %s -- %d failed" % ("FAILED" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
