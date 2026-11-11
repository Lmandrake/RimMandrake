"""Record the unmodified authorized runner, observed externally with strace for raw PASS output.

This does not inject a test, monkeypatch the runner, or invoke a second suite.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
paths = subprocess.check_output(['git', 'ls-files', 'src/RimMandrake/FlowWorks/Source'], cwd=root, text=True).splitlines()
paths += ['src/RimMandrake/Utils/' + p for p in ('run_selftests.py', 'selftest_flowworks_stock.py',
          'selftest_winstage.py', 'winbuild.py')]
def hashes():
    return {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}

before = dict(time=time.time(), HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              sha256=hashes(), status=subprocess.check_output(['git', 'status', '--short'], cwd=root, text=True))
assert not (here / 'integrity_before.json').exists()
(here / 'integrity_before.json').write_text(json.dumps(before, indent=2) + '\n')
cmd = ['python3', 'src/RimMandrake/Utils/run_selftests.py', '--only',
       'src/RimMandrake/Utils/selftest_flowworks_stock.py', '--workers', '1']
observer = Path('/home/mandrake/.seat-tmp/fw-two-stray-tools/usr/bin/strace')
argv = [str(observer), '-f', '-ttt', '--trace=write', '--trace-fds=1,2', '-s', '2000000',
        '-E', 'LD_LIBRARY_PATH', '-o', str(here / 'selftest_writes.strace'), *cmd]
env = dict(os.environ, LD_LIBRARY_PATH=str(observer.parents[1] / 'lib/x86_64-linux-gnu'))
started = time.time()
receipt = dict(command=cmd, observer_argv=argv, observer_sha256=hashlib.sha256(observer.read_bytes()).hexdigest(),
               started=started, tested_HEAD=before['HEAD'], cwd=str(root), timeout_seconds=1260,
               purpose='Capture stdout writes discarded by the runner on PASS; source/tests/runner are unmodified')
with (here / 'selftest_stdout.txt').open('wb') as out, (here / 'selftest_stderr.txt').open('wb') as err:
    proc = subprocess.Popen(argv, cwd=root, env=env, stdout=out, stderr=err)
    receipt['pid'] = proc.pid
    (here / 'selftest_running.json').write_text(json.dumps(receipt, indent=2) + '\n')
    try:
        proc.wait(timeout=1260)
        receipt['returncode'] = proc.returncode
    except subprocess.TimeoutExpired:
        proc.terminate()
        receipt['error'] = 'observer timeout; inspect and stop own remaining processes'
receipt.update(elapsed=time.time() - started, sha256_after=hashes())
receipt['source_test_hashes_unchanged'] = receipt['sha256_after'] == before['sha256']
(here / 'selftest_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'sha256_after'}))
