#!/usr/bin/env python3
"""Selftest: the PRODUCTION map-awareness core (JawaBenchAwarenessCore.cs) built and unit-tested offline.

Items THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER / INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED /
PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN. Builds bridgetools/AwarenessSelfTest (net8.0, no RimWorld references) through
winbuild staging and runs its unit group: context chain, explicit cross-thread tokens, skip-safe scopes, epochs,
bounded tags and seen-set, reuse-not-overwrite, spawn classification, forbidden-upgrade lint, switches, TTL arming,
thing_explain selector and provider rules.

Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_map_awareness_core.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)


def main(argv):
    if "--no-cs" in argv:
        print("map awareness core: SKIPPED by --no-cs")
        return 0
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        print("FAIL map awareness core UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept)")
        return 1
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "AwarenessSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "AwarenessSelfTest.csproj"), stage_name="AwarenessSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\AwarenessSelfTest.dll"
    p = subprocess.run([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev")
    lines = [ln.strip() for ln in p.stdout.splitlines() if ln.startswith("U ")]
    count = [ln for ln in p.stdout.splitlines() if ln.startswith("U-count ")]
    bad = [ln for ln in lines if " FAIL" in ln]
    for ln in lines:
        print(("ok   " if " ok" in ln and " FAIL" not in ln else "FAIL ") + ln[2:])
    want = int(count[0].split()[1]) if count else -1
    if want != len(lines) or want < 40:
        print("FAIL unit count: printed %d, declared %s (expected >= 40) -- the harness did not run whole: %s"
              % (len(lines), want, p.stderr[-400:]))
        return 1
    print("map awareness core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
