#!/usr/bin/env python3
"""regprobe.py - build, install and run SteveDesktop's register probe (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS).

  build              regprobe.exe and regprobe_inject.exe (the RED build: VZEROUPPER in every real AVX hold) from regprobe.c +
                     regprobe_asm.S with MinGW-w64, into <agent storage>/rimmandrake/build/regprobe/. The compiler is the
                     Ubuntu mingw-w64 packages unpacked (no root) under <agent storage>/rimmandrake/build/mingw_w64/root; a
                     missing one is fetched with `apt download` + `dpkg -x`.
  once <normal|inject> [--log <windows path>]
                     copy that build to Steve and run it once (control + one cycle) into a test log (never the live one);
                     prints the log's lines and the verdict; exit = the probe's (0 clean, 1 fault, 2 could not look).
  install            copy regprobe.exe to C:\\SteveDesktop\\diag\\regprobe\\, register the task "SteveDiag Register Probe"
                     (SYSTEM, at startup, restart on failure) and start it. Stops nothing else; the old probe process, if
                     any, is replaced.
  status             the task's state, the process, and the newest lines of the live log.
Read the live log's verdict with `python3 src/RimMandrake/Utils/testq/fault_monitor.py regprobe` (from the tick's mirror).
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "testq"))
import fault_monitor as FM  # noqa: E402

STEVE_DIR = r"C:\SteveDesktop\diag\regprobe"
LIVE_LOG = FM.REGPROBE_LOG
TASK = "SteveDiag Register Probe"
# timeouts below: a hung local call (apt on a dead mirror, a stuck drvfs read) would hold the tool for ever; each bound is
# several times the measured time (2026-11-20: apt download 64 MB in 1 s, a build ~5 s from D:).
PKGS = ["gcc-mingw-w64-x86-64-posix", "gcc-mingw-w64-x86-64-posix-runtime", "binutils-mingw-w64-x86-64",
        "mingw-w64-x86-64-dev", "gcc-mingw-w64-base", "binutils-mingw-w64-base", "mingw-w64-common"]


def storage():
    r = subprocess.run([sys.executable, os.path.expanduser("~/dev/Lodestar/bin/lib/agent_storage.py")], capture_output=True,
                       text=True, timeout=60)
    if r.returncode or not r.stdout.strip():
        raise SystemExit("FAIL agent_storage.py gave no root: %s" % r.stderr.strip()[-200:])
    return os.path.join(r.stdout.strip(), "rimmandrake", "build")


def compiler():
    root = os.path.join(storage(), "mingw_w64", "root")
    gcc = os.path.join(root, "usr", "bin", "x86_64-w64-mingw32-gcc-13-posix")
    if not os.path.exists(gcc):
        debs = os.path.join(storage(), "mingw_w64", "debs")
        os.makedirs(debs, exist_ok=True)
        subprocess.run(["apt", "download"] + PKGS, cwd=debs, check=True, timeout=900)
        for f in sorted(os.listdir(debs)):
            if f.endswith(".deb"):
                subprocess.run(["dpkg", "-x", os.path.join(debs, f), root], check=True, timeout=300)
    if not os.path.exists(gcc):
        raise SystemExit("FAIL no MinGW-w64 gcc at %s after unpacking" % gcc)
    return gcc


def build(_a=None):
    gcc, out = compiler(), os.path.join(storage(), "regprobe")
    os.makedirs(out, exist_ok=True)
    srcs = [os.path.join(HERE, "regprobe.c"), os.path.join(HERE, "regprobe_asm.S")]
    for name, extra in (("regprobe.exe", []), ("regprobe_inject.exe", ["-DRP_FORCE_INJECT=1"])):
        r = subprocess.run([gcc, "-O2", "-Wall", "-Wno-unused-function", "-static", "-o", os.path.join(out, name)] + extra + srcs
                           + ["-lwinmm"], capture_output=True, text=True, timeout=600)
        if r.returncode:
            raise SystemExit("FAIL build %s:\n%s" % (name, r.stderr[-2000:]))
        print("BUILT %s" % os.path.join(out, name))
    return 0


def _up(name):
    path = os.path.join(storage(), "regprobe", name)
    if not os.path.exists(path):
        build()
    rc, out = FM.ps("New-Item -ItemType Directory -Force '%s' | Out-Null; 'MKDIR ok'" % STEVE_DIR)
    if rc != 0:
        raise SystemExit("FAIL Steve unreachable or mkdir refused (%s): %s" % (rc, out.strip()[-200:]))
    FM.scp_to(path, STEVE_DIR)


def once(a):
    name = "regprobe_inject.exe" if a.build == "inject" else "regprobe.exe"
    log = a.log or STEVE_DIR + "\\once_%s.log" % a.build
    if log.lower() == LIVE_LOG.lower():
        raise SystemExit("REFUSED: a --once run never writes the live log %s" % LIVE_LOG)
    _up(name)
    rc, out = FM.ps(r"""Remove-Item '%s' -EA 0
$o=& '%s\%s' --once --log '%s'; $rc=$LASTEXITCODE
'EXIT '+$rc; $o; 'LOG'; Get-Content '%s'""" % (log, STEVE_DIR, name, log, log), timeout=300)
    print(out.rstrip())
    if rc is None:
        print("FAIL Steve unreachable")
        return 2
    ex = [li for li in out.splitlines() if li.startswith("EXIT ")]
    return int(ex[0].split()[1]) if ex else 2


INSTALL_PS = r"""$ErrorActionPreference='Stop'; $d='@DIR@'
Stop-ScheduledTask -TaskName '@TASK@' -EA 0
Get-Process regprobe -EA 0 | ?{$_.Path -eq "$d\regprobe.exe"} | Stop-Process -Force -EA 0
Start-Sleep 1
Copy-Item -Force "$d\regprobe.exe.new" "$d\regprobe.exe"
$a=New-ScheduledTaskAction -Execute "$d\regprobe.exe" -WorkingDirectory $d
$t=New-ScheduledTaskTrigger -AtStartup
$p=New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName '@TASK@' -TaskPath '\' -Action $a -Trigger $t -Principal $p -Settings $s -Description 'YMM/XMM/GPR register-hold probe every 5 min (RIMMANDRAKE_BUILD_STEVE_REGISTER_PROBE_SEES_UPPER_HALF_LOSS)' -Force | Out-Null
Start-ScheduledTask -TaskName '@TASK@'
Start-Sleep 20
Get-ScheduledTask -TaskName '@TASK@' | %{'TASK '+$_.State}
Get-Process regprobe -EA 0 | %{'PROC '+$_.Id+' '+$_.Path}
'LOG'; if(Test-Path '@LOG@'){Get-Content '@LOG@' -Tail 4}
"""


def install(_a=None):
    path = os.path.join(storage(), "regprobe", "regprobe.exe")
    build()
    staged = path + ".new"
    shutil.copyfile(path, staged)
    _up("regprobe.exe.new")
    rc, out = FM.ps(INSTALL_PS.replace("@DIR@", STEVE_DIR).replace("@TASK@", TASK).replace("@LOG@", LIVE_LOG), timeout=180)
    print(out.rstrip())
    ok = rc == 0 and "TASK Running" in out and "PROC " in out
    print("INSTALLED" if ok else "FAIL install (rc %s)" % rc)
    return 0 if ok else 1


def status(_a=None):
    rc, out = FM.ps(r"""Get-ScheduledTask -TaskName '%s' -EA 0 | %%{'TASK '+$_.State}
Get-Process regprobe -EA 0 | %%{'PROC '+$_.Id+' '+$_.StartTime.ToUniversalTime().ToString('s')+'Z'}
'LOG'; if(Test-Path '%s'){Get-Content '%s' -Tail 6}else{'NO LOG'}""" % (TASK, LIVE_LOG, LIVE_LOG))
    print(out.rstrip() if rc is not None else "UNMEASURED: Steve unreachable")
    return 0 if rc == 0 and "TASK Running" in out else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    o = sub.add_parser("once")
    o.add_argument("build", choices=("normal", "inject"))
    o.add_argument("--log")
    sub.add_parser("install")
    sub.add_parser("status")
    a = ap.parse_args()
    return {"build": build, "once": once, "install": install, "status": status}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
