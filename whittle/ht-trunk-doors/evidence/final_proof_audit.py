"""Read actual accepted outputs and frozen bytes, then independently measure cleanup. Never drives a game."""
from pathlib import Path
import ast,hashlib,json,math,os,re,shlex,struct,subprocess,sys,time
root=Path(__file__).resolve().parents[3];b=root/'whittle/ht-trunk-doors';raw=b/'evidence/raw';attempt=sys.argv[1];a=raw/attempt
out=raw/'final-proof-audit.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((a/'process-receipt.json').read_text());p=json.loads((a/'trunk-doors.json').read_text());assert r['ok'] and p['ok'] and p['restoration']['ok'] and p['cut_recovered']
script=root/'src/RimMandrake/HugeThings/northstar/trunk_doors_live.py';assert p['script_sha256']==sha(script)
tree=ast.parse(script.read_text());ns={'struct':struct,'math':math,'CUT':'RM_CutHugePlantFromTrunk'}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('kv','work_bits','loaded_cut_matches')],type_ignores=[]),str(script),'exec'),ns)
arm=ns['kv'](p['reload_observer_arm']);capture=ns['kv'](p['cut_before_native_load_tick']);saved=p['serialized_cut']['state']
assert ns['loaded_cut_matches'](saved,capture,p['plant_id'],p['sealed']['blockers'][0]['id'],arm['nonce'])
assert p['sealed']['access'] is False and set(p['doorway_claims'])=={'99,101','100,101'}
assert p['geometry_control']['restored_access'] and p['cut_probes']['root']['gates']['canReachTouchDeadly'] is False
assert ns['kv'](p['cut_order'])['forced']=='False' and any(float(ns['kv'](s)['work'])>0 for s in p['cut_work_samples'])
assert p['reservation_control']['root']['gates']['canReserve'] is False
assert p['controls']['disabled'] and p['controls']['reenabled'] and p['controls']['vacated_pawn_retried']
assert len(set(p['fixture_ids']))==2 and len(p['baseline']['map_pawns'])==3 and p['actor_roles']['guard']==p['actor_roles']['second']
assert p['baseline']['supplement']==p['restored']['supplement'] and len(p['baseline']['supplement']['actor_policies'])==3
assert not any(c['tool']=='jawa/spawn_pawn' for c in p['calls'])
for name in ('startup-log','post-proof-log'):
 log=json.loads((a/(name+'.json')).read_text());assert not log['first_exception'] and log['exception_count']==0 and not log['config_errors'] and not log['parse_errors']
for phase in ('offline','live'):
 pf=json.loads((a/('preflight-'+phase+'.json')).read_text());assert not [x for x in pf['rows'] if x['required'] and x['id']!='O02' and x['status']!='PASS']
meta=json.loads((b/'SOURCE_COMMITTED.json').read_text());assert subprocess.check_output(['git','show',meta['script_sha']+':'+str(script.relative_to(root))],cwd=root)==script.read_bytes()
manifest=json.loads((raw/'source-ready-v9-compiled-inputs.json').read_text());build=json.loads((raw/'build-candidate7.receipt.json').read_text());assert sha(raw/'source-ready-v9-compiled-inputs.json')==build['compile_manifest_sha256']
for x in manifest['inputs']:
 assert sha(root/x['path'])==x['sha256'];assert hashlib.sha256(subprocess.check_output(['git','show',build['commit']+':'+x['path']],cwd=root)).hexdigest()==x['sha256']
for ext in ('dll','dll.srchash'):
 assert sha(root/build[ext]['path'])==build[ext]['sha256'];assert hashlib.sha256(subprocess.check_output(['git','show',meta['artifact_sha']+':'+build[ext]['path']],cwd=root)).hexdigest()==build[ext]['sha256']
copy=Path(r['live_copy']['path']);assert sha(copy)==r['live_copy']['sha256'] and json.loads(copy.read_text())==p
prefix='export RIMFLOW_SEAT=CODEX_STEVEDESKTOP_HUGETHINGS AGENT_SEAT=CODEX_STEVEDESKTOP_HUGETHINGS RIMFLOW_BRIDGE_SEAT=CODEX_STEVEDESKTOP_HUGETHINGS; source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh; export RM_GUARD_SEAT=CODEX_STEVEDESKTOP_HUGETHINGS RM_CODEX_SIDE=wsl; export WSLENV="${WSLENV:+${WSLENV}:}RIMFLOW_SEAT:AGENT_SEAT:RIMFLOW_BRIDGE_SEAT:RM_GUARD_SEAT"; '
cleanup=[]
for name,cmd,expected in [('guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json'],0),('ledger',['python3','src/RimMandrake/rimflow/cli.py','bridge','who','--host','stevedesktop'],0),('game',['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh','status'],3)]:
 q=subprocess.run(['bash','-c',prefix+shlex.join(cmd)],cwd=root,capture_output=True,timeout=45)
 for ext,data in [('stdout.txt',q.stdout),('stderr.txt',q.stderr),('rc',str(q.returncode).encode()+b'\n')]:
  dest=raw/('accepted-cleanup-'+name+'.'+ext);assert not dest.exists();dest.write_bytes(data)
 assert q.returncode==expected
 if name=='guard':assert json.loads(q.stdout)['state']=='FREE'
 elif name=='ledger':assert b'bridge FREE in the ledger' in q.stdout
 else:assert b'stopped' in q.stdout
 cleanup.append(dict(name=name,command=cmd,rc=q.returncode))
paths=[a/'trunk-doors.json',a/'process-receipt.json',a/'driver-input.py',a/'trunk-doors-input.py',raw/'build-candidate7.receipt.json',raw/'source-ready-v9-compiled-inputs.json',raw/'source-ready-v9-inputs.json',raw/'tests-after5.receipt.json',raw/'planner-before-replay.receipt.json',raw/'planner-after-replay.receipt.json',raw/'candidate7-persistence-checker-v2.json',raw/'candidate9-python-check.json',b/'SOURCE_COMMITTED.json',b/'STATEMENT.md',b/'NOTES.md',b/'evidence/item-before.txt']
out.write_text(json.dumps(dict(utc=time.time(),attempt=attempt,source_commit=build['commit'],script_commit=meta['script_sha'],artifact_commit=meta['artifact_sha'],runtime_inputs=len(manifest['inputs']),observed_capture=capture,serialized_cut=saved,cleanup=cleanup,files=[dict(path=str(x.relative_to(root)),sha256=sha(x)) for x in paths],accepted_compact=dict(path=str(copy),sha256=sha(copy)),ok=True),indent=2)+'\n')
print('actual accepted proof/source/bit-exact persistence/compact-copy/independent cleanup audit PASS')
