"""Independently audit the preserved executions and the readability-only follow-up."""
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
FLOWWORKS = ROOT / 'src/RimMandrake/FlowWorks'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((EVIDENCE / name).read_text())


before = read('integrity_before.json')['sha256']
current = {path: digest(ROOT / path) for path in before}
changes = [path for path, value in before.items() if current[path] != value]
formatted = [
    'Source/SelfTest/RailingToggleHarness.cs',
    'Source/SelfTest/RailingToggleHarness.targets',
    'Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj',
    'northstar/railing_toggle_live.py',
]
assert sorted(changes) == sorted([
    'src/RimMandrake/FlowWorks/' + path for path in formatted
] + [
    'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll',
    'src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash',
])

comparison = []
for relative in formatted[:2]:
    path = FLOWWORKS / relative
    original = EVIDENCE / ('pre_format_' + path.name)
    command = [
        '/mnt/c/Users/Mandrake/.dotnet/dotnet.exe',
        'D:/ClaudeWork/rimmandrake/scratch/fw-railing-format/bin/Release/net8.0/Compare.dll',
    ] + [subprocess.check_output(['wslpath', '-w', str(p)], text=True).strip()
         for p in (original, path)]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    comparison.append({'path': relative, 'command': command, 'result': result.stdout.strip()})

project = FLOWWORKS / formatted[2]
original_project = EVIDENCE / ('pre_format_' + project.name)

def xml_structure(path):
    root = ET.parse(path).getroot()
    for element in root.iter():
        element.text = (element.text or '').strip()
        element.tail = ''
    return ET.tostring(root)

assert xml_structure(project) == xml_structure(original_project)
script = FLOWWORKS / formatted[3]
original_script = EVIDENCE / ('pre_format_' + script.name)
assert ast.dump(ast.parse(script.read_text())) == ast.dump(ast.parse(original_script.read_text()))
assert digest(original_script) == read('driver_publication.json')['sha256']

suite = read('selftest_receipt.json')
assert suite['returncode'] == 0 and suite['source_test_hashes_unchanged']
assert suite['sha256_after'] == before
build = read('build_integrity.json')
for path, value in build['staged_compile_inputs'].items():
    assert digest(ROOT / path) == digest(Path(build['stage']) / path) == value == before[path]
for path, value in build['artifacts'].items():
    assert digest(ROOT / path) == value
staged = read('integrity_after_test.json')['staged']
assert not staged['missing'] and not staged['mismatch']
for path, value in staged['sha256'].items():
    assert digest(Path(staged['stage']) / path) == value

# Decode the sampled wrapper's writes directly from the preserved whole trace.
extraction = read('output_extraction.json')
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
assert bytes(streams[1]) == (EVIDENCE / 'csharp_stdout.txt').read_bytes()
assert bytes(streams[2]) == (EVIDENCE / 'csharp_stderr.txt').read_bytes()
assert b'1252/1252 passed' in streams[1] and b'hose: 457/457 assertions passed' in streams[1]
assert read('fast_parent_format/receipt.json')['returncode'] == 0
assert '8/8 PASS; 0 FAIL' in (EVIDENCE / 'fast_parent_format/stdout.txt').read_text()
assert all(row['restore']['status'] == 'PASS' for row in read('parent_live_driver_checks.json'))

live = read('live_attempt2.json')
assert live['status'] == live['restore']['status'] == 'PASS'
assert live['before'] == live['restore']['rect']
assert live['settings_before'] == live['restore']['settings']
assert live['railings_before'] == live['railings_after'] and len(live['railings_after']) == 4
assert read('live_attempt1.json')['status'] == 'FAIL'
assert read('live_attempt1.json')['restore']['status'] == 'PASS'
assert read('preflight_live2.json')['verdict'] == read('preflight_offline2.json')['verdict'] == 'GREEN'
assert read('live_census2.json')['ordered_list_matches']
for path, value in read('deployed_dlls.json')['sha256'].items():
    assert digest(Path(path)) == value
save_folder = Path('/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Saves')
for name, value in read('live_inputs_before.json')['saves'].items():
    assert digest(save_folder / name) == value['sha256']

for name in ('publication.json', 'driver_publication.json'):
    subprocess.run(['git', 'merge-base', '--is-ancestor', read(name)['PUBLISHED'], 'origin/main'], check=True)
process = subprocess.run(['tasklist.exe', '/FI', 'IMAGENAME eq RimWorldWin64.exe', '/FO', 'CSV', '/NH'], check=True, capture_output=True)
rows = list(csv.reader(io.StringIO(process.stdout.decode(errors='replace'))))
assert not any(row and row[0].lower() == 'rimworldwin64.exe' for row in rows)
assert not Path('/mnt/d/ClaudeWork/rimmandrake/scratch/DRIVER_LOCK.json').exists()
bridge_lines = (ROOT / 'infrastructure/state/BRIDGE').read_text().splitlines()
assert sum(line.startswith('FREE') for line in bridge_lines) == 1
(EVIDENCE / 'parent_tasklist_stdout.txt').write_bytes(process.stdout)

record = {
    'time': time.time(),
    'input_hashes': current,
    'rehash_count': len(current),
    'source_changes_since_suite': changes,
    'csharp_token_equivalence': comparison,
    'project_xml_equivalent': True,
    'live_driver_ast_equivalent_to_live_publication': True,
    'shipping_compile_inputs_byte_identical': len(build['staged_compile_inputs']),
    'preserved_suite_stage_inputs': len(staged['sha256']),
    'whole_observer_sha256': digest(trace),
    'independently_decoded_wrapper_output_matches': True,
    'formatted_actual_method_checks': '8/8 PASS',
    'formatted_driver_controls': 'success and intentional failure both restore',
    'suite': 'PASS 1/1, main 1252/1252, hose 457/457 assertions',
    'live': 'attempt 1 failed in reader before toggle, restored. Attempt 2 PASS, restored',
    'final_game': 'DOWN, process absent, bridge FREE and host driver lock absent',
    'qualification': 'Full suite ran pre-format. Syntax tokens, project XML and driver AST match. Formatted harness and driver controls ran afterward. Live ran the AST-equivalent pre-format driver. Shipping inputs are byte-identical.',
}
output = EVIDENCE / (sys.argv[1] if len(sys.argv) > 1 else 'parent_acceptance.json')
assert not output.exists()
output.write_text(json.dumps(record, indent=2) + '\n')
print('PASS independent raw decode, input hashes, syntax/AST equivalence, live restoration and final host state')
