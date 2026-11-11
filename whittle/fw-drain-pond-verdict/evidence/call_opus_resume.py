"""Bounded fresh Opus calls; retain exact stdout, stderr and process receipt."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
mode = sys.argv[1]
assert mode == 'judge', 'Only a fresh judgment is required; preserve completed broaden'
prompt = here / 'broaden_prompt.txt' if mode == 'broaden' else here.parent / 'JUDGE_PROMPT.md'
cmd = ['claude', '-p', '--model', 'opus', '--tools', '' if mode == 'broaden' else 'Read,Glob,Grep,Write',
       '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '',
       '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '6']
if mode == 'judge':
    cmd += ['--add-dir', str(root), '--allowedTools', 'Read', 'Glob', 'Grep',
            'Write(%s)' % (here.parent / 'JUDGE.md'), '--permission-mode', 'dontAsk']
env = dict(os.environ)
removed = [k for k in env if k == 'CLAUDECODE' or 'HOOK' in k.upper() or k == 'CLAUDE_PROJECT_DIR']
for key in removed:
    env.pop(key)
env['WHITTLE'] = '0'
started = time.time()
receipt = {'command': cmd, 'input': str(prompt), 'started': started, 'timeout_seconds': 360,
           'WHITTLE': env['WHITTLE'], 'removed_environment_keys': sorted(removed),
           'history': 'new print session; no resume, fork or persistence', 'setting_sources': '', 'mcp_servers': {}}
with tempfile.TemporaryDirectory(prefix='pond-verdict-opus-') as neutral:
    receipt['cwd'] = neutral
    try:
        proc = subprocess.run(cmd, input=prompt.read_bytes(), capture_output=True, timeout=360, env=env, cwd=neutral)
        stdout, stderr = proc.stdout, proc.stderr
        receipt['returncode'] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        receipt['error'] = 'timeout'
(here / ('resume_' + mode + '_raw.json')).write_bytes(stdout)
(here / ('resume_' + mode + '_stderr.txt')).write_bytes(stderr)
receipt.update(elapsed=time.time() - started, stdout=str(here / ('resume_' + mode + '_raw.json')))
(here / ('resume_' + mode + '_call.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
