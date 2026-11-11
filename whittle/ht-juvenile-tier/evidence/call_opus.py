"""One bounded fresh consultation; preserve raw response and process receipt."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

here = Path(__file__).resolve().parent
prompt = here / 'design_prompt.txt'
cmd = ['claude', '-p', '--model', 'opus', '--tools', '',
       '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '',
       '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '6']
env = dict(os.environ)
removed = [k for k in env if k == 'CLAUDECODE' or 'HOOK' in k.upper() or k == 'CLAUDE_PROJECT_DIR']
for key in removed:
    env.pop(key)
env['WHITTLE'] = '0'
started = time.time()
receipt = {'command': cmd, 'input': str(prompt), 'input_sha256': hashlib.sha256(prompt.read_bytes()).hexdigest(),
           'started': started, 'timeout_seconds': 360, 'WHITTLE': env['WHITTLE'],
           'removed_environment_keys': sorted(removed), 'history': 'new print session; no resume, fork or persistence',
           'setting_sources': '', 'mcp_servers': {}}
with tempfile.TemporaryDirectory(prefix='juvenile-design-opus-', dir=here) as neutral:
    receipt['cwd'] = neutral
    try:
        proc = subprocess.run(cmd, input=prompt.read_bytes(), capture_output=True, timeout=360, env=env, cwd=neutral)
        stdout, stderr = proc.stdout, proc.stderr
        receipt['returncode'] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        receipt['error'] = 'timeout'
(here / 'design_raw.json').write_bytes(stdout)
(here / 'design_stderr.txt').write_bytes(stderr)
receipt.update(elapsed=time.time() - started, stdout_sha256=hashlib.sha256(stdout).hexdigest(), stderr_sha256=hashlib.sha256(stderr).hexdigest())
(here / 'design_call.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
