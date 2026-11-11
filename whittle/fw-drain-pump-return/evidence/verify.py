"""Fresh offline verification of immutable live receipts and final source; never edits an input receipt."""
from copy import deepcopy
import hashlib,json,re,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8-sig'))
def require(ok,msg):
 if not ok:raise AssertionError(msg)
def assess(result):
 problems=[]
 try:
  require(result['chains_run']==['liquid_pump'],'wrong chain scope')
  rows=result['chains'][0]['components'];names=['pump_unpowered_idle','pump_draws_into_tank','pump_off_idles','pump_pours_back']
  require([x['name'] for x in rows]==names,'incomplete chain')
  require(result['all_green'] is True and all(x['verdict']=='PASS' for x in rows),'nonpassing row')
  def data(row):return [e['result'] for e in row['evidence'] if isinstance(e['result'],dict)]
  def pumps(row):return [x for x in data(row) if 'ProofPump(' in x.get('method','')]
  def cells(row):return [x for x in data(row) if 'rows' in x]
  def volume(reply):
   require(reply['success'] is True and len(reply['rows'])==3,'unreadable channel')
   require(all(x['isSource'] is False and x['isSink'] is False for x in reply['rows']),'source or sink in channel')
   return sum(x['dl'] for x in reply['rows'])
  require(pumps(rows[0])[0]['result']=='PUMP running=False moved=0 pour=False tank=empty:0','unpowered')
  require(volume(cells(rows[0])[0])==60000,'unpowered channel changed')
  draw=pumps(rows[1])[0]['result'];m=re.fullmatch(r'PUMP running=True moved=(\d+) pour=False tank=RM_Liquid_FreshWater:(\d+)',draw)
  require(m is not None,'draw readback')
  moved,stock=map(int,m.groups());require(moved>=2 and stock==moved*10000,'draw tank accounting')
  require(abs(volume(cells(rows[1])[0])-(60000-moved*10000))<200,'draw channel accounting')
  off=pumps(rows[2]);require(len(off)==2 and off[0]['result']==off[1]['result'] and 'running=False' in off[0]['result'],'disabled control')
  ev=rows[3]['evidence'];tank=[(i,e['result']) for i,e in enumerate(ev) if isinstance(e['result'],dict) and 'ProofTank(' in e['result'].get('method','')]
  require(len(tank)==1,'no unique tank readback')
  i,tr=tank[0];require(tr.get('success') is True and re.fullmatch(r'TANK mode=Dump effective=Dump liquid=RM_Liquid_FreshWater units=\d+',tr['result']) is not None,'tank Dump readback')
  p=pumps(rows[3]);require(len(p)==1 and p[0].get('success') is True and 'running=True' in p[0]['result'] and 'pour=True' in p[0]['result'],'pour switch not confirmed')
  pi=next(j for j,e in enumerate(ev) if e.get('result')==p[0]);wi=next(j for j,e in enumerate(ev) if e['call'].startswith('wait_ticks'))
  require(i<pi<wi,'Dump must precede Pour and tick wait')
  vols=[volume(x) for x in cells(rows[3])];require(len(vols)==2 and vols[1]>vols[0]+200,'no measured rise')
  require(p[0]['ticksGame']==tr['ticksGame'] and cells(rows[3])[-1]['ticksGame']-p[0]['ticksGame']==600,'pour real tick interval')
  watch=result['chains'][0]['situational'];require(watch['ticks_spent']==2600 and not watch['surprises'] and not watch['close_problems'] and watch['runValidity']['verdict']=='CLEAN','disturbed run')
 except (AssertionError,KeyError,TypeError,ValueError,StopIteration) as ex:problems.append(str(ex))
 return problems
r=read('result.json');require(not assess(r),assess(r));negative=[]
for label,mut in [('wrong-pump-readback',lambda x:x['chains'][0]['components'][-1]['evidence'][2]['result'].update(result='PUMP running=True moved=3 pour=False tank=RM_Liquid_FreshWater:30000')),
                  ('missing-tank-readback',lambda x:x['chains'][0]['components'][-1]['evidence'][0]['result'].update(result='REFUSED: no tank')),
                  ('external-source',lambda x:x['chains'][0]['components'][-1]['evidence'][-1]['result']['rows'][0].update(isSource=True))]:
 c=deepcopy(r);mut(c);problems=assess(c);require(bool(problems),'negative receipt accepted '+label);negative.append({'case':label,'refused':problems})
scene=read('scene-public.json');drive=read('drive.json')
require(scene['status']=='PASS' and scene['restore']['status']=='PASS' and not scene['restore']['errors'],'scene restoration')
require(scene['site']['verified'] and scene['site']['save']=='RM_TestSite_calm_v3' and scene['baseline_reload']['verified'],'registered/reloaded baseline')
require(scene['baseline_rect']==scene['restore']['rect'],'map fingerprint')
require(all(x['value']==x['after'] for x in scene['restore']['settings']) and len(scene['restore']['settings'])==410,'mod setting readbacks')
require(scene['debug_before']==scene['restore']['debug'] and scene['difficulty_before']==scene['restore']['difficulty'],'debug/difficulty')
require(scene['canonical_before']==scene['canonical_after'] and not scene['saves_changed'],'existing saves')
require(scene['mode_precondition']['tankModesEnabled']=='True','modes bypassed')
require(drive['status']=='PASS' and drive['bridge_and_lock_free'] and not drive['cleanup_errors'],'shutdown/release')
for p in ['preflight-offline-2.json','preflight-live.json']:require(read(p)['verdict']=='GREEN',p)
for p in ['log-scan-loaded.json','log-scan-after-scene.json','log-final.json']:require(read(p)['hits']==[],p)
identity=read('artifact-identity.json');require(r['env']['assembly_sha256']==identity['mods']['FlowWorks']['RimMandrakeFlowWorks.dll']['source_sha256'],'live artifact')
for mod in identity['mods'].values():require(all(x['same'] for x in mod.values()),'artifact mismatch')
# Match every source entry and the DLL's own header, from the final worktree.
stamp=ROOT/'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash';lines=stamp.read_text().splitlines();project=lines[0].split(': ',1)[1];source=ROOT/'src'/Path(project).parent
entries=[]
for line in lines[1:]:
 if not line or line.startswith('#'):continue
 expected,relative=line.split(' ',1);path=source/relative.replace('\\','/');actual=hashlib.sha256(path.read_bytes()).hexdigest();require(actual==expected,'source stamp '+relative);entries.append(relative)
require(next(l.split(': ',1)[1] for l in lines if l.startswith('# dll:'))==r['env']['assembly_sha256'],'DLL stamp')
redaction=read('scene-redaction.json')
raw=Path(redaction['raw_private']).read_bytes();public=(HERE/'scene-public.json').read_bytes()
require(hashlib.sha256(raw).hexdigest()==redaction['raw_sha256'] and hashlib.sha256(public).hexdigest()==redaction['public_sha256'],'redaction provenance')
private_log=Path(read('log-final.json')['private_path']).read_text(errors='replace')
secrets=re.findall(r'Bridge token:\s*(\S+)',private_log)
expected_public=raw
for secret in secrets:expected_public=expected_public.replace(secret.encode(),b'[REDACTED_BRIDGE_TOKEN]')
require(expected_public==public,'extract differs beyond exact secret redaction')
# Final source guard replays the actual live reply in the production row.
comparison=read('readback-comparison.json');require(comparison['actual_live_reply_replay']['verdict']=='PASS','final guard/live reply replay')
require(all(x['old']['verdict']=='PASS' and x['fixed']['verdict']=='UNMEASURED' for x in comparison['cases']),'can-fail readback regression')
require(all(x['verdict'] in ('PASS','FAIL','UNMEASURED') for x in read('readback-cases.json').values()),'case statuses')
require(len(read('failure-cases.json'))==3,'finally failure cases')
require('selftest_extensions: PASS' in (HERE/'extensions-offline.stdout.log').read_text(),'existing extension offline regression')
require('PASS Windows 1314' in (HERE/'rewrite-regression.log').read_text() and 'PASS Windows 1314' in (HERE/'rewrite-regression-windows.log').read_text(),'rewrite platform regressions')
# These are checks of historical receipts, not a new live run or a modified receipt.
files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file() and p.name not in ['verification.json','verify.stdout.log','verify.stderr.log'] and not p.name.startswith(('judge','done-'))}
sources=['src/RimMandrake/FlowWorks/northstar/extensions.py','src/RimMandrake/FlowWorks/northstar/selftest_pump_return_readback.py','src/RimMandrake/Utils/biomes_compose.py','src/RimMandrake/Utils/selftest_biomes_rewrite_windows.py']
summary={'checked_at':time.time(),'status':'PASS','scope':'liquid_pump only, four rows; no full-suite or rate/mode-persistence acceptance','original_live_source':'landed 0ce8db3227245542f51656802a7b6c72afd9b641 repair, clone HEAD '+identity['head'],'post_live_change':'strict mode-token and malformed-payload parser only; exact raw live reply replayed offline; no changed gameplay artifact','raw_hashes':files,'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},'source_stamp_entries_checked':len(entries),'negative_receipt_checks':negative,'actual_channel_dl':[60000,30000,60000],'actual_draw_moved':3,'actual_pour_ticks':600,'governed_ticks':2600,'baseline_rect':scene['baseline_rect'],'settings_checked':410,'canonical_hashes':scene['canonical_after'],'bridge_and_lock_free':True,'known_limits':['no post-pour pump/tank counter probe; no rate claim','isolated tier, not full mod list','companion embedded source verified; no srchash beside ignored companion artifact'], 'failure_classification':{'preflight-offline.json':'HARNESS: Windows symlink privilege 1314 in rewrite staging; fixed and cold/live rerun GREEN','live_chain_nonpasses':0}}
(HERE/'verification.json').write_text(json.dumps(summary,indent=2));print('PASS immutable live chain, exact restore, artifact/stamp, negative readback and cleanup checks')
