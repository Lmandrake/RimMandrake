"""Fresh Codex call with the frozen prompt as exact stdin; no model override."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root=Path(__file__).resolve().parents[3]
here=Path(__file__).resolve().parent
prompt=(here.parent/'JUDGE_PROMPT.md').read_bytes()
cmd=[sys.executable,'src/RimMandrake/Utils/agent_runner.py','--codex','wsl','--cwd',str(root),
     '--result','whittle/ht-reefback-combat/evidence/judge.last.txt',
     '--events','whittle/ht-reefback-combat/evidence/judge.events.jsonl',
     '--spend','whittle/ht-reefback-combat/evidence/judge.spend.json',
     '--sandbox','danger-full-access','--timeout','900']
started=time.time()
p=subprocess.run(cmd,input=prompt,capture_output=True,cwd=root,timeout=960)
(here/'judge.process.stdout.txt').write_bytes(p.stdout)
(here/'judge.process.stderr.txt').write_bytes(p.stderr)
receipt={'command':cmd,'stdin_file':'whittle/ht-reefback-combat/JUDGE_PROMPT.md',
 'stdin_sha256':hashlib.sha256(prompt).hexdigest(),'started':started,'elapsed_seconds':time.time()-started,
 'rc':p.returncode,'RM_CODEX_SIDE':os.environ.get('RM_CODEX_SIDE'),
 'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest(),
 'session':'fresh exec; no fork/resume/agent/model arguments'}
(here/'judge.process.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(p.returncode)
