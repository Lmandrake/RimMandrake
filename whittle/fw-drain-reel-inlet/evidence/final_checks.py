"""Final readback of preserved raw proof and current inputs after live cleanup. Never reruns a suite."""
from pathlib import Path
import json,hashlib,re,subprocess,time
here=Path(__file__).resolve().parent;root=here.parents[2];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda n:json.loads((here/n).read_text())
fast=read('fast_final_correct_fixture/receipt.json');assert fast['returncode']==0
for p,h in fast['source_sha256'].items():assert sha(root/p)==h,p
assert 'CHECKS 47 FAILURES 0' in (here/'fast_final_correct_fixture/stdout.txt').read_text()
suite=read('selftest_receipt.json');assert suite['returncode']==0 and suite['source_test_hashes_unchanged']
before=read('integrity_before.json')['sha256'];assert before==suite['sha256_after']
stdout=(here/'csharp_stdout.txt').read_text();assert '1244/1244 passed' in stdout and 'hose: 457/457 assertions passed' in stdout
for name in ['ReelBodyInlet_multicell_contacts_all_sides','ReelBodyInlet_filtered_oracle','ReelBodyInlet_filtered_pick_no_alloc','ReelBodyInlet_reachable_candidate_ranking']:assert 'ok    '+name in stdout
stage=read('integrity_after_test.json')['staged'];assert not stage['missing'] and not stage['mismatch']
build=read('build_integrity.json')
for p,h in build['staged_compile_inputs'].items():
 assert sha(root/p)==h and sha(Path(build['stage'])/p)==h,p
for p,h in build['artifacts'].items():assert sha(root/p)==h
pub=read('publication.json');subprocess.run(['git','merge-base','--is-ancestor',pub['PUBLISHED'],'origin/main'],cwd=root,check=True)
changed=[p for p,h in before.items() if sha(root/p)!=h]
assert sorted(changed)==sorted(list(build['artifacts'])+['src/RimMandrake/Utils/selftest_settings_screens.py']),changed
assert sha(root/'src/RimMandrake/FlowWorks/northstar/reel_body_inlet_live.py')==pub['live_driver_sha256']
mirror=Path('/mnt/d/Luke/dev/RimMandrake')
for p,h in build['artifacts'].items():assert sha(mirror/p)==h
live=read('live_attempt1.json');assert live['status']=='PASS' and live['restore']['status']=='PASS'
assert live['before']==live['restore']['rect'] and str(live['restore']['rules']).lower()=='true'
rows=live['readings'];assert len(rows)==6
for r in rows.values():assert r['portId']==r['hydraulicPortId']
assert rows['same_band_multicell']['contact']==[40,36]
assert rows['alternate_contact_same_tank']['contact']==[40,37]
assert rows['sheer_wall_refused']['portId']==-1
assert rows['rules_off']['portId']==rows['same_band_multicell']['portId']
assert rows['alternate_neighbour']['portId']==rows['invalid_preferred_east_pipe']['portId']
for label in ['depth_first','depth_second']:
 r=live[label];assert r['depth']==4 and r['fill']==0 and r['isExcavated'] is True
batches=[r for r in live['calls'] if r['tool']=='jawa/build_batch'];assert len(batches)==3
for row,count in zip(batches,[2,1,1]):
 r=row['result'];assert r['placed']==r['survived']==count and r['failed']==[] and r['lostToLaterOps']==0 and r['displaced']==[]
assert build['artifacts']['src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'] in live['identity']
for name in ['preflight_offline_repaired.json','preflight_live.json']:assert read(name)['verdict']=='GREEN'
assert 'driver lock: FREE' in (here/'bridge_final.txt').read_text() and 'bridge FREE' in (here/'bridge_final.txt').read_text()
assert 'NOT RUNNING' in (here/'game_final.txt').read_text() and 'DOWN' in (here/'game_final.txt').read_text()
saves=Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves');original=read('live_inputs_before.json')['saves'];canonical={n:dict(bytes=(saves/n).stat().st_size,sha256=sha(saves/n)) for n in original};assert canonical==original
raw=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/reel-inlet-raw');log=Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log');final_log=raw/'Player.after_shutdown.log';assert not final_log.exists();final_log.write_bytes(log.read_bytes())
lines=final_log.read_text(errors='replace').splitlines();issues=[(i+1,l) for i,l in enumerate(lines) if any(k in l for k in ['Exception','Config error in','Recovered from incompatible','Resetting mods config','Reached max messages limit'])];assert not issues,issues[:5]
assert sha(raw/'selftest_writes.strace')==read('output_extraction.json')['original_observer_sha256']
raw_hashes={p.name:dict(sha256=sha(p),bytes=p.stat().st_size) for p in raw.iterdir() if p.is_file()}
evidence=['fast_checks.json','fast_original_expanded/stdout.txt','fast_unfiltered_mutant/stdout.txt','fast_final_correct_fixture/stdout.txt','selftest_receipt.json','csharp_stdout.txt','integrity_after_test.json','build_integrity.json','publication.json','deployed_dlls.json','live_attempt1.json','bridge_final.txt','game_final.txt','live_scene.png']
result=dict(time=time.time(),PUBLISHED=pub['PUBLISHED'],ancestry_verified=True,fast_checks='47/47; unchanged original expanded 17 expected failures/43; isolated filter mutant 1 expected failure/47',suite='PASS 1/1; 1244/1244 main, 188/188 hose checks, 457/457 hose assertions',suite_hashes_stable=len(before),staged_suite_inputs=len(stage['sha256']),stamped_shipping_inputs=len(build['staged_compile_inputs']),changes_since_suite=changed,publication_qualification=pub['unrelated_publication_input_change'],gss_files_unchanged=sum(p.startswith('src/RimMandrake/GimmeSomeSlack/') for p in before),artifacts=build['artifacts'],live=rows,restoration=live['restore'],canonical_unchanged=canonical,log_issue_lines=issues,final_game='DOWN; NOT RUNNING',bridge='FREE; driver lock FREE',raw_external=raw_hashes,evidence_sha256={n:sha(here/n) for n in evidence},limits=['Forced Find/Port geometry, not normal cache convergence or liquid transfer','Relay intake indexing, on-footprint free-end semantics, water/swim/deck behavior unchanged and not newly accepted','Adapter uses explicit engine doubles; ladder/ramp witnesses do not simulate actual placement','Screenshot supporting only; GSS art preserved by exact hashes, no new visual approval','Known unrelated fuzz route note retained; cache admission refused despite stable recorded input bytes','Published unrelated settings-screen selftest update was not retested'])
(here/'final_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('live','restoration','raw_external','canonical_unchanged','evidence_sha256')},indent=2))
