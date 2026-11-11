"""Passage-pool orchestration primitives, adapted from ht-two-hour-warning.
Every shell sources SteveDesktop environment. No ledger/deploy/baseline writes.
"""
import hashlib,json,os,re,shlex,signal,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=Path(os.environ.get('HT_PASSAGE_EVIDENCE',str(Path(__file__).resolve().parent)))
ADAPTER=Path(__file__).resolve().parent/'steam_adapter'
ENV=dict(os.environ)
TIER='mods__mandrake_rm_flowworks__mandrake_rm_hugethings__mandrake_rm_patches__mandrake_rm_biomes__oskarpotocki_vanillafactionsexpanded_core'
GAME=['bash','/home/mandrake/rm/runner/infrastructure/stevedesktop/rw_game.sh']
BRIDGE=['python3','src/RimMandrake/rimflow/cli.py','bridge']
def run(name,args,require=True,timeout=900):
 command='source /home/mandrake/rm/runner/infrastructure/stevedesktop/testcentre_env.sh\nexport RIMFLOW_SEAT=BENCH RM_CODEX_SIDE=wsl\n'+shlex.join(args)
 proc=subprocess.Popen(['bash','-c',command],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 interrupted=None
 try:stdout,stderr=proc.communicate(timeout=timeout)
 except BaseException as ex:
  interrupted=ex
  os.killpg(proc.pid,signal.SIGTERM)
  try:stdout,stderr=proc.communicate(timeout=10)
  except subprocess.TimeoutExpired:
   os.killpg(proc.pid,signal.SIGKILL);stdout,stderr=proc.communicate()
 p=subprocess.CompletedProcess(proc.args,proc.returncode,stdout,stderr)
 def safe(b):return b'\n'.join(b'[credential line redacted]' if re.search(rb'bridge token:|authorization:|bearer ',l,re.I) else l for l in b.split(b'\n'))
 for ext,data in [('stdout',safe(p.stdout)),('stderr',safe(p.stderr)),('rc',str(p.returncode).encode()+b'\n')]: (E/(name+'.'+ext)).write_bytes(data)
 print(name,'rc',p.returncode,flush=True)
 if interrupted:
  (E/(name+'.interruption.json')).write_text(json.dumps({'error':repr(interrupted),'owned_process_group':proc.pid,'returncode':p.returncode})+'\n')
  raise interrupted
 if require and p.returncode:raise RuntimeError(name+' failed')
 return p
def guard(name):
 g=json.loads(run(name,['python3','src/RimMandrake/rimflow/host_guard.py','status','--json']).stdout)
 assert g['state']=='HELD' and g['seat']=='BENCH' and g['purpose']=='HT: TITAN_PASSAGE_PRUNE_WHALES_ON_FOOT'
 assert g['generation']>=1402 and str(g['generation'])==ENV.get('RM_HOST_GUARD_GEN')
 assert g['identity']['pid']==2835258
 ENV['RM_DRIVER_PID']=str(g['identity']['pid'])
 # actual host_guard status independently verifies pid/start/boot, not pid number alone
 return g
def preflight(name,live=False):
 path=E/(name+'.json')
 assert not path.exists(),'refuse stale preflight receipt'
 args=['/home/mandrake/.cache/ht-warning-venv/bin/python3','src/RimMandrake/Utils/preflight_bridge.py','--tier','quicktest','--modset',TIER,'--deep','--all','--seat','BENCH','--json',str(path)]
 if live:args+=['--live']
 run(name,args,require=False)
 assert path.is_file(),'preflight failed to produce a new receipt'
 r=json.loads(path.read_text());bad=[x for x in r['rows'] if x['required'] and x['id']!='O02' and x['status']!='PASS']
 (E/(name+'_assessment.json')).write_text(json.dumps({'other_required_nonpasses':bad,'O02':{'status':'N/A','raw_rows':[x for x in r['rows'] if x['id']=='O02'],'reason':'other-host bridge file; actual SteveDesktop host separately guarded'},'authorized_exception':'O02 only; actual host independently guarded','ok':not bad},indent=2)+'\n')
 assert not bad,[(x['id'],x['status']) for x in bad]
def launch(name):
 guard(name+'_guard')
 real=ENV.get('HT_POWERSHELL_REAL')
 if not real or real==str(ADAPTER/'powershell.exe'):
  real=run(name+'_powershell',['which','powershell.exe']).stdout.decode().strip()
 assert real!=str(ADAPTER/'powershell.exe'),'genuine PowerShell required'
 assert (ADAPTER/'powershell.exe').is_file(),'scoped Steam adapter missing'
 ENV['HT_POWERSHELL_REAL']=real
 ENV['HT_STEAM_ADAPTER_RECEIPT']=str(E/'steam_route.jsonl')
 ENV['PATH']=str(ADAPTER)+os.pathsep+ENV['PATH']
 resolved=run(name+'_adapter_resolved',['which','powershell.exe']).stdout.decode().strip()
 assert resolved==str(ADAPTER/'powershell.exe'),'Steam adapter must actually resolve before launch'
 p=run(name+'_up',GAME+['up','--wait'],False)
 if p.returncode:
  for i in range(12):
   time.sleep(5)
   p=run(name+'_delayed_'+str(i),GAME+['status'],False)
   if p.returncode==0 and b'bridge port in Player.log: 5174' in p.stdout:break
  else:raise RuntimeError('Steam delayed process/bridge absent')
 time.sleep(45)
 route=E/'steam_route.jsonl'
 assert route.is_file(),'actual Steam adapter route receipt absent'
 rows=[json.loads(x) for x in route.read_text().splitlines()]
 assert len(rows)==1 and rows[0]['route']=='steam://rungameid/294100' and rows[0]['generation']==ENV['RM_HOST_GUARD_GEN'],'missing/ambiguous Steam launch route'
 preflight(name+'_preflight_live',True)
def inspect_log(name):
 import sys
 sys.path.insert(0,str(ROOT/'src/RimMandrake/Utils'));import game_paths
 p=Path(game_paths.PLAYER_LOG);lines=p.read_text(errors='replace').splitlines()
 ex=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Exception|Traceback',s)]
 cfg=[(i+1,s) for i,s in enumerate(lines) if 'Config error' in s]
 parse=[(i+1,s) for i,s in enumerate(lines) if re.search(r'Error while loading|could not parse|exception parsing|XML error|Could not resolve cross.ref|Could not find type named',s,re.I)]
 r={'path':str(p),'first_exception':ex[0] if ex else None,'exception_count':len(ex),'config_errors':cfg,'scribe_parse_errors':parse}
 (E/(name+'.json')).write_text(json.dumps(r,indent=2)+'\n')
 return r
