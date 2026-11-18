#!/usr/bin/env python3
# selftest-timeout: 600   (lost WSL launches winbuild.run_interop repeats: up to 3 at ~2 min each, INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT)
"""Selftest: the PRODUCTION jawa/run_scenes pure core (JawaBenchSceneRunnerCore.cs) and the PRODUCTION RMTestAttribute
(src/RimMandrake/_Shared/SceneRunner/RMTestAttribute.cs) built and unit-tested offline (RIMMANDRAKE_BUILD_SHARED_SCENE_RUNNER_FIRST_SLICE):
discovery by attribute type name, refusals of a broken suite, plots, Outside reads, the PASS / FAIL / UNMEASURED row table
(could-not-look never becomes FAIL or PASS; no rows is EMPTY, never PASS) and the short-advance rule.
Builds bridgetools/SceneRunnerSelfTest (net8.0, no RimWorld references) through winbuild staging.
Without dotnet.exe this FAILS as UNMEASURED (pass --no-cs to accept that). No game, no bridge.
Run: python3 src/RimMandrake/Utils/selftest_scene_runner_core.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

MIN_UNITS = 70


def main(argv):
    if "--no-cs" in argv:
        print("scene-runner core: SKIPPED by --no-cs")
        return 0
    if not any(os.path.exists(c) for c in ["/mnt/c/Users/Mandrake/.dotnet/dotnet.exe", "/mnt/c/Program Files/dotnet/dotnet.exe"]):
        print("FAIL scene-runner core UNMEASURED: no dotnet.exe on this machine (pass --no-cs to accept)")
        return 1
    import winbuild
    proj = os.path.join(REPO, "src", "RimMandrake", "bridgetools", "SceneRunnerSelfTest")
    rc, rec = winbuild.stage_build(os.path.join(proj, "SceneRunnerSelfTest.csproj"), stage_name="SceneRunnerSelfTest")
    if rc:
        print("FAIL harness build FAILED (rc %s)" % rc)
        return 1
    dll = winbuild.staged_win(rec, proj) + "\\bin\\Release\\net8.0\\SceneRunnerSelfTest.dll"
    p = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev")
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
    print("scene-runner core: %d/%d passed" % (len(lines) - len(bad), len(lines)))
    return 1 if bad or p.returncode else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
