"""Record the unmodified authorized runner, observed externally with strace for raw PASS output.

This does not inject a test, monkeypatch the runner, or invoke a second suite.
"""
import hashlib
import json
import sys
import os
from pathlib import Path
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
if len(sys.argv) > 1:
    here = here / sys.argv[1]
    here.mkdir(exist_ok=True)
from integrity import hashes

before = dict(time=time.time(), HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              sha256=hashes(), status=subprocess.check_output(['git', 'status', '--short'], cwd=root, text=True))
assert not (here / 'integrity_before.json').exists()
(here / 'integrity_before.json').write_text(json.dumps(before, indent=2) + '\n')
cmd = ['python3', 'src/RimMandrake/Utils/run_selftests.py', '--only',
       'src/RimMandrake/Utils/selftest_flowworks_stock.py', '--workers', '1']
observer = Path('/home/mandrake/.seat-tmp/fw-two-stray-tools/usr/bin/strace')
argv = [str(observer), '-f', '-ttt', '--trace=write', '--trace-fds=1,2', '-s', '2000000',
        '-E', 'LD_LIBRARY_PATH', '-o', '/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-fuzz-raw/selftest_writes.strace', *cmd]
env = dict(os.environ, TMPDIR='/home/mandrake/.seat-tmp/fw-hose-fuzz', LD_LIBRARY_PATH=str(observer.parents[1] / 'lib/x86_64-linux-gnu'))
env['RIMWORLD_DECOMPILED'] = subprocess.check_output(['wslpath', '-w', str(root / 'whittle/fw-drain-selftest-resume/evidence/reference')], text=True).strip()
env['WSLENV'] = ':'.join(filter(None, [env.get('WSLENV', ''), 'RIMWORLD_DECOMPILED']))
env_tmp = '/home/mandrake/.seat-tmp/fw-hose-fuzz'
os.environ['TMPDIR'] = env_tmp
started = time.time()
receipt = dict(command=cmd, observer_argv=argv, observer_sha256=hashlib.sha256(observer.read_bytes()).hexdigest(),
               started=started, tested_HEAD=before['HEAD'], TMPDIR=env_tmp, RIMWORLD_DECOMPILED=env['RIMWORLD_DECOMPILED'], WSLENV=env['WSLENV'], cwd=str(root), timeout_seconds=1260,
               purpose='Capture stdout writes discarded by the runner on PASS; external observation only; modified SelfTest guards are included in integrity manifest')
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-fuzz-raw')
assert not (raw / 'selftest_writes.strace').exists()
with (raw / 'selftest_stdout.txt').open('wb') as out, (raw / 'selftest_stderr.txt').open('wb') as err:
    proc = subprocess.Popen(argv, cwd=root, env=env, stdout=out, stderr=err)
    receipt['pid'] = proc.pid
    (here / 'selftest_running.json').write_text(json.dumps(receipt, indent=2) + '\n')
    try:
        while proc.poll() is None and time.time() - started < 1260:
            ps = subprocess.check_output(['ps', '-eo', 'pid,ppid,etimes,comm,args'], text=True).splitlines()[1:]
            descendants = {proc.pid}
            for _ in range(8):
                descendants.update(int(row.split()[0]) for row in ps if int(row.split()[1]) in descendants)
            selected = [row for row in ps if int(row.split()[0]) in descendants]
            with (here / 'process_samples.jsonl').open('a') as sample:
                sample.write(json.dumps(dict(time=time.time(), processes=selected)) + '\n')
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        if proc.poll() is None:
            raise subprocess.TimeoutExpired(argv, 1260)
        receipt['returncode'] = proc.returncode
    except subprocess.TimeoutExpired:
        proc.terminate()
        receipt['error'] = 'observer timeout; inspect and stop own remaining processes'
for name in ('selftest_stdout.txt', 'selftest_stderr.txt'):
    (here / name).write_bytes((raw / name).read_bytes())
receipt.update(elapsed=time.time() - started, sha256_after=hashes())
receipt['source_test_hashes_unchanged'] = receipt['sha256_after'] == before['sha256']
(here / 'selftest_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'sha256_after'}))
