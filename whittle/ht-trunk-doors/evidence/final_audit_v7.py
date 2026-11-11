"""Read-only checks of the frozen inputs and actual process receipts."""
from pathlib import Path
import hashlib,json,re,sys,time,subprocess
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
attempt=sys.argv[1]
out=e/'raw/final-audit-v7.json'
assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=e/'raw/source-ready-v7-compiled-inputs.json';m=json.loads(manifest.read_text())
rows=[]
for row in m['inputs']:
 actual=sha(root/row['path']);assert actual==row['sha256'],row['path']
 rows.append(dict(path=row['path'],sha256=actual))
assert sha(root/m['project'])==m['project_sha256']
build=json.loads((e/'raw/build-candidate7.receipt.json').read_text());assert build['rc']==0
assert build['compile_manifest_sha256']==sha(manifest)
stdout=(e/'raw/build-candidate7.stdout.txt').read_text()
assert '0 Warning(s)' in stdout and '0 Error(s)' in stdout
for ext in ('dll','dll.srchash'):assert sha(root/build[ext]['path'])==build[ext]['sha256']
dll=root/build['dll']['path'];stamp=root/build['dll.srchash']['path']
assert '# dll: '+sha(dll) in stamp.read_text()
tests=json.loads((e/'raw/tests-after5.receipt.json').read_text());assert tests['rc']==0
assert 'PASS 5/5  FAIL 0/5' in (e/'raw/tests-after5.stdout.txt').read_text()
for arm,rc in [('before',1),('after',0)]:
 rec=json.loads((e/'raw'/('planner-'+arm+'-replay.receipt.json')).read_text());assert rec['rc']==rc
 original=json.loads((e/'raw'/('planner-'+arm+'.receipt.json')).read_text())
 for row in original['inputs']:assert sha(root/row['path'])==row['sha256']
claims='src/RimMandrake/HugeThings/Source/Kernel/RM_HugeClaimsKernel.cs'
assert sha(e/'raw/planner-before-inputs/Claims.cs')==sha(e/'raw/source-before'/claims)
assert sha(e/'raw/planner-after-inputs/Claims.cs')==sha(root/claims)
run=json.loads((e/'raw'/attempt/'process-receipt.json').read_text());assert run['ok']
proof=json.loads((e/'raw'/attempt/'trunk-doors.json').read_text());assert proof['ok'] and proof['restoration']['ok']
assert proof['script_sha256']==sha(root/'src/RimMandrake/HugeThings/northstar/trunk_doors_live.py')
for phase in ('offline','live'):
 pf=json.loads((e/'raw'/attempt/('preflight-'+phase+'.json')).read_text())
 assert not [r for r in pf['rows'] if r['required'] and r['id']!='O02' and r['status']!='PASS']
source_rows=json.loads((e.parent/'SOURCE_READY_INPUTS.json').read_text())
current=[]
for row in source_rows:
 p=root/row['path'];assert p.is_file()==row['exists']
 if row['exists']:assert sha(p)==row['sha256']
 current.append(row)
p1=root/'src/RimMandrake/HugeThings/northstar/p1_live.py';assert not p1.exists()
kernel=(root/claims).read_text()
assert not any(x in kernel for x in ('RootServed(', 'Reconnects(', 'bool[] Reach('))
record=dict(checked_utc=time.time(),runtime_inputs=rows,project=dict(path=m['project'],sha256=sha(root/m['project'])),
source_paths=current,build_receipt_sha256=sha(e/'raw/build-candidate7.receipt.json'),
tests_receipt_sha256=sha(e/'raw/tests-after5.receipt.json'),
process_receipt_sha256=sha(e/'raw'/attempt/'process-receipt.json'),
proof_sha256=sha(e/'raw'/attempt/'trunk-doors.json'),
artifact_sha256=sha(dll),stamp_sha256=sha(stamp),
comparison_receipts={arm:sha(e/'raw'/('planner-'+arm+'-replay.receipt.json')) for arm in ('before','after')})
out.write_text(json.dumps(record,indent=2)+'\n')
print('frozen input/process audit PASS')
