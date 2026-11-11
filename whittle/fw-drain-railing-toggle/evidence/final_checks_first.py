"""Fresh readback of preserved raw executions and exact current bytes; never reruns a suite."""
from pathlib import Path
import json,hashlib,subprocess,time
from integrity import here,root,hashes
read=lambda n:json.loads((here/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pub=read('publication.json');subprocess.run(['git','merge-base','--is-ancestor',pub['PUBLISHED'],'origin/main'],cwd=root,check=True)
before=read('integrity_before.json')['sha256'];now=hashes();changed=[p for p,h in before.items() if now.get(p)!=h];build=read('build_integrity.json')
driver=read('driver_publication.json');subprocess.run(['git','merge-base','--is-ancestor',driver['PUBLISHED'],'origin/main'],cwd=root,check=True)
assert sorted(changed)==sorted(list(build['artifacts'])+[driver['only_source_change']]),changed
assert sha(root/driver['only_source_change'])==driver['sha256']
for p,h in build['artifacts'].items():assert sha(root/p)==h
for p,h in build['staged_compile_inputs'].items():assert sha(root/p)==sha(Path(build['stage'])/p)==h and before[p]==h,p
st=read('integrity_after_test.json')['staged'];assert not st['missing'] and not st['mismatch']
for p,h in st['sha256'].items():assert sha(Path(st['stage'])/p)==h,p
orig=here/'original_RM_MapComponent_SuspensionBridges.cs';path='src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs'
assert orig.read_bytes()==subprocess.check_output(['git','show',read('selftest_receipt.json')['tested_HEAD']+':'+path],cwd=root)
assert (here/'fast_broaden/RM_MapComponent_SuspensionBridges.cs').read_bytes()==(root/path).read_bytes()
for label,rc,line in [('red',1,'4/6 PASS; 2 FAIL'),('expanded_red',1,'3/8 PASS; 5 FAIL'),('broaden',0,'8/8 PASS; 0 FAIL'),('delete_all',1,'7/8 PASS; 1 FAIL'),('first_only',1,'7/8 PASS; 1 FAIL')]:
 r=read('fast_'+label+'/receipt.json');assert r['returncode']==rc and line in (here/('fast_'+label+'/stdout.txt')).read_text()
 for n,h in r['inputs_sha256'].items():assert sha(here/('fast_'+label)/n)==h
suite=read('selftest_receipt.json');assert suite['returncode']==0 and suite['source_test_hashes_unchanged'] and suite['sha256_after']==before
out=(here/'csharp_stdout.txt').read_text();assert '1252/1252 passed' in out and 'hose: 457/457 assertions passed' in out and out.count('ok    RailingToggle_')==8
assert 'PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in (here/'selftest_stdout.txt').read_text()
ex=read('output_extraction.json');trace=Path(ex['original_observer_path']);assert sha(trace)==ex['original_observer_sha256'] and trace.stat().st_size==ex['original_observer_bytes']
assert sha(here/'csharp_stdout.txt')==ex['stdout_sha256'] and sha(here/'csharp_stderr.txt')==ex['stderr_sha256']
for n in ('preflight_offline2.json','preflight_live2.json'):assert read(n)['verdict']=='GREEN'
live=read('live_attempt2.json');assert live['status']=='PASS' and live['restore']['status']=='PASS'
assert live['before']==live['restore']['rect'] and live['settings_before']==live['restore']['settings']
a=live['railings_before'];b=live['railings_after'];assert a==b and len(a)==4
rows=[live['designations_'+x] for x in ('off','on','repeat')]
marks=lambda r:sorted((d['x'],d['z']) for d in r['designations'] if d['def']=='Deconstruct' and d['thing']=='RM_SuspensionRailing' and 30<=d['x']<54 and 30<=d['z']<48)
assert marks(rows[0])==sorted((t['x'],t['z']) for t in a) and not marks(rows[1]) and not marks(rows[2])
for r in rows:
 assert any(d['def']=='Plan' and (d['x'],d['z'])==(38,36) for d in r['designations'])
 assert any(d['def']=='Deconstruct' and d['thing']=='Wall' and (d['x'],d['z'])==(48,40) for d in r['designations'])
assert len({r['ticksGame'] for r in rows})==1
assert 'sha256='+build['artifacts']['src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'] in live['identity']
canonical={};saves=Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves')
for n,r in read('live_inputs_before.json')['saves'].items():
 canonical[n]=dict(bytes=(saves/n).stat().st_size,sha256=sha(saves/n));assert canonical[n]==r,n
for p,h in read('deployed_dlls.json')['sha256'].items():assert sha(Path(p))==h
assert read('live_census2.json')['ordered_list_matches']
assert 'NOT RUNNING' in (here/'game_final_stdout.txt').read_text() and 'DOWN' in (here/'game_final_stdout.txt').read_text()
assert 'driver lock: FREE' in (here/'bridge_final_stdout.txt').read_text() and 'bridge FREE' in (here/'bridge_final_stdout.txt').read_text()
raw=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/railing-toggle-raw');raw_hashes={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in raw.iterdir() if p.is_file()}
r=dict(time=time.time(),PUBLISHED=pub['PUBLISHED'],driver_PUBLISHED=driver['PUBLISHED'],post_suite_python_change=driver,ancestry_verified=True,fast='8/8; original initial 2 failures/6; expanded original 5 failures/8; each isolated mutant 1 failure/8',suite='PASS 1/1; main 1252/1252; hose 188/188 checks, 457/457 assertions; 8 normal RailingToggle cases',suite_elapsed=suite['elapsed'],test_hashes_stable=len(before),stage_readback=len(st['sha256']),shipping_compile_inputs=len(build['staged_compile_inputs']),changes_since_suite=changed,artifacts=build['artifacts'],live_identity=live['identity'],live_railings=a,restoration=live['restore'],canonical_and_site_unchanged=canonical,gss_files_unchanged=sum('GimmeSomeSlack/' in p for p in before),final_game='DOWN; NOT RUNNING',bridge='FREE; host driver FREE',raw_external=raw_hashes,limits=['Paused before-work cancellation, no pawn scheduler/completed deconstruction or in-progress-job claim','Raised leaf/multiple railings/same-thing unrelated designation/material/style and blueprint/frame variants are offline actual-method checks with explicit engine doubles','Live ordinary timber span; no mid-off occupied reload or stale-ON save automatic healing claim','Small ordered all-DLC tier, not full-list integration; no fresh GSS visual approval','Companion exact deployed artifact matches repository but lacks its own .srchash; FlowWorks shipping pair is stamped','Runner cache admission refused despite byte-stable recorded inputs'])
assert not (here/'final_checks.json').exists();(here/'final_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('restoration','canonical_and_site_unchanged','raw_external')},indent=2))
