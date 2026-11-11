"""Fresh independent native Codex judge, exact frozen stdin, no fork/resume/model override."""
from pathlib import Path
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
work=E.parent
env=dict(os.environ,RM_CODEX_SIDE='wsl',PYTHONDONTWRITEBYTECODE='1')
for name in ['CODEX_MODEL','CODEX_EFFORT','RM_HOST_GUARD_GEN','RM_DRIVER_PID']:
    env.pop(name,None)
prompt=work/'JUDGE_PROMPT.md'
command=['python3','src/RimMandrake/Utils/agent_runner.py','--codex','wsl','--cwd',str(ROOT),'--result',str(E/'judge.last.txt'),'--events',str(E/'judge.events.jsonl'),'--spend',str(E/'judge.spend.json'),'--sandbox','danger-full-access','--timeout','900']
assert not (work/'JUDGE.md').exists(),'retain/resolve any prior judge before a new launch'
started=time.time()
p=subprocess.run(command,input=prompt.read_bytes(),capture_output=True,env=env,cwd=ROOT,timeout=960)
(E/'judge.process.stdout.txt').write_bytes(p.stdout);(E/'judge.process.stderr.txt').write_bytes(p.stderr)
(E/'judge.process.receipt.json').write_text(json.dumps({'command':command,'stdin':str(prompt.relative_to(ROOT)),'stdin_sha256':hashlib.sha256(prompt.read_bytes()).hexdigest(),'rc':p.returncode,'elapsed_seconds':time.time()-started,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()},indent=2)+'\n')
print('fresh judge process rc',p.returncode,'elapsed',time.time()-started)
raise SystemExit(p.returncode)
