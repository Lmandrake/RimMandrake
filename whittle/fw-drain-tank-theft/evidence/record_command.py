"""Preserve a command's original stdout/stderr and receipt without overwriting attempts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
label = sys.argv[1]
cmd = sys.argv[2:]
assert cmd and '/' not in label
receipt_path = here / (label + '_command.json')
assert not receipt_path.exists(), 'Preserve prior attempt'
receipt = dict(command=cmd, cwd=os.getcwd(), started=time.time(),
               seats={k: os.environ.get(k) for k in ('RIMFLOW_SEAT','AGENT_SEAT','RIMFLOW_BRIDGE_SEAT')},
               WSLENV=os.environ.get('WSLENV'), TMPDIR=os.environ.get('TMPDIR'))
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
with (here / (label + '_stdout.txt')).open('wb') as out, (here / (label + '_stderr.txt')).open('wb') as err:
    proc = subprocess.Popen(cmd, stdout=out, stderr=err)
    receipt['pid'] = proc.pid
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    receipt['returncode'] = proc.wait()
receipt['finished'] = time.time()
receipt['elapsed'] = receipt['finished'] - receipt['started']
for stream in ('stdout','stderr'):
    p = here / (label + '_' + stream + '.txt')
    receipt[stream + '_sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
sys.exit(receipt['returncode'])
