"""Fresh post-cleanup audit of immutable live receipts and current source/host.
Does not rerun or relabel historical trials; retain exact input digests and times.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import session_control as S

ROOT=S.ROOT
E=S.E
candidate=Path(sys.argv[1]).resolve()
out=E/'final-verification.json'
assert not out.exists(), 'preserve previous final audit'
sys.path.insert(0,str(ROOT/'src/RimMandrake/HugeThings/northstar'))
import passage_pool_live as P
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda name:json.loads((candidate/name).read_text())
live=read('live.json')
session=read('session.json')
assert live['status']==session['status']=='PASS'
assert not live['restore_errors'] and not live['restore_differences'] and not session['cleanup_errors']
assert {r['id'] for r in live['rows'] if r['status']=='PASS'}=={'event_off_fresh_tick','A2_complete_land_pool','A3_real_forced_arrival','exact_scene_and_settings_restored'}
assert live['baseline']==live['restored']
assert live['original_disk_hashes']==live['restored_disk_hashes']
driver=ROOT/'src/RimMandrake/HugeThings/northstar/passage_pool_driver.py'
assert digest(driver)==live['driver_source_sha256'], 'driver changed since live proof'
audit=P.audit({k:live[k] for k in ('pool_response','arrival_response','own_roster')})
assert audit['ok']
assert set(live['tile_changes'])=={'biome'} and live['staged_tile']['biome']=='RM_Stillsand'
assert len(live['new_pawns'])==1 and live['new_pawns'][0]['id']==live['arrived']['pawn']
assert live['arrived']['kind'] in live['own_roster']
for name in ('preflight_offline','steam_launch_preflight_live'):
 r=read(name+'.json')
 assert not [x for x in r['rows'] if x['required'] and x['id']!='O02' and x['status']!='PASS']
 assert read(name+'_assessment.json')['O02']['status']=='N/A'
 assert (candidate/(name+'.rc')).read_text().strip()=='0'
for name in ('startup_log_gate','post_live_log_gate'):
 r=read(name+'.json');assert not r['first_exception'] and not r['config_errors'] and not r['scribe_parse_errors']
held=read('actual_guard_before_drive.stdout')
assert held['state']=='HELD' and held['seat']=='BENCH' and held['identity']['pid']==2835258 and held['purpose']=='HT: TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT'
route=[json.loads(x) for x in (candidate/'steam_route.jsonl').read_text().splitlines()]
assert len(route)==1 and route[0]['route']=='steam://rungameid/294100' and int(route[0]['generation'])==held['generation']
artifact=read('artifact-inventory.json')
assert all(x['equal'] for x in artifact['HugeThings'].values())
assert all(x['equal'] for x in artifact['compiled_inputs'])
assert all(x['equal'] for x in artifact['HugeThings_xml'])
assert artifact['five_dlc_present'] and len(artifact['ModsConfig']['ordered'])==16
assert artifact['HugeThings']['dll']['deployed_sha256']==live['artifact_sha256']
assert all(digest(Path(x['source']))==x['expected'] for x in artifact['compiled_inputs'])
down=S.run('final_actual_game_status',S.GAME+['status'],False)
assert down.stdout.strip()==b'stopped'
free=json.loads(S.run('final_actual_guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert free['state']=='FREE' and free['generation']==held['generation']
assert b'FREE' in S.run('final_bridge_free',S.BRIDGE+['who','--host','stevedesktop']).stdout
credentials=[]
for f in candidate.iterdir():
 if f.is_file() and f.suffix in ('.json','.jsonl','.stdout','.stderr'):
  if re.search(rb'bridge token:\s*(?!\[credential redacted\])[A-Za-z0-9+/=_-]{16,}|authorization:\s*bearer\s*(?!\[credential redacted\])[A-Za-z0-9+/=_-]{16,}|"token"\s*:\s*"[A-Za-z0-9+/=_-]{20,}',f.read_bytes(),re.I):credentials.append(str(f))
assert not credentials, 'credential pattern detected; do not print its contents'
inputs={str(p.relative_to(ROOT)):{'sha256':digest(p),'mtime':p.stat().st_mtime} for p in sorted(candidate.iterdir()) if p.is_file()}
rec={'checked_at':time.time(),'scope':'Fresh read-only post-cleanup verification of recorded live trial and unchanged current source; not a new live trial and not an mtime refresh of raw evidence.',
 'candidate':str(candidate.relative_to(ROOT)),'status':'PASS','live_status':live['status'],'raw_content_audit':audit,
 'recorded_baseline_exactly_restored':True,'actual_host_now':free,'actual_game_now':down.stdout.decode().strip(),
 'generation_during_trial':held['generation'],'driver_source_sha256':digest(driver),'credential_pattern_matches':len(credentials),
 'inputs':inputs,'limits':['Synthetic tile-biome fixture on existing calm_v3 map, not native Stillsand terrain generation','DebugArriveNow plus governed tick compresses warning timing','No completed crossing, showcase or flight claim','Recorded job fields replayed only for changed idle wander targets; internal toil/RNG state not certified']}
out.write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({k:rec[k] for k in ('status','candidate','actual_game_now','generation_during_trial')}))
