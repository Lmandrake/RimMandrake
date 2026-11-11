"""Freeze exact old production inputs for the before-fix functional run, then restore candidate in finally."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
root=Path(__file__).resolve().parents[3]
e=Path(__file__).resolve().parent
rows=json.loads((e/'raw/candidate-prebaseline-manifest.json').read_text())
restore=[]
for row in rows:
    p=root/row['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    old=e/'raw/source-before'/row['path']
    if old.is_file():restore.append(row['path'])
rec=dict(started=time.time(),candidate_manifest_sha256=hashlib.sha256((e/'raw/candidate-prebaseline-manifest.json').read_bytes()).hexdigest(),restored_paths=restore)
(e/'raw/before-source-freeze.json').write_text(json.dumps(rec,indent=2)+'\n')
(root/'whittle/ht-trunk-doors/BEFORE_SOURCE_FREEZE.json').write_text(json.dumps(rec,indent=2)+'\n')
rc=1
try:
    for path in restore:shutil.copyfile(e/'raw/source-before'/path,root/path)
    rc=subprocess.run(['python3',str(e/'run_live.py'),'live-before1'],cwd=root).returncode
finally:
    for row in rows:
        p=root/row['path'];shutil.copyfile(e/'raw/candidate-prebaseline'/row['path'],p)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    rec.update(finished=time.time(),process_rc=rc,candidate_restored=True)
    (e/'raw/before-source-restored.json').write_text(json.dumps(rec,indent=2)+'\n')
    (root/'whittle/ht-trunk-doors/BEFORE_SOURCE_FREEZE.json').unlink()
print('before run rc',rc,'candidate restored')
sys.exit(rc)
