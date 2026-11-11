import json,subprocess,sys,time
from pathlib import Path
name=sys.argv[1]
cmd=['/home/mandrake/.cache/ht-warning-venv/bin/python3','src/RimMandrake/Utils/run_selftests.py','--only',
'src/RimMandrake/Utils/selftest_hugethings_fuzz.py','src/RimMandrake/Utils/selftest_hugethings_budget.py',
'src/RimMandrake/Utils/selftest_hugethings_lint.py','src/RimMandrake/Utils/selftest_hugethings_trunk_doors.py','src/RimMandrake/HugeThings/selftest_hugethings_footprint.py','--workers','1']
p=Path(__file__).resolve().parent/'raw'; start=time.time()
assert not (p/(name+'.receipt.json')).exists()
with (p/(name+'.stdout.txt')).open('wb') as out,(p/(name+'.stderr.txt')).open('wb') as err:r=subprocess.run(cmd,stdout=out,stderr=err)
(p/(name+'.receipt.json')).write_text(json.dumps(dict(command=cmd,rc=r.returncode,elapsed=time.time()-start),indent=2)+'\n')
print(name,'rc',r.returncode)
sys.exit(r.returncode)
