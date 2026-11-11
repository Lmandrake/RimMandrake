from session_control import *
g=json.loads((E/'attempt4_guard_taken.stdout').read_text())
ENV['RM_DRIVER_PID']=str(g['identity']['pid']);ENV['RM_HOST_GUARD_GEN']=str(g['generation'])
try:
 guard('localization_deploy_guard')
 status=run('localization_deploy_down',GAME+['status'],False);assert status.stdout.strip()==b'stopped'
 run('localization_deploy_apply',['python3','src/RimMandrake/Utils/deploy_custom_mods.py','--mod','HugeThings','--apply'])
except Exception:
 run('deploy_failure_down',GAME+['down'],False)
 run('deploy_failure_release',BRIDGE+['release','--host','stevedesktop'],False)
 raise
