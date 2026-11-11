"""Keep exact runner/wrapper output; discard redundant syscall dumps of Git/source staging.

No rerun: decode the observed writes from the recorded wrapper PID only.
"""
import ast
import hashlib
import json
import sys
from pathlib import Path
import re
import time

here = Path(__file__).resolve().parent
if len(sys.argv) > 1:
    here = here / sys.argv[1]
    here.mkdir(exist_ok=True)
receipt = json.loads((here / 'selftest_receipt.json').read_text())
assert isinstance(receipt['returncode'], int) and receipt['source_test_hashes_unchanged']
samples = [json.loads(line) for line in (here / 'process_samples.jsonl').read_text().splitlines()]
wrapper_pids, runner_pids = set(), set()
for sample in samples:
    for row in sample['processes']:
        parts = row.split()
        if len(parts) < 5:
            continue
        if parts[-1].endswith('/src/RimMandrake/Utils/selftest_flowworks_stock.py') and '--_harness-child' not in row:
            wrapper_pids.add(int(parts[0]))
        if 'python3 src/RimMandrake/Utils/run_selftests.py --only' in row and '--trace-fds' not in row:
            runner_pids.add(int(parts[0]))
assert len(wrapper_pids) == len(runner_pids) == 1, (wrapper_pids, runner_pids)
wrapper_pid = next(iter(wrapper_pids))
keep_pids = wrapper_pids | runner_pids
trace = here / 'selftest_writes.strace'
digest = hashlib.sha256()
kept, streams = [], {1: bytearray(), 2: bytearray()}
pending = {}
for line in trace.open('rb'):
    digest.update(line)
    m = re.match(rb'(\d+) \S+ (.*)', line)
    if not m or int(m[1]) not in keep_pids:
        continue
    kept.append(line)
    if int(m[1]) != wrapper_pid:
        continue
    call = m[2]
    w = re.match(rb'write\(([12]), ("(?:[^"\\]|\\.)*"), (\d+)\)(.*)', call)
    if w:
        payload = ast.literal_eval('b' + w[2].decode('ascii'))
        assert len(payload) == int(w[3]), 'truncated observer output'
        if b'<unfinished ...>' in w[4]:
            pending[wrapper_pid] = (int(w[1]), payload)
            continue
        ret = re.search(rb'= (\d+)', w[4])
        assert ret, call[-100:]
        streams[int(w[1])].extend(payload[:int(ret[1])])
    elif call.startswith(b'<... write resumed>'):
        fd, payload = pending.pop(wrapper_pid)
        ret = re.search(rb'= (\d+)', call)
        assert ret
        streams[fd].extend(payload[:int(ret[1])])
assert not pending
assert streams[1], 'No actual wrapper output captured'
(here / 'selftest_output_writes.strace').write_bytes(b''.join(kept))
(here / 'csharp_stdout.txt').write_bytes(streams[1])
(here / 'csharp_stderr.txt').write_bytes(streams[2])
record = dict(time=time.time(), operation='Decode actual stdout/stderr writes from the sampled selftest wrapper PID',
              wrapper_pid=wrapper_pid, runner_pid=next(iter(runner_pids)),
              original_observer_sha256=digest.hexdigest(), original_observer_bytes=trace.stat().st_size,
              kept_raw='selftest_output_writes.strace',
              stdout_sha256=hashlib.sha256(streams[1]).hexdigest(),
              stderr_sha256=hashlib.sha256(streams[2]).hexdigest(),
              omitted='Unrelated subprocess syscalls, including redundant source/Git/rsync payloads; no test log omitted')
(here / 'output_extraction.json').write_text(json.dumps(record, indent=2) + '\n')
trace.unlink()
print(json.dumps(record, indent=2))
