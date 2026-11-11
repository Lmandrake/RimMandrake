from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import time

root = Path(__file__).resolve().parents[3]
here = Path(__file__).resolve().parent
prompt = here.parent / 'JUDGE_PROMPT.md'
command = ['python3', 'src/RimMandrake/Utils/agent_runner.py', '--cwd', str(root),
           '--codex', 'wsl', '--sandbox', 'danger-full-access', '--timeout', '1200',
           '--result', str(here / 'judge.last.txt'), '--events', str(here / 'judge.events.jsonl'),
           '--spend', str(here / 'judge.spend.json')]
env = dict(os.environ, RM_CODEX_SIDE='wsl', WHITTLE='0')
record = dict(command=command, prompt=str(prompt.relative_to(root)),
              prompt_sha256=hashlib.sha256(prompt.read_bytes()).hexdigest(),
              started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              history='fresh exec, exact prompt on stdin, no fork/resume/agent prefix/model override')
(here / 'judge.process.json').write_text(json.dumps(record, indent=2) + '\n')
started = time.time()
with (here / 'judge.runner.stdout').open('wb') as out, (here / 'judge.runner.stderr').open('wb') as err:
    result = subprocess.run(command, input=prompt.read_bytes(), stdout=out, stderr=err, cwd=root, env=env)
record.update(rc=result.returncode, elapsed_seconds=time.time()-started,
              finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(here / 'judge.process.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'judge_rc': result.returncode, 'elapsed_seconds': record['elapsed_seconds']}))
raise SystemExit(result.returncode)
