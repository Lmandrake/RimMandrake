#!/usr/bin/env python3
"""Offline selftest of the Messy Conduit core (graph reduction, planner, slack laying) against the
Python oracle (src/RimMandrake/Utils/mockups/messy_conduit/).

    python3 src/RimMandrake/Utils/selftest_messyconduit.py [--probe] [--no-export] [--dump <dir on /mnt/...>]

1. Re-exports the oracle's scenes and answers (export_oracle.py) unless --no-export.
2. Builds src/RimMandrake/MessyConduit/Source/SelfTest/ (net8.0, compiles ../Core/*.cs, the
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

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeMessyConduit.SelfTest.csproj")


def main(argv):
    if "--no-export" not in argv:
        r = subprocess.run([sys.executable, os.path.join(HERE, "mockups", "messy_conduit", "export_oracle.py")])
        if r.returncode:
            return r.returncode
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="MessyConduitSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "MessyConduit", "Source", "Core")])
    if rc:
        print("selftest build FAILED")
        return rc
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeMessyConduit.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll] + (["--probe"] if "--probe" in argv else [])
    if "--dump" in argv:
        args += ["--dump", winbuild.win(os.path.abspath(argv[argv.index("--dump") + 1]))]
    return subprocess.run(args, cwd="/mnt/d/Luke/dev").returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
