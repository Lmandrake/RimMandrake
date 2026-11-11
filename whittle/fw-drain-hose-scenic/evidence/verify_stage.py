"""Read staged source identities against the real wrapper run's input manifest."""
import hashlib,json,sys,time
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
import selftest_winstage,winbuild
before=json.loads((here/'integrity_before.json').read_text())
project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
stage=Path(winbuild.BUILD_ROOT)/selftest_winstage.stage_name_for(str(project),str(root))
records={}
for p,h in before['sha256'].items():
 path=stage/p
 records[p]=dict(expected_sha256=h,stage_sha256=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
# Some full manifest entries are evidence or non-source image assets, intentionally absent from staged build.
required=[p for p in records if p.startswith('src/') and (p.endswith(('.cs','.csproj','.props','.targets','.xml')))]
bad=[p for p in required if records[p]['expected_sha256']!=records[p]['stage_sha256']]
record=dict(time=time.time(),stage=str(stage),inputs=records,required_paths=required,mismatches=bad)
out=here/('stage_'+sys.argv[1]+'.json'); assert not out.exists(); out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(time=record['time'],stage=str(stage),required_count=len(required),mismatches=bad),indent=2)); assert not bad
