"""Independent read-only broaden call; raw stdout/stderr retained unchanged."""
import json
import os
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
cmd = ['claude', '-p', '--model', 'opus', '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '', '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '3']
env = dict(os.environ)
env.pop('CLAUDECODE', None)
env['WHITTLE'] = '0'
started = time.time()
try:
    r = subprocess.run(cmd, input=(here / 'broaden_prompt.txt').read_text(), text=True, capture_output=True, timeout=180, env=env)
    (here / 'broaden_raw.json').write_text(r.stdout)
    (here / 'broaden_stderr.txt').write_text(r.stderr)
    result = {'command': cmd, 'input': str(here / 'broaden_prompt.txt'), 'stdout': str(here / 'broaden_raw.json'), 'returncode': r.returncode}
except subprocess.TimeoutExpired as e:
    (here / 'broaden_raw.json').write_bytes(e.stdout or b'')
    (here / 'broaden_stderr.txt').write_bytes(e.stderr or b'')
    result = {'command': cmd, 'error': 'timeout'}
result.update(started=started, elapsed=time.time() - started)
(here / 'broaden_call.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
