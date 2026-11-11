"""Settings-hardening orchestration primitives, adapted from ht-two-hour-warning.
Every shell sources SteveDesktop environment. No ledger/deploy/baseline writes.
"""
import hashlib,json,os,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=Path(os.environ.get('HT_SETTINGS_EVIDENCE',str(Path(__file__).resolve().parent)))
ENV=dict(os.environ)
TIER='mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_hugethingstestraces__mandrake_rm_patches'
GAME=['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh']
BRIDGE=['python3','src/RimMandrake/rimflow/cli.py','bridge']
def run(name,args,require=True,timeout=900):
 command='source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\nexport RIMFLOW_SEAT=BENCH RM_CODEX_SIDE=wsl\n'+shlex.join(args)
 p=subprocess.run(['bash','-c',command],cwd=ROOT,env=ENV,capture_output=True,timeout=timeout)
 def safe(b):return b'\n'.join(b'[credential line redacted]' if re.search(rb'bridge token:|authorization:|bearer ',l,re.I) else l for l in b.split(b'\n'))
 for ext,data in [('stdout',safe(p.stdout)),('stderr',safe(p.stderr)),('rc',str(p.returncode).encode()+b'\n')]: (E/(name+'.'+ext)).write_bytes(data)
 print(name,'rc',p.returncode,flush=True)
 if require and p.returncode:raise RuntimeError(name+' failed')
 return p
def guard(name):
 g=json.loads(run(name,['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
 assert g['state']=='HELD' and g['seat']=='BENCH' and g['purpose']=='HT: HUGETHINGS_SETTINGS_HARDENING_1'
 assert g['generation']>1395 and str(g['generation'])==ENV.get('RM_HOST_GUARD_GEN')
 ENV['RM_DRIVER_PID']=str(g['identity']['pid'])
 # actual host_guard status independently verifies pid/start/boot, not pid number alone
 return g
def preflight(name,live=False):
 path=E/(name+'.json')
 args=['/home/mandrake/.cache/ht-warning-venv/bin/python3','src/RimMandrake/Utils/preflight_bridge.py','--tier','quicktest','--modset',TIER,'--deep','--all','--seat','BENCH','--json',str(path)]
 if live:args+=['--live']
 run(name,args,require=False)
 r=json.loads(path.read_text());bad=[x for x in r['rows'] if x['required'] and x['id']!='O02' and x['status']!='PASS']
 (E/(name+'_assessment.json')).write_text(json.dumps({'other_required_nonpasses':bad,'O02': [x for x in r['rows'] if x['id']=='O02'],'authorized_exception':'O02 other-host lease only; actual host independently guarded','ok':not bad},indent=2)+'\n')
 assert not bad,[(x['id'],x['status']) for x in bad]
def launch(name):
 guard(name+'_guard')
 real=ENV.get('HT_POWERSHELL_REAL')
 if not real or real==str(E/'steam_adapter/powershell.exe'):
  real=run(name+'_powershell',['which','powershell.exe']).stdout.decode().strip()
 assert real!=str(E/'steam_adapter/powershell.exe'),'genuine PowerShell required'
 ENV['HT_POWERSHELL_REAL']=real
 ENV['PATH']=str(E/'steam_adapter')+os.pathsep+ENV['PATH']
 p=run(name+'_up',GAME+['up','--wait'],False)
 if p.returncode:
  for i in range(12):
   time.sleep(5)
   p=run(name+'_delayed_'+str(i),GAME+['status'],False)
   if p.returncode==0 and b'bridge port in Player.log: 5174' in p.stdout:break
  else:raise RuntimeError('Steam delayed process/bridge absent')
 time.sleep(45)
 preflight(name+'_preflight_live',True)
def inspect_log(name):
 import sys
 sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
 p=Path(game_paths.PLAYER_LOG);lines=p.read_text(errors='replace').splitlines()
 ex=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Exception|Traceback',s)]
 cfg=[(i+1,s) for i,s in enumerate(lines) if 'Config error' in s]
 parse=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Error while loading|could not parse|exception parsing|XML error',s,re.I)]
 r={'path':str(p),'first_exception':ex[0] if ex else None,'exception_count':len(ex),'config_errors':cfg,'scribe_parse_errors':parse}
 (E/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
 return r
