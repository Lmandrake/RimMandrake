#!/usr/bin/env python3
"""steve_cpu_sweep.py - ONE-OFF per-core CPU load sweep of SteveDesktop. No reboot, no state machine, no numproc change.
(Owner 2026-11-17: "a small one-off sweep mode sounds like a good idea to have given Steve Desktop's behavior.")

For each logical CPU in turn: Prime95 torture pinned to that CPU for SECS seconds (default 60; 18 CPUs ~ 20 min),
stevetemp.exe sampling package/core temperature and vcore under that load, WHEA-Logger events in the window.
Per CPU: PASS, or FAIL = Prime95 error (FATAL / hardware failure in results.txt), WHEA event, Prime95 died early, or no answer.
A missing sensor reading is None / UNMEASURED, never 0.
Refuses to start if a testq job runs, the worker is busy or unknown, RimWorld or Prime95 is already running on Steve, or
Prime95 is missing. Yields (stops cleanly) between CPUs when a job arrives, RimWorld starts, or Steve rebooted.
Prime95 is killed on every exit path (try/finally on Steve, and again here). fault_monitor / watch2 are never touched.
Usage: steve_cpu_sweep.py run [--secs N] [--cpus LO-HI] [--out FILE.json]  |  merge A.json B.json --out FILE.json     (the pure decisions are what selftest_steve_cpu_retest checks)
"""
import json, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steve_cpu_retest as rt

OUT_DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/steve_diag/retest/sweep_%s.json"
D = r"C:\SteveDesktop\diag"


def _kv(line):
    return dict(p.split("=", 1) for p in line.split() if "=" in p)


def parse_pre(text):
    for line in text.splitlines():
        if line.startswith("PRE "):
            return _kv(line)
    return {}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_heat(heat):
    """stevetemp's one line -> {pkg_max_c, core_max_c, vcore}; any missing piece is None (UNMEASURED), never 0."""
    m = re.search(r"pkg_c=(\d+)/(\d+) core_max_c=(\d+)", heat or "")
    v = re.search(r"vcore_v=([\d.]+)", heat or "")
    return {"pkg_max_c": int(m.group(2)) if m else None, "core_max_c": int(m.group(3)) if m else None,
            "vcore": float(v.group(1)) if v else None}


def parse_core(text):
    for line in text.splitlines():
        if line.startswith("SWEEPCORE "):
            head, _, heat = line.partition(" heat=")
            d = _kv(head)
            d["heat"] = heat
            return d
    return {}


def core_result(d, cpu):
    """One CPU's record. FAIL on a Prime95 error, a WHEA event, a worker that died early, or no answer."""
    r = {"cpu": cpu, "status": "FAIL", "why": []}
    if not d or "fatal" not in d:
        r["why"].append("NO_ANSWER")
        r.update(parse_heat(""))
        return r
    fatal, whea = int(_num(d.get("fatal")) or 0), int(_num(d.get("whea")) or 0)
    alive, cpusec = d.get("alive") == "1", _num(d.get("cpusec"))
    if fatal:
        r["why"].append("prime95_error x%d" % fatal)
    if whea:
        r["why"].append("WHEA x%d" % whea)
    if not alive:
        r["why"].append("prime95_died_early")
    r.update(fatal=fatal, whea=whea, alive=alive, cpusec=cpusec)
    r.update(parse_heat(d.get("heat", "")))
    if not r["why"]:
        r["status"] = "PASS"
    return r


def decide_start(pre, job_files, worker_busy):
    if not pre:
        return False, "Steve unreachable or preflight unreadable"
    if pre.get("p95") != "1":
        return False, "Prime95 missing on Steve"
    if job_files:
        return False, "testq job running: %s" % [os.path.basename(p) for p in job_files]
    if worker_busy is not False:
        return False, "worker busy=%s" % worker_busy
    if pre.get("rimworld", "0") != "0":
        return False, "RimWorld running on Steve"
    if pre.get("p95run", "0") != "0":
        return False, "Prime95 already running on Steve"
    return True, "idle"


def decide_continue(job_files, worker_busy, rimworld, boot0, boot_now):
    if job_files:
        return False, "job arrived: %s" % [os.path.basename(p) for p in job_files]
    if worker_busy is True:
        return False, "worker became busy"
    if str(rimworld) != "0":
        return False, "RimWorld started"
    if boot_now is not None and boot_now != boot0:
        return False, "Steve rebooted (boot %s -> %s)" % (boot0, boot_now)
    return True, "quiet"


def summarize(cores, idle_vcore, stopped):
    failed = [c["cpu"] for c in cores if c["status"] == "FAIL"]
    vs = [c["vcore"] for c in cores if c.get("vcore") is not None]
    ts = [c["core_max_c"] for c in cores if c.get("core_max_c") is not None]
    vmax = max(vs) if vs else None
    if stopped:
        verdict = "YIELDED" if not failed else "FAIL"
    elif failed:
        verdict = "FAIL"
    elif not vs or not ts:
        verdict = "PASS_UNMEASURED_HEAT"
    else:
        verdict = "PASS"
    f = lambda x, u: ("%s %s" % (x, u)) if x is not None else "UNMEASURED"
    line = ("SteveDesktop per-core load sweep: %s - %d CPU(s) read, failed %s; vcore under load max %s vs idle %s; hottest core %s%s"
            % (verdict, len(cores), failed or "none", f(vmax, "V"), f(idle_vcore, "V"), f(max(ts) if ts else None, "C"),
               ("; stopped: %s" % stopped) if stopped else ""))
    return {"verdict": verdict, "n_read": len(cores), "failed": failed, "vcore_load_max": vmax, "vcore_idle": idle_vcore,
            "core_max_c": max(ts) if ts else None, "stopped": stopped, "line": line}


PRE_PS = r"""$d='@D@'; $n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$b=([DateTimeOffset](Get-CimInstance Win32_OperatingSystem).LastBootUpTime).ToUniversalTime().ToUnixTimeSeconds()
$rw=@(Get-Process RimWorldWin64 -EA 0).Count; $pr=@(Get-Process prime95 -EA 0).Count
$t='';if(Test-Path "$d\heat\stevetemp.exe"){ $t=(& "$d\heat\stevetemp.exe" 4 500 2>&1 | Select -Last 1) }
$v=[regex]::Match("$t",'vcore_v=([\d.]+)').Groups[1].Value
"PRE n=$n p95=$([int](Test-Path "$d\p95\prime95.exe")) temp=$([int](Test-Path "$d\heat\stevetemp.exe")) rimworld=$rw p95run=$pr boot=$b vcore_idle=$v"
"""

# one CPU: sampler + pinned Prime95 for @S@ s; everything torn down in finally. Kept small: the ssh command line is limited.
CORE_PS = r"""$d='@D@'; $p="$d\p95"; $ho="$d\logs\sweep-heat.txt"; $hs="$d\logs\sweep-heat.stop"; $t0=Get-Date; $h='UNMEASURED(no_sampler)'; $f=0;$s=-1;$a=0;$w=0
try{ Remove-Item $ho,$hs,"$p\results.txt" -EA 0
 "V24OptionsConverted=1`r`nStressTester=1`r`nUsePrimenet=0`r`nEnableSetAffinity=0`r`nEnableSetPriority=0`r`nMinTortureFFT=8`r`nMaxTortureFFT=128`r`nTortureMem=0`r`nTortureTime=1`r`nNumCores=@W@`r`nTortureHyperthreading=0`r`nNumWorkers=@W@`r`nCoresPerTest=1" | Set-Content "$p\prime.txt"
 if(Test-Path "$d\heat\stevetemp.exe"){ $sp=Start-Process "$d\heat\stevetemp.exe" -ArgumentList @('@T@','500',$hs) -RedirectStandardOutput $ho -WindowStyle Hidden -PassThru }
 Start-Process cmd.exe -ArgumentList "/c start `"`" /affinity @H@ prime95.exe -t" -WorkingDirectory $p -WindowStyle Hidden
 Start-Sleep @S@; $pr=Get-Process prime95 -EA 0|Select -First 1; if($pr){$a=1;$s=[int]$pr.TotalProcessorTime.TotalSeconds}
 if(Test-Path "$p\results.txt"){ $f=@(Get-Content "$p\results.txt"|?{$_ -match 'FATAL|[Hh]ardware failure|Possible hardware'}).Count }
 if($sp){ New-Item -ItemType File -Force $hs | Out-Null; if($sp.WaitForExit(20000)){ $l=@(Get-Content $ho -EA 0|?{$_.Trim()}); if($l.Count){$h=$l[-1].Trim()}else{$h='UNMEASURED(no_output)'} }else{ try{$sp.Kill()}catch{}; $h='UNMEASURED(sampler_hung)' } }
 $w=@(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-WHEA-Logger';StartTime=$t0} -EA 0).Count
}finally{ Get-Process prime95 -EA 0|Stop-Process -Force; Get-Process stevetemp -EA 0|?{$_.StartTime -ge $t0}|Stop-Process -Force }
"SWEEPCORE cpu=@C@ alive=$a cpusec=$s fatal=$f whea=$w heat=$h"
"""


def core_script(cpu, secs, mask=None, workers=1):
    return (CORE_PS.replace("@W@", str(workers)).replace("@D@", D).replace("@S@", str(secs)).replace("@T@", str(secs + 20))
            .replace("@H@", "%x" % (mask if mask else 1 << cpu)).replace("@C@", str(cpu)))


def kill_prime95():
    return rt.ps(r"Get-Process prime95 -EA 0|Stop-Process -Force; 'KILLED'", 60)


def run(secs=60, out=None, cpus=None):
    out = out or OUT_DEFAULT % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    os.makedirs(os.path.dirname(out), exist_ok=True)
    rc, o = rt.ps(PRE_PS.replace("@D@", D), 90)
    pre = parse_pre(o)
    ok, why = decide_start(pre, rt.lane_job_running(), rt.worker_busy())
    res = {"started": rt.now(), "secs_per_cpu": secs, "pre": pre}
    cores, stopped = [], None
    if not ok:
        stopped = "REFUSED: " + why
        res.update(summarize(cores, None, stopped), verdict="REFUSED")
        res["cores"] = cores
        json.dump(res, open(out, "w"), indent=1)
        print("REFUSED: " + why, "-> result:", out)
        return res
    n, boot0, idle = int(pre["n"]), pre["boot"], _num(pre.get("vcore_idle"))
    try:
        for cpu in (cpus if cpus is not None else range(n)):
            rc, o = rt.ps(core_script(cpu, secs), secs + 120)
            if rc is None:       # ssh down: Steve may have faulted or rebooted - that is a result, no retry
                cores.append(core_result({}, cpu))
                cores[-1]["why"] = ["STEVE_UNREACHABLE_DURING_CPU"]
                stopped = "Steve unreachable during CPU %d (fault or reboot?)" % cpu
                break
            cores.append(core_result(parse_core(o), cpu))
            print("cpu %d %s %s vcore=%s core_max_c=%s (%d/%d)" % (cpu, cores[-1]["status"], cores[-1]["why"] or "",
                  cores[-1].get("vcore"), cores[-1].get("core_max_c"), len(cores), len(cpus or range(n))), flush=True)
            if cpu != (cpus or range(n))[-1]:
                f = rt.steve_facts()
                go, why = decide_continue(rt.lane_job_running(), rt.worker_busy(), (f or {}).get("rimworld", "0"), boot0,
                                          (f or {}).get("boot"))
                if not go:
                    stopped = "yielded: " + why
                    break
    finally:
        kill_prime95()
    res.update(summarize(cores, idle, stopped))
    res["cores"], res["ended"] = cores, rt.now()
    json.dump(res, open(out, "w"), indent=1)
    print(res["line"])
    print("result:", out)
    return res


def allcore(secs=30, out=None):
    """After the sweep: ALL logical CPUs loaded at once (what a RimWorld job does) - the vcore a single pinned core never shows."""
    rc, o = rt.ps(PRE_PS.replace("@D@", D), 90)
    pre = parse_pre(o)
    ok, why = decide_start(pre, rt.lane_job_running(), rt.worker_busy())
    if not ok:
        print("REFUSED: " + why)
        return None
    n = int(pre["n"])
    try:
        rc, o = rt.ps(core_script(0, secs, (1 << n) - 1, n), secs + 120)
        r = core_result(parse_core(o), -1)
    finally:
        kill_prime95()
    r["workers"] = n
    print("allcore", r["status"], r["why"], "vcore=%s core_max_c=%s pkg_max_c=%s" % (r.get("vcore"), r.get("core_max_c"), r.get("pkg_max_c")))
    if out:
        json.dump({"pre": pre, "allcore": r, "ts": rt.now()}, open(out, "w"), indent=1)
    return r


def merge(paths, out):
    """Chunked runs (a foreground call is limited to ~9 min) -> one result; idle vcore from the first chunk."""
    parts = [json.load(open(p)) for p in paths]
    cores = [c for p in parts for c in p.get("cores", [])]
    stopped = next((p["stopped"] for p in parts if p.get("stopped")), None)
    res = {"started": parts[0]["started"], "ended": parts[-1].get("ended"), "secs_per_cpu": parts[0]["secs_per_cpu"],
           "pre": parts[0]["pre"], "chunks": paths}
    res.update(summarize(cores, parts[0].get("vcore_idle"), stopped))
    res["cores"] = cores
    json.dump(res, open(out, "w"), indent=1)
    print(res["line"])
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "run":
        secs = int(a[a.index("--secs") + 1]) if "--secs" in a else 60
        out = a[a.index("--out") + 1] if "--out" in a else None
        cp = None
        if "--cpus" in a:
            lo, _, hi = a[a.index("--cpus") + 1].partition("-")
            cp = list(range(int(lo), int(hi or lo) + 1))
        run(secs, out, cp)
    elif a and a[0] == "allcore":
        allcore(int(a[a.index("--secs") + 1]) if "--secs" in a else 30, a[a.index("--out") + 1] if "--out" in a else None)
    elif a and a[0] == "merge":
        merge(a[a.index("--out") + 1:][:1] and a[1:a.index("--out")], a[a.index("--out") + 1])
    else:
        print(__doc__)
