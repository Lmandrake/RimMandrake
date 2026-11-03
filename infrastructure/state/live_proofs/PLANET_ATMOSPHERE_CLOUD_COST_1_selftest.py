#!/usr/bin/env python3
"""Offline selftest of PLANET_ATMOSPHERE_CLOUD_COST_1_live.py: drives main() end to end over planet_atmosphere_cost
with its impure readers stubbed (process sample, mod list, ModsConfig, Player.log, samples file in a tempdir).

Each A1/A2/A3 outcome must be the right one of PASS 0 / FAIL 1 / UNMEASURED 2: a wrong-condition launch defers, a
broken instrument or an unpairable list fails, and only a recorded sample or a real pair passes."""
import contextlib
import datetime as dt
import io
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import PLANET_ATMOSPHERE_CLOUD_COST_1_live as live  # noqa: E402

pac = live.pac
FAILS = []


def check(name, cond):
    if not cond:
        FAILS.append(name)
        print("FAIL " + name)


LOG = "[RimBridge] STARTUP_TIMING phase=tools.construct durationMs=0 elapsedMs=98200\n"
WITH = ["ludeon.rimworld"] + pac.DLC + [pac.PKG]
WITHOUT = [m for m in WITH if m != pac.PKG]
G = 1024 ** 3

with tempfile.TemporaryDirectory() as tmp:
    now = dt.datetime.now(dt.timezone.utc)
    cfg = os.path.join(tmp, "ModsConfig.xml")
    plog = os.path.join(tmp, "Player.log")
    samples = os.path.join(tmp, "out", "samples.jsonl")
    with open(cfg, "w") as fh:
        fh.write("<ModsConfigData/>")
    proc_start = (now - dt.timedelta(seconds=60)).isoformat().replace("+00:00", "Z")
    base_proc = {"running": True, "pid": 7, "start": proc_start, "private": 2 * G, "working": G,
                 "gpu_dedicated": 3 * G, "gpu_shared": 1024 ** 2, "gpu_counters": 2}
    saved = (pac.sample_process, pac.active_mods, pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path)
    pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path = cfg, plog, (lambda: samples)

    def stage(mods, proc=None, log=LOG, cfg_age=-120):
        """One staged launch: what the running game, its list, ModsConfig and Player.log look like."""
        p = dict(base_proc) if proc is None else proc
        pac.sample_process = lambda: dict(p)
        pac.active_mods = lambda: list(mods)
        with open(plog, "w") as fh:
            fh.write(log)
        t = now.timestamp()
        os.utime(cfg, (t + cfg_age, t + cfg_age))
        os.utime(plog, (t, t))

    LAST = {}

    def go(clause):
        before = os.path.getsize(samples) if os.path.exists(samples) else 0
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = live.main([clause])
        LAST["out"] = buf.getvalue()
        after = os.path.getsize(samples) if os.path.exists(samples) else 0
        return rc, after > before

    def last_row():
        with open(samples) as fh:
            return json.loads([l for l in fh if l.strip()][-1])

    try:
        # load 1: the 'with' list
        stage(WITH)
        check("A3 before any sample is UNMEASURED", go("A3") == (2, False))
        check("A2 on a 'with' launch is UNMEASURED, records nothing", go("A2") == (2, False))
        check("A1 on a 'with' launch PASSES and records", go("A1") == (0, True))
        # A1 'recorded': the row holds the launch's own numbers (3 GiB dedicated, 1 MiB shared, 2 GiB private,
        # 98.2 s load), and the SAMPLE line shows them
        r = last_row()
        check("A1 row records the measured numbers",
              (r.get("with"), r.get("load_ms"), r.get("gpu_dedicated_mb"), r.get("gpu_shared_mb"),
               r.get("private_mb")) == (True, 98200, 3072.0, 1.0, 2048.0))
        check("A1 prints its SAMPLE figures",
              "SAMPLE with: load 98.2 s, GPU dedicated 3072.0 MB, shared 1.0 MB, private 2048.0 MB" in LAST["out"])
        check("A3 with only the 'with' side is UNMEASURED", go("A3") == (2, False))
        # load 2: the same list minus the mod, with smaller numbers so every delta is non-zero and known
        stage(WITHOUT, proc=dict(base_proc, gpu_dedicated=2 * G, gpu_shared=0, private=G + G // 2),
              log=LOG.replace("98200", "88200"))
        check("A1 on a 'without' launch is UNMEASURED, records nothing", go("A1") == (2, False))
        check("A2 on a 'without' launch PASSES and records", go("A2") == (0, True))
        r = last_row()
        check("A2 row records the measured numbers",
              (r.get("with"), r.get("load_ms"), r.get("gpu_dedicated_mb"), r.get("gpu_shared_mb"),
               r.get("private_mb")) == (False, 88200, 2048.0, 0.0, 1536.0))
        check("A3 with a true pair PASSES", go("A3")[0] == 0)
        # A3 'prints the load-time and VRAM deltas': the figures themselves, with minus without
        check("A3 prints the load and VRAM deltas",
              re.search(r"^A/B \S+ \(with \S+, without \S+\): load \+10\.0 s \(98\.2 vs 88\.2\), "
                        r"GPU dedicated \+1024\.0 MB, shared \+1\.0 MB, private \+512\.0 MB$",
                        LAST["out"], re.M) is not None)
        # a verdict that exits 0 but prints nothing (or wrong figures) is no A3 pass
        saved_v = pac.verdict
        try:
            pac.verdict = lambda a: 0
            check("A3 rc 0 with no A/B line FAILS", go("A3") == (1, False))
            pac.verdict = lambda a: (print("A/B x (with a, without b): load +0.0 s (1.0 vs 1.0), GPU dedicated "
                                           "+0.0 MB, shared +0.0 MB, private +0.0 MB"), 0)[1]
            check("A3 rc 0 with wrong figures FAILS", go("A3") == (1, False))
        finally:
            pac.verdict = saved_v
        # a record that exits 0 but appends nothing, or a row without its numbers, is no A1/A2 pass
        saved_r = pac.record
        try:
            pac.record = lambda a: (print("SAMPLE with: load 1.0 s, GPU dedicated 1.0 MB, shared 1.0 MB, "
                                          "private 1.0 MB -> x"), 0)[1]
            check("A1 rc 0 that appends no row FAILS", go("A1")[0] == 1)
        finally:
            pac.record = saved_r
        # staging facts defer
        stage(WITH, proc={"running": False})
        check("A1 with no game is UNMEASURED", go("A1") == (2, False))
        stage(WITH, cfg_age=pac.LAUNCH_SLACK_S + 60)
        check("A1 when ModsConfig moved after launch is UNMEASURED", go("A1") == (2, False))
        stage(WITH[:2] + [pac.PKG])
        check("A1 on a list missing DLC is UNMEASURED", go("A1") == (2, False))
        # a broken instrument fails
        stage(WITH, proc=dict(base_proc, gpu_counters=0))
        check("A1 with no GPU counter FAILS", go("A1") == (1, False))
        stage(WITHOUT, log="no timing here\n")
        check("A2 with no STARTUP_TIMING FAILS", go("A2") == (1, False))
        stage(WITH, proc=dict(base_proc, gpu_counters=0), cfg_age=pac.LAUNCH_SLACK_S + 60)
        check("A1 staging + instrument reasons together FAIL", go("A1") == (1, False))
        # A1/A2 are sampled at the MAIN MENU after the load: a launch that has since started or loaded a game
        # (VRAM and private bytes swollen by a map) must never record. Markers are vanilla's own log lines
        # (decomp rw16 Verse/Game.cs InitNewGame, Verse/SavedGameLoaderNow.cs); seen in a real Player-prev.log.
        # Each is a FRESH launch (its own pid) that went straight to a game, so no main-menu row of it exists.
        later = dt.timedelta(hours=2).total_seconds()
        fresh = iter(range(100, 200))
        for marker in ("Initializing new game with mods:\nludeon.rimworld\n",
                       "Loading game from file Colony1 with mods:\nludeon.rimworld\n"):
            for clause, mods in (("A1", WITH), ("A2", WITHOUT)):
                stage(mods, proc=dict(base_proc, pid=next(fresh)), log=LOG + marker)
                os.utime(plog, (now.timestamp() + later, now.timestamp() + later))
                rc, wrote = go(clause)
                check("%s after '%s' (in a game, not at the menu) refuses and records nothing"
                      % (clause, marker.split(" with")[0]), rc in (1, 2) and not wrote)
        # staging records at the main menu, then starts a map; the supervisor's later A1/A2 run sees the game
        # marker. A main-menu row of THIS launch (same pid and start, wanted condition, all numbers) passes it,
        # without writing a second row; anything else stays UNMEASURED, and an instrument FAIL stays FAIL.
        GAME = "Initializing new game with mods:\nludeon.rimworld\n"
        menu = dict(base_proc, pid=500)
        stage(WITH, proc=menu)
        check("staging's main-menu A1 records", go("A1") == (0, True))
        stage(WITH, proc=menu, log=LOG + GAME)
        check("A1 later in a game, with a menu row of this launch, PASSES and writes nothing", go("A1") == (0, False))
        check("A1 rescue prints the menu row's figures",
              "MENU SAMPLE with of this launch (pid 500, start %s)" % proc_start in LAST["out"]
              and "load 98.2 s, GPU dedicated 3072.0 MB, shared 1.0 MB, private 2048.0 MB" in LAST["out"])
        check("A2 in a game on a 'with' launch stays UNMEASURED", go("A2") == (2, False))
        stage(WITH, proc=dict(menu, pid=501), log=LOG + GAME)
        check("A1 in a game, menu row of ANOTHER pid, stays UNMEASURED", go("A1") == (2, False))
        later_start = (now - dt.timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
        stage(WITH, proc=dict(menu, start=later_start), log=LOG + GAME)
        check("A1 in a game, menu row of another start (pid reused), stays UNMEASURED", go("A1") == (2, False))
        stage(WITH, proc=dict(menu, gpu_counters=0), log=LOG + GAME)
        check("A1 instrument FAIL is not rescued by a menu row", go("A1") == (1, False))
        stage(WITH, proc=menu, log=LOG + GAME, cfg_age=pac.LAUNCH_SLACK_S + 60)
        check("A1 in a game with ModsConfig moved since launch is not rescued", go("A1") == (2, False))
        with open(samples, "a") as fh:
            fh.write(json.dumps({"at": "x", "pid": 502, "start": proc_start, "with": False, "mods": WITHOUT,
                                 "dlc_missing": [], "load_ms": 1000, "gpu_dedicated_mb": 1.0,
                                 "gpu_shared_mb": None, "private_mb": 1.0}) + "\n")
        stage(WITHOUT, proc=dict(base_proc, pid=502), log=LOG + GAME)
        check("A2 in a game, menu row missing a number, stays UNMEASURED", go("A2") == (2, False))
        # both sides present, but no pair differing by the mod alone
        os.remove(samples)
        stage(WITH)
        go("A1")
        stage(WITHOUT + ["someone.else"])
        go("A2")
        check("A3 with both sides but no clean pair FAILS", go("A3") == (1, False))
    finally:
        pac.sample_process, pac.active_mods, pac.MODSCONFIG, pac.PLAYER_LOG, pac.samples_path = saved

# the pure classifiers' edges
check("unparsed rc 1 output FAILS", live.classify_record(1, "Traceback ...") == 1)
check("rc other than 0/1 FAILS", live.classify_record(2, "UNMEASURED: this launch is the 'with' condition") == 1)
check("empty reason list FAILS", live.classify_record(1, "UNMEASURED: ") == 1)
check("bad clause name is usage, not a pass", live.main(["A9"]) == 3)
ok = {"with": True, "load_ms": 1000, "gpu_dedicated_mb": 5.0, "gpu_shared_mb": 1.0, "private_mb": 2.0}
okline = "SAMPLE with: load 1.0 s, GPU dedicated 5.0 MB, shared 1.0 MB, private 2.0 MB -> p\n"
check("recorded_ok accepts a matching row", live.recorded_ok(okline, [ok], "with"))
check("recorded_ok refuses a row missing a number", not live.recorded_ok(okline, [dict(ok, gpu_shared_mb=None)], "with"))
check("recorded_ok refuses a row whose numbers the line does not show",
      not live.recorded_ok(okline, [dict(ok, gpu_dedicated_mb=6.0)], "with"))
check("recorded_ok refuses the wrong condition", not live.recorded_ok(okline, [ok], "without"))
mrow = {"pid": 9, "start": "s", "with": True, "mods": WITH, "dlc_missing": [], "load_ms": 1000,
        "gpu_dedicated_mb": 5.0, "gpu_shared_mb": 1.0, "private_mb": 2.0}
mproc = {"running": True, "pid": 9, "start": "s"}
check("menu_row_ok accepts this launch's row", live.menu_row_ok(mrow, mproc, WITH, "with"))
check("menu_row_ok refuses a stopped game", not live.menu_row_ok(mrow, {"running": False}, WITH, "with"))
check("menu_row_ok refuses a stopped game even at the same pid/start",
      not live.menu_row_ok(mrow, dict(mproc, running=False), WITH, "with"))
check("menu_row_ok refuses a row whose own condition flag is the other one",
      not live.menu_row_ok(dict(mrow, **{"with": False}), mproc, WITH, "with"))
check("menu_row_ok refuses another list", not live.menu_row_ok(mrow, mproc, WITH + ["x.y"], "with"))
check("menu_row_ok refuses the wrong condition", not live.menu_row_ok(mrow, mproc, WITH, "without"))
check("menu_row_ok refuses a row missing DLC", not live.menu_row_ok(dict(mrow, dlc_missing=["d"]), mproc, WITH, "with"))
check("menu_row_ok refuses a row with no mods", not live.menu_row_ok(dict(mrow, mods=None), mproc, WITH, "with"))
check("only_in_a_game: the marker alone", live.only_in_a_game("UNMEASURED: a game was started after the load: x\n"))
check("only_in_a_game: marker plus ModsConfig moved is not rescued",
      not live.only_in_a_game("UNMEASURED: ModsConfig.xml written 900 s after launch; a game was started after the load\n"))
check("only_in_a_game: no UNMEASURED line", not live.only_in_a_game("SAMPLE with: ...\n"))
check("classify_verdict rc 0 with no output FAILS", live.classify_verdict(0, [], "") == 1)

print("PLANET_ATMOSPHERE_CLOUD_COST_1_selftest: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
