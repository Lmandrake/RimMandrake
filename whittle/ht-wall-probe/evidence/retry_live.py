"""Authorized same-parent-driver retake after diagnosed attempt 1 and proven FREE."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

root=Path(__file__).resolve().parents[3]; e=Path(__file__).resolve().parent
initial=json.loads((e/'live_run_1/guard_before.stdout').read_text())
env=dict(os.environ)
assert initial['generation']==1394 and str(initial['generation'])==env['RM_HOST_GUARD_GEN']
pid=initial['identity']['pid']; os.kill(pid,0)
env['RM_DRIVER_PID']=str(pid)
def run(name,args):
 p=subprocess.run(['bash','-c','source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\n'+shlex.join(args)],env=env,cwd=root,capture_output=True)
 for ext,data in [('stdout',p.stdout),('stderr',p.stderr),('rc',str(p.returncode).encode()+b'\n')]: (e/(name+'.'+ext)).write_bytes(data)
 if p.returncode: raise RuntimeError(name+' failed')
 return p
before=json.loads(run('retake_guard_before',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert before['state']=='FREE'
run('retake',['python3','src/RimMandrake/rimflow/cli.py','bridge','take','--host','stevedesktop','--idle-ok','--for','HT: TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS'])
after=json.loads(run('retake_guard_after',['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
assert after['state']=='HELD' and after['seat']=='BENCH' and after['identity']==initial['identity'] and after['generation']>initial['generation']
env['RM_HOST_GUARD_GEN']=str(after['generation'])
(e/'retake_chain.json').write_text(json.dumps(dict(original=initial,before=before,after=after),indent=2)+'\n')
p=subprocess.run(['bash','-c','source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\npython3 whittle/ht-wall-probe/evidence/run_live.py live_run_2'],env=env,cwd=root)
sys.exit(p.returncode)
