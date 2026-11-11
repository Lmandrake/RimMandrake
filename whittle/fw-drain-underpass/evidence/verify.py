"""Reproducible offline checks; never edits production/test sources or invokes live tools."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
production = root / 'src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py'
test = 'src/RimMandrake/Utils/selftest_drawbridge_underpass.py'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

initial = digest(production)
results = []
for name, target, old in [('focused', test, False), ('regression_old', test, True),
                          ('existing_drawbridge', 'src/RimMandrake/FlowWorks/northstar/selftest_drawbridge_proof.py', False)]:
    env = dict(os.environ)
    env.pop('DRAWBRIDGE_UNDERPASS_MODULE', None)
    env.pop('DRAWBRIDGE_UNDERPASS_ROWS', None)
    if target == test:
        env['DRAWBRIDGE_UNDERPASS_ROWS'] = str(evidence / (name + '_rows.json'))
    if old:
        env['DRAWBRIDGE_UNDERPASS_MODULE'] = str(evidence / 'old_drawbridge_proof.py')
    cmd = ['python3', 'src/RimMandrake/Utils/run_selftests.py', '--only', target, '--workers', '1']
    started = time.time()
    r = subprocess.run(cmd, cwd=root, env=env, text=True, capture_output=True, timeout=120)
    (evidence / (name + '.stdout.log')).write_text(r.stdout)
    (evidence / (name + '.stderr.log')).write_text(r.stderr)
    result = {'name': name, 'command': cmd, 'started': started, 'elapsed': time.time() - started,
              'returncode': r.returncode, 'expected_returncode': 1 if old else 0,
              'stdout': str(evidence / (name + '.stdout.log')), 'env': {k: v for k, v in env.items() if k.startswith('DRAWBRIDGE_UNDERPASS_')}}
    results.append(result)
    print(name, 'exit', r.returncode, 'expected', result['expected_returncode'], flush=True)
receipt = {'mode': 'offline acceptance instrument only; no live game or bridge', 'calls': results,
           'production_sha256_before': initial, 'production_sha256_after': digest(production),
           'old_sha256': digest(evidence / 'old_drawbridge_proof.py'), 'selftest_sha256': digest(root / test),
           'diff_check': subprocess.run(['git', 'diff', '--check'], cwd=root, text=True, capture_output=True).stdout,
           'status': subprocess.check_output(['git', 'status', '--short'], cwd=root, text=True),
           'filesystem': subprocess.check_output(['findmnt', '-T', str(evidence), '-n', '-o', 'FSTYPE,TARGET'], text=True)}
(evidence / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
# Fresh inspectable source evidence, independently hashable against the worktree.
(evidence / 'production_final.py').write_bytes(production.read_bytes())
producer = root / 'src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs'
lines = producer.read_text().splitlines()
(evidence / 'producer.txt').write_text(str(producer.relative_to(root)) + '\n' + '\n'.join('%d: %s' % (i+1, lines[i]) for i in range(1159,1205)) + '\n')
old_rows = json.loads((evidence / 'regression_old_rows.json').read_text())
new_rows = json.loads((evidence / 'focused_rows.json').read_text())
summary = []
for new, old in zip(new_rows['rows'], old_rows['rows']):
    assert new['case'] == old['case']
    summary.append({'case': new['case'], 'expected': new['expected'],
                    'new': [new['row']['status'], new['row']['class']],
                    'old': [old['row']['status'], old['row']['class']]})
(evidence / 'verdict_comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
assert receipt['production_sha256_before'] == receipt['production_sha256_after']
assert all(c['returncode'] == c['expected_returncode'] for c in results)
assert len(new_rows['rows']) == len(old_rows['rows'])
assert new_rows['failures'] == new_rows['errors'] == 0
print(len(summary), 'production-row scenarios; tracked sources unchanged by regression replay')
