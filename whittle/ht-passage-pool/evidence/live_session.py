"""One guarded live attempt; always shut down and release actual host."""
import json
import os
from pathlib import Path
import sys
import time
import traceback
import session_control as S

E=S.E
assert E.is_relative_to(S.ROOT),'evidence must remain inside own clone'
E.mkdir(exist_ok=False)
rec={'started':time.time(),'status':'IN_PROGRESS'}
rc=1
try:
 S.guard('actual_guard_before')
 S.run('game_before',S.GAME+['status'],False)
 S.run('tier_apply',['python3','src/RimMandrake/Utils/modset_builder.py','--tier',S.TIER,'--apply','--not-my-bridge','Actual SteveDesktop host_guard independently HELD BENCH under the verified fresh generation and parent PID; the legacy bridge companion file is on the other host (authorized O02 boundary).'])
 S.preflight('preflight_offline')
 S.guard('actual_guard_before_launch')
 S.launch('steam_launch')
 logs=S.inspect_log('startup_log_gate')
 assert not logs['first_exception'] and not logs['config_errors'] and not logs['scribe_parse_errors'],logs
 S.guard('actual_guard_before_drive')
 rootwin=S.run('clone_windows_path',['wslpath','-w',str(S.ROOT)]).stdout.decode().strip()
 out=rootwin+'\\'+str(E.relative_to(S.ROOT)).replace('/','\\')+'\\live.json'
 p=S.run('live_driver',['python.exe',rootwin+'\\src\\RimMandrake\\HugeThings\\northstar\\passage_pool_driver.py','--out',out],False,timeout=900)
 rec['driver_rc']=p.returncode
 rec['post_log']=S.inspect_log('post_live_log_gate')
 assert not rec['post_log']['first_exception'] and not rec['post_log']['config_errors'] and not rec['post_log']['scribe_parse_errors'],rec['post_log']
 assert p.returncode==0,'live driver non-pass'
 rec['status']='PASS'
 rc=0
except BaseException as ex:
 rec.update(status='FAIL',error=repr(ex),traceback=traceback.format_exc())
finally:
 errors=[]
 for name,args in [('cleanup_down',S.GAME+['down','--wait']),('cleanup_game_status',S.GAME+['status']),
                   ('cleanup_release',S.BRIDGE+['release','--host','stevedesktop']),
                   ('cleanup_actual_guard',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']),
                   ('cleanup_bridge_free',S.BRIDGE+['who','--host','stevedesktop'])]:
  try:
   p=S.run(name,args,False)
   if name=='cleanup_down': assert p.returncode==0
   if name=='cleanup_game_status': assert p.stdout.strip()==b'stopped'
   if name=='cleanup_actual_guard': assert json.loads(p.stdout)['state']=='FREE'
   if name=='cleanup_bridge_free': assert b'FREE' in p.stdout
   if name=='cleanup_release': assert p.returncode==0
  except Exception as ex:errors.append(name+': '+repr(ex))
 rec.update(cleanup_errors=errors,finished=time.time())
 if errors:rec['status']='FAIL';rc=1
 (E/'session.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(rec),flush=True)
sys.exit(rc)
