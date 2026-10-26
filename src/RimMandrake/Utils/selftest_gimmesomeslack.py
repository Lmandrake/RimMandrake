#!/usr/bin/env python3
"""Offline selftest of the Gimme Some Slack core (graph reduction, planner, slack laying) against the
Python oracle (src/RimMandrake/Utils/mockups/messy_conduit/).

    python3 src/RimMandrake/Utils/selftest_gimmesomeslack.py [--probe] [--no-export] [--dump <dir on /mnt/...>]

1. Re-exports the oracle's scenes and answers (export_oracle.py) unless --no-export.
2. Builds src/RimMandrake/GimmeSomeSlack/Source/SelfTest/ (net8.0, compiles ../Core/*.cs, the
   production files) through winbuild.stage_build: dotnet.exe is Windows-native and cannot build
   from the ext4 clone, so the project is staged on D:.
3. Runs it. --probe plants one wrong expectation per scene; the run must then report every scene
   as FAILING (a selftest that cannot fail proves nothing).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeGimmeSomeSlack.SelfTest.csproj")
SOURCE = os.path.dirname(SELFTEST)


def selftest_cwd():
    """Working directory for dotnet.exe: agent scratch on D:, a drive path Windows can use. It was the read-only mirror
    /mnt/d/Luke/dev (review 9.7), which an agent must never write and which the run could litter."""
    d = os.path.join("/mnt/d/ClaudeWork/rimmandrake/scratch", "gss_selftest_cwd")
    os.makedirs(d, exist_ok=True)
    return d


def sliced_rebuild_callers():
    """GSS round 3 review (2026-10-26): a budgeted Rebuild lays only ~8 ms of edges and leaves the rest to later frames, so a
    scripted caller that reads Pieces right after it (cstyles probe, JawaBench gss staging) saw a half-laid set. The public
    Rebuild() must be the complete build; only the component's own frame paths may ask for a slice (Rebuild(false))."""
    comp = os.path.join(SOURCE, "RM_MapComponent_CordGraph.cs")
    with open(comp, encoding="utf-8") as f:
        text = f.read()
    import re
    bad = []
    if not re.search(r"public void Rebuild\(\)\s*=>\s*Rebuild\(true\);", text):
        bad.append("RM_MapComponent_CordGraph.Rebuild() is not the complete build (Rebuild(true))")
    if text.count("Rebuild(false)") < 2:
        bad.append("the frame paths (PiecesForSection, MapComponentUpdate) do not ask for a budgeted slice")
    for root, dirs, files in os.walk(SOURCE):
        dirs[:] = [d for d in dirs if d not in ("SelfTest", "bin", "obj")]
        for n in files:
            p = os.path.join(root, n)
            if n.endswith(".cs") and p != comp:
                with open(p, encoding="utf-8") as f:
                    if "Rebuild(false)" in f.read():
                        bad.append(os.path.relpath(p, SOURCE) + " asks for a budgeted slice outside the component")
    for b in bad:
        print("FAIL sliced rebuild: " + b)
    print("sliced rebuild callers: " + ("FAIL" if bad else "ok"))
    return 1 if bad else 0


def main(argv):
    if sliced_rebuild_callers():
        return 1
    if "--no-export" not in argv:
        r = subprocess.run([sys.executable, os.path.join(HERE, "mockups", "messy_conduit", "export_oracle.py")])
        if r.returncode:
            return r.returncode
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="GimmeSomeSlackSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Source", "Core")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeGimmeSomeSlack.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll] + (["--probe"] if "--probe" in argv else []) + (["--perdig-only"] if "--perdig-only" in argv else [])
    for i, a in enumerate(argv):   # approach B fuzz knobs (GssFuzz.cs): --fuzz-scale F, --fuzz-only NAME, --fuzz-seed N
        if a.startswith("--fuzz") and i + 1 < len(argv):
            args += [a, argv[i + 1]]
    if "--unroutable-census" in argv:   # A7 census (UnroutableCensus.cs): --unroutable-census OUT.json [SEEDS]
        i = argv.index("--unroutable-census")
        args += ["--unroutable-census", winbuild.win(os.path.abspath(argv[i + 1]))] + argv[i + 2:i + 3]
    if "--dump" in argv:
        args += ["--dump", winbuild.win(os.path.abspath(argv[argv.index("--dump") + 1]))]
    return subprocess.run(args, cwd=selftest_cwd()).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
