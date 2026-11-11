"""Fresh source and artifact readback after final changes; compares retained exact test/build inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
raw = Path('/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/kinetic-sway-raw')
tag = sys.argv[1] if len(sys.argv) > 1 else ''
tests = json.loads((here / ('tests_final' + tag + '.json')).read_text())
build = json.loads((here / ('build_final' + tag + '.json')).read_text())
assert tests['returncode'] == build['returncode'] == 0
assert tests['inputs_unchanged'] and build['inputs_unchanged']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

current = {p: digest(root / p) for p in tests['after']}
assert current == tests['after'] == build['after']
source_paths = [p for p in current if p.startswith('src/RimMandrake/GimmeSomeSlack/') and (
    p.endswith(('AerialMath.cs', 'AerialProbe.cs', 'SwitchFlipChecks.cs', 'ExplodeProbeChecks.cs')) or
    Path(p).suffix == '.py')]
source_paths += ['infrastructure/state/live_proofs/GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt',
                 'infrastructure/state/live_proofs/GSS_SWITCHES_PROVE_LAST_FOUR_STANDING.txt',
                 'infrastructure/state/live_proofs/GSS_RESTRING_FIX_STYLES_UNRECONCILED.txt',
                 'infrastructure/state/items/GSS_SWAY_PROVE_KINETIC_LIVE_ROW.md',
                 'src/RimMandrake/KineticArms/Defs/DamageDefs/RM_KineticArms_Damages.xml']
source_readback = {p: dict(sha256=digest(root / p), text=(root / p).read_text()) for p in source_paths}
for name in ('STATEMENT.md', 'NOTES.md', 'JUDGE_PROMPT.md'):
    p = here.parent / name
    source_readback[str(p.relative_to(root))] = dict(sha256=digest(p), text=p.read_text())

dll = root / 'src/RimMandrake/GimmeSomeSlack/Assemblies/RimMandrakeGimmeSomeSlack.dll'
stamp = dll.with_name(dll.name + '.srchash')
lines = stamp.read_text().splitlines()
assert '# dll: ' + digest(dll) in lines
project = root / 'src' / lines[0].split(': ', 1)[1]
stamp_inputs = {}
for line in lines:
    if not line or line.startswith('#'):
        continue
    sha, rel = line.split(' ', 1)
    path = (project.parent / rel).resolve()
    stamp_inputs[rel] = dict(expected=sha, actual=digest(path))
assert all(v['expected'] == v['actual'] for v in stamp_inputs.values())
assert any('AerialProbe.cs' in p for p in stamp_inputs) and any('AerialMath.cs' in p for p in stamp_inputs)

build_stage = Path('/mnt/d/ClaudeWork/rimmandrake/build/GimmeSomeSlack')
selftest_stage = Path('/mnt/d/ClaudeWork/rimmandrake/build/GimmeSomeSlackSelfTest')
stage_records = {}
for label, stage in (('shipping', build_stage), ('normal_selftest', selftest_stage)):
    provenance = stage / 'BUILD_SOURCE.json'
    stage_records[label] = dict(path=str(provenance), sha256=digest(provenance), provenance=json.loads(provenance.read_text()))
    provenance_copy = here / (label + tag + '_BUILD_SOURCE.json')
    assert not provenance_copy.exists()
    provenance_copy.write_bytes(provenance.read_bytes())
    for p in ('src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialMath.cs',
              'src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialProbe.cs',
              'src/RimMandrake/GimmeSomeSlack/Source/SelfTest/SwitchFlipChecks.cs'):
        if (stage / p).is_file():
            assert digest(stage / p) == digest(root / p), 'stage source mismatch ' + label + p
    outputs = {str(p.relative_to(stage)): digest(p) for p in stage.rglob('RimMandrakeGimmeSomeSlack*.dll')
               if 'ref' not in p.parts and 'refint' not in p.parts}
    stage_records[label]['artifact_sha256'] = outputs
    assert outputs

original = json.loads((here / 'original_sources.json').read_text())
assert all(digest(Path(original['root']) / p) == sha for p, sha in original['sha256'].items())
red = (raw / 'original_parse_red2.stdout').read_text()
assert 'FAIL actual dispatched object ,RM_Repulse_Palm' in red and 'failures=14' in red and 'error CS' not in red
original_m22 = json.loads((here / 'original_m22_red.json').read_text())
assert all(r['original_statuses'] == ['PASS', 'PASS'] for r in original_m22['results'])
dispatch = json.loads((here / 'dispatch_before_fix.json').read_text()) if tag else None
if dispatch:
    assert all(digest(Path(dispatch['root']) / 'Source/Aerial' / Path(p).name) == sha for p, sha in dispatch['sha256'].items())
    dispatch_red = (raw / 'service_dispatch_red2.stdout').read_text()
    assert 'failures=3' in dispatch_red and 'error CS' not in dispatch_red
test_logs = {k: Path(tests[k]).read_text() for k in ('stdout', 'stderr')}
assert all(n in test_logs['stderr'] for n in ('[1/4] PASS', '[2/4] PASS', '[3/4] PASS', '[4/4] PASS'))
trace = Path(tests['trace'])
assert trace.is_file()
trace_text = trace.read_text()
assert 'failures=0' in trace_text
normal_tests = tests if 'selftest_gimmesomeslack.py' in ' '.join(tests['command']) else json.loads((here / 'tests_final2.json').read_text())
assert normal_tests['returncode'] == 0 and normal_tests['inputs_unchanged']
assert all(digest(root / p) == sha for p, sha in normal_tests['after'].items() if Path(p).suffix in ('.cs', '.csproj', '.json'))
normal_trace = Path(normal_tests['trace']).read_text()
assert 'aerial: 155/155 checks passed' in normal_trace and '4485/4485 checks passed' in normal_trace
key_output = [line for line in trace_text.splitlines() if any(token in line for token in
              ('production_math_sha256=', 'production_branch_sha256=', 'production_normalization_sha256=', 'Ran 16 tests', 'failures=0'))]
main = (root / 'src/RimMandrake/GimmeSomeSlack/Source/SelfTest/Program.cs').read_text()
assert 'SwitchFlipChecks.Run();' in main and 'AerialSelfTest.Run(Check);' in main
raw_checks = {str(p): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in raw.iterdir() if p.is_file()}
for record in (tests, build):
    assert all(digest(Path(p)) == sha for p, sha in record['raw_sha256'].items())

out = here / ('fresh_readback' + tag + '.json')
assert not out.exists()
out.write_text(json.dumps(dict(time=time.time(), HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
    source_readback=source_readback, source_test_build_inputs_match=True, input_sha256=current,
    test_command=tests['command'], test_summary=test_logs, trace_sha256=digest(trace),
    observed_focused_key_output=key_output,
    normal_gss_test_command=normal_tests['command'], normal_gss_test_trace_sha256=digest(Path(normal_tests['trace'])),
    test_returncode=tests['returncode'], build_command=build['command'], build_returncode=build['returncode'],
    dll_sha256=digest(dll), stamp_sha256=digest(stamp), stamp_text=stamp.read_text(), stamp_inputs=stamp_inputs,
    stage_records=stage_records, original_sources_preserved=True, original_parse_behavioral_failures=14,
    request_normalization_red_snapshot=dispatch,
    original_m22_false_passes=original_m22['results'], raw_files=raw_checks,
    limitations=['Offline engine doubles prove parsing/dispatch, not actual engine effects',
                 'No live game, bridge, deploy, mod list change or KineticArms integration run',
                 'Separate GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC live acceptance remains open',
                 'No render math, appearance or art change', 'Parent alone publishes and verifies/closes/archives']), indent=2) + '\n')
print(json.dumps(dict(path=str(out.relative_to(root)), sha256=digest(out), dll_sha256=digest(dll),
                     stamp_inputs=len(stamp_inputs), stage_records=list(stage_records)), indent=2))
