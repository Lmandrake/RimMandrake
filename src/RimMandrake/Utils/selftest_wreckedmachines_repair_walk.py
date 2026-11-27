#!/usr/bin/env python3
"""T_REPAIR_STATE_WALK (tree check C_repair_state_walk; design/concepts/WreckedMachines/models.md, Repair state walk): the offline
walk of the repair state machine in the SHIPPED kernel (src/RimMandrake/WreckedMachines/Source/Kernel/RM_WreckedMachinesRepair.cs)
against a fake game, no game needed. Not a copy of the logic: the self-test project compiles the kernel file that the mod compiles.

    python3 src/RimMandrake/Utils/selftest_wreckedmachines_repair_walk.py [--walk-scale F] [--walk-seed N] [--walk-table PATH]

The range it walks, the rows it reads and the planted faults are written at the top of
src/RimMandrake/WreckedMachines/Source/SelfTest/RepairWalk.cs. Its last line is the verdict, `T_REPAIR_STATE_WALK: PASS|FAIL`.
Exit 0 PASS; 1 FAIL (a row broken, a row that read nothing, or a planted fault not caught); another code: the build of the
self-test did not run, which is COULD NOT LOOK and never a verdict on the kernel.
  --walk-scale F   multiply the count of random event strings (4000 at 1)
  --walk-seed N    replay one random string
  --walk-table P   write the table of states by events (tab separated, a Windows path or a path under /mnt)
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import winbuild  # noqa: E402

SELFTEST = os.path.join(REPO, "src", "RimMandrake", "WreckedMachines", "Source", "SelfTest")
CSPROJ = os.path.join(SELFTEST, "RimMandrakeWreckedMachines.SelfTest.csproj")


def main(argv):
    rc, rec = winbuild.stage_build(CSPROJ, stage_name="WreckedMachinesFuzzSelfTest",
                                   extra_dirs=[os.path.join(REPO, "src", "RimMandrake", "WreckedMachines", "Source", "Kernel")])
    if rc:
        print("T_REPAIR_STATE_WALK: COULD NOT LOOK (the self-test build failed, rc %s)" % rc)
        return 2
    dll = winbuild.staged_win(rec, SELFTEST) + "\\bin\\Release\\net8.0\\RimMandrakeWreckedMachines.SelfTest.dll"
    args = [winbuild.dotnet_exe(), dll, "--walk"]
    for i, a in enumerate(argv):
        if a.startswith("--walk-") and i + 1 < len(argv):
            v = argv[i + 1]
            if a == "--walk-table" and v.startswith("/mnt/"):
                v = subprocess.run(["wslpath", "-w", v], capture_output=True, text=True).stdout.strip() or v
            args += [a, v]
    return winbuild.run_interop(args, cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
