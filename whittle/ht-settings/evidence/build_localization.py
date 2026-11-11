"""Parent source commit gate -> prescribed build -> reviewed dry plan only.
No deployment until the complete generated plan has been read.
"""
from session_control import *
import sys
req=json.loads((E/'localization_source_request.json').read_text())
for name in ['src/RimMandrake/HugeThings/Source/RM_HugeThingsSettings.cs','src/RimMandrake/HugeThings/Languages/English/Keyed/RM_HugeThings.xml']:
 p=subprocess.run(['git','show','HEAD:'+name],capture_output=True,cwd=ROOT)
 assert p.returncode==0 and hashlib.sha256(p.stdout).hexdigest()==req['files'][name]
g=json.loads(run('attempt4_guard_free',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout);assert g['state']=='FREE'
original=json.loads((E/'guard_initial.stdout').read_text());ENV['RM_DRIVER_PID']=str(original['identity']['pid'])
run('attempt4_take',BRIDGE+['take','--host','stevedesktop','--idle-ok','--for','HT: HUGETHINGS_SETTINGS_HARDENING_1'])
g=json.loads(run('attempt4_guard_taken',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert g['state']=='HELD' and g['generation']>1398 and g['identity']==original['identity']
ENV['RM_HOST_GUARD_GEN']=str(g['generation'])
try:
 status=run('build_game_status',GAME+['status'],False);assert status.stdout.strip()==b'stopped'
 run('localization_winbuild',['python3','src/RimMandrake/Utils/winbuild.py','HugeThings','--','/p:HarmonyDll=D:/SteamLibrary/steamapps/workshop/content/294100/2009463077/1.6/Assemblies/0Harmony.dll','/p:RimWorldManaged=D:/SteamLibrary/steamapps/common/RimWorld/RimWorldWin64_Data/Managed'])
 run('localization_deploy_plan',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThings'],False)
except Exception:
 run('build_failure_down',GAME+['down'],False)
 run('build_failure_release',BRIDGE+['release','--host','stevedesktop'],False)
 run('build_failure_guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json'],False)
 raise
