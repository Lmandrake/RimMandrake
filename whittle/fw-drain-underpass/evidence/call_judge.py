"""Fresh independent judge, supplied only JUDGE_PROMPT.md; no fork or builder context."""
import json
import os
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
prompt = here.parent / 'JUDGE_PROMPT.md'
cmd = ['claude', '-p', '--model', 'opus', '--tools', 'Read,Glob,Grep,Write',
       '--allowedTools', 'Read', 'Glob', 'Grep', 'Write', '--permission-mode', 'dontAsk',
       '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '',
       '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '6']
env = dict(os.environ)
env.pop('CLAUDECODE', None)
env['WHITTLE'] = '0'
started = time.time()
try:
    r = subprocess.run(cmd, input=prompt.read_text(), cwd=root, env=env, text=True, capture_output=True, timeout=240)
    (here / 'judge_raw.json').write_text(r.stdout)
    (here / 'judge_stderr.txt').write_text(r.stderr)
    result = {'command': cmd, 'input': str(prompt), 'cwd': str(root), 'stdout': str(here / 'judge_raw.json'), 'returncode': r.returncode}
except subprocess.TimeoutExpired as e:
    (here / 'judge_raw.json').write_bytes(e.stdout or b'')
    (here / 'judge_stderr.txt').write_bytes(e.stderr or b'')
    result = {'command': cmd, 'error': 'timeout'}
result.update(started=started, elapsed=time.time() - started)
(here / 'judge_call.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
