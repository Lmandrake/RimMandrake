#!/usr/bin/env python3
"""Selftest: the PRODUCTION new-game start-flow core (JawaBenchStartFlowCore.cs) built and unit-tested offline.
The decisions behind scenario_select / start_site_select / ideo_load_rid (JawaBenchStartFlowTools.cs): scenario
matching (defName then exact name, ambiguity refused, never a substring pick), .rid path resolution (Windows, /mnt/x,
bare name in the Ideos folder; Linux-only, relative and non-.rid refused), start-tile list parsing and
first-acceptable choice with every skipped tile's reason kept.
Builds bridgetools/StartFlowSelfTest (net8.0, no RimWorld references) through winbuild staging.
Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_start_flow_core.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

MIN_UNITS = 41


def main(argv):
    if "--no-cs" in argv:
        print("start-flow core: SKIPPED by --no-cs")
        return 0
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        print("FAIL start-flow core UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept)")
        return 1
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "StartFlowSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "StartFlowSelfTest.csproj"), stage_name="StartFlowSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\StartFlowSelfTest.dll"
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
    print("start-flow core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
