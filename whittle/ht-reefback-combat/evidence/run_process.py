"""Run one explicit offline process; preserve unedited streams and receipt."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

a = argparse.ArgumentParser()
a.add_argument('--name', required=True)
a.add_argument('--timeout', type=int, default=180)
a.add_argument('command', nargs=argparse.REMAINDER)
args = a.parse_args()
cmd = args.command
if cmd[0] == '--':
    cmd = cmd[1:]
out = Path(__file__).resolve().parent / 'raw'
started = time.time()
try:
    p = subprocess.run(cmd, capture_output=True, timeout=args.timeout)
    stdout, stderr, rc = p.stdout, p.stderr, p.returncode
except subprocess.TimeoutExpired as e:
    stdout, stderr, rc = e.stdout or b'', e.stderr or b'', 124
for name, data in [('stdout.txt', stdout), ('stderr.txt', stderr)]:
    (out / (args.name + '.' + name)).write_bytes(data)
receipt = {'command': cmd, 'cwd': str(Path.cwd()), 'started': started,
           'elapsed_seconds': time.time()-started, 'rc': rc,
           'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
           'stderr_sha256': hashlib.sha256(stderr).hexdigest()}
(out / (args.name + '.receipt.json')).write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(rc)
