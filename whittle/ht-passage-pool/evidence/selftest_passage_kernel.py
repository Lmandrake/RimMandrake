#!/usr/bin/env python3
# selftest-timeout: 600
"""Existing production Verse-free eligibility kernel, bounded Visitors family (1,500 deterministic cases).

This builds only the existing SelfTest project; never production DLL or source.
Visitors has explicit positive T2 own-hint matching-water and sea-on-land,
land-on-sea, opted-out, foreign-list, foreign-roster, no-home negative controls.
"""
import json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import selftest_hugethings_fuzz as F
if __name__=='__main__':
    # Same existing SelfTest project as F.main; its hardcoded Archmagi runtime
    # cwd /mnt/d/Luke/dev is absent on SteveDesktop. Use the actual build stage.
    rc, rec = F.winbuild.stage_build(F.CSPROJ, stage_name='HugeThingsPassageSelfTest')
    if rc:
        sys.exit(rc)
    dll = F.winbuild.staged_win(rec,F.SELFTEST) + '\\bin\\Release\\net8.0\\RimMandrakeHugeThings.SelfTest.dll'
    command=[F.winbuild.dotnet_exe(),dll,'--fuzz-only','visitors']
    started=time.time()
    run=F.winbuild.run_interop_captured(command,cwd=rec['stage'],timeout=180,capture_output=True,text=True)
    e=Path(__file__).resolve().parent
    (e/'kernel-raw.stdout').write_text(run.stdout)
    (e/'kernel-raw.stderr').write_text(run.stderr)
    (e/'kernel-run.json').write_text(json.dumps({'command':command,'cwd':rec['stage'],'started':started,
        'elapsed':time.time()-started,'returncode':run.returncode,'family':'visitors','bounded_cases':1500,
        'production_kernel':str(root/'src/RimMandrake/HugeThings/Source/Kernel/RM_TitanicKernel.cs'),
        'scope':'offline production eligibility positive/negative controls only; not A2/A3 live proof'},indent=2)+'\n')
    print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
    sys.exit(run.returncode)
