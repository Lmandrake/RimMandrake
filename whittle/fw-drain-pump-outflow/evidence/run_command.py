"""Retain exact stdout/stderr and invocation for one command; never overwrite a receipt."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
label = sys.argv[1]
command = sys.argv[2:]
if command and command[0] == '--':
    command = command[1:]
for suffix in ('_stdout.txt', '_stderr.txt', '_command.json'):
    assert not (here / (label + suffix)).exists(), label
started = time.time()
env = dict(os.environ, RIMFLOW_SEAT='BENCH', TMPDIR='/home/mandrake/.seat-tmp/fw-pump-outflow')
with (here / (label + '_stdout.txt')).open('wb') as out, (here / (label + '_stderr.txt')).open('wb') as err:
    proc = subprocess.run(command, cwd=root, env=env, stdout=out, stderr=err)
receipt = dict(command=command, cwd=str(root), started=started,
               elapsed=time.time() - started, returncode=proc.returncode, TMPDIR=env['TMPDIR'])
(here / (label + '_command.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
print((here / (label + '_stdout.txt')).read_text(errors='replace')[-1800:])
print((here / (label + '_stderr.txt')).read_text(errors='replace')[-1000:])
sys.exit(proc.returncode)
