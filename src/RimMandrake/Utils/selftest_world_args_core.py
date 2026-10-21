#!/usr/bin/env python3
"""Selftest: the PRODUCTION world-tool argument core (JawaBenchWorldArgsCore.cs) built and unit-tested offline.
The argument parsing behind the world tools (JawaBenchWorldTools.cs; review 2026-10-20 D1/D5/D6): tile-id
lists and 'from-to' ranges clamped to the grid before allocating ("0-2147483647" used to hang the main thread),
every dropped token or off-grid id named, a hard per-call cap, object-id lists, and NaN/Infinity refusal.
Builds bridgetools/WorldArgsSelfTest (net8.0, no RimWorld references) through winbuild staging.
Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_world_args_core.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

MIN_UNITS = 56


def main(argv):
    if "--no-cs" in argv:
        print("world-args core: SKIPPED by --no-cs")
        return 0
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        print("FAIL world-args core UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept)")
        return 1
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "WorldArgsSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "WorldArgsSelfTest.csproj"), stage_name="WorldArgsSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\WorldArgsSelfTest.dll"
    p = subprocess.run([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev")
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.startswith("U ")]
    count = [ln for ln in p.stdout.splitlines() if ln.startswith("U-count ")]
    bad = [ln for ln in lines if " FAIL" in ln]
    for ln in lines:
        print(("ok   " if " FAIL" not in ln else "FAIL ") + ln[2:])
    want = int(count[0].split()[1]) if count else -1
    if want != len(lines) or want < MIN_UNITS:
        print("FAIL unit count: printed %d, declared %s (expected >= %d) -- the harness did not run whole: %s"
              % (len(lines), want, MIN_UNITS, p.stderr[-400:]))
        return 1
    print("world-args core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
