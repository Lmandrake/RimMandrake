#!/bin/bash
# usage: mut.sh NAME FILE PYREPLACE_OLD PYREPLACE_NEW
R=/home/mandrake/rm/relentless/clones/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP
S=/mnt/d/ClaudeWork/rimmandrake/scratch/LEVEL_STAGING_mutants
M=$S/root_$1; rm -rf $M
for f in infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/tprof_T3.txt infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/perf_L0_timed.txt infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/README.md src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs src/RimMandrake/FlowWorks/Source/Hose/HoseLayQueue.cs src/RimMandrake/FlowWorks/Source/RimMandrake_FlowWorks.csproj src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs design/validation_walks/RimMandrake/FlowWorks.md; do mkdir -p $M/$(dirname $f); cp $R/$f $M/$f; done
if [ "$2" = "RM" ]; then rm $M/$3; else
python3 -c "import sys;p=sys.argv[1];s=open(p).read();o=sys.argv[2];assert o in s,'mutant anchor missing';open(p,'w').write(s.replace(o,sys.argv[3],int(sys.argv[4]) if len(sys.argv)>4 else -1))" $M/$2 "$3" "$4" $5 || exit 9; fi
python3 $R/src/RimMandrake/FlowWorks/selftest_freeze_big_map.py --root $M > $S/out_$1.txt 2>&1; e=$?
echo "$1 exit=$e $(grep -c FAIL $S/out_$1.txt) FAIL: $(grep -o '^F[0-9][^ ]*' <(grep FAIL $S/out_$1.txt) | tr '\n' ' ')"
