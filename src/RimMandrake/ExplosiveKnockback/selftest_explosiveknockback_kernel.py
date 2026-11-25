#!/usr/bin/env python3
"""Offline kernel selftest for Explosive Knockback (design §8.1, K-01..K-12).

Runs Source/SelfTest (net8.0, compiles the production RM_KnockbackMath.cs). dotnet.exe is Windows-native and
cannot build from an ext4 clone, so the two source files are staged into D:\\ClaudeWork\\rimmandrake\\build\\ExplosiveKnockbackSelfTest
first (same staging root as winbuild.py).

    python3 src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_kernel.py
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[3] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
from winbuild import run_interop_captured  # noqa: E402  (WSL lost-launch retry)
import fcntl
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = os.environ.get("WINBUILD_ROOT", rm_str("build")) + "/ExplosiveKnockbackSelfTest"
DOTNET = ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]


def win(p):
    p = os.path.abspath(p)
    return "%s:\\%s" % (p[5].upper(), p[7:].replace("/", "\\"))


def main(extra=()):
    dotnet = next((d for d in DOTNET if os.path.isfile(d)), None)
    if dotnet is None or not os.path.isdir(os.path.dirname(STAGE)):
        print("UNMEASURED: no Windows dotnet.exe / D: staging root on this machine")
        return (1, "UNMEASURED") if extra else 1
    # the lock is machine-wide (/tmp, not the per-seat TMPDIR) and covers the staging too: every clone stages into
    # the same folder (RIMMANDRAKE_RESTAGE_CSHARP_SUITES_FRESH_MTIME_STALE_FAULT_BINARY)
    with open(os.path.join("/tmp", "explosiveknockback_selftest.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        for d in ("obj", "bin"):     # retained outputs can look newer than fresh sources (a clock step back): build clean
            shutil.rmtree(os.path.join(STAGE, "SelfTest", d), ignore_errors=True)
        os.makedirs(os.path.join(STAGE, "SelfTest"), exist_ok=True)
        # shutil.copy, never copy2: a fresh mtime makes dotnet rebuild; an old one ran a stale binary, the last planted
        # fault or another clone's build (RIMMANDRAKE_RESTAGE_CSHARP_SUITES_FRESH_MTIME_STALE_FAULT_BINARY)
        for f in ("RM_KnockbackMath.cs", "RM_KnockbackPlan.cs", "RM_KnockbackVerdicts.cs"):
            shutil.copy(os.path.join(HERE, "Source", f), os.path.join(STAGE, f))
        for f in ("Program.cs", "KnockbackFuzz.cs", "KnockbackSweep.cs", "KnockbackMap.cs", "RimMandrakeExplosiveKnockback.SelfTest.csproj"):
            shutil.copy(os.path.join(HERE, "Source", "SelfTest", f), os.path.join(STAGE, "SelfTest", f))
        r = run_interop_captured([dotnet, "run", "--project", win(os.path.join(STAGE, "SelfTest",
                            "RimMandrakeExplosiveKnockback.SelfTest.csproj")), "-c", "Release"] + (["--"] + list(extra) if extra else []),
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
    out = (r.stdout or "").replace("\r", "")
    if extra:
        return r.returncode, out + (r.stderr or "")
    if r.returncode == 0 and out.strip():
        # each 0.2.0 sweep prints its cases read, its failing count and its worst value (the Stage 3 brief's rule)
        for line in out.strip().splitlines()[:-1]:
            if " sweep: " in line:
                print(line)
        print(out.strip().splitlines()[-1])
    else:
        print(out + (r.stderr or ""))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
