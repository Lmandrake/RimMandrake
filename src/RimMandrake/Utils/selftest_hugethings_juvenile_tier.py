#!/usr/bin/env python3
# selftest-timeout: 600
"""Compile the production tier adapter/kernel, then check independent policy and complete gate truth tables. L0 only."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild


def main():
    relative = "src/RimMandrake/HugeThings/Source/SelfTest/JuvenileTier"
    project = os.path.join(winbuild.ROOT, relative, "JuvenileTier.csproj")
    rc, record = winbuild.stage_build(project, stage_name="HugeThingsJuvenileTierSelfTest")
    if rc:
        return rc
    dll = winbuild.staged_win(record, os.path.dirname(project)) + "\\bin\\Release\\net8.0\\JuvenileTier.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd=record['stage'], timeout=None)


if __name__ == '__main__':
    sys.exit(main())
