"""Actually rerun offline measurement and review retained artifacts after final edits."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import time

here=Path(__file__).resolve().parent
root=here.parents[2]
raw=here/'raw'
receipts=[]
for name,cmd in (
    ('engine-final',['python3',str(here/'run_engine.py')]),
    ('measure-final',['python3',str(here/'run_measure.py')]),
    ('diff-check',['git','diff','--check'])):
    started=time.time()
    r=subprocess.run(cmd,cwd=root,capture_output=True,timeout=120)
    (raw/(name+'.stdout.txt')).write_bytes(r.stdout)
    (raw/(name+'.stderr.txt')).write_bytes(r.stderr)
    receipts.append({'name':name,'command':cmd,'rc':r.returncode,'elapsed':time.time()-started,
                     'stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),
                     'stderr_sha256':hashlib.sha256(r.stderr).hexdigest()})
    if r.returncode:
        (raw/'final-process.receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
        raise SystemExit(r.returncode)
source=root/'src/RimMandrake/HugeThings/northstar/measure_reefback_calf.py'
ast.parse(source.read_text())
for path in (source,root/'design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_CALF_DECISION.md'):
    cmd=['git','diff','--no-index','--check','/dev/null',str(path)]
    r=subprocess.run(cmd,cwd=root,capture_output=True)
    receipts.append({'name':'new-file-whitespace','command':cmd,'rc':r.returncode,
                     'stdout':r.stdout.decode(),'stderr':r.stderr.decode()})
    if r.stdout or r.stderr or r.returncode not in (0,1):
        raise SystemExit('new-file whitespace check failed')
(raw/'final-process.receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')

def hashfile(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

manifest=json.loads((raw/'measure/inputs.json').read_text())
verified=[]
for row in manifest:
    name=row['input']
    if ':selected' in name or ':nodes' in name:
        continue
    p=Path(name)
    if not p.is_absolute():
        p=root/p
    if hashfile(p)!=row['sha256']:
        raise SystemExit('input drift: '+name)
    verified.append(name)
design=json.loads((here/'design_raw.json').read_text())
design_call=json.loads((here/'design_call.json').read_text())
assert design_call['returncode']==0 and not design.get('is_error') and design.get('subtype')=='success'
assert hashfile(here/'design_prompt.txt')==design_call['input_sha256']
assert hashfile(here/'design_raw.json')==design_call['stdout_sha256']
for n in ('read_engine.ps1','run_engine.py','run_measure.py'):
    (raw/'measure/snapshots'/n).write_bytes((here/n).read_bytes())
paths=[source.relative_to(root).as_posix(),
       'design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_CALF_DECISION.md',
       'whittle/ht-reefback-calf/STATEMENT.md','whittle/ht-reefback-calf/NOTES.md',
       'whittle/ht-reefback-calf/JUDGE_PROMPT.md']
paths += [(here/p).relative_to(root).as_posix() for p in
          ('design_prompt.txt','design_raw.json','design_call.json','raw/engine.receipt.json',
           'raw/measure.receipt.json','raw/final-process.receipt.json','raw/measure/inputs.json',
           'raw/measure/measurement.json','raw/measure/negative-controls.json','raw/measure/broaden-followups.json')]
receipt={'checked_at':time.time(),'mode':'actual offline rerun and content verification',
         'verified_measurement_inputs':verified,
         'design_process_rc':design_call['returncode'],'design_response_error':design.get('is_error'),
         'artifacts':[{'path':p,'sha256':hashfile(root/p)} for p in paths],
         'git_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
         'limit':'Fresh Codex judgment and Whittle validation follow DONE; those receipts are separate. No runtime or publication claim.'}
(here/'final-evidence.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'rc':0,'verified_input_count':len(verified),'artifact_count':len(paths)}))
