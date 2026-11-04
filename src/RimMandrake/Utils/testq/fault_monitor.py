#!/usr/bin/env python3
"""fault_monitor.py - SteveDesktop's uptime SIMD fault: time its onset, quarantine its results, reboot it away
(STEVE_FAULT_MONITOR_ONSET_BEFORE_RESULTS; the measurements are on STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO).

The fault: a logical CPU starts computing wrong SIMD results some hours into a boot; a reboot clears it; root cause
unmeasured. The canary is watch2.ps1, a scheduled task on Steve: every 300 s, a 4 s pinned `stevecheck core` per logical
CPU, one CYCLE line in C:\\SteveDesktop\\diag\\logs\\watch.log. This module is the half on Archmagi that reads it
(rm-steve-fault.timer, `tick`, every 2 min).

  analyse()   the watch log -> one fault window per faulty boot, a pure function of the log (so history backfills itself).
              A window runs from the last clean cycle before the first bad one (the boot, if none) to the next boot.
              A clean cycle after the first bad one closes nothing: only a reboot is known to clear it (the cycles wander
              between CPUs and include clean ones, measured 2026-11-03).
  gate()      what a finished Steve job's result is worth: `quarantine` (it overlaps a window), `hold` (no clean cycle read
              since it finished, so the fault may already have begun under it) or `count`. ingest.py asks before any
              verdict and does the moving. No fault_state.json = monitor not installed = count.
  tick        CLEAN -> onset: snapshot for the cause, pause the lane -> DRAIN: job finished, worker idle, two ticks ->
              reboot -> WAIT_BOOT -> VERIFY: two clean cycles on the new boot -> resume the lane -> CLEAN.
              The train's idle RimWorld does not hold a reboot (the CPU retest's rule that it should cost 9.5 h, 11-01).
              STUCK (sticky until a new boot): the fault is back within MIN_UPTIME_S of a boot, or the reboot cap is spent:
              the lane stays paused and its pause's expiry escalates through the steward.
              PASSIVE: QHOME/fault_monitor.stop, or steve_cpu_retest owns the machine: windows and gate go on, no act.
              A pause by someone else holds the reboot; an auto pause born inside the window (a red canary) does not.
  report      the onset table: boot, uptime at onset, CPUs, jobs under it; check: the reading is honest (exit 0/1).
  deploy-watch  copy watch2.ps1 to Steve and restart its task.

Files in QHOME: fault_state.json (the reading), fault_windows.json (what gate reads), fault_watch.log (the mirror),
fault_snapshots/<window>.txt (cause evidence), quarantined/<job>.json (results that must not count, kept).
"""
import argparse
import base64
import calendar
import fcntl
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import testq as T  # noqa: E402

S = T.S
STEVE_WIN = os.environ.get("STEVE_WIN", "stevedesktop")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR", STEVE_WIN]
RETEST_STATE = os.environ.get("STEVE_RETEST_HOME", "/mnt/d/ClaudeWork/rimmandrake/steve_diag/retest") + "/state.json"
RETEST_IDLE = ("DONE_CLEAN", "END_FAULT", "ABORTED", "DISARMED")
WATCH_LOG = r"C:\SteveDesktop\diag\logs\watch.log"
WATCH_PS1 = r"C:\SteveDesktop\diag\watch2.ps1"
MARK = "STEVE_FAULT_MONITOR:"       # a pause of ours says so; only ours is lifted
PAUSE_HOURS = 6
QUIET_TICKS = 2
CLEAN_TO_RESUME = 2
MIN_UPTIME_S = 20 * 60              # the fault back sooner than this: a reboot is not clearing it
MAX_REBOOTS_DAY = 12                # measured onset ~3 h on BIOS 3401: 8 a day is the honest worst case
BOOT_TIMEOUT_S = 40 * 60
BLIND_S = 20 * 60                   # reachable, up this long, and no cycle this recent: the canary is dead
HOLD_S = 2 * 3600                   # a result waits this long for a clean cycle, then counts as unguarded
STALE_S = 30 * 60                   # a reading older than this says nothing (hold goes on, check fails)
RERUN_WITHIN_S = 48 * 3600          # older quarantined jobs are not re-queued; the fill's gap scan owns those
RERUN_DEPTH = 2                     # a job re-queued this many times stays out

_TS = r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)Z"
CYCLE_RE = re.compile("^" + _TS + r" CYCLE uptime_h=([\d.]+) bad_cpus=\[([\d,\s]*)\]")
START_RE = re.compile("^" + _TS + r" WATCH START boot=" + _TS)
CONTROL_RE = re.compile("^" + _TS + r" CONTROL inject_exit=(-?\d+) clean_exit=(-?\d+)")


def epoch(ts):
    """A UTC stamp, either spelling (2026-11-03 19:59:21Z / 2026-11-03T19:59:21Z) -> seconds."""
    return calendar.timegm(time.strptime(ts.replace("T", " ").rstrip("Z"), "%Y-%m-%d %H:%M:%S"))


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def norm(ts):
    return ts.replace(" ", "T") + "Z" if "T" not in ts else ts


def analyse(lines, live_boot=None):
    """The watch log's lines, oldest first, -> {windows, boot, last_cycle, clean_through, clean_cycles, unparsed, control}.
    live_boot (epoch) is the machine's own boot: newer than the log's, it closes what is open and starts an empty boot."""
    wins, boot, unparsed, control = [], None, 0, None
    last_clean = last_cycle = open_w = None
    clean_cycles = 0

    def new_boot(t):
        nonlocal boot, last_clean, open_w, clean_cycles
        if boot is not None and t <= boot:
            return
        if open_w:
            open_w["end"] = stamp(t)
        boot, last_clean, open_w, clean_cycles = t, None, None, 0

    for line in lines:
        m = START_RE.match(line)
        if m:
            new_boot(epoch(m.group(2)))
            continue
        m = CONTROL_RE.match(line)
        if m:
            control = {"at": norm(m.group(1)), "inject_exit": int(m.group(2)), "clean_exit": int(m.group(3)),
                       "ok": m.group(2) == "1" and m.group(3) == "0"}
            continue
        m = CYCLE_RE.match(line)
        if not m:
            unparsed += bool(line.strip())
            continue
        t, up = epoch(m.group(1)), float(m.group(2))
        if boot is None or t - up * 3600 > boot + 600:     # a cycle with no start line of its boot: its uptime says when
            new_boot(int(t - up * 3600))
        last_cycle = t
        cpus = [int(c) for c in m.group(3).replace(" ", "").split(",") if c]
        if not cpus:
            clean_cycles += 1
            last_clean = t
            if open_w:
                open_w["clean_after"] += 1
            continue
        if not open_w:
            open_w = {"id": "F" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(boot)), "boot": stamp(boot),
                      "start": stamp(last_clean if last_clean is not None else boot), "first_bad": stamp(t),
                      "onset_uptime_h": up, "first_cpus": cpus, "bad_cycles": 0, "clean_after": 0, "cpus": {},
                      "end": None}
            wins.append(open_w)
        open_w["bad_cycles"] += 1
        open_w["last_bad"] = stamp(t)
        for c in cpus:
            open_w["cpus"][str(c)] = open_w["cpus"].get(str(c), 0) + 1
    if live_boot is not None and (boot is None or live_boot > boot + 600):     # an inferred boot rounds: not a reboot
        new_boot(int(live_boot))
    return {"windows": wins, "boot": boot, "last_cycle": last_cycle, "open": open_w, "clean_cycles": clean_cycles,
            "clean_through": last_clean if not open_w else None, "unparsed": unparsed, "control": control}


def job_span(rec):
    """-> (start, end) epochs of a done record's run, the widest the record states, or None."""
    res = rec.get("result") or {}
    out = []
    for v in (res.get("started"), rec.get("sent"), res.get("finished"), rec.get("finished")):
        if v:
            try:
                out.append(epoch(v))
            except ValueError:
                pass
    return (min(out), max(out)) if out else None


def window_of(span, windows):
    for w in windows:
        end = epoch(w["end"]) if w.get("end") else float("inf")
        if span[0] < end and span[1] > epoch(w["start"]):
            return w
    return None


def gate(rec, windows, state, now=None):
    """-> ("quarantine", window) | ("hold", why) | ("count", why or None). Only SteveDesktop's results are its business."""
    if state is None or (rec.get("result") or {}).get("host", T.STEVE) != T.STEVE:
        return "count", None
    span = job_span(rec)
    if span is None:
        return "hold", "the record states no time"
    w = window_of(span, windows)
    if w:
        return "quarantine", w
    if (state.get("clean_through_s") or 0) >= span[1]:
        return "count", None
    now = time.time() if now is None else now
    if now - span[1] >= HOLD_S:
        return "count", "unguarded: no clean canary cycle read within %d s of the finish" % HOLD_S
    return "hold", "no clean canary cycle read since it finished"


def load():
    """-> (windows, state) as the monitor last wrote them; ([], None) when it has never run."""
    state = T.read_json(T.q("fault_state.json"))
    return (T.read_json(T.q("fault_windows.json")) or []), state


def write_json(name, obj):
    S.dump(obj, T.q(name))


def _qdir():
    os.makedirs(T.q("quarantined"), exist_ok=True)


def quarantine_move(rec, window, extra):
    """The done record moves to quarantined/: nothing that reads done/ (the fill, its gaps, the brake) sees it again."""
    _qdir()
    jid = rec["job"]["id"]
    T.move(jid, "done", "quarantined", dict(rec, quarantined=dict(extra, window=window["id"], at=S.utcnow())))


def rerun_job(rec, now=None):
    """-> a new pending job for a quarantined item job, or None (no item, too old, re-queued often enough)."""
    job = rec["job"]
    if not (job.get("item") or job.get("row_items")):
        return None
    now = time.time() if now is None else now
    span = job_span(rec)
    if not span or now - span[1] > RERUN_WITHIN_S:
        return None
    reruns = T.read_json(T.q("fault_reruns.json")) or {}
    depth = reruns.get(job["id"], 0) + 1
    if depth > RERUN_DEPTH:
        return None
    kw = {k: job[k] for k in S.DEFAULTS if k in job and k not in ("not_before", "supersedes")}
    new = S.make_job(job["mod"], job["selector"], job["purpose"], job["requested_by"], job["source_sha"], **kw)
    reruns[new["id"]] = depth
    write_json("fault_reruns.json", reruns)
    S.dump(new, T.q("pending", new["id"] + ".json"))
    return new["id"]


# ---------------------------------------------------------------- SteveDesktop, over ssh (a selftest replaces these)

def ps(script, timeout=120):
    """PowerShell on Steve -> (rc, stdout); rc None = ssh down."""
    enc = base64.b64encode(("$ProgressPreference='SilentlyContinue'\n" + script).encode("utf-16-le")).decode()
    try:
        r = subprocess.run(SSH + ["powershell -NoProfile -NonInteractive -EncodedCommand " + enc],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, ""
    return (None if r.returncode == 255 else r.returncode), r.stdout


def steve_read():
    """-> {boot, cpus, rimworld, lines} or None when unreachable."""
    rc, out = ps(r"""$o=Get-CimInstance Win32_OperatingSystem
$b=([DateTimeOffset]$o.LastBootUpTime).ToUnixTimeSeconds(); $n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$rw=@(Get-Process RimWorldWin64 -EA 0).Count
"FACTS $b $n $rw"
if(Test-Path '%s'){Get-Content '%s' -Tail 600}""" % (WATCH_LOG, WATCH_LOG))
    if rc is None:
        return None
    lines = out.splitlines()
    for i, line in enumerate(lines):
        p = line.split()
        if line.startswith("FACTS ") and len(p) == 4:
            return {"boot": int(p[1]), "cpus": int(p[2]), "rimworld": int(p[3]), "lines": lines[i + 1:]}
    return None


SNAPSHOT_PS = r"""$since=[datetime]::Parse('@SINCE@').ToUniversalTime().AddMinutes(-15)
'== when'; (Get-Date).ToUniversalTime().ToString('s')+'Z'
$o=Get-CimInstance Win32_OperatingSystem; 'boot '+$o.LastBootUpTime.ToUniversalTime().ToString('s')+'Z'
'== firmware'; $b=Get-CimInstance Win32_BIOS; 'BIOS '+$b.SMBIOSBIOSVersion+' '+$b.ReleaseDate
$c=Get-ItemProperty 'HKLM:\HARDWARE\DESCRIPTION\System\CentralProcessor\0'; $u=$c.'Update Revision'; 'ucode '+(($u|%{'{0:x2}' -f $_}) -join '')
'logical '+(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors; bcdedit /enum '{current}' | Select-String 'numproc'
'== thermal'; try{Get-CimInstance -Namespace root/wmi MSAcpi_ThermalZoneTemperature -EA Stop|%{$_.InstanceName+' '+[math]::Round($_.CurrentTemperature/10-273.15,1)}}catch{'UNMEASURED '+$_.Exception.Message}
'== top processes by cpu seconds'; Get-Process|Sort-Object CPU -Descending|Select -First 20|%{'{0,-28} cpu={1,10:n0} ws={2,6:n0}MB start={3}' -f $_.Name,$_.CPU,($_.WorkingSet64/1MB),$_.StartTime}
'== running drivers, not Microsoft'; Get-CimInstance Win32_SystemDriver -Filter "State='Running'"|?{$_.PathName -and (Get-Item ($_.PathName -replace '^\\\?\?\\','' -replace '^\\SystemRoot','C:\Windows' -replace '^system32','C:\Windows\system32') -EA 0).VersionInfo.CompanyName -notmatch 'Microsoft'}|%{$_.Name+' '+$_.PathName}
'== system events since 15 min before the window'; Get-WinEvent -FilterHashtable @{LogName='System';StartTime=$since;Level=1,2,3} -EA 0|Select -First 60|%{$_.TimeCreated.ToUniversalTime().ToString('s')+'Z '+$_.ProviderName+' '+$_.Id+' '+(($_.Message -split "`n")[0])}
'== application crashes in it'; Get-WinEvent -FilterHashtable @{LogName='Application';StartTime=$since;Id=1000,1001,1026} -EA 0|Select -First 40|%{$_.TimeCreated.ToUniversalTime().ToString('s')+'Z '+$_.Id+' '+(($_.Message -split "`n")[0])}
'== power and sleep'; Get-WinEvent -FilterHashtable @{LogName='System';StartTime=$since;ProviderName='Microsoft-Windows-Kernel-Power','Microsoft-Windows-Power-Troubleshooter','Microsoft-Windows-WHEA-Logger'} -EA 0|Select -First 30|%{$_.TimeCreated.ToUniversalTime().ToString('s')+'Z '+$_.ProviderName+' '+$_.Id}
'== the canary, last cycles'; Get-Content '@LOG@' -Tail 8
"""


def snapshot(window):
    """Cause evidence, taken while the faulty boot is still up -> the file, or None when Steve would not answer."""
    rc, out = ps(SNAPSHOT_PS.replace("@SINCE@", window["start"]).replace("@LOG@", WATCH_LOG), timeout=180)
    if rc is None:
        return None
    os.makedirs(T.q("fault_snapshots"), exist_ok=True)
    path = T.q("fault_snapshots", window["id"] + ".txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return path


def reboot(why):
    rc, out = ps('shutdown /r /t 15 /c "%s"' % why)
    return rc == 0, out.strip()[-200:]


def worker_busy():
    """True / False; None when the worker cannot be asked."""
    try:
        return bool(T.remote(["status"])[1].get("busy"))
    except (T.SshDown, AttributeError, TypeError, ValueError):
        return None


def lane_pause(reason):
    T.cmd_pause(argparse.Namespace(reason=MARK + " " + reason, hours=PAUSE_HOURS))


def lane_resume(reason):
    T.cmd_resume(argparse.Namespace(reason=MARK + " " + reason, lane=T.STEVE))


# ---------------------------------------------------------------- the state machine

def retest_active():
    st = T.read_json(RETEST_STATE)
    return bool(st) and st.get("state") not in RETEST_IDLE


def pause_is_ours(pz, windows):
    """A pause of ours, or an auto pause (a red canary, it names a job) born inside a window: the fault's own doing."""
    if not pz:
        return False
    if MARK in (pz.get("reason") or ""):
        return True
    return bool(pz.get("job")) and bool(pz.get("since")) and window_of((epoch(pz["since"]),) * 2, windows) is not None


def _to_verify(st, now):
    st.update(phase="VERIFY", verify_since=now, quiet=0)


def step(st, a, fx, now):
    """One move of the machine. st is mutated; effects go through the module's functions."""
    phase = st.get("phase", "CLEAN")
    opened, windows = a["open"], a["windows"]
    if os.path.exists(T.q("fault_monitor.stop")) or retest_active():
        st["phase"] = "PASSIVE"
        return
    if phase == "PASSIVE":      # back in charge: a pause of ours still on means a recovery was under way
        phase = "CLEAN"
        st["phase"] = "CLEAN"
        if pause_is_ours(T.paused(), windows):
            _to_verify(st, now)
            phase = "VERIFY"
    uptime = now - a["boot"] if a["boot"] else 0
    new_boot = st.get("boot") is not None and a["boot"] is not None and a["boot"] > st["boot"]
    if new_boot and phase in ("WAIT_BOOT", "STUCK", "DRAIN"):
        st.pop("stuck", None)
        st.pop("alarm", None)
        _to_verify(st, now)
        phase = "VERIFY"
    if phase in ("CLEAN", "VERIFY") and opened:
        if phase == "VERIFY" and uptime < MIN_UPTIME_S:
            st.update(phase="STUCK", stuck="the fault is back %d s into a boot: a reboot does not clear it" % uptime)
            st["alarm"] = "STUCK " + st["stuck"]
            return
        if not opened.get("snapshot"):
            opened["snapshot"] = snapshot(opened)
        st.update(phase="DRAIN", quiet=0, window=opened["id"])
        phase = "DRAIN"
    if phase == "DRAIN":
        if not opened:      # cleared under us (a reboot that was not ours): nothing left to clear
            _to_verify(st, now)
            return
        pz = T.paused()
        if pz and not pause_is_ours(pz, windows):
            st["quiet"], st["why_held"] = 0, "a pause that is not ours: %s" % (pz.get("reason") or "")[:120]
            return
        if not pz:
            lane_pause("%s onset %s, CPUs %s: drain, reboot, verify" % (opened["id"], opened["first_bad"],
                                                                       opened["first_cpus"]))
        running = T.steve_running()
        busy = worker_busy()
        if running or busy is not False:
            st["quiet"], st["why_held"] = 0, "job running or worker busy (%s)" % busy
            return
        st.pop("why_held", None)
        st["quiet"] = st.get("quiet", 0) + 1
        if st["quiet"] < QUIET_TICKS:
            return
        recent = [t for t in st.get("reboots", []) if now - t < 86400]
        if len(recent) >= MAX_REBOOTS_DAY or uptime < MIN_UPTIME_S:
            why = "%d reboots in 24 h" % len(recent) if len(recent) >= MAX_REBOOTS_DAY else \
                "the fault is back %d s into a boot: a reboot does not clear it" % uptime
            st.update(phase="STUCK", stuck=why, alarm="STUCK " + why)
            return
        ok, out = reboot("Steve SIMD fault %s: drained, rebooting" % opened["id"])
        st["last_reboot_out"] = out
        if not ok:
            st["quiet"] = 0
            return
        st.update(phase="WAIT_BOOT", reboot_t0=now, reboots=recent + [now], boot_before=a["boot"])
        return
    if phase == "WAIT_BOOT":
        if now - st.get("reboot_t0", now) > BOOT_TIMEOUT_S:
            st["alarm"] = "NO_RETURN Steve not back %d s after the fault reboot" % (now - st["reboot_t0"])
        return
    if phase == "VERIFY":
        if a["clean_cycles"] >= CLEAN_TO_RESUME and not opened:
            pz = T.paused()
            if pause_is_ours(pz, windows):
                lane_resume("%d clean cycles on the new boot" % a["clean_cycles"])
            st.update(phase="CLEAN", quiet=0)
            st.pop("window", None)
            st.pop("alarm", None)
        elif now - st.get("verify_since", now) > BOOT_TIMEOUT_S:
            st["alarm"] = "VERIFY no clean cycles %d s into the new boot" % (now - st["verify_since"])
        return


def merge_mirror(lines):
    """Union of the mirror and what Steve just gave, by timestamp, so Steve's log can rotate and we still hold history."""
    path = T.q("fault_watch.log")
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read().splitlines()
    seen, out = set(), []
    for line in old + [li.rstrip() for li in lines]:
        if line.strip() and line not in seen:
            seen.add(line)
            out.append(line)
    out.sort(key=lambda li: li[:19])        # stable: a start line and a cycle of one second keep their log order
    if len(out) != len(old):
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
        os.replace(tmp, path)
    return out


def tick(now=None):
    now = time.time() if now is None else now
    T.ensure_dirs()
    _qdir()
    with open(T.q("fault_monitor.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        st = T.read_json(T.q("fault_state.json")) or {"phase": "CLEAN"}
        fx = steve_read()
        lines = merge_mirror(fx["lines"] if fx else [])
        # the highest boot ever seen, or a window a reboot closed would reopen when ssh fails before the next watch line
        a = analyse(lines, live_boot=max(fx["boot"] if fx else 0, st.get("boot") or 0) or None)
        anno = {w["id"]: w for w in T.read_json(T.q("fault_windows.json")) or []}
        for w in a["windows"]:
            if anno.get(w["id"], {}).get("snapshot"):
                w["snapshot"] = anno[w["id"]]["snapshot"]
        st.pop("blind", None)
        if fx:
            if a["boot"] and now - a["boot"] > BLIND_S and now - (a["last_cycle"] or 0) > BLIND_S:
                st["blind"] = "no canary cycle since %s" % (stamp(a["last_cycle"]) if a["last_cycle"] else "ever")
            step(st, a, fx, now)
        elif st.get("phase") == "WAIT_BOOT" and now - st.get("reboot_t0", now) > BOOT_TIMEOUT_S:
            st["alarm"] = "NO_RETURN Steve not back %d s after the fault reboot" % (now - st["reboot_t0"])
        st.update(schema="steve.fault/1", at=stamp(now), reachable=bool(fx), boot=a["boot"],
                  boot_iso=stamp(a["boot"]) if a["boot"] else None, last_cycle=stamp(a["last_cycle"]) if a["last_cycle"] else None,
                  clean_through=stamp(a["clean_through"]) if a["clean_through"] else None,
                  clean_through_s=a["clean_through"], open_window=a["open"]["id"] if a["open"] else None,
                  windows=len(a["windows"]), unparsed=a["unparsed"], control=a["control"])
        write_json("fault_windows.json", a["windows"])      # before the state: gate never reads a state ahead of its windows
        write_json("fault_state.json", st)
        print(json.dumps({k: st.get(k) for k in ("phase", "open_window", "last_cycle", "clean_through", "alarm", "blind")}))
    return 0


# ---------------------------------------------------------------- reading it

def jobs_in(w):
    """The Steve jobs that ran inside window W, wherever their record now lives -> [(job, mod, item, state)]."""
    out = []
    for state in ("quarantined", "done", "running"):
        for rec in T.records(state) if os.path.isdir(T.q(state)) else []:
            span = job_span(rec)
            if span and window_of(span, [w]):
                job = rec.get("job") or {}
                out.append((job.get("id"), job.get("mod"), job.get("item"), state))
    return sorted(out, key=lambda x: str(x[0]))


def report(_a=None):
    windows, st = load()
    if st is None:
        print("UNMEASURED: the monitor has not run (no fault_state.json)")
        return 1
    print("phase %s, boot %s, last cycle %s, clean through %s, open %s, alarm %s"
          % (st.get("phase"), st.get("boot_iso"), st.get("last_cycle"), st.get("clean_through"), st.get("open_window"),
             st.get("alarm")))
    print("%-20s %-21s %8s %-21s %-21s %5s %5s %s" % ("window", "last clean", "onset_h", "first bad", "end", "bad", "clean", "cpus"))
    for w in windows:
        print("%-20s %-21s %8.2f %-21s %-21s %5d %5d %s" % (
            w["id"], w["start"], w["onset_uptime_h"], w["first_bad"], w.get("end") or "OPEN", w["bad_cycles"], w["clean_after"],
            ",".join("%s:%d" % kv for kv in sorted(w["cpus"].items(), key=lambda kv: int(kv[0])))))
        jobs = jobs_in(w)
        under = [j for j in jobs if j[3] != "quarantined"]
        print("    %d jobs inside (%d not yet quarantined): %s" % (len(jobs), len(under), ", ".join(sorted({str(j[1]) for j in jobs}))))
        if w.get("snapshot"):
            print("    cause evidence: %s" % w["snapshot"])
    return 0


def check(_a=None, now=None):
    """Exit 0 when the reading is fresh and true to the queue; 1 with the reason on each failed line."""
    now = time.time() if now is None else now
    windows, st = load()
    if st is None:
        print("FAIL no fault_state.json: the monitor has never run")
        return 1
    bad = []
    age = now - epoch(st["at"])
    if age > STALE_S:
        bad.append("reading %d s old" % age)
    if st.get("unparsed"):
        bad.append("%d watch lines not understood: the parser no longer reads the canary" % st["unparsed"])
    if st.get("reachable") and st.get("blind"):
        bad.append("canary blind: %s" % st["blind"])
    if st.get("alarm"):
        bad.append("alarm: %s" % st["alarm"])
    nleft = 0
    for rec in T.records("done"):
        span = job_span(rec)
        if (rec.get("result") or {}).get("host", T.STEVE) == T.STEVE and span and window_of(span, windows) \
                and now - span[1] > 600:
            nleft += 1
    if nleft:
        bad.append("%d done records inside a fault window are not quarantined" % nleft)
    for line in bad:
        print("FAIL " + line)
    print("%s phase=%s reading_age=%ds windows=%d open=%s quarantined=%d last_cycle=%s" % (
        "BAD" if bad else "OK", st.get("phase"), age, len(windows), st.get("open_window"),
        len(os.listdir(T.q("quarantined"))) if os.path.isdir(T.q("quarantined")) else 0, st.get("last_cycle")))
    return 1 if bad else 0


def deploy_watch(_a=None):
    """Copy watch2.ps1 to Steve and restart its task, which starts a new watcher (its control line first)."""
    src = os.path.join(HERE, "..", "steve_cpu_retest", "watch2.ps1")
    with open(src, "rb") as f:
        body = base64.b64encode(f.read()).decode()
    rc, out = ps(r"""[IO.File]::WriteAllBytes('%s',[Convert]::FromBase64String('%s'))
Stop-ScheduledTask -TaskName 'SteveDiag Fault Watch' -EA 0
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'"|?{$_.CommandLine -match 'watch2\.ps1'}|%%{Stop-Process -Id $_.ProcessId -Force -EA 0}
Start-ScheduledTask -TaskName 'SteveDiag Fault Watch'
Get-ScheduledTask -TaskName 'SteveDiag Fault Watch'|%%{'TASK '+$_.State}""" % (WATCH_PS1, body))
    print(rc, out.strip()[-200:])
    return 0 if rc == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", choices=("tick", "report", "check", "deploy-watch"))
    a = ap.parse_args()
    return {"tick": tick, "report": report, "check": check, "deploy-watch": deploy_watch}[a.cmd]() or 0


if __name__ == "__main__":
    sys.exit(main())
