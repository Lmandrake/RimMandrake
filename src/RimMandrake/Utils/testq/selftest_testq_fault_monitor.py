#!/usr/bin/env python3
"""selftest_testq_fault_monitor.py - fault_monitor.py and its gate in ingest.py (STEVE_FAULT_MONITOR_ONSET_BEFORE_RESULTS).

No ssh, no game: the machine is replaced by a fake with a log, a boot and a worker. Proves: the onset is timed from the last
clean cycle, a clean cycle after it closes nothing, only a new boot does; history backfills itself; a result in a window is
quarantined, one with no clean cycle read since it finished is held, one after a clean cycle counts; the whole round
onset -> pause -> drain -> one reboot -> two clean cycles -> resume; a fault back at once is STUCK, not a reboot loop; a
foreign pause holds the reboot and a red canary inside the window does not; ingest writes no verdict from a window,
notes what it already wrote and queues the item job again; `check` fails on what it says it fails on, and the formats
the parser reads are the ones watch2.ps1 writes. Heat (STEVE_HEAT_MEASURE_BEFORE_THE_SCREWDRIVER): the sampler's line on a
CYCLE parses, a window says how hot the boot ran before its onset, a pre-sampler line is no reading (not cool), a
heat=UNMEASURED cycle fails check, and stevetemp.cs prints the format HEAT_RE reads.
"""
import json
import os
import subprocess
import sys
import tempfile
import shutil
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
sys.path.insert(0, HERE)
import fault_monitor as FM  # noqa: E402

T, S = FM.T, FM.S
FAILS = []
ITEM = "SOME_ITEM_FIX_IT"
BOOT = "2026-11-03 19:59:21"
BOOT_S = FM.epoch(BOOT)


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def start(boot=BOOT):
    return "%sZ WATCH START boot=%sZ logical_cpus=18 cycle=300s per-cpu core check 4s each" % (FM.stamp(FM.epoch(boot) + 90).replace("T", " ").rstrip("Z"), boot)


def cyc(minutes, bad=(), boot=BOOT):
    t = FM.epoch(boot) + minutes * 60
    return "%sZ CYCLE uptime_h=%.2f bad_cpus=[%s] n_ok=%d" % (FM.stamp(t).replace("T", " ").rstrip("Z"), minutes / 60.0, ",".join(map(str, bad)), 18 - len(bad))


def at(minutes, boot=BOOT):
    return FM.stamp(FM.epoch(boot) + minutes * 60)


def analyse_checks():
    a = FM.analyse([start(), cyc(5), cyc(10)])
    check(not a["windows"] and a["open"] is None and a["clean_through"] == BOOT_S + 600 and a["clean_cycles"] == 2, "clean cycles: no window, clean through the last one")
    a = FM.analyse([start(), cyc(5), cyc(170), cyc(175, [0]), cyc(180), cyc(185, [2, 8])])
    w = a["open"]
    check(w and w["start"] == at(170) and w["first_bad"] == at(175) and w["first_cpus"] == [0], "the onset runs from the last clean cycle to the first bad one")
    check(w["end"] is None and w["clean_after"] == 1 and w["bad_cycles"] == 2 and a["clean_through"] is None, "a clean cycle after the onset closes nothing")
    check(w["cpus"] == {"0": 1, "2": 1, "8": 1} and abs(w["onset_uptime_h"] - 175 / 60.0) < 0.01, "CPUs and uptime at onset are kept")
    b2 = "2026-11-04 03:00:00"
    a2 = FM.analyse([start(), cyc(175, [0]), start(b2), cyc(5, boot=b2)])
    check(a2["windows"][0]["end"] == FM.stamp(FM.epoch(b2)) and a2["open"] is None and a2["clean_cycles"] == 1 and a2["clean_through"] == FM.epoch(b2) + 300, "a new boot closes the window, its clean cycle counts")
    a3 = FM.analyse([start(), cyc(5, [3])])
    check(a3["open"]["start"] == FM.stamp(BOOT_S), "bad at the first cycle: the window starts at the boot")
    a4 = FM.analyse([start(), cyc(175, [0])], live_boot=FM.epoch(b2))
    check(a4["open"] is None and a4["windows"][0]["end"] == FM.stamp(FM.epoch(b2)) and a4["clean_cycles"] == 0, "the machine's own newer boot closes it before any watch line")
    a5 = FM.analyse([cyc(60), "junk line", start()])
    check(a5["unparsed"] == 1 and a5["clean_cycles"] == 1, "a line not understood is counted; a cycle with no start line gets its boot from its uptime")
    a7 = FM.analyse([cyc(60, [3])], live_boot=BOOT_S + 30)
    check(a7["open"] is not None, "a machine boot within rounding of the inferred one is the same boot: the window stays open")
    a6 = FM.analyse([start(), start(), cyc(5), start(), cyc(10)])
    check(a6["clean_cycles"] == 2, "a restarted watcher on the same boot is the same boot")
    with open(os.path.join(HERE, "..", "steve_cpu_retest", "watch2.ps1"), encoding="utf-8") as f:
        ps1 = f.read()
    check("CYCLE uptime_h=$up bad_cpus=[$($fails -join ',')]" in ps1 and "WATCH START boot=" in ps1 and "CONTROL inject_exit=$ia clean_exit=$ic" in ps1, "the formats parsed are the ones watch2.ps1 writes")
    check("ToUniversalTime().AddMinutes" not in FM.SNAPSHOT_PS and "probe:" in FM.SNAPSHOT_PS, "the snapshot asks the event log in local time, and says the log can be seen")
    c = FM.analyse(["2026-11-03 20:00:00Z CONTROL inject_exit=1 clean_exit=0"])["control"]
    check(c["ok"], "a control with an injected fault seen is ok")
    check(not FM.analyse(["2026-11-03 20:00:00Z CONTROL inject_exit=0 clean_exit=0"])["control"]["ok"], "a control that misses it is not")


def hcyc(minutes, core, bad=(), pkg=None, boot=BOOT):
    pkg = core - 3 if pkg is None else pkg
    return cyc(minutes, bad, boot) + " exits=[] pkg_c=%d/%d core_max_c=%d hot_core=4 cores_max_c=[%d,%d] samples=150 vcore_v=1.298" % (
        pkg - 10, pkg, core, core - 5, core)


def heat_checks(tmp):
    h = FM.heat_of(hcyc(5, 71))
    check(h == {"pkg0": 58, "pkg": 68, "core": 71, "hot": 4, "cores": [66, 71], "vcore": 1.298}, "the sampler's line on a CYCLE parses")
    check("vcore" not in FM.heat_of(hcyc(5, 71).replace(" vcore_v=1.298", "")), "vcore is optional: a board that does not report it still gives heat")
    check(FM.heat_of(cyc(5) + " exits=[] heat=UNMEASURED(pawnio_not_installed)") == {"unmeasured": "pawnio_not_installed"},
          "heat=UNMEASURED parses with its reason")
    check(FM.heat_of(cyc(5)) is None, "a line from before the sampler carries no reading")
    a = FM.analyse([start(), cyc(5), hcyc(60, 60), hcyc(110, 70), hcyc(150, 84), hcyc(170, 88), hcyc(175, 91, [0]), hcyc(180, 60)])
    w = a["windows"][0]["heat"]
    check(w["at_onset"] == 91 and w["last_clean"] == 88 and w["pre_max"] == 88 and w["boot_max_before"] == 88,
          "a window says the hottest core at onset, at the last clean cycle, in the hour before and over the boot")
    check(w["cycles_measured_before"] == 4 and w["cycles_before"] == 5 and w["pre_mean"] == 86.0,
          "the pre-sampler cycle is not averaged in as cool; the hour before is the hour before")
    check("91 C" in FM.heat_line(w) and "hour before: max 88 C" in FM.heat_line(w), "report's heat line carries the numbers")
    old = FM.analyse([start(), cyc(170), cyc(175, [0])])["windows"][0]["heat"]
    check(FM.heat_line(old).startswith("UNMEASURED") and FM.heat_line(None).startswith("UNMEASURED"),
          "a window with no reading says UNMEASURED, never a temperature")
    b2 = "2026-11-04 03:00:00"
    a2 = FM.analyse([start(), hcyc(170, 80), hcyc(175, 92, [0]), start(b2), hcyc(5, 50, boot=b2), hcyc(10, 54, boot=b2)])
    b = a2["boots"]
    check(len(b) == 2 and b[0]["onset_uptime_h"] == round(175 / 60.0, 2) and b[0]["core_max"] == 92
          and b[1]["onset_uptime_h"] is None and b[1]["core_max"] == 54 and b[1]["vcore_max"] == 1.298 and b[1]["core_median"] == 54 and b[1]["measured"] == 2,
          "one heat row per boot: how hot it ran and when (or whether) it faulted, for the open-case comparison")
    check(a2["last_heat"]["core"] == 54, "the newest cycle's reading is kept for check")
    saved = T.QHOME
    T.QHOME = tempfile.mkdtemp(dir=tmp)
    try:
        T.ensure_dirs()
        st = {"at": FM.stamp(BOOT_S), "phase": "CLEAN", "last_heat": {"unmeasured": "sampler_hung"}}
        T.S.dump(st, T.q("fault_state.json"))
        check(FM.check(now=BOOT_S + 60) == 1, "check fails when the newest cycle says heat=UNMEASURED")
        T.S.dump(dict(st, last_heat=None), T.q("fault_state.json"))
        check(FM.check(now=BOOT_S + 60) == 0, "a cycle with no heat field (pre-sampler) does not fail check")
        T.S.dump(a2["boots"], T.q("fault_heat.json"))
        check(FM.heat() == 0, "the heat table prints from fault_heat.json")
        # report() itself prints each window's heat line (the blind check's mutant deleted that print and stayed green).
        hot = dict(a["windows"][0], id="W_HOT")
        cold = dict(FM.analyse([start(), cyc(170), cyc(175, [0])])["windows"][0], id="W_COLD")
        T.S.dump([hot, cold], T.q("fault_windows.json"))
        T.S.dump(dict(st, phase="CLEAN"), T.q("fault_state.json"))
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = FM.report()
        lines = buf.getvalue().splitlines()
        heat_rows = [ln.strip() for ln in lines if ln.strip().startswith("heat: ")]
        check(rc == 0 and len(heat_rows) == 2 and "hottest core at onset 91 C" in heat_rows[0]
              and "last clean cycle 88 C" in heat_rows[0] and heat_rows[1].startswith("heat: UNMEASURED"),
              "report prints every window's heat line: the onset temperature for a heated window, UNMEASURED for an old one")
        hot_i = next((i for i, ln in enumerate(lines) if ln.startswith("W_HOT")), None)
        cold_i = next((i for i, ln in enumerate(lines) if ln.startswith("W_COLD")), None)
        check(hot_i is not None and cold_i is not None
              and any("91 C" in ln for ln in lines[hot_i:cold_i]) and not any("91 C" in ln for ln in lines[cold_i:]),
              "the heat line sits under its own window, not another's")
    finally:
        T.QHOME = saved
    with open(os.path.join(HERE, "..", "steve_cpu_retest", "stevetemp.cs"), encoding="utf-8") as f:
        cs = f.read()
    check('"pkg_c={0:0}/{1:0} core_max_c={2:0} hot_core={3} cores_max_c=[{4}] samples={5}"' in cs and '" vcore_v={0:0.000}"' in cs
          and 'StartsWith("CPU Core #"' in cs
          and '"heat=UNMEASURED(' in cs, "stevetemp.cs prints the format HEAT_RE reads")
    with open(os.path.join(HERE, "..", "steve_cpu_retest", "watch2.ps1"), encoding="utf-8") as f:
        ps1 = f.read()
    check("exits=[$($rcs -join ',')] $heat\"" in ps1 and "$heat='heat=UNMEASURED(no_sampler)'" in ps1,
          "watch2.ps1 ends every CYCLE with the sampler's line or heat=UNMEASURED")
    live_fixture_checks()


# Verbatim lines 360-374 of SteveDesktop's fault_watch.log (mirror D:\ClaudeWork\rimmandrake\testq\fault_watch.log),
# copied 2026-11-04 after deploy-heat (PawnIO + LibreHardwareMonitor stevetemp.exe): the live evidence, committed so a
# checker without the D: mirror or ssh can see the machine really logs core temperatures each cycle.
LIVE_FIXTURE = os.path.join(HERE, "fixtures", "steve_fault_watch_heat_2026-11-04.log")


def live_fixture_checks():
    with open(LIVE_FIXTURE, encoding="utf-8") as f:
        lines = f.read().splitlines()
    cycles = [ln for ln in lines if " CYCLE " in ln]
    heated = [(ln, FM.heat_of(ln)) for ln in cycles if FM.heat_of(ln)]
    check(len(cycles) >= 10 and all(h is None for h in map(FM.heat_of, cycles[:8])),
          "live fixture: the cycles before deploy-heat carry no reading")
    check(len(heated) >= 3 and all("core" in h and 20 <= h["core"] <= 105 and 20 <= h["pkg"] <= 105
                                   and len(h["cores"]) >= 8 and max(h["cores"]) == h["core"] for _, h in heated),
          "live fixture: every CYCLE after deploy-heat on SteveDesktop carries numeric package and per-core temperatures")
    check([ln[:20] for ln, _ in heated] == ["2026-11-04 03:45:56Z", "2026-11-04 03:50:57Z", "2026-11-04 04:00:11Z"]
          and heated[0][1]["core"] == 67 and heated[0][1]["hot"] == 7 and heated[0][1]["vcore"] == 1.301,
          "live fixture: the first heated cycle is CPU 2 faulting at a 67 C hottest core (core 7), vcore 1.301 V")
    a = FM.analyse(lines)
    check(a["last_heat"] and a["last_heat"]["core"] == 65 and a["unparsed"] == 0,
          "live fixture: analyse keeps the newest real reading for check, and parses every line")
    b = a["boots"]
    check(len(b) == 2 and b[0]["core_max"] == 67 and b[0]["measured"] == 2 and b[0]["onset_uptime_h"] == 0.96
          and b[1]["core_max"] == 65 and b[1]["onset_uptime_h"] is None,
          "live fixture: one heat row per real boot (the faulting boot ran to 67 C, the fresh boot clean at 65 C)")
    w = a["windows"][0]["heat"]
    check(w["at_onset"] is None and w["cycles_measured_before"] == 0 and FM.heat_line(w).startswith("UNMEASURED"),
          "live fixture: the 03:43 fault began before the sampler, so its window says UNMEASURED, never a guess")


def rec(started, finished, item=None, host="stevedesktop", ingested=None, jid=None):
    job = S.make_job("Mock", {"rows": ["r1"]}, "fix", "BENCH", "abc1234", item=item)
    if jid:
        job["id"] = jid
    res = {"schema": S.RESULT_SCHEMA, "job": job["id"], "attempt": job["id"] + ".a1", "outcome": "DONE", "cause": None, "host": host,
           "rows": [{"chain": "c1", "row": "r1", "verdict": "PASS", "detail": ""}], "counts": {"PASS": 1}, "runner_sha": "def5678",
           "started": started, "finished": finished, "artifacts": [{"path": "/x/Mock_1.json"}], "note": ""}
    out = {"job": job, "result": res, "attempts": [res["attempt"]], "finished": finished}
    if ingested:
        out["ingested"] = ingested
    return out


def gate_checks():
    saved_home = FM.T.QHOME
    FM.T.QHOME = tempfile.mkdtemp(prefix="rf_gate_")     # never the live fault_advisory.json
    try:
        _gate_checks()
        _advisory_checks()
    finally:
        shutil.rmtree(FM.T.QHOME, ignore_errors=True)
        FM.T.QHOME = saved_home


def _advisory_checks():
    a = FM.analyse([start(), cyc(170), cyc(175, [0])])
    w, now, st = a["windows"], BOOT_S + 3600 * 8, {"clean_through_s": None}
    r = rec(at(172), at(180))
    check(not FM.advisory() and FM.gate(r, w, st, now)[0] == "quarantine", "default (no switch file): still quarantines")
    path = FM.T.q(FM.ADVISORY_FILE)
    S_ = FM.S
    S_.dump({"advisory": False}, path)
    check(FM.gate(r, w, st, now)[0] == "quarantine", "switch file with advisory false: still quarantines")
    S_.dump({"advisory": True}, path)
    v, why = FM.gate(r, w, st, now)
    check(v == "count" and why == "advisory: " + w[0]["id"], "advisory ON: an in-window result is counted and names its window (got %s %s)" % (v, why))
    check(FM.gate(rec(at(172), at(180), host="archmagi"), w, st, now) == ("count", None), "advisory ON: Archmagi unaffected")
    for d in ("quarantined", "done"):
        os.makedirs(FM.T.q(d), exist_ok=True)
    for jid in ("J20261112T000000Z-aaaaaa", "J20261111T000000Z-bbbbbb"):
        FM.S.dump(dict(rec(at(172), at(180), jid=jid), quarantined={"window": "FX"}), FM.T.q("quarantined", jid + ".json"))
    FM.release(type("A", (), {"prefix": "J20261112"})())
    got = FM.T.read_json(FM.T.q("done", "J20261112T000000Z-aaaaaa.json")) or {}
    check(got.get("fault_window", {}).get("id") == "FX" and "quarantined" not in got and got.get("was_quarantined"), "release: record back in done/ carrying its window id")
    check(os.path.exists(FM.T.q("quarantined", "J20261111T000000Z-bbbbbb.json")), "release: other prefixes stay quarantined")
    os.remove(path)
    check(FM.release(type("A", (), {"prefix": "J"})()) == 1, "release refuses with the switch off")


def periodic_checks():
    """advisory + reboot_every_h: old boot -> pause, drain, reboot once, resume only after a NEW boot answers; never mid-job."""
    saved = (FM.T.QHOME, FM.worker_busy, FM.reboot, FM.T.steve_running, FM.T.paused, FM.T.cmd_pause, FM.T.cmd_resume)
    FM.T.QHOME = tempfile.mkdtemp(prefix="rf_pr_")
    log, box = [], {"pz": None, "running": [True], "busy": True}
    try:
        FM.S.dump({"advisory": True, "reboot_every_h": 12}, FM.T.q(FM.ADVISORY_FILE))
        FM.worker_busy = lambda: box["busy"]
        FM.reboot = lambda why: (log.append("reboot") or True, "")
        FM.T.steve_running = lambda: box["running"]
        FM.T.paused = lambda host=None: box["pz"]
        FM.T.cmd_pause = lambda a: box.update(pz={"reason": a.reason}) or log.append("pause")
        FM.T.cmd_resume = lambda a: box.update(pz=None) or log.append("resume")
        st, B = {}, 1000000
        young = {"boot": B}
        FM.periodic_reboot(st, young, B + 11 * 3600)
        check(not log and not st.get("pr"), "periodic: a boot younger than reboot_every_h is left alone")
        old = {"boot": B}
        FM.periodic_reboot(st, old, B + 13 * 3600)
        check(log == ["pause"] and st["pr"]["state"] == "DRAIN", "periodic: an old boot pauses the lane")
        for _ in range(3):
            FM.periodic_reboot(st, old, B + 13 * 3600 + 60)
        check("reboot" not in log, "periodic: never reboots while a job runs")
        box.update(running=[], busy=False)
        for _ in range(3):
            FM.periodic_reboot(st, old, B + 13 * 3600 + 120)
        check(log.count("reboot") == 1 and st["pr"]["state"] == "WAIT_BOOT", "periodic: reboots once, between jobs")
        FM.periodic_reboot(st, old, B + 13 * 3600 + 600)
        check("resume" not in log, "periodic: no resume until a new boot is seen")
        FM.periodic_reboot(st, {"boot": B + 13 * 3600 + 400}, B + 13 * 3600 + 900)
        check(log[-1] == "resume" and not st["pr"]["state"], "periodic: new boot answering resumes the lane")
        os.remove(FM.T.q(FM.ADVISORY_FILE))
        log.clear()
        FM.periodic_reboot({}, old, B + 99 * 3600)
        check(not log, "periodic: without the advisory switch nothing is scheduled (default unchanged)")
    finally:
        shutil.rmtree(FM.T.QHOME, ignore_errors=True)
        (FM.T.QHOME, FM.worker_busy, FM.reboot, FM.T.steve_running, FM.T.paused, FM.T.cmd_pause, FM.T.cmd_resume) = saved


def _gate_checks():
    a = FM.analyse([start(), cyc(170), cyc(175, [0]), start("2026-11-04 03:00:00")])
    w, now = a["windows"], BOOT_S + 3600 * 8
    st = {"clean_through_s": BOOT_S + 170 * 60}
    check(FM.gate(rec(at(160), at(172)), w, st, now)[0] == "quarantine", "ending inside the window: quarantine")
    check(FM.gate(rec(at(172), at(180)), w, st, now)[0] == "quarantine", "wholly inside: quarantine")
    check(FM.gate(rec(at(160), at(170)), w, st, now)[0] == "count", "finished at the last clean cycle: it counts")
    check(FM.gate(rec("2026-11-04T03:10:00Z", "2026-11-04T03:20:00Z"), w, {"clean_through_s": FM.epoch("2026-11-04 03:25:00")}, now)[0] == "count", "after the reboot, with a clean cycle since: counts")
    r = rec("2026-11-04T03:10:00Z", "2026-11-04T03:20:00Z")
    check(FM.gate(r, w, {"clean_through_s": FM.epoch("2026-11-04 03:15:00")}, FM.epoch("2026-11-04 03:21:00"))[0] == "hold", "no clean cycle since it finished: held")
    v, why = FM.gate(r, w, {"clean_through_s": None}, FM.epoch("2026-11-04 03:20:00") + FM.HOLD_S)
    check(v == "count" and "unguarded" in why, "a dead canary holds a result only so long, and says so")
    check(FM.gate(rec(at(172), at(180), host="archmagi"), w, st, now)[0] == "count", "Archmagi's results are not this fault's")
    check(FM.gate(rec(at(172), at(180)), w, None, now)[0] == "count", "no monitor on this queue: nothing changes")
    openw = FM.analyse([start(), cyc(170), cyc(175, [0])])["windows"]
    check(FM.gate(rec(at(300), at(310)), openw, {"clean_through_s": None}, now)[0] == "quarantine", "an open window runs on until the reboot")


class Machine:
    """The fake SteveDesktop."""

    def __init__(self):
        self.boot, self.lines, self.up = BOOT_S, [start()], True
        self.busy, self.snaps, self.reboots = False, 0, 0

    def install(self):
        FM.steve_read = lambda: {"boot": self.boot, "cpus": 18, "rimworld": 1, "lines": list(self.lines)} if self.up else None
        FM.worker_busy = lambda: self.busy
        FM.snapshot = self._snap
        FM.reboot = self._reboot

    def _snap(self, w):
        self.snaps += 1
        return "/snap/%s.txt" % w["id"]

    def _reboot(self, _why):
        self.reboots += 1
        return True, ""


def quiet_tick(now):
    with open(os.devnull, "w") as dn:
        out, sys.stdout = sys.stdout, dn
        try:
            FM.tick(now)
        finally:
            sys.stdout = out
    return T.read_json(T.q("fault_state.json"))


def machine_checks(tmp):
    saved = T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot, FM.RETEST_STATE
    FM.RETEST_STATE = os.path.join(tmp, "no_retest.json")

    def fresh():
        T.QHOME = tempfile.mkdtemp(dir=tmp)
        m = Machine()
        m.install()
        return m

    try:
        m = fresh()
        m.lines += [cyc(5), cyc(10)]
        st = quiet_tick(BOOT_S + 11 * 60)
        check(st["phase"] == "CLEAN" and not T.paused() and st["clean_through_s"] == BOOT_S + 600, "clean: lane alone, the reading says clean through")
        m.lines += [cyc(175, [0])]
        m.busy = True
        st = quiet_tick(BOOT_S + 176 * 60)
        check(st["phase"] == "DRAIN" and T.paused() and FM.MARK in T.paused()["reason"] and m.snaps == 1, "onset: cause snapshot, lane paused, draining")
        windows = T.read_json(T.q("fault_windows.json"))
        check(windows[0]["snapshot"] == "/snap/%s.txt" % windows[0]["id"], "the snapshot's path is on the window")
        st = quiet_tick(BOOT_S + 178 * 60)
        check(st["phase"] == "DRAIN" and m.reboots == 0 and m.snaps == 1, "a busy worker holds the reboot; no second snapshot")
        m.busy = False
        st = quiet_tick(BOOT_S + 180 * 60)
        check(st["phase"] == "DRAIN" and m.reboots == 0, "one idle tick is not drained")
        st = quiet_tick(BOOT_S + 182 * 60)
        check(st["phase"] == "WAIT_BOOT" and m.reboots == 1, "two idle ticks: one reboot (the train's idle RimWorld holds nothing)")
        m.up = False
        st = quiet_tick(BOOT_S + 184 * 60)
        check(st["phase"] == "WAIT_BOOT" and m.reboots == 1 and not st["reachable"], "down: waits, no second reboot")
        b2 = "2026-11-03 23:05:00"
        m.up, m.boot = True, FM.epoch(b2)
        st = quiet_tick(FM.epoch(b2) + 120)
        check(st["phase"] == "VERIFY" and T.paused() and st["open_window"] is None, "back: window closed, lane stays paused until it is shown clean")
        m.up = False
        st = quiet_tick(FM.epoch(b2) + 150)
        check(st["open_window"] is None and T.read_json(T.q("fault_windows.json"))[0]["end"], "ssh lost before the next watch line: the closed window stays closed")
        m.up = True
        m.lines += [start(b2), cyc(5, boot=b2)]
        st = quiet_tick(FM.epoch(b2) + 6 * 60)
        check(st["phase"] == "VERIFY" and T.paused(), "one clean cycle is not enough")
        m.lines += [cyc(10, boot=b2)]
        st = quiet_tick(FM.epoch(b2) + 11 * 60)
        check(st["phase"] == "CLEAN" and not T.paused() and not st.get("alarm"), "two clean cycles: lane resumed, clean")
        windows = T.read_json(T.q("fault_windows.json"))
        check(len(windows) == 1 and windows[0]["end"] == FM.stamp(FM.epoch(b2)) and windows[0]["snapshot"], "the window keeps its end and its snapshot")

        m.lines += [cyc(15, [4], boot=b2)]
        st = quiet_tick(FM.epoch(b2) + 16 * 60)
        check(st["phase"] == "DRAIN" and len(T.read_json(T.q("fault_windows.json"))) == 2, "a second onset on the new boot is a new window")
        quiet_tick(FM.epoch(b2) + 18 * 60)
        st = quiet_tick(FM.epoch(b2) + 19 * 60)
        check(st["phase"] == "STUCK" and m.reboots == 1 and st["alarm"].startswith("STUCK") and T.paused(), "back within minutes of a boot: STUCK, no reboot loop, lane stays paused")
        st = quiet_tick(FM.epoch(b2) + 200 * 60)
        check(st["phase"] == "STUCK" and m.reboots == 1, "STUCK is sticky")
        b3 = "2026-11-04 05:00:00"
        m.boot = FM.epoch(b3)
        st = quiet_tick(FM.epoch(b3) + 60)
        check(st["phase"] == "VERIFY" and not st.get("alarm"), "a new boot by any hand ends STUCK")

        m = fresh()
        m.lines += [cyc(170), cyc(175, [0])]
        T.S.dump({"since": S.utcnow(), "job": None, "reason": "remote hardware tests", "until": None}, T.pause_path())
        quiet_tick(BOOT_S + 176 * 60)
        st = quiet_tick(BOOT_S + 178 * 60)
        st = quiet_tick(BOOT_S + 180 * 60)
        check(st["phase"] == "DRAIN" and m.reboots == 0 and "not ours" in st["why_held"], "a foreign pause holds the reboot")
        os.remove(T.pause_path())
        T.S.dump({"since": at(175), "job": "J1", "outcome": "INVALID", "cause": "CANARY", "reason": "red canary"}, T.pause_path())
        quiet_tick(BOOT_S + 182 * 60)
        st = quiet_tick(BOOT_S + 184 * 60)
        check(st["phase"] == "WAIT_BOOT" and m.reboots == 1, "a red canary born in the window does not hold it")
        b4 = "2026-11-03 23:30:00"
        m.boot = FM.epoch(b4)
        m.lines += [start(b4), cyc(5, boot=b4), cyc(10, boot=b4)]
        st = quiet_tick(FM.epoch(b4) + 11 * 60)
        st = quiet_tick(FM.epoch(b4) + 12 * 60)
        check(st["phase"] == "CLEAN" and not T.paused(), "and that pause is lifted with ours")

        m = fresh()
        m.lines += [cyc(170), cyc(175, [0])]
        with open(FM.RETEST_STATE, "w") as f:
            json.dump({"state": "RUNNING"}, f)
        st = quiet_tick(BOOT_S + 176 * 60)
        check(st["phase"] == "PASSIVE" and not T.paused() and m.reboots == 0 and st["open_window"], "the CPU retest owns the machine: window yes, act no")
        os.remove(FM.RETEST_STATE)
        open(T.q("fault_monitor.stop"), "w").close()
        st = quiet_tick(BOOT_S + 178 * 60)
        check(st["phase"] == "PASSIVE" and not T.paused(), "the stop file too")
        os.remove(T.q("fault_monitor.stop"))
        b5 = "2026-11-03 23:50:00"
        m.boot = FM.epoch(b5)
        T.S.dump({"since": S.utcnow(), "job": None, "reason": FM.MARK + " x", "until": None}, T.pause_path())
        m.lines += [start(b5), cyc(5, boot=b5), cyc(10, boot=b5)]
        st = quiet_tick(FM.epoch(b5) + 11 * 60)
        st = quiet_tick(FM.epoch(b5) + 12 * 60)
        check(st["phase"] == "CLEAN" and not T.paused(), "back from PASSIVE with our pause on: recovery resumes, the pause is lifted")

        m = fresh()
        m.lines += [cyc(170), cyc(175, [0])]
        now = BOOT_S + 176 * 60
        st = T.read_json(T.q("fault_state.json")) or {}
        T.S.dump(dict(st, phase="CLEAN", reboots=[now - 3600 * i for i in range(FM.MAX_REBOOTS_DAY)]), T.q("fault_state.json"))
        quiet_tick(now)
        quiet_tick(now + 60)
        st = quiet_tick(now + 120)
        check(st["phase"] == "STUCK" and m.reboots == 0 and "reboots" in st["stuck"], "the reboot cap is STUCK too")

        m = fresh()
        m.lines += [cyc(5)]
        st = quiet_tick(BOOT_S + 60 * 60)
        check("no canary cycle" in st.get("blind", ""), "reachable and no recent cycle: blind")
        check(FM.check(now=BOOT_S + 60 * 60) == 1, "check fails on a blind canary")
        m.lines += [cyc(58)]
        quiet_tick(BOOT_S + 60 * 60)
        check(FM.check(now=BOOT_S + 60 * 60) == 0, "check passes on a fresh clean reading")
        check(FM.check(now=BOOT_S + 60 * 60 + FM.STALE_S + 60) == 1, "check fails on a stale reading")

        m = fresh()
        m.lines += [cyc(170), cyc(175, [0])]
        quiet_tick(BOOT_S + 176 * 60)
        os.makedirs(T.q("done"), exist_ok=True)
        r = rec(at(172), at(174))
        S.dump(r, T.q("done", r["job"]["id"] + ".json"))
        check(FM.check(now=BOOT_S + 180 * 60) == 0, "check allows a record just finished, before ingest has moved it")
        check(FM.check(now=BOOT_S + 190 * 60) == 1, "check fails on a done record left inside a window")
        T.S.dump(dict(T.read_json(T.q("fault_state.json")), at=FM.stamp(BOOT_S + 190 * 60), unparsed=2, alarm=None), T.q("fault_state.json"))
        os.remove(T.q("done", r["job"]["id"] + ".json"))
        check(FM.check(now=BOOT_S + 190 * 60) == 1, "check fails when the parser stops reading the canary")
    finally:
        T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot, FM.RETEST_STATE = saved


def ingest_checks(tmp):
    """The real ingest.py over a temp queue and ledger, with fault_windows/fault_state as the monitor writes them."""
    queue, items = os.path.join(tmp, "iq"), os.path.join(tmp, "items")
    led = os.path.join(tmp, "ledger", "events.jsonl")
    for d in (os.path.join(queue, "done"), os.path.join(queue, "pending"), items, os.path.dirname(led)):
        os.makedirs(d)
    open(led, "w").close()
    env = {k: v for k, v in os.environ.items() if k not in ("RIMFLOW_SEAT", "CLAUDE_PROJECT_DIR")}
    env.update(TESTQ_QUEUE=queue, RIMFLOW_LEDGER=led, RIMFLOW_ITEMS=items, TESTQ_INGEST_PUSH="0", TESTQ_FAULT_ITEM=ITEM)
    r = subprocess.run([sys.executable, CLI, "file", ITEM, "--for", "BENCH", "--title", "t", "--seat", "BENCH"], env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0, "the test item is filed: %s" % r.stderr[-200:])
    shard = os.path.join(tmp, "ledger", "events", "RUNNER.jsonl")

    def events(kind):
        try:
            return [e for e in map(json.loads, open(shard)) if e.get("event") == kind]
        except OSError:
            return []

    def ingest():
        p = subprocess.run([sys.executable, os.path.join(HERE, "ingest.py")], env=env, capture_output=True, text=True, timeout=300)
        check(p.returncode == 0, "ingest ran: %s" % p.stderr[-300:])

    def put(r):
        S.dump(r, os.path.join(queue, "done", r["job"]["id"] + ".json"))
        return r["job"]["id"]

    # The boot is six hours before the wall clock, never a fixed date: rerun_job re-queues only results under
    # RERUN_WITHIN_S (48 h) old, so a pinned boot turned this test red two days after it was written.
    ib = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - 6 * 3600))
    at = lambda m, boot=ib: FM.stamp(FM.epoch(boot) + m * 60)            # noqa: E731
    start_ = lambda boot=ib: start(boot)                                  # noqa: E731
    cyc_ = lambda m, bad=(), boot=ib: cyc(m, bad, boot)                   # noqa: E731
    a = FM.analyse([start_(), cyc_(170), cyc_(175, [0])])
    S.dump(a["windows"], os.path.join(queue, "fault_windows.json"))
    S.dump({"phase": "DRAIN", "clean_through_s": None, "boot_iso": at(0), "at": S.utcnow()}, os.path.join(queue, "fault_state.json"))
    now_iso = soon = S.utcnow()
    inside = put(rec(at(172), at(174), item=ITEM))
    was = put(rec(at(160), at(176), item=ITEM, ingested={"run": ITEM + "/run-1@x", "result": "pass", "at": at(177)}))
    filler = put(rec(at(172), at(174)))
    before = put(rec(at(100), at(120), item=ITEM))
    ingest()
    q = lambda j: os.path.exists(os.path.join(queue, "quarantined", j + ".json"))
    d = lambda j: os.path.exists(os.path.join(queue, "done", j + ".json"))
    check(q(inside) and not d(inside) and q(was) and not d(was) and q(filler) and not d(filler), "records from inside the window left done/ for quarantined/")
    runs = events("verify")
    check(not any(inside in json.dumps(e) for e in runs), "no verdict from inside the window")
    notes = [e.get("text", "") for e in events("note")]
    check(any(inside in n and "no verdict recorded" in n for n in notes), "an unjudged job: a note says so")
    check(any(was in n and "must not be counted" in n and ITEM + "/run-1@x" in n for n in notes), "one judged before the fault was known: its verdict is named as not to count")
    check(any("Steve fault window %s:" % a["windows"][0]["id"] in n for n in notes), "the onset itself is on the fault's item")
    pend = [T.read_json(os.path.join(queue, "pending", f)) for f in os.listdir(os.path.join(queue, "pending"))]
    check(len(pend) == 2 and all(p["item"] == ITEM for p in pend), "both item jobs are queued again, the filler is not (the fill finds its gap)")
    check(d(before) and T.read_json(os.path.join(queue, "done", before + ".json")).get("ingested", {}).get("result") == "pass", "a job before the window is untouched by the quarantine")
    n_notes = len(notes)
    ingest()
    check(len(events("note")) == n_notes, "a second pass writes nothing new")
    # no window over it, but no clean cycle read since: held, then counted once one is
    b2 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(FM.epoch(ib) + 210 * 60))   # after the window, before now
    a2 = FM.analyse([start_(), cyc_(170), cyc_(175, [0]), start_(b2), cyc_(5, boot=b2)])
    S.dump(a2["windows"], os.path.join(queue, "fault_windows.json"))
    S.dump({"phase": "CLEAN", "clean_through_s": a2["clean_through"], "boot_iso": b2, "at": now_iso}, os.path.join(queue, "fault_state.json"))
    r = rec(FM.stamp(FM.epoch(soon) - 600), soon, item=ITEM)
    held = put(r)
    ingest()
    check("ingested" not in T.read_json(os.path.join(queue, "done", held + ".json")), "held: no verdict until a clean cycle follows it")
    S.dump({"phase": "CLEAN", "clean_through_s": FM.epoch(soon) + 1, "boot_iso": b2, "at": S.utcnow()}, os.path.join(queue, "fault_state.json"))
    ingest()
    check(T.read_json(os.path.join(queue, "done", held + ".json")).get("ingested", {}).get("result") == "pass", "and counted when one does")
    # depth: a re-run of a re-run of a re-run stays out
    saved = T.QHOME
    T.QHOME = queue
    try:
        job = rec(soon, soon, item=ITEM)
        S.dump({job["job"]["id"]: FM.RERUN_DEPTH}, T.q("fault_reruns.json"))
        check(FM.rerun_job(job) is None, "a job re-queued often enough stays out")
        old = rec(at(10), at(20), item=ITEM)
        check(FM.rerun_job(old, now=FM.epoch(at(20)) + FM.RERUN_WITHIN_S + 60) is None, "an old result is quarantined but not re-queued")
    finally:
        T.QHOME = saved


def main():
    analyse_checks()
    gate_checks()
    periodic_checks()
    tmp = tempfile.mkdtemp(prefix="rf_fault_")
    try:
        machine_checks(tmp)
        ingest_checks(tmp)
        heat_checks(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
