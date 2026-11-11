from pathlib import Path
import json,subprocess,hashlib,time
root=Path(__file__).resolve().parents[3];e=Path(__file__).resolve().parent
out=e/'raw/checkpoint-audit.json';assert not out.exists()
rows=[]
for name,cmd,expected in [
 ('guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json'],0),
 ('ledger',['python3','src/RimMandrake/rimflow/cli.py','bridge','who','--host','stevedesktop'],0),
 ('game',['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh','status'],3)]:
 r=subprocess.run(cmd,cwd=root,capture_output=True)
 for ext,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr)]:(e/'raw'/('checkpoint-'+name+'.'+ext)).write_bytes(data)
 rows.append(dict(command=cmd,rc=r.returncode));assert r.returncode==expected
 if name=='guard':assert json.loads(r.stdout)['state']=='FREE'
 elif name=='ledger':assert b'bridge FREE in the ledger' in r.stdout
 else:assert b'stopped' in r.stdout
m=json.loads((e/'raw/source-ready-v3-compiled-inputs.json').read_text())
for x in m['inputs']:assert hashlib.sha256((root/x['path']).read_bytes()).hexdigest()==x['sha256']
build=json.loads((e/'raw/build-candidate3.receipt.json').read_text());assert build['rc']==0
for ext in ('dll','dll.srchash'):assert hashlib.sha256((root/build[ext]['path']).read_bytes()).hexdigest()==build[ext]['sha256']
test=json.loads((e/'raw/tests-after5.receipt.json').read_text());assert test['rc']==0
for arm,rc in [('before',1),('after',0)]:
 assert json.loads((e/'raw'/('planner-'+arm+'-replay.receipt.json')).read_text())['rc']==rc
for attempt in ('live-before1','live-after1','live-after2','live-after3'):
 p=e/'raw'/attempt/'process-receipt.json';r=json.loads(p.read_text())
 assert not r['ok']
 assert [x for x in r['commands'] if x['name']=='guard-after' and x['rc']==0]
 assert [x for x in r['commands'] if x['name']=='lease-after' and x['rc']==0]
 assert [x for x in r['commands'] if x['name']=='status-after' and x['rc']==3]
assert not any((e/'raw'/a/'trunk-doors.json').exists() for a in ('live-after1','live-after2','live-after3'))
out.write_text(json.dumps(dict(utc=time.time(),cleanup_commands=rows,runtime_input_manifest_sha256=hashlib.sha256((e/'raw/source-ready-v3-compiled-inputs.json').read_bytes()).hexdigest(),
build_commit=build['commit'],build_receipt_sha256=hashlib.sha256((e/'raw/build-candidate3.receipt.json').read_bytes()).hexdigest(),
runtime_input_count=len(m['inputs']),test_rc=test['rc'],gameplay_proof_files=[]),indent=2)+'\n')
print('checkpoint source/artifact/cleanup checks PASS; gameplay unseen')
