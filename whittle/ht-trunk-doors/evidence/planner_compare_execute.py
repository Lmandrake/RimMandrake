from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src/RimMandrake/Utils'));import winbuild
arm=sys.argv[1];assert arm in ('before','after')
folder=e/'raw'/('planner-'+arm+'-inputs')
rc,stage=winbuild.stage_build(str(folder/'Planner.csproj'),stage_name='HTTrunkDoorCompareReplay'+arm)
if rc:raise SystemExit(rc)
dll=winbuild.staged_win(stage,str(folder))+r'\bin\Release\net8.0\Planner.dll'
raise SystemExit(winbuild.run_interop([winbuild.dotnet_exe(),dll],cwd=stage['stage'],timeout=120))
