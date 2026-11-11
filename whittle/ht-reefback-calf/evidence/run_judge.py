"""Required fresh Codex process; stdin is EXACT frozen JUDGE_PROMPT.md bytes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

here=Path(__file__).resolve().parent
root=here.parents[2]
prompt=here.parent/'JUDGE_PROMPT.md'
cmd=['python3','src/RimMandrake/Utils/agent_runner.py','--codex','wsl',
     '--cwd',str(root),'--result','whittle/ht-reefback-calf/evidence/judge.last.txt',
     '--events','whittle/ht-reefback-calf/evidence/judge.events.jsonl',
     '--spend','whittle/ht-reefback-calf/evidence/judge.spend.json',
     '--sandbox','danger-full-access','--timeout','600']
env=dict(os.environ)
# Avoid an ambient model override and Whittle builder hooks; do not change auth.
removed=[k for k in env if k=='CODEX_MODEL' or k=='CLAUDECODE' or 'HOOK' in k.upper()]
for key in removed:
    env.pop(key)
env['WHITTLE']='0'
started=time.time()
receipt={'command':cmd,'stdin_file':str(prompt.relative_to(root)),
         'stdin_sha256':hashlib.sha256(prompt.read_bytes()).hexdigest(),
         'started':started,'freshness':'new Codex exec; no fork, resume, agent prefix or model override',
         'removed_environment_keys':removed}
(here/'judge.process.pending.json').write_text(json.dumps(receipt,indent=2)+'\n')
try:
    r=subprocess.run(cmd,input=prompt.read_bytes(),cwd=root,env=env,capture_output=True,timeout=660)
    stdout,stderr=r.stdout,r.stderr
    receipt['rc']=r.returncode
except subprocess.TimeoutExpired as exc:
    stdout,stderr=exc.stdout or b'',exc.stderr or b''
    receipt.update(rc=124,error='outer timeout')
(here/'judge.process.stdout.txt').write_bytes(stdout)
(here/'judge.process.stderr.txt').write_bytes(stderr)
receipt.update(elapsed=time.time()-started,stdout_sha256=hashlib.sha256(stdout).hexdigest(),
               stderr_sha256=hashlib.sha256(stderr).hexdigest())
(here/'judge.process.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'judge_process_rc':receipt['rc'],'elapsed':receipt['elapsed']}))
raise SystemExit(receipt['rc'])
