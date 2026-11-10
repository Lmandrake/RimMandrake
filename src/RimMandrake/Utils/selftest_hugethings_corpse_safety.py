#!/usr/bin/env python3
# selftest-timeout: 600
"""Production corpse queue/placement/butcher code against a destructive engine stand-in; no game or bridge."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild


def main():
    relative = "src/RimMandrake/HugeThings/Source/SelfTest/CorpseSafety"
    project = os.path.join(winbuild.ROOT, relative, "CorpseSafety.csproj")
    rc, record = winbuild.stage_build(project, stage_name="HugeThingsCorpseSafetySelfTest")
    if rc:
        return rc
    dll = winbuild.staged_win(record, os.path.dirname(project)) + "\\bin\\Release\\net8.0\\CorpseSafety.dll"
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd="/mnt/d/Luke/dev", timeout=None)


if __name__ == "__main__":
    sys.exit(main())
