#!/usr/bin/env python3
"""selftest_testq_fault_monitor.py - fault_monitor.py and its gate in ingest.py (STEVE_FAULT_MONITOR_ONSET_BEFORE_RESULTS).

No ssh, no game: the machine is replaced by a fake with a log, a boot and a worker. Proves: the onset is timed from the last
clean cycle, a clean cycle after it closes nothing, only a new boot does; history backfills itself; a result in a window is
quarantined, one with no clean cycle read since it finished is held, one after a clean cycle counts; the whole round
onset -> pause -> drain -> one reboot -> two clean cycles -> resume; a fault back at once is STUCK, not a reboot loop; a
foreign pause holds the reboot and a red canary inside the window does not; ingest writes no verdict from a window,
notes what it already wrote and queues the item job again; `check` fails on what it says it fails on, and the retired probe's history still reads. One tracker (owner, 2026-11-23): the
register probe's lines make the windows, a cycle that could not look is no cycle, an old boot's torn line is not a
blind parser, and the periodic reboot runs only while the fault or its driver was seen. Audio driver
(RIMMANDRAKE_DISABLE_STEVE_SONIC_STUDIO_DRIVER_SOUND_IS_UNUSED): the AUDIODRV line parses, each tick writes
steve_audio_driver.json, and `check` fails on LOADED or ENABLED and passes on OFF.
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
    check("ToUniversalTime().AddMinutes" not in FM.SNAPSHOT_PS and "probe:" in FM.SNAPSHOT_PS, "the snapshot asks the event log in local time, and says the log can be seen")
    c = FM.analyse(["2026-11-03 20:00:00Z CONTROL inject_exit=1 clean_exit=0"])["control"]
    check(c["ok"], "a control with an injected fault seen is ok")
    check(not FM.analyse(["2026-11-03 20:00:00Z CONTROL inject_exit=0 clean_exit=0"])["control"]["ok"], "a control that misses it is not")


def rp(minutes, bad=(), boot=BOOT, result=None):
    t = FM.epoch(boot) + minutes * 60
    result = result or ("fault" if bad else "clean")
    return "%sZ RPCYCLE uptime_h=%.2f result=%s cpus_measured=18/18 holds=396 bad_holds=%d bad=[%s] unmeasured=[] secs=8.5" % (
        FM.stamp(t).replace("T", " ").rstrip("Z"), minutes / 60.0, result, len(bad),
        ",".join("%d:upper_half_loss" % c for c in bad))


def rpstart(boot=BOOT, build="normal", ok=1):
    ts = FM.stamp(FM.epoch(boot) + 10).replace("T", " ").rstrip("Z")
    return ["%sZ RPSTART boot=%sZ logical_cpus=18 cycle=300s build=%s mode=loop pid=3060 version=1" % (ts, boot, build),
            "%sZ RPCONTROL cpu=3 upper_seen=1 lower_seen=1 sse_seen=1 scalar_seen=1 clean_seen=1 ok=%d" % (ts, ok)]


def one_tracker_checks(tmp):
    """the-register-probe-alone-opens-and-closes-the-window, and what it must not call clean."""
    a = FM.analyse(FM.from_probe(rpstart() + [rp(5), rp(10), rp(15, [4, 7]), rp(20)]))
    w = a["open"]
    check(w and w["first_bad"] == at(15) and w["first_cpus"] == [4, 7] and w["start"] == at(10) and w["clean_after"] == 1,
          "the-register-probe-alone-opens-the-window: last clean cycle to first bad one, CPUs kept")
    b2 = "2026-11-04 03:00:00"
    a = FM.analyse(FM.from_probe(rpstart() + [rp(15, [4])] + rpstart(b2) + [rp(5, boot=b2)]))
    check(a["open"] is None and a["windows"][0]["end"] == FM.stamp(FM.epoch(b2)) and a["clean_cycles"] == 1 and a["control"]["ok"],
          "the next boot's clean cycle closes it")
    for name, lines in (("a failed control", rpstart(ok=0) + [rp(5)]), ("a planted build", rpstart(build="inject_vz") + [rp(5, [1])]),
                        ("a partial cycle", rpstart() + [rp(5, result="partial")]), ("no start line", [rp(5)]),
                        ("an unmeasured cycle", rpstart() + [rp(5, result="unmeasured")])):
        a = FM.analyse(FM.from_probe(lines))
        check(a["clean_through"] is None and not a["windows"] and a["last_cycle"] is None, "%s is no cycle: neither clean nor bad" % name)
    torn = "2026-11-03 20:30\x00\x00\x00\x00e_h=15.96 bad=[2]"
    a = FM.analyse(FM.from_probe(rpstart() + [torn, rp(60)]))
    check(a["unparsed"] == 1, "a torn line on this boot is counted")
    a = FM.analyse(FM.from_probe(rpstart() + [torn] + rpstart(b2) + [rp(5, boot=b2)]))
    check(a["unparsed"] == 0, "a torn line of an older boot is not a blind parser")
    import regprobe_log as RPL
    check(RPL.analyse(rpstart() + [torn] + rpstart(b2) + [rp(5, boot=b2)])["unparsed"] == 0
          and RPL.analyse(rpstart() + [rp(5), torn])["unparsed"] == 1, "the probe report's unparsed count is this boot's too")
    saved = T.QHOME
    T.QHOME = tempfile.mkdtemp(dir=tmp)
    try:
        T.ensure_dirs()
        with open(T.q("fault_watch.log"), "w") as f:
            f.write("\n".join([start(), cyc(5), cyc(10, [3])]) + "\n")
        got = FM.cycle_lines(rpstart() + [rp(3, [9]), rp(20)] + rpstart(b2) + [rp(5, boot=b2)])
        a = FM.analyse(got)
        check(len(a["windows"]) == 1 and a["windows"][0]["first_cpus"] == [3] and a["windows"][0]["clean_after"] == 1
              and a["windows"][0]["end"] == FM.stamp(FM.epoch(b2)) and a["clean_through"] == FM.epoch(b2) + 300,
              "the frozen history stands, the probe's cycles carry on after it and never rewrite it")
    finally:
        T.QHOME = saved
    src = open(os.path.join(HERE, "fault_monitor.py")).read()
    check("logs\\watch.log" not in src and "deploy-watch" not in src and not os.path.exists(os.path.join(HERE, "..", "steve_cpu_retest", "watch2.ps1")),
          "one tracker: nothing here reads or deploys the retired probe")


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
        shown = [{"first_bad": FM.stamp(B), "last_bad": FM.stamp(B + 3600)}]
        young = {"boot": B, "windows": shown}
        FM.periodic_reboot(st, young, B + 11 * 3600)
        check(not log and not st.get("pr"), "periodic: a boot younger than reboot_every_h is left alone")
        FM.periodic_reboot(st, {"boot": B, "windows": []}, B + 13 * 3600)
        check(not log, "periodic: no fault seen and no driver back, an old boot is left alone")
        FM.periodic_reboot(st, {"boot": B, "windows": [{"first_bad": FM.stamp(B - FM.PR_FAULT_S)}]}, B + 13 * 3600)
        check(not log, "periodic: a fault older than PR_FAULT_S no longer reboots")
        FM.S.dump({"verdict": "LOADED"}, FM.T.q("steve_audio_driver.json"))
        st1 = {}
        FM.periodic_reboot(st1, {"boot": B, "windows": []}, B + 13 * 3600)
        check(log == ["pause"], "periodic: the fault's driver loaded again reboots as before")
        log.clear()
        box.update(pz=None)
        FM.S.dump({"verdict": "OFF"}, FM.T.q("steve_audio_driver.json"))
        old = {"boot": B, "windows": shown}
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
        log.clear()
        box.update(pz=None)
        FM.periodic_reboot({}, {"boot": B, "open": {"id": "FX"}}, B + 600)
        check(not log, "periodic: an open window on a boot under MIN_UPTIME_S waits (a reboot is not clearing it)")
        capped = {"reboots": [B + i for i in range(FM.MAX_REBOOTS_DAY)]}
        FM.periodic_reboot(capped, {"boot": B, "open": {"id": "FX"}}, B + 3600)
        check(not log, "periodic: the daily reboot cap holds against an open window")
        st2 = {}
        FM.periodic_reboot(st2, {"boot": B, "open": {"id": "FX"}}, B + 3600)
        check(log == ["pause"] and st2["pr"]["state"] == "DRAIN", "periodic: an open window drains early, long before reboot_every_h")
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
        self.boot, self.lines, self.up = BOOT_S, rpstart(), True
        self.busy, self.snaps, self.reboots = False, 0, 0
        self.audio = None

    def install(self):
        FM.steve_read = lambda: dict({"boot": self.boot, "cpus": 18, "rimworld": 1, "rp_lines": list(self.lines)},
                                     **({"audio": self.audio} if self.audio else {})) if self.up else None
        FM.worker_busy = lambda: self.busy
        FM.snapshot = self._snap
        FM.reboot = self._reboot

    def _snap(self, w):
        self.snaps += 1
        return "/snap/%s.txt" % w["id"]

    def _reboot(self, _why):
        self.reboots += 1
        return True, ""


def audio_checks():
    got = [FM.audio_of([x]).get("verdict") for x in ("AUDIODRV 4 Stopped", "AUDIODRV 3 Running", "AUDIODRV 3 Stopped",
                                                     "AUDIODRV none ABSENT", "AUDIODRV x", "FACTS 1 2 3")]
    check(got == ["OFF", "LOADED", "ENABLED", "ABSENT", "UNMEASURED", "UNMEASURED"], "AUDIODRV parse table (got %r)" % got)
    src = open(os.path.join(HERE, "fault_monitor.py")).read()
    check('"AUDIODRV "+' in src and "Win32_SystemDriver" in src, "steve_read's PowerShell writes the AUDIODRV line audio_of reads")


def quiet_tick(now):
    with open(os.devnull, "w") as dn:
        out, sys.stdout = sys.stdout, dn
        try:
            FM.tick(now)
        finally:
            sys.stdout = out
    return T.read_json(T.q("fault_state.json"))


def machine_checks(tmp):
    saved = T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot

    def fresh():
        T.QHOME = tempfile.mkdtemp(dir=tmp)
        m = Machine()
        m.install()
        return m

    try:
        m = fresh()
        m.lines += [rp(5), rp(10)]
        st = quiet_tick(BOOT_S + 11 * 60)
        check(st["phase"] == "CLEAN" and not T.paused() and st["clean_through_s"] == BOOT_S + 600, "clean: lane alone, the reading says clean through")
        m.lines += [rp(175, [0])]
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
        m.lines += rpstart(b2) + [rp(5, boot=b2)]
        st = quiet_tick(FM.epoch(b2) + 6 * 60)
        check(st["phase"] == "VERIFY" and T.paused(), "one clean cycle is not enough")
        m.lines += [rp(10, boot=b2)]
        st = quiet_tick(FM.epoch(b2) + 11 * 60)
        check(st["phase"] == "CLEAN" and not T.paused() and not st.get("alarm"), "two clean cycles: lane resumed, clean")
        windows = T.read_json(T.q("fault_windows.json"))
        check(len(windows) == 1 and windows[0]["end"] == FM.stamp(FM.epoch(b2)) and windows[0]["snapshot"], "the window keeps its end and its snapshot")

        m.lines += [rp(15, [4], boot=b2)]
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
        m.lines += [rp(170), rp(175, [0])]
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
        m.lines += rpstart(b4) + [rp(5, boot=b4), rp(10, boot=b4)]
        st = quiet_tick(FM.epoch(b4) + 11 * 60)
        st = quiet_tick(FM.epoch(b4) + 12 * 60)
        check(st["phase"] == "CLEAN" and not T.paused(), "and that pause is lifted with ours")

        m = fresh()
        m.lines += [rp(170), rp(175, [0])]
        open(T.q("fault_monitor.stop"), "w").close()
        st = quiet_tick(BOOT_S + 178 * 60)
        check(st["phase"] == "PASSIVE" and not T.paused(), "the stop file too")
        os.remove(T.q("fault_monitor.stop"))
        b5 = "2026-11-03 23:50:00"
        m.boot = FM.epoch(b5)
        T.S.dump({"since": S.utcnow(), "job": None, "reason": FM.MARK + " x", "until": None}, T.pause_path())
        m.lines += rpstart(b5) + [rp(5, boot=b5), rp(10, boot=b5)]
        st = quiet_tick(FM.epoch(b5) + 11 * 60)
        st = quiet_tick(FM.epoch(b5) + 12 * 60)
        check(st["phase"] == "CLEAN" and not T.paused(), "back from PASSIVE with our pause on: recovery resumes, the pause is lifted")

        m = fresh()
        m.lines += [rp(170), rp(175, [0])]
        now = BOOT_S + 176 * 60
        st = T.read_json(T.q("fault_state.json")) or {}
        T.S.dump(dict(st, phase="CLEAN", reboots=[now - 3600 * i for i in range(FM.MAX_REBOOTS_DAY)]), T.q("fault_state.json"))
        quiet_tick(now)
        quiet_tick(now + 60)
        st = quiet_tick(now + 120)
        check(st["phase"] == "STUCK" and m.reboots == 0 and "reboots" in st["stuck"], "the reboot cap is STUCK too")

        m = fresh()
        m.lines += [rp(5)]
        st = quiet_tick(BOOT_S + 60 * 60)
        check("no probe cycle" in st.get("blind", ""), "reachable and no recent cycle: blind")
        check(FM.check(now=BOOT_S + 60 * 60) == 1, "check fails on a blind probe")
        m.lines += [rp(58)]
        quiet_tick(BOOT_S + 60 * 60)
        check(FM.check(now=BOOT_S + 60 * 60) == 0, "check passes on a fresh clean reading")
        check(FM.check(now=BOOT_S + 60 * 60 + FM.STALE_S + 60) == 1, "check fails on a stale reading")
        ad = lambda: T.read_json(T.q("steve_audio_driver.json")) or {}  # noqa: E731
        check(ad().get("verdict") == "UNMEASURED", "a read with no audio field: the reading says UNMEASURED, not OFF")
        m.audio = FM.audio_of(["AUDIODRV 3 Running"])
        quiet_tick(BOOT_S + 60 * 60)
        check(ad().get("verdict") == "LOADED" and FM.check(now=BOOT_S + 60 * 60) == 1, "audio driver LOADED: reading LOADED, check fails")
        m.audio = FM.audio_of(["AUDIODRV 3 Stopped"])
        quiet_tick(BOOT_S + 60 * 60)
        check(ad().get("verdict") == "ENABLED" and FM.check(now=BOOT_S + 60 * 60) == 1, "audio driver re-enabled, not loaded: check fails")
        m.audio = FM.audio_of(["AUDIODRV 4 Stopped"])
        quiet_tick(BOOT_S + 60 * 60)
        check(ad().get("verdict") == "OFF" and FM.check(now=BOOT_S + 60 * 60) == 0, "audio driver OFF: check passes")
        m.up = False
        quiet_tick(BOOT_S + 60 * 60)
        check(ad().get("verdict") == "UNMEASURED" and "did not answer" in ad().get("why", ""), "Steve unreachable: audio reading UNMEASURED with its cause")
        m.up = True

        m = fresh()
        m.lines += [rp(170), rp(175, [0])]
        quiet_tick(BOOT_S + 176 * 60)
        os.makedirs(T.q("done"), exist_ok=True)
        r = rec(at(172), at(174))
        S.dump(r, T.q("done", r["job"]["id"] + ".json"))
        check(FM.check(now=BOOT_S + 180 * 60) == 0, "check allows a record just finished, before ingest has moved it")
        check(FM.check(now=BOOT_S + 190 * 60) == 1, "check fails on a done record left inside a window")
        T.S.dump(dict(T.read_json(T.q("fault_state.json")), at=FM.stamp(BOOT_S + 190 * 60), unparsed=2, alarm=None), T.q("fault_state.json"))
        os.remove(T.q("done", r["job"]["id"] + ".json"))
        check(FM.check(now=BOOT_S + 190 * 60) == 1, "check fails when the parser stops reading the probe")
    finally:
        T.QHOME, FM.steve_read, FM.worker_busy, FM.snapshot, FM.reboot = saved


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
    # a-fault-return-wakes-the-sleeping-ticket-once
    def unblocks():
        return events("unblock")
    r = subprocess.run([sys.executable, CLI, "block", ITEM, "--kind", "external", "--reason", "WAKES ON steve-fault: asleep",
                        "--seat", "BENCH"], env=env, capture_output=True, text=True, timeout=120)
    check(r.returncode == 0, "the fault ticket is put to sleep: %s" % r.stderr[-200:])
    S.dump({"verdict": "OFF"}, os.path.join(queue, "steve_audio_driver.json"))
    ingest()
    check(not unblocks(), "the windows that were there before the sleep wake nothing")
    S.dump({"verdict": "UNMEASURED"}, os.path.join(queue, "steve_audio_driver.json"))
    ingest()
    check(not unblocks(), "a driver reading that could not look wakes nothing")
    b3 = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(FM.epoch(b2) + 60 * 60))
    a3 = FM.analyse([start_(), cyc_(170), cyc_(175, [0]), start_(b2), cyc_(5, boot=b2), start_(b3), cyc_(5, [2], boot=b3)])
    S.dump(a3["windows"], os.path.join(queue, "fault_windows.json"))
    ingest()
    check(len(unblocks()) == 1 and a3["windows"][-1]["id"] in unblocks()[0].get("reason", ""), "a new window wakes it, and says which")
    ingest()
    check(len(unblocks()) == 1, "once, not every pass")
    subprocess.run([sys.executable, CLI, "block", ITEM, "--kind", "external", "--reason", "WAKES ON steve-fault: asleep",
                    "--seat", "BENCH"], env=env, capture_output=True, text=True, timeout=120)
    S.dump({"verdict": "ENABLED"}, os.path.join(queue, "steve_audio_driver.json"))
    ingest()
    check(len(unblocks()) == 2 and "AVoluteSS3Vad is ENABLED" in unblocks()[1].get("reason", ""), "the driver enabled again wakes it too")
    # a-quarantined-job-is-queued-again: a machine fault spends no re-run, however often it struck
    saved = T.QHOME
    T.QHOME = queue
    try:
        job = rec(soon, soon, item=ITEM)
        S.dump({job["job"]["id"]: 5}, T.q("fault_reruns.json"))
        check(FM.rerun_job(job) is not None, "a-quarantined-job-is-queued-again: the sixth quarantine queues it again")
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
        audio_checks()
        ingest_checks(tmp)
        one_tracker_checks(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("FAILED %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
