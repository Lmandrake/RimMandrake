"""Bounded commands with immutable raw logs and exact before/after input hashes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/kinetic-sway-raw')
label = sys.argv[1]
command = sys.argv[3:]
assert sys.argv[2] == '--' and command
receipt = here / (label + '.json')
assert not receipt.exists()
paths = set()
for directory in ('src/RimMandrake/GimmeSomeSlack/Source', 'src/RimMandrake/_Shared'):
    paths.update(p for p in (root / directory).rglob('*') if p.is_file() and
                 not {'bin', 'obj', '__pycache__'}.intersection(p.relative_to(root).parts) and p.suffix in ('.cs', '.csproj', '.json'))
paths.update(root / p for p in (
    'src/RimMandrake/GimmeSomeSlack/validation_aerial.py', 'src/RimMandrake/GimmeSomeSlack/validation.py',
    'src/RimMandrake/GimmeSomeSlack/restring_style_proof.py', 'src/RimMandrake/GimmeSomeSlack/kinetic_sway_proof.py',
    'src/RimMandrake/GimmeSomeSlack/selftest_gss_kinetic_sway.py', 'src/RimMandrake/GimmeSomeSlack/selftest_gss_explode_parse.py',
    'src/RimMandrake/GimmeSomeSlack/selftest_gss_restring_proof.py',
    'src/RimMandrake/GimmeSomeSlack/selftest_gss_proof_drivers.py',
    'src/RimMandrake/Utils/run_selftests.py', 'src/RimMandrake/Utils/selftest_gimmesomeslack.py',
    'src/RimMandrake/Utils/winbuild.py', 'src/RimMandrake/Utils/dll_source_stamp.py',
    'src/RimMandrake/KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml',
    'infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt',
    'infrastructure/state/items/GSS_SWAY_PROVE_KINETIC_LIVE_ROW.md',
    'src/Directory.Build.props', 'src/Directory.Build.targets'))

def hashes():
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

env = dict(os.environ)
record = dict(command=command, cwd=str(root), started=time.time(), timeout_seconds=1500,
              HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              before=hashes(), TMPDIR=env.get('TMPDIR'),
              seat_environment={k: env.get(k) for k in ('RIMFLOW_SEAT', 'AGENT_SEAT', 'RIMFLOW_BRIDGE_SEAT', 'WSLENV')})
argv = command
if label.startswith('tests'):
    # The standard runner discards successful child output. Observe its stdout/stderr writes externally.
    observer = Path('/home/mandrake/.seat-tmp/fw-two-stray-tools/usr/bin/strace')
    assert observer.is_file()
    trace = raw / (label + '.writes.strace')
    assert not trace.exists()
    env['LD_LIBRARY_PATH'] = str(observer.parents[1] / 'lib/x86_64-linux-gnu')
    argv = [str(observer), '-f', '-ttt', '--trace=write', '--trace-fds=1,2', '-s', '2000000',
            '-E', 'LD_LIBRARY_PATH', '-o', str(trace), *command]
    record.update(observer_argv=argv, observer_sha256=hashlib.sha256(observer.read_bytes()).hexdigest(), trace=str(trace))
stdout, stderr = raw / (label + '.stdout'), raw / (label + '.stderr')
record.update(stdout=str(stdout), stderr=str(stderr))
with stdout.open('xb') as out, stderr.open('xb') as err:
    child = subprocess.Popen(argv, cwd=root, env=env, stdout=out, stderr=err)
    (here / (label + '_running.json')).write_text(json.dumps(dict(record, pid=child.pid), indent=2) + '\n')
    try:
        child.wait(timeout=record['timeout_seconds'])
        record['returncode'] = child.returncode
    except subprocess.TimeoutExpired:
        child.terminate()
        child.wait(timeout=15)
        record.update(returncode=child.returncode, error='timeout')
record.update(finished=time.time(), after=hashes())
record['inputs_unchanged'] = record['before'] == record['after']
record['raw_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (stdout, stderr)}
receipt.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: v for k, v in record.items() if k not in ('before', 'after')}, indent=2))
print(stdout.read_text()[-4000:])
print(stderr.read_text()[-4000:])
sys.exit(0 if record.get('returncode') == 0 and record['inputs_unchanged'] else 1)
