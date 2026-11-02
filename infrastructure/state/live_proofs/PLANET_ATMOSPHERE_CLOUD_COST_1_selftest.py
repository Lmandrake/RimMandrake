#!/usr/bin/env python3
"""Offline selftest of PLANET_ATMOSPHERE_CLOUD_COST_1_live.py: drives main() end to end over planet_atmosphere_cost
with its impure readers stubbed (process sample, mod list, ModsConfig, Player.log, samples file in a tempdir).

Each A1/A2/A3 outcome must be the right one of PASS 0 / FAIL 1 / UNMEASURED 2: a wrong-condition launch defers, a
broken instrument or an unpairable list fails, and only a recorded sample or a real pair passes."""
import contextlib
import datetime as dt
import io
import os
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

    def go(clause):
        before = os.path.getsize(samples) if os.path.exists(samples) else 0
        with contextlib.redirect_stdout(io.StringIO()):
            rc = live.main([clause])
        after = os.path.getsize(samples) if os.path.exists(samples) else 0
        return rc, after > before

    try:
        # load 1: the 'with' list
        stage(WITH)
        check("A3 before any sample is UNMEASURED", go("A3") == (2, False))
        check("A2 on a 'with' launch is UNMEASURED, records nothing", go("A2") == (2, False))
        check("A1 on a 'with' launch PASSES and records", go("A1") == (0, True))
        check("A3 with only the 'with' side is UNMEASURED", go("A3") == (2, False))
        # load 2: the same list minus the mod
        stage(WITHOUT)
        check("A1 on a 'without' launch is UNMEASURED, records nothing", go("A1") == (2, False))
        check("A2 on a 'without' launch PASSES and records", go("A2") == (0, True))
        check("A3 with a true pair PASSES", go("A3")[0] == 0)
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

print("PLANET_ATMOSPHERE_CLOUD_COST_1_selftest: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
