#!/usr/bin/env python3
# selftest-timeout: 600
"""Production footprint scheduler, geometry, ledger and planner under adversarial budgets; no game or bridge."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild


def main():
    project = os.path.join(winbuild.ROOT, "src/RimMandrake/HugeThings/Source/SelfTest/FootprintBudget/FootprintBudget.csproj")
    rc, record = winbuild.stage_build(project, stage_name="HugeThingsBudgetSelfTest")
    if rc:
        return rc
    dll = winbuild.staged_win(record, os.path.dirname(project)) + "\\bin\\Release\\net8.0\\FootprintBudget.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main())
