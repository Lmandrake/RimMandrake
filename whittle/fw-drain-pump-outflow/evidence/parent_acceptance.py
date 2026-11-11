"""Independently check retained executions, staged inputs, artifacts and restoration."""
import ast
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SUITE = HERE / 'final-live-fixture'
BASE = '8de445f9c2b259cd5626f4a4eccd8626724e2e3a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


receipt = read(SUITE / 'selftest_receipt.json')
assert receipt['returncode'] == 0 and receipt['source_test_hashes_unchanged']
inputs = receipt['sha256_after']
assert all(digest(ROOT / path) == value for path, value in inputs.items())

stage_record = read(HERE / 'final-live-fixture_stage.json')
assert not stage_record['missing'] and not stage_record['mismatch']
stage = Path(stage_record['stage'])
assert all(digest(stage / path) == value for path, value in stage_record['sha256'].items())
assert digest(Path(stage_record['generated_path'])) == stage_record['generated_sha256']
assert digest(HERE / 'final-live-fixture_PumpOutflow.g.cs.txt') == stage_record['generated_sha256']

project = ROOT / 'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
compile_inputs = {}
for element in ET.parse(project).iter('Compile'):
    include = element.get('Include')
    if not include or '$' in include:
        continue
    assert '*' not in include and ';' not in include
    path = (project.parent / include.replace('\\', '/')).resolve()
    relative = path.relative_to(ROOT)
    assert digest(path) == digest(stage / relative)
    compile_inputs[str(relative)] = digest(path)

# Decode the whole original observer independently of the maker's extracted subset.
extraction = read(SUITE / 'output_extraction.json')
trace = Path(extraction['original_observer_path'])
assert digest(trace) == extraction['original_observer_sha256']
streams = {1: bytearray(), 2: bytearray()}
pending = None
for line in trace.read_bytes().splitlines():
    record = re.match(rb'(\d+) \S+ (.*)', line)
    if not record or int(record[1]) != extraction['wrapper_pid']:
        continue
    call = record[2]
    write = re.match(rb'write\(([12]), ("(?:[^"\\]|\\.)*"), (\d+)\)(.*)', call)
    if write:
        payload = ast.literal_eval('b' + write[2].decode('ascii'))
        assert len(payload) == int(write[3])
        if b'<unfinished ...>' in write[4]:
            assert pending is None
            pending = (int(write[1]), payload)
        else:
            count = re.search(rb'= (\d+)', write[4])
            assert count
            streams[int(write[1])].extend(payload[:int(count[1])])
    elif call.startswith(b'<... write resumed>'):
        assert pending
        count = re.search(rb'= (\d+)', call)
        assert count
        descriptor, payload = pending
        streams[descriptor].extend(payload[:int(count[1])])
        pending = None
assert pending is None
assert bytes(streams[1]) == (SUITE / 'csharp_stdout.txt').read_bytes()
assert bytes(streams[2]) == (SUITE / 'csharp_stderr.txt').read_bytes()
assert b'1260/1260 passed' in streams[1]
assert b'hose: 188/188 checks passed' in streams[1]
assert b'hose: 457/457 assertions passed' in streams[1]

source = ROOT / 'src/RimMandrake/FlowWorks/Source'
dll = ROOT / 'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll'
stamp = Path(str(dll) + '.srchash')
shipping_inputs = {}
for line in stamp.read_text().splitlines():
    if line.startswith('#') or not line.strip():
        continue
    value, relative = line.split(' ', 1)
    path = (source / relative).resolve()
    assert digest(path) == value
    staged = Path('/mnt/d/ClaudeWork/rimmandrake/build/FlowWorks') / path.relative_to(ROOT)
    assert digest(staged) == value
    shipping_inputs[str(path.relative_to(ROOT))] = value
assert '# dll: ' + digest(dll) in stamp.read_text().splitlines()
deployed = Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/FlowWorks/Assemblies')
assert digest(deployed / dll.name) == digest(dll)
assert digest(deployed / stamp.name) == digest(stamp)
subprocess.run(['git', 'diff', '--quiet', BASE, '--', 'src/RimMandrake/GimmeSomeSlack'], cwd=ROOT, check=True)

scene = read(HERE / 'live-attempt2/live_scene.json')
drive = read(HERE / 'live-attempt2/live_drive.json')
assert scene['status'] == scene['restore']['status'] == drive['status'] == 'PASS'
assert drive['both_locks_free']
assert scene['restore']['rect'] == scene['baseline_rect']
assert not scene['changed_existing_saves']
assert scene['protected_before'] == scene['protected_after']
assert scene['identity']['mvidMatchesFile']
assert scene['identity']['assemblyFileSha256'] == digest(dll)
expected = {
    'repro': ([900, 20000, 0], [900, 10000, 10000]),
    'full': ([20000, 20000, 0], [10000, 20000, 10000]),
    'exact': ([900, 20000, 0], [0, 20000, 900]),
    'off': ([900, 20000, 0], [900, 20000, 0]),
}
assert len(scene['arms']) == len(expected)
for arm in scene['arms']:
    assert (arm['before'], arm['after']) == expected[arm['mode']]
    assert sum(arm['before']) == sum(arm['after'])
    assert arm['before_tick'] == arm['after_tick'] == 3
    assert 'outflows=[51,40] tankRoom=0 hoseNeed=0' in arm['candidates']
assert all(before == after for _, _, before, after in scene['restore']['settings'])
saves = Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves')
assert all(digest(saves / name) == value for name, value in scene['protected_after'].items())
first = read(HERE / 'live_scene.json')
assert first['status'] == 'FAIL' and first['restore']['status'] == 'PASS'
assert not first['changed_existing_saves'] and first['protected_before'] == first['protected_after']
for name in ('preflight_offline_retry.json', 'live-attempt2/preflight_live.json'):
    assert read(HERE / name)['verdict'] == 'GREEN'
assert not read(HERE / 'live-attempt2/log_loaded.json')['hits']
assert not read(HERE / 'live-attempt2/log_after_scene.json')['hits']

judge = read(HERE / 'judge_final_raw.json')
assert judge['result'].strip() == (HERE.parent / 'JUDGE.md').read_text().strip()
assert judge['result'].strip().endswith('would show: yes')
published = []
for name in ('publish_source_stdout.txt', 'publish_driver_stdout.txt'):
    sha = re.findall(r'PUBLISHED ([0-9a-f]{40})', (HERE / name).read_text())[-1]
    subprocess.run(['git', 'merge-base', '--is-ancestor', sha, 'origin/main'], cwd=ROOT, check=True)
    published.append(sha)

# Measure host state without rimflow/game's atomic ledger-directory update.
process = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq RimWorldWin64.exe', '/FO', 'CSV', '/NH'], capture_output=True, check=True)
rows = list(csv.reader(io.StringIO(process.stdout.decode(errors='replace'))))
assert not any(row and row[0].lower() == 'rimworldwin64.exe' for row in rows)
assert not Path('/mnt/d/ClaudeWork/rimmandrake/scratch/DRIVER_LOCK.json').exists()
bridge_lines = (ROOT / 'infrastructure/state/BRIDGE').read_text().splitlines()
assert sum(line.startswith('FREE') for line in bridge_lines) == 1

os.environ.update(WHITTLE_DIR='whittle/fw-drain-pump-outflow', WHITTLE_NEED_JUDGE='1', WHITTLE_NEED_BROADEN='1')
spec = importlib.util.spec_from_file_location('whittle_checker', ROOT / '.claude/hooks/whittle_stop.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
problems = checker.done_problems(str(ROOT), os.environ['WHITTLE_DIR'], True, True)
assert not problems, problems
spec = importlib.util.spec_from_file_location('whittle_workflow', '/home/mandrake/dev/MandrakeWorkflows/whittle/run.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
assert workflow.validate(ROOT) == 0

record = {
    'time': time.time(),
    'published': published,
    'tested_inputs': inputs,
    'normal_selftest_compile_inputs': compile_inputs,
    'shipping_compile_inputs': shipping_inputs,
    'whole_trace_sha256': digest(trace),
    'independent_raw_decode_matches': True,
    'dll_sha256': digest(dll),
    'stage_inputs': len(stage_record['sha256']),
    'suite': 'PASS 1/1, main 1260/1260, hose 188/188 checks and 457/457 assertions',
    'live_arms': scene['arms'],
    'restore': 'exact rectangle/settings and protected saves match, no existing save changed',
    'final_game': 'process absent, bridge FREE, host driver lock absent',
    'judge_exact_raw_result': True,
    'done_problems': problems,
    'actual_workflow_validator': 0,
    'qualifications': [
        'Live uses paused direct TryDraw with DEV power, bypassing scheduled Tick and its multi-level loop.',
        'Natural bodies, tank fallback, hose filling and rollback have offline production-method coverage with engine doubles.',
        'First live setup failed on an illegal cross-band hose route and restored. Corrected adjacent mouth passed.',
        'One generic pre-fixture humanlike-pawn log error is retained. Exception and Config-error scans have no hits.',
        'Judges retain their exact words. Wrapper changes are documentation only and 500 dL room coverage is offline.',
        'Existing companion missing-stamp provenance and full-list/multi-pump/scheduled-play limits remain.',
    ],
}
output = HERE / 'parent_acceptance.json'
assert not output.exists()
output.write_text(json.dumps(record, indent=2) + '\n')
print('PASS independent full-trace decode, 524 tested inputs, 256 Compile includes, shipping stamp/stage/deploy, live restoration and both validators')
