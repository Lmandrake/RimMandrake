from session_control import *
import sys
sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
# inventory before ANY settings edit, including a close that can persist settings.
config=Path(game_paths.MODS_CONFIG).parent
linux=Path.home()/'.config/unity3d/Ludeon Studios/RimWorld by Ludeon Studios/Config'
r={'game_config':str(config),'game_config_windows':game_paths.wsl_to_win(str(config)),'linux_config':str(linux),'linux_exists':linux.exists(),'settings':{}}
for label,folder in [('game',config),('linux',linux)]:
 for p in folder.glob('*'):
  if 'hugethings' in p.name.lower():
   target=E/('original_'+label+'_'+p.name);target.write_bytes(p.read_bytes());r['settings'][str(p)]={'backup':target.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
r['hugethings_absent']=not r['settings']
(E/'original_settings_inventory.json').write_text(json.dumps(r,indent=2)+'\n')
try:
 guard('guard_initial');run('lease_initial',BRIDGE+['who','--host','stevedesktop'])
 preflight('baseline_preflight_offline');launch('baseline');inspect_log('baseline_startup_log')
except Exception:
 run('baseline_failure_down',GAME+['down'],False)
 run('baseline_failure_release',BRIDGE+['release','--host','stevedesktop'],False)
 raise
