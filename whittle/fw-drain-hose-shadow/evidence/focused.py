"""Sanctioned focused wrapper; preserve all attempts and source inputs."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[2]
raw=Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-shadow-raw')
name=sys.argv[1]
selector=sys.argv[2] if len(sys.argv)>2 else 'HS_*,HoseCarryChecks,HX4*'
assert not (h/(name+'.json')).exists()
env=dict(os.environ)
env['RIMWORLD_DECOMPILED']=subprocess.check_output(['wslpath','-w',str(root/'whittle/fw-drain-selftest-resume/evidence/reference')],text=True).strip()
env['WSLENV'] += ':RIMWORLD_DECOMPILED'
paths=list((root/'src/RimMandrake/FlowWorks/Source/SelfTest').glob('*'))+list((root/'src/RimMandrake/FlowWorks/Source/Hose').glob('*.cs'))
inputs={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
cmd=['python3','src/RimMandrake/Utils/selftest_flowworks_stock.py','--only',selector]
receipt=dict(command=cmd,started=time.time(),sha256=inputs,env={k:env[k] for k in ['WSLENV','RIMWORLD_DECOMPILED','RIMFLOW_SEAT','AGENT_SEAT','RIMFLOW_BRIDGE_SEAT','TMPDIR']})
(h/(name+'_running.json')).write_text(json.dumps(receipt,indent=2)+'\n')
with (raw/(name+'_stdout.txt')).open('wb') as out, (raw/(name+'_stderr.txt')).open('wb') as err:
 p=subprocess.run(cmd,cwd=root,env=env,stdout=out,stderr=err,timeout=900)
receipt.update(returncode=p.returncode,elapsed=time.time()-receipt['started'],stdout=str(raw/(name+'_stdout.txt')),stderr=str(raw/(name+'_stderr.txt')))
(h/(name+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='sha256'}))
print((raw/(name+'_stdout.txt')).read_text()[-6500:])
print((raw/(name+'_stderr.txt')).read_text()[-1500:])
sys.exit(p.returncode)
