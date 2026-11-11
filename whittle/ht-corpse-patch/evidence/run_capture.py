"""Run an explicit command and preserve unmodified stdout/stderr and its process receipt."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
here = Path(__file__).resolve().parent
label, *cmd = sys.argv[1:]
started = time.time()
p = subprocess.run(cmd, capture_output=True)
(here / (label + '.stdout.txt')).write_bytes(p.stdout)
(here / (label + '.stderr.txt')).write_bytes(p.stderr)
r = {'command': cmd, 'cwd': os.getcwd(), 'started': started, 'elapsed_seconds': time.time()-started,
     'returncode': p.returncode, 'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(),
     'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()}
(here / (label + '.receipt.json')).write_text(json.dumps(r, indent=2)+'\n')
sys.stdout.buffer.write(p.stdout)
sys.stderr.buffer.write(p.stderr)
print(json.dumps(r), flush=True)
sys.exit(p.returncode)
