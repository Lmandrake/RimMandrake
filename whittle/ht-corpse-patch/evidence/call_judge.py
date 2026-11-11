"""Fresh independent Codex transport; stdin is exactly the frozen JUDGE_PROMPT.md bytes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

here=Path(__file__).resolve().parent
root=here.parents[2]
prompt=here.parent/'JUDGE_PROMPT.md'
cmd=[sys.executable,'src/RimMandrake/Utils/agent_runner.py','--codex','wsl',
     '--cwd',str(root),'--result','whittle/ht-corpse-patch/evidence/judge.last.txt',
     '--events','whittle/ht-corpse-patch/evidence/judge.events.jsonl',
     '--spend','whittle/ht-corpse-patch/evidence/judge.spend.json',
     '--sandbox','danger-full-access','--timeout','600']
env=dict(os.environ)
removed=[k for k in env if k in ('CODEX_MODEL','CLAUDECODE','CLAUDE_PROJECT_DIR') or 'HOOK' in k.upper()]
for k in removed: env.pop(k)
env['WHITTLE']='0'; env['WHITTLE_DIR']='whittle/ht-corpse-patch'
started=time.time()
receipt={'command':cmd,'cwd':str(root),'stdin_file':str(prompt),'stdin_sha256':hashlib.sha256(prompt.read_bytes()).hexdigest(),
         'history':'new agent_runner Codex exec, no resume/fork/model override; only frozen judge prompt on stdin',
         'removed_environment_keys':sorted(removed),'WHITTLE':env['WHITTLE'],'started':started}
p=subprocess.run(cmd,input=prompt.read_bytes(),cwd=root,capture_output=True,env=env)
(here/'judge.process.stdout.txt').write_bytes(p.stdout)
(here/'judge.process.stderr.txt').write_bytes(p.stderr)
receipt.update(returncode=p.returncode,elapsed_seconds=time.time()-started,
               stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr_sha256=hashlib.sha256(p.stderr).hexdigest())
(here/'judge.process.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(p.returncode)
