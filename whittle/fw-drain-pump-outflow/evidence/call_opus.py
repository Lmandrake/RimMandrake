"""Fresh bounded CLI review calls; no history, project settings or MCP."""
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
assert mode in ('broaden', 'judge', 'judge_final', 'pilot')
prompt = here / (mode + '_prompt.txt') if mode in ('broaden', 'pilot') else here.parent / 'JUDGE_PROMPT.md'
cmd = ['claude', '-p', '--model', 'opus', '--effort', 'high', '--tools', 'Read,Glob,Grep',
       '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--setting-sources', '',
       '--no-session-persistence', '--output-format', 'json', '--max-budget-usd', '6']
cmd += ['--add-dir', str(root), '--add-dir', '/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/pump-outflow-raw', '--allowedTools', 'Read', 'Glob', 'Grep', '--permission-mode', 'dontAsk']
env = dict(os.environ)
removed = [k for k in env if k == 'CLAUDECODE' or 'HOOK' in k.upper() or k == 'CLAUDE_PROJECT_DIR']
for key in removed:
    env.pop(key)
env['WHITTLE'] = '0'
env['TMPDIR'] = '/home/mandrake/.seat-tmp/fw-pump-outflow'
started = time.time()
receipt = dict(command=cmd, input=str(prompt), started=started, timeout_seconds=360,
               WHITTLE='0', removed_environment_keys=sorted(removed),
               history='fresh print process; no resume, fork or persistence', setting_sources='', mcp_servers={})
assert not (here / (mode + '_raw.json')).exists(), 'Preserve completed calls'
with tempfile.TemporaryDirectory(prefix='fw-pump-outflow-opus-', dir=env['TMPDIR']) as neutral:
    receipt['cwd'] = neutral
    with (here / (mode + '_raw.json')).open('wb') as out, (here / (mode + '_stderr.txt')).open('wb') as err:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=out, stderr=err, cwd=neutral, env=env)
        receipt['pid'] = proc.pid
        (here / (mode + '_running.json')).write_text(json.dumps(receipt, indent=2) + '\n')
        try:
            proc.communicate(prompt.read_bytes(), timeout=360)
            receipt['returncode'] = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=15)
            receipt.update(error='timeout', returncode=proc.returncode)
receipt['elapsed'] = time.time() - started
(here / (mode + '_call.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
