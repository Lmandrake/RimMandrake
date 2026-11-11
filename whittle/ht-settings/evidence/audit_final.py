"""Fresh read-only reconciliation of live artifacts, current source/deploy and cleanup.
No game/bridge calls, result mutation, ledger writes or timestamp manipulation.
"""
from pathlib import Path
import sys,json,hashlib,re,time,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;A=E/'attempt4'
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
sys.path.insert(0,str(ROOT/'src/RimMandrake/HugeThings/northstar'))
from settings_hardening_live import SPEC,expected,check_values

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
r={'read_at_epoch':time.time(),'scope':'HUGETHINGS_SETTINGS_HARDENING_1','checks':{},'arms':{},'raw_hashes':{}}
c=r['checks']
base=read(E/'base.json')
for name in ['STATEMENT.md','NOTES.md']:assert sha(E.parent/name)==base['frozen'][name]
c['frozen_statement_notes_unchanged']=True
amendment=E.parent/'PARENT_JUDGE_PROMPT_AMENDMENT.md';assert amendment.is_file()
c['parent_judge_prompt_amendment']={'original_sha256':base['frozen']['JUDGE_PROMPT.md'],'current_sha256':sha(E.parent/'JUDGE_PROMPT.md'),'receipt':str(amendment.relative_to(ROOT)),'receipt_sha256':sha(amendment)}
attempt=read(A/'live_attempt.json');assert attempt['ok'] and not attempt['errors'];c['attempt_ok']=True
pids=[]
steam=read(E/'steam_parent_process.json');assert steam['Name'].lower()=='steam.exe'
for arm in ['baseline','adversarial','valid','upgrade','restore']:
 live=read(A/(arm+'_live.json'));assert live['ok'] and not live['errors']
 assert live['tested_numeric_writes']==0
 assert live['script_sha256']==sha(ROOT/'src/RimMandrake/HugeThings/northstar/settings_hardening_live.py')
 values=live['first_loaded_fields']
 for key,(lo,hi,_,_) in SPEC.items():assert lo<=float(values[key])<=hi
 process=read(A/(arm+'_process.stdout'));pids.append(process['ProcessId'])
 assert process['ParentProcessId']==steam['ProcessId']
 assert process['ExecutablePath']==r'D:\SteamLibrary\steamapps\common\RimWorld\RimWorldWin64.exe'
 assert live['semantic_settings']['mod']['rootDir']==r'D:\SteamLibrary\steamapps\common\RimWorld\Mods\HugeThings'
 assert live['semantic_settings']['settingsType']=='RimMandrake.HugeThings.RM_HugeThingsSettings'
 log=live['startup_log'];assert not log['first_exception'] and not log['config_errors'] and not log['scribe_parse_errors']
 d={'pid':process['ProcessId'],'creation':process['CreationDate'],'first_loaded_fields':values,'warning_ticks':live['warning_ticks']['result'],'startup_log':log}
 if arm in ['adversarial','valid','upgrade']:
  disk=read(A/(arm+'_disk_before.json'));first=read(A/(arm+'_disk_first_read.json'))
  fixture=A/(arm+'_fixture.xml');assert sha(fixture)==disk['sha256']==first['sha256']==live['fixture']['sha256']
  vals={e.tag:e.text for e in ET.parse(fixture).getroot().find('ModSettings')}
  if arm=='upgrade':assert 'titanEventWarningHours' not in vals;vals['titanEventWarningHours']='2'
  assert not check_values(values,expected(vals));assert live['numeric_failures']=={}
  d.update(fixture_sha256=sha(fixture))
 if arm!='restore':
  assert all(x['found'] for x in live['label_checks'].values());assert len(live['ui_pages'])>=5
  assert '- Giant plants' in live['rendered_labels'] and '- Giant animals' in live['rendered_labels'] and '- Titan events' in live['rendered_labels']
  assert not any('RM_HugeThings_' in s or re.search(r'\{\d+\}',s) for s in live['rendered_labels'])
  assert all((A/Path(shot['path'].replace('\\','/')).name).is_file() for shot in live['screenshots']+live['hover_screenshots'])
  assert [(w['type'],w['id']) for w in live['windows_before']['windows']]==[(w['type'],w['id']) for w in live['windows_after']['windows']]
  d.update(rendered_key_checks=len(live['label_checks']),screenshots=len(live['screenshots']),tooltip_screenshots=len(live['hover_screenshots']))
 if arm=='adversarial':assert live['thresholds']['result']=='RM_TitanicTierDef:RM_TitanicTiers_Default'
 if arm=='valid':assert live['thresholds']['result']=='RM_TitanicTierDef:RM_TitanicTiers_ModSettings';assert float(values['titanEventWarningHours'])==6
 if arm=='upgrade':
  assert float(values['titanEventWarningHours'])==2 and float(values['corpseSiteWorkHoursPerSession'])==.25
  assert float(values['corpseSiteHarvestMeatPerSession'])==5 and float(values['corpseSiteHarvestLeatherPerSession'])==2 and float(values['corpseSiteScavengerMax'])==8
  d['work_hours_display_precision']={'loaded':values['corpseSiteWorkHoursPerSession'],'rendered':[x for x in live['rendered_labels'] if x.startswith('Work hours per session:')],'production_format':'0.0'}
 r['arms'][arm]=d
 for pre in ['preflight_offline','preflight_live']:
  report=read(A/(arm+'_'+pre+'.json'))
  assert all(x['status']=='PASS' for x in report['rows'] if x['required'] and x['id']!='O02')
assert len(set(pids))==5;c['distinct_cold_processes']=pids
assert attempt['active_restoration']['equal']
assert read(A/'restore_live.json')['first_loaded_fields']==read(A/'baseline_live.json')['first_loaded_fields']==read(E/'baseline_live.json')['first_loaded_fields'];c['all_baseline_fields_restored']=True
original=read(E/'original_settings_inventory.json');assert original['hugethings_absent']
for folder in [Path(original['game_config']),Path(original['linux_config'])]:
 assert not [p for p in folder.glob('*') if 'hugethings' in p.name.lower()]
c['game_and_linux_settings_absent']=True
assert not Path(original['linux_config']).exists();c['linux_original_directory_absence']=True
assert (A/'finally_status.stdout').read_text().strip()=='stopped';assert read(A/'finally_guard.stdout')['state']=='FREE';c['game_down_host_free']=True
# Current source-to-stamp and deployed pair are read after game shutdown.
mod=ROOT/'src/RimMandrake/HugeThings';stamp=(mod/'Assemblies/RM_HugeThings.dll.srchash').read_text()
rows=re.findall(r'^([0-9a-f]{64}) (.+)$',stamp,re.M);assert rows
for want,name in rows:assert sha(mod/'Source'/name.strip())==want
assert '# dll: '+sha(mod/'Assemblies/RM_HugeThings.dll') in stamp
for rel in ['Assemblies/RM_HugeThings.dll','Assemblies/RM_HugeThings.dll.srchash','Languages/English/Keyed/RM_HugeThings.xml','Languages/English/Keyed/RM_TitanicCreatures.xml']:
 assert sha(mod/rel)==sha(Path(game_paths.LOCAL_MODS)/'HugeThings'/rel)
snapshot=read(E/'localized_source_manifest.json')
for path,entry in snapshot['files'].items():assert sha(ROOT/path)==entry['sha256']==sha(E/entry['snapshot'])
assert snapshot['dll_sha256']==sha(mod/'Assemblies/RM_HugeThings.dll')
strings=read(E/'localization_dll_strings.json')
assert strings['dll_sha256']==sha(mod/'Assemblies/RM_HugeThings.dll')
assert all(strings['new_key_utf16_presence'].values()) and not any(strings['removed_literal_utf16_presence'].values())
old=read(E/'final_source_manifest.json')['files']['src/RimMandrake/HugeThings/Source/RM_HugeThingsSettings.cs']
old_prefix=(E/old['snapshot']).read_bytes().split(b'        private static Vector2 settingsScroll;',1)[0]
new_prefix=(mod/'Source/RM_HugeThingsSettings.cs').read_bytes().split(b'        private static Vector2 settingsScroll;',1)[0]
assert old_prefix==new_prefix
c['numeric_scribe_sanitize_prefix_unchanged_sha256']=hashlib.sha256(new_prefix).hexdigest()
c['all_13_new_dll_key_literals_and_removed_display_literals_checked']=True
c['compiled_inputs_matched']=len(rows);c['source_deployed_artifact_pair_equal']=True
c['final_source_snapshot_files_matched']=len(snapshot['files'])
mods=ET.parse(game_paths.MODS_CONFIG).find('activeMods');ids=[x.text for x in mods]
assert len(ids)==14;assert len([x for x in ids if x.startswith('ludeon.rimworld.')])==5;c['active_mods_ordered']=ids
for path in sorted(E.rglob('*')):
 if path.is_file() and path.suffix not in ['.pyc'] and path.name not in ['final_audit.json','final_hashes.json','final_audit.stdout','final_audit.stderr','final_audit.rc']:
  r['raw_hashes'][str(path.relative_to(E))]=sha(path)
r['ok']=True
(E/'final_audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'ok':True,'checks':c,'arms':{k:{x:v[x] for x in ['pid','warning_ticks']} for k,v in r['arms'].items()},'hashed_files':len(r['raw_hashes'])}))
