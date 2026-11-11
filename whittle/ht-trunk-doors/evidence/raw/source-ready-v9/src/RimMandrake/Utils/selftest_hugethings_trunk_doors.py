#!/usr/bin/env python3
# selftest-timeout: 600
"""Production trunk-contact IL rewrite: exact driver injection and fail-closed mismatch mutations."""
import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winbuild
import game_paths


def main():
    project = os.path.join(winbuild.ROOT, 'src/RimMandrake/HugeThings/Source/SelfTest/TrunkDoors/TrunkDoors.csproj')
    harmony_root = Path(game_paths.WORKSHOP)/'2009463077'
    candidates = [harmony_root/'1.6/Assemblies/0Harmony.dll', harmony_root/'Current/Assemblies/0Harmony.dll']
    harmony = next((path for path in candidates if path.is_file()), None)
    if harmony is None:
        print('FAIL required installed Harmony input missing: '+str(harmony_root))
        return 1
    rc, record = winbuild.stage_build(project, stage_name='HugeThingsTrunkDoorsSelfTest',
        extra=['/p:HarmonyDll='+winbuild.win(str(harmony))])
    if rc:
        return rc
    dll = winbuild.staged_win(record, os.path.dirname(project))+'\\bin\\Release\\net8.0\\TrunkDoors.dll'
    return winbuild.run_interop([winbuild.dotnet_exe(), dll], cwd=record['stage'], timeout=None)


if __name__ == '__main__':
    sys.exit(main())
