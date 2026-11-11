"""One settings-hardening attempt: three cold fixture arms, exact restore, shutdown.
Adapted to HUGETHINGS_SETTINGS_HARDENING_1 from ht-two-hour-warning/run_live.py.
No deploy needed: full dry plan + direct bytes already match. Never change tier.
"""
from session_control import *
CONTROL=Path(__file__).resolve().parent
import sys,xml.etree.ElementTree as ET
sys.path.insert(0,str(ROOT/'src/RimMandrake/HugeThings/northstar'))
from settings_hardening_live import fixture_values,SPEC
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
config=Path(game_paths.MODS_CONFIG).parent
settings=config/'Mod_HugeThings_RM_HugeThingsMod.xml'
manifest=json.loads((E/'original_settings_inventory.json').read_text())
script=ROOT/'src/RimMandrake/HugeThings/northstar/settings_hardening_live.py'
summary={'started':time.time(),'item':'HUGETHINGS_SETTINGS_HARDENING_1','ok':False,'arms':[],'errors':[]}
def persist(): (E/'live_attempt.json').write_text(json.dumps(summary,indent=2)+'\n')
def disk_restore(name):
 # Only HugeThings paths owned by this proof, exact original bytes or absence.
 touched=set(manifest['settings'])|{str(settings)}
 for path in touched:
  p=Path(path)
  if path in manifest['settings']:p.write_bytes((E/manifest['settings'][path]['backup']).read_bytes())
  elif p.exists():p.unlink()
 r={p:{'exists':Path(p).exists(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).exists() else None} for p in touched}
 for path,v in r.items():
  assert v['sha256']==manifest['settings'].get(path,{}).get('sha256')
 (E/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
def probe(arm,fixture=None,ui=False):
 args=['python.exe',run(arm+'_script_winpath',['wslpath','-w',str(script)]).stdout.decode().strip(),'--arm',arm,'--out',run(arm+'_out_winpath',['wslpath','-w',str(E/(arm+'_live.json'))]).stdout.decode().strip()]
 if fixture:args+=['--fixture',run(arm+'_fixture_winpath',['wslpath','-w',str(fixture)]).stdout.decode().strip()]
 if ui:args+=['--ui']
 run(arm+'_probe',args,timeout=300)
 r=json.loads((E/(arm+'_live.json')).read_text());assert r['ok'],r['errors'];return r
try:
 guard('attempt_guard');run('attempt_lease',BRIDGE+['who','--host','stevedesktop'])
 run('baseline_stop',GAME+['down'])
 assert not settings.exists(),'baseline original absence required'
 preflight('baseline_preflight_offline');launch('baseline')
 run('baseline_identity',['python3',str(CONTROL/'capture_process.py'),'baseline_process'])
 probe('baseline',ui=True)
 run('baseline_after_stop',GAME+['down'])
 for arm in ['adversarial','valid','upgrade']:
  # Use native-generated XML root/class; do not guess Scribe structure.
  tree=ET.parse(E/'native_saved_Mod_HugeThings_RM_HugeThingsMod.xml');node=tree.getroot().find('ModSettings')
  values=fixture_values('valid' if arm=='upgrade' else arm)
  if arm=='upgrade':
   values.update(corpseSiteWorkHoursPerSession='0',corpseSiteHarvestMeatPerSession='0',corpseSiteScavengerMax='99999',corpseSiteHarvestLeatherPerSession='-7')
   del values['titanEventWarningHours']
  for k,v in values.items():ET.SubElement(node,k).text=v
  ET.SubElement(node,'tierThresholdsCustom').text='true'
  data=ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)
  fixture=E/(arm+'_fixture.xml');fixture.write_bytes(data);settings.write_bytes(data)
  before={'linux_path':str(settings),'windows_path':game_paths.wsl_to_win(str(settings)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'pre_start_readback_sha256':hashlib.sha256(settings.read_bytes()).hexdigest()}
  (E/(arm+'_disk_before.json')).write_text(json.dumps(before,indent=2)+'\n')
  preflight(arm+'_preflight_offline');launch(arm)
  run(arm+'_identity',['python3',str(CONTROL/'capture_process.py'),arm+'_process'])
  log=inspect_log(arm+'_startup_log');assert not log['first_exception'] and not log['config_errors'],log
  # Hash again before any test-field read or UI draw. Existing cold process did all Scribe loading.
  loaded_hash=hashlib.sha256(settings.read_bytes()).hexdigest()
  (E/(arm+'_disk_first_read.json')).write_text(json.dumps({'sha256':loaded_hash,'fixture_sha256':before['sha256'],'equal':loaded_hash==before['sha256']},indent=2)+'\n')
  assert loaded_hash==before['sha256']
  r=probe(arm,fixture,ui=True)
  post=inspect_log(arm+'_post_ui_log');assert not post['first_exception'] and not post['config_errors'],post
  summary['arms'].append({'arm':arm,'ok':r['ok'],'fixture_sha256':before['sha256']});persist()
  run(arm+'_stop',GAME+['down'])
 summary['ok']=True
except Exception as ex:
 summary['errors'].append(str(ex));print('FAILED',ex,flush=True)
finally:
 # Cleanup continues after every failed check, including restore launch failure.
 try:
  run('cleanup_down',GAME+['down']);disk_restore('disk_restored_before_restart')
  preflight('restore_preflight_offline');launch('restore')
  run('restore_identity',['python3',str(CONTROL/'capture_process.py'),'restore_process'])
  restored=probe('restore')
  baseline=json.loads((E/'baseline_live.json').read_text())['first_loaded_fields']
  summary['active_restoration']={'equal':restored['first_loaded_fields']==baseline,'baseline':baseline,'readback':restored['first_loaded_fields']}
  assert summary['active_restoration']['equal'],'active settings not restored'
  log=inspect_log('restore_startup_log');assert not log['first_exception'] and not log['config_errors']
 except Exception as ex:
  summary['errors'].append('restoration: '+str(ex));summary['ok']=False
 try:
  run('finally_down',GAME+['down']);disk_restore('disk_restored_final')
  status=run('finally_status',GAME+['status'],require=False)
  assert status.stdout.strip()==b'stopped','game is not stopped'
 except Exception as ex:summary['errors'].append('down/disk: '+str(ex));summary['ok']=False
 try:
  run('finally_release',BRIDGE+['release','--host','stevedesktop'])
  run('finally_lease',BRIDGE+['who','--host','stevedesktop'])
  free=json.loads(run('finally_guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
  assert free['state']=='FREE',free
 except Exception as ex:summary['errors'].append('release: '+str(ex));summary['ok']=False
 summary['finished']=time.time();persist()
print(json.dumps(summary));sys.exit(0 if summary['ok'] else 1)
