#!/usr/bin/env python3
"""steve_cpu_retest.py - drain-triggered unmask retest of SteveDesktop CPUs 18 and 19.
(CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH)

A systemd user timer on the PC runs `tick` every 60 s. State machine (state.json):
  DRAIN       lane paused (no new jobs); wait until no testq job runs, the worker is idle, no RimWorld on Steve,
              for two ticks in a row
  REBOOT_OFF  bcdedit export + deletevalue numproc, armed.flag, shutdown /r
  WAIT_BOOT   wait for a newer boot with 20 logical CPUs; resume the lane (the load); steve-side tasks take over
  RUNNING     mirror readings.jsonl; watch fault.json / done.json
  FAULT_DRAIN a fault: stop, pause the lane, wait for it to drain
  REBOOT_RESTORE bcdedit /set numproc 18, shutdown /r
  WAIT_RESTORE   wait for the boot with 18 CPUs, resume the lane           -> END_FAULT
  DONE_CLEAN  clean past the onset time: leave unmasked, final
Never reboots while a job runs. Persistent log: <HOME>/events.jsonl, readings mirror <HOME>/readings.jsonl.
Subcommands: tick | status | arm | install-timer
"""
import base64, fcntl, json, os, subprocess, sys, time, glob

HOME = os.environ.get("STEVE_RETEST_HOME", "/mnt/d/ClaudeWork/rimmandrake/steve_diag/retest")
TESTQ_HOME = os.environ.get("TESTQ_HOME", "/mnt/d/ClaudeWork/rimmandrake/testq")
TESTQ = os.environ.get("TESTQ_PY", "/home/mandrake/rm/bench/src/RimMandrake/Utils/testq/testq.py")
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR", "stevedesktop"]
WSL = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR", "mandrake@stevedesktop-wsl"]
D = r"C:\SteveDesktop\diag"
R = D + r"\retest"
BOOT_TIMEOUT_S = 40 * 60
ONSET_H = 144   # old onset: unknown, <= ~5 d of uptime (absent at the 10-26 boot, present 10-31 ~17:16Z); 6 d used


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(event, **kw):
    os.makedirs(HOME, exist_ok=True)
    rec = {"ts": now(), "event": event}
    rec.update(kw)
    with open(os.path.join(HOME, "events.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec))


def load():
    try:
        return json.load(open(os.path.join(HOME, "state.json")))
    except (OSError, ValueError):
        return None


def save(st):
    tmp = os.path.join(HOME, "state.json.tmp")
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, os.path.join(HOME, "state.json"))


def ps(script, timeout=90):
    """Run PowerShell on Steve (EncodedCommand UTF-16LE base64). -> (rc, stdout) ; rc None = ssh down."""
    enc = base64.b64encode(script.encode("utf-16-le")).decode()
    try:
        r = subprocess.run(SSH + ["powershell -NoProfile -NonInteractive -EncodedCommand " + enc],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, ""
    if r.returncode == 255:
        return None, ""
    out = r.stdout
    return r.returncode, out


def testq(*a):
    r = subprocess.run([sys.executable, TESTQ] + list(a), capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def lane_paused():
    return os.path.exists(os.path.join(TESTQ_HOME, "paused.json"))


def lane_job_running():
    return glob.glob(os.path.join(TESTQ_HOME, "running", "*.json"))


def ensure_paused(reason):
    if not lane_paused():
        rc, o = testq("pause", "--reason", reason, "--hours", "12")
        log("lane_pause", rc=rc, out=o[-200:])


def worker_busy():
    """True / False, None when unknown. Asks the runner's worker over the WSL door."""
    try:
        r = subprocess.run(WSL + ["cd ~/rm/runner && python3 infrastructure/stevedesktop/worker.py status"], capture_output=True, text=True, timeout=60)
        for line in reversed(r.stdout.strip().splitlines()):
            if line.startswith("{"):
                return bool(json.loads(line).get("busy"))
    except Exception:
        pass
    return None


def steve_facts():
    rc, o = ps(r"""$o=Get-CimInstance Win32_OperatingSystem; $n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$rw=@(Get-Process RimWorldWin64 -EA 0).Count
$np=(bcdedit /enum '{current}' | Select-String '^numproc\s+(\d+)' | % { $_.Matches[0].Groups[1].Value })
$b=([DateTimeOffset]$o.LastBootUpTime).ToUnixTimeSeconds()
"FACTS boot=$b cpus=$n rimworld=$rw numproc=$np"
""")
    if rc is None:
        return None
    for line in o.splitlines():
        if line.startswith("FACTS "):
            return {k: v for k, v in (p.split("=") for p in line[6:].split())}
    return None


def mirror_readings():
    rc, o = ps(r"if(Test-Path C:\SteveDesktop\diag\retest\readings.jsonl){Get-Content C:\SteveDesktop\diag\retest\readings.jsonl}", 60)
    lines = [l for l in o.splitlines() if l.startswith("{")]
    if lines:
        p = os.path.join(HOME, "readings.jsonl")
        old = sum(1 for _ in open(p)) if os.path.exists(p) else 0
        if len(lines) >= old:
            open(p, "w").write("\n".join(lines) + "\n")
    return lines


def steve_json(name):
    rc, o = ps(r"if(Test-Path %s\%s){Get-Content %s\%s -Raw}" % (R, name, R, name), 60)
    if rc is None:
        return None
    s = o[o.find("{"):] if "{" in o else ""
    try:
        return json.loads(s[: s.rfind("}") + 1])
    except ValueError:
        return {}


def reboot(st, why):
    st["reboot_t0"] = int(time.time())
    save(st)
    rc, o = ps(r'shutdown /r /t 15 /c "%s"' % why)
    log("reboot_sent", why=why, rc=rc, out=o.strip()[-200:])


def tick():
    st = load()
    if not st or st["state"] in ("DONE_CLEAN", "END_FAULT", "ABORTED", "DISARMED"):
        return
    s = st["state"]
    if s == "DRAIN":
        ensure_paused("CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH: drain for unmask reboot (current job finishes, none admitted)")
        why = []
        if lane_job_running():
            why.append("job running %s" % [os.path.basename(p) for p in lane_job_running()])
        wb = worker_busy()
        if wb is not False:
            why.append("worker busy=%s" % wb)
        f = steve_facts()
        if f is None:
            why.append("steve unreachable")
        elif f["rimworld"] != "0":
            why.append("RimWorld running")
        if why:
            st["quiet"] = 0
            if st.get("last_why") != why:
                log("drain_wait", why=why)
            st["last_why"] = why
            save(st)
            return
        st["quiet"] = st.get("quiet", 0) + 1
        save(st)
        if st["quiet"] < 2:
            return
        st["state"] = "REBOOT_OFF"
        st["drained_at"] = now()
        log("drained", facts=f)
        save(st)
        s = "REBOOT_OFF"
    if s == "REBOOT_OFF":
        f = steve_facts()
        if lane_job_running() or worker_busy() is not False or f is None or f["rimworld"] != "0":   # slipped in: wait again
            st["state"], st["quiet"] = "DRAIN", 0
            save(st)
            return
        rc, o = ps(r"""$ErrorActionPreference='Stop'
$r='@R@'; New-Item -ItemType Directory -Force $r | Out-Null
$before=(bcdedit /enum '{current}') -join "`n"; Set-Content "$r\bcd.current.before-unmask.txt" $before
if(-not (Test-Path "$r\bcd.before-unmask")){ bcdedit /export "$r\bcd.before-unmask" | Out-Null }
bcdedit /deletevalue numproc | Out-Null
$after=(bcdedit /enum '{current}') -join "`n"; Set-Content "$r\bcd.current.after-unmask.txt" $after
Remove-Item "$r\fault.json","$r\done.json" -EA 0
Set-Content "$r\armed.flag" (Get-Date).ToUniversalTime().ToString('s')
"NUMPROC_LEFT=" + ([regex]::Matches($after,'(?m)^numproc').Count)
Get-ScheduledTask 'SteveDiag CPU Retest','SteveDiag Fault Watch' | % { "TASK " + $_.TaskName + " " + $_.State }
""".replace("@R@", R))
        log("unmask", before=f, rc=rc, out=o.strip()[-400:])
        if rc != 0 or "NUMPROC_LEFT=0" not in o:
            st["state"] = "ABORTED"
            log("ABORT_unmask_failed")
            save(st)
            return
        st["state"] = "WAIT_BOOT"
        st["boot_before"] = f["boot"] if f else None
        reboot(st, "CPU retest: numproc mask removed")
        save(st)
        return
    if s in ("WAIT_BOOT", "WAIT_RESTORE"):
        f = steve_facts()
        waited = time.time() - st["reboot_t0"]
        if f is None or int(f["boot"]) < st["reboot_t0"]:
            if waited > BOOT_TIMEOUT_S and not st.get("alerted"):
                st["alerted"] = True
                log("ALERT_NO_RETURN", waited_s=int(waited), state=s)
                save(st)
            return
        want = "20" if s == "WAIT_BOOT" else "18"
        log("back", cpus=f["cpus"], numproc=f["numproc"], boot=f["boot"], waited_s=int(waited), want=want)
        if f["cpus"] != want and s == "WAIT_BOOT":
            log("ALERT_CPU_COUNT", cpus=f["cpus"], want=want)
            st["fault"] = {"event": "cpu_count", "cpus": f["cpus"]}
            st["state"] = "REBOOT_RESTORE"          # put the mask back; reboot is safe, lane still paused
            save(st)
            return
        rc, o = testq("resume", "--reason", "CPU retest: Steve back with %s CPUs; lane resumed as the retest load" % f["cpus"]
                      if s == "WAIT_BOOT" else "CPU retest: mask restored after fault; lane resumed")
        log("lane_resume", rc=rc, out=o[-160:])
        st["state"] = "RUNNING" if s == "WAIT_BOOT" else "END_FAULT"
        st["boot"] = f["boot"]
        st["running_since"] = now()
        save(st)
        return
    if s == "RUNNING":
        f = steve_facts()
        if f is None:
            return
        if f["boot"] != st.get("boot"):
            log("BOOT_CHANGED", old=st.get("boot"), new=f["boot"], cpus=f["cpus"])
            st["boot"] = f["boot"]
            save(st)
        lines = mirror_readings()
        fault = steve_json("fault.json")
        if fault:
            log("FAULT", fault=fault)
            st.update(state="FAULT_DRAIN", fault=fault, quiet=0)
            save(st)
            ensure_paused("CPU retest FAULT: drain, restore numproc 18, reboot")
            return
        done = steve_json("done.json")
        if done:
            log("DONE_CLEAN", done=done, readings=len(lines))
            ps(r"Remove-Item C:\SteveDesktop\diag\retest\armed.flag -EA 0")
            st["state"] = "DONE_CLEAN"
            save(st)
            return
        if f["cpus"] != "20":
            log("RUNNING_BUT_CPUS", cpus=f["cpus"])
        return
    if s == "FAULT_DRAIN":
        ensure_paused("CPU retest FAULT: drain, restore numproc 18, reboot")
        busy = lane_job_running() or worker_busy() is not False
        f = steve_facts()
        if busy or f is None or f["rimworld"] != "0":
            st["quiet"] = 0
            save(st)
            return
        st["quiet"] = st.get("quiet", 0) + 1
        save(st)
        if st["quiet"] < 2:
            return
        st["state"] = "REBOOT_RESTORE"
        save(st)
        s = "REBOOT_RESTORE"
    if s == "REBOOT_RESTORE":
        if lane_job_running():
            return
        mirror_readings()
        rc, o = ps(r"""$r='@R@'; bcdedit /set numproc 18 | Out-Null
Remove-Item "$r\armed.flag" -EA 0
"NUMPROC=" + ((bcdedit /enum '{current}' | Select-String '^numproc\s+(\d+)' | % { $_.Matches[0].Groups[1].Value }))""".replace("@R@", R))
        log("restore_numproc", rc=rc, out=o.strip()[-100:])
        if "NUMPROC=18" not in o:
            return
        st["state"] = "WAIT_RESTORE"
        reboot(st, "CPU retest fault: numproc 18 restored")
        save(st)


def cmd_arm():
    os.makedirs(HOME, exist_ok=True)
    if load() and load()["state"] not in ("DONE_CLEAN", "END_FAULT", "ABORTED"):
        print("already armed:", load()["state"])
        return
    save({"state": "DRAIN", "armed_at": now(), "onset_h": ONSET_H, "quiet": 0})
    log("armed", onset_h=ONSET_H, note="drain trigger: lane paused, wait for no running job + idle worker + no RimWorld, 2 ticks")
    ensure_paused("CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH: drain for unmask reboot (current job finishes, none admitted)")


UNIT = """[Unit]
Description=Steve CPU 18/19 unmask retest controller (CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH)

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {path} tick
TimeoutStartSec=300
"""
TIMER = """[Unit]
Description=Steve CPU retest tick

[Timer]
OnBootSec=60
OnUnitActiveSec=60
AccuracySec=5s

[Install]
WantedBy=timers.target
"""


def cmd_install():
    ud = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(ud, exist_ok=True)
    dst = os.path.join(HOME, "steve_cpu_retest.py")
    os.makedirs(HOME, exist_ok=True)
    src = open(os.path.abspath(__file__)).read()
    open(dst, "w").write(src)
    # the installed copy finds testq next to the repo copy
    open(os.path.join(ud, "steve-cpu-retest.service"), "w").write(UNIT.format(path=dst))
    open(os.path.join(ud, "steve-cpu-retest.timer"), "w").write(TIMER)
    for a in (["daemon-reload"], ["enable", "--now", "steve-cpu-retest.timer"]):
        r = subprocess.run(["systemctl", "--user"] + a, capture_output=True, text=True)
        print("systemctl --user", " ".join(a), r.returncode, r.stderr.strip()[-150:])


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    os.makedirs(HOME, exist_ok=True)
    if cmd == "status":
        print(json.dumps(load(), indent=1))
        return
    if cmd == "install-timer":
        return cmd_install()
    with open(os.path.join(HOME, "tick.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        if cmd == "arm":
            return cmd_arm()
        if cmd == "tick":
            return tick()


if __name__ == "__main__":
    main()
