"""Freshly inspect final raw results/source hashes; never relabel an old receipt."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

root=Path(__file__).resolve().parents[3]; e=Path(__file__).resolve().parent; run=e/'live_run_2'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise RuntimeError(why)
live=read(run/'live.json');process=read(run/'receipt.json');initial=read(e/'initial_manifest.json');m=read(e/'source_manifest.json')
require(process['ok'] is True and live['ok'] is True,'live process did not pass')
require(live['restoration']['ok'] is True and live['restore_hash']==live['baseline'],'scene restoration failed')
require(live['originals']==live['restored_settings'] and live['debug_originals']==live['restored_debug'],'raw settings differ')
require(all(live['difficulty_original'][f]==live['difficulty_restored'][f] for f in ('threatScale','allowBigThreats')),'difficulty differs')
require(live['clock_before']==live['clock_after'],'clock advanced')
arms=live['roofwall']['arms'];require(len(arms)==2 and all(a['status']=='PASS' and len(a['probes'])==2 for a in arms),'missing mode/control')
require(all(p['ok'] is True and p['stable'] is True and p['clean'] is True for a in arms for p in a['probes']),'unstable/missing calls')
require(len({tuple(p['cell']) for a in arms for p in a['probes']})==1,'geometry drift')
require(live['summary']['gameplay_pass'] is True and len(live['rows'])==1,'strict focused aggregate failed')
require(len(live['residue_checks'])==4 and all(r['clean'] for r in live['residue_checks']),'residue check failed')
fc=live['fingerprint_control'];require(len({fc['empty'],fc['roof'],fc['wall']})==3,'fingerprint control blind')
preflights={}
for name in ('preflight_offline','preflight_live'):
 raw=read(run/(name+'.json')); bad=[r for r in raw['rows'] if r['required'] and r['id']!='O02' and r['status']!='PASS']
 require(not bad,'required preflight nonpasses')
 preflights[name]=dict(verdict=raw['verdict'],other_required_nonpasses=bad,O02='N/A by frozen owner note: reads other host BRIDGE',raw_O02=[r for r in raw['rows'] if r['id']=='O02'])
for name in ('player_log_inspection','player_log_after_probe'):
 raw=read(run/(name+'.json'));require(raw['exception_line_count']==raw['config_error_count']==0,'log errors')
require(read(run/'guard_after.stdout')['state']=='FREE','host not FREE')
require('FREE' in (run/'lease_after.stdout').read_text(),'lease not FREE')
require((run/'game_after.stdout').read_text().strip()=='stopped','game not stopped')
require(int((e/'residue_fix_tests.rc').read_text())==0 and (e/'residue_fix_tests_detail.stdout').read_text().splitlines()[-1]=='195/195 PASS','focused tests fail')
require(int((e/'prefIx_tests.rc').read_text())==1,'pre-fix failure absent')
for p,v in m.items():
 if p=='launch_adapter':continue
 require(sha(root/p)==v['sha256'],'final source differs: '+p)
require(live['script_sha256']==sha(root/'src/RimMandrake/HugeThings/northstar/roofwall_modes_live.py'),'live script is not final')
for p,h in initial['frozen_hashes'].items():require(sha(root/p)==h,'frozen input changed')
raw_paths=[e/'prefIx_tests.stdout',e/'prefIx_tests.rc',e/'residue_fix_tests.stdout',e/'residue_fix_tests.rc',e/'residue_fix_tests_detail.stdout',e/'source_manifest.json',e/'source.diff',e/'initial_manifest.json',e/'retake_chain.json',e/'broaden_raw.json',e/'broaden_call.json']
raw_paths += [p for p in run.iterdir() if p.is_file()]
report=dict(inspected_at=time.time(),base_sha=initial['base_sha'],
 source_files={p:dict(sha256=sha(root/p),bytes=(root/p).stat().st_size) for p in m if p!='launch_adapter'},
 raw_files={str(p.relative_to(root)):dict(sha256=sha(p),bytes=p.stat().st_size) for p in raw_paths})
(e/'evidence_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print(str(e/'evidence_manifest.json'))
