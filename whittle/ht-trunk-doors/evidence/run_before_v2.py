"""Exact old production input freeze, candidate-only file removal, and unconditional candidate restoration."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
root=Path(__file__).resolve().parents[3]
e=Path(__file__).resolve().parent
attempt=sys.argv[1] if len(sys.argv)>1 else 'live-before2'
candidate=e/'raw'/('candidate-'+attempt)
candidate.mkdir(exist_ok=False)
paths=[*Path(root/'src/RimMandrake/HugeThings/Source').rglob('*.cs'),
       *Path(root/'src/RimMandrake/HugeThings/Source').rglob('*.csproj'),
       *Path(root/'src/RimMandrake/HugeThings/Defs').rglob('*.xml'),
       root/'src/RimMandrake/HugeThingsTestRaces/Defs/ThingDefs_Plants/RM_TestContactPlant.xml']
rows=[]
for p in paths:
    if '/obj/' in str(p) or '/bin/' in str(p):continue
    rel=p.relative_to(root);dst=candidate/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    rows.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
manifest=e/'raw'/('candidate-'+attempt+'-manifest.json')
manifest.write_text(json.dumps(rows,indent=2)+'\n')
restore=[r['path'] for r in rows if (e/'raw/source-before'/r['path']).is_file()]
remove=[r['path'] for r in rows if r['path'] not in restore]
rec=dict(started=time.time(),candidate_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),restored_paths=restore,removed_candidate_only_paths=remove)
(e/'raw'/(attempt+'-source-freeze.json')).write_text(json.dumps(rec,indent=2)+'\n')
marker=root/'whittle/ht-trunk-doors/BEFORE_SOURCE_FREEZE.json'
assert not marker.exists()
marker.write_text(json.dumps(rec,indent=2)+'\n')
rc=1
try:
    for path in restore:shutil.copyfile(e/'raw/source-before'/path,root/path)
    for path in remove:(root/path).unlink()
    with (e/'raw'/(attempt+'-orchestration.stdout.txt')).open('wb') as out,(e/'raw'/(attempt+'-orchestration.stderr.txt')).open('wb') as err:
        rc=subprocess.run(['python3',str(e/'run_live.py'),attempt],cwd=root,stdout=out,stderr=err).returncode
finally:
    for row in rows:
        p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate/row['path'],p)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    rec.update(finished=time.time(),process_rc=rc,candidate_restored=True)
    (e/'raw'/(attempt+'-source-restored.json')).write_text(json.dumps(rec,indent=2)+'\n')
    marker.unlink()
print('before run rc',rc,'candidate restored')
sys.exit(rc)
