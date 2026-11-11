"""Record the focused selftest and replay identical parsed fixtures against actual old/current predicates.

No tracked source is mutated. Only the old predicate is saved, with its git revision and hashes.
The final selftest's fixture function/table are AST-extracted, never copied before finalization.
"""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
production = 'src/RimMandrake/FlowWorks/northstar/liquid_checks.py'
selftest = 'src/RimMandrake/FlowWorks/northstar/selftest_liquid_checks.py'
original_sha = '4ca1fc48d3efb86bd061ee9edbc5d10365ef0f05'
sha256 = lambda data: hashlib.sha256(data).hexdigest()
started = time.time()
before = {p: sha256((root / p).read_bytes()) for p in (production, selftest)}
cmd = ['python3', 'src/RimMandrake/Utils/run_selftests.py', '--only', selftest, '--workers', '1']
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True, timeout=120)
(here / 'selftest_stdout.txt').write_bytes(proc.stdout)
(here / 'selftest_stderr.txt').write_bytes(proc.stderr)
assert proc.returncode == 0, (proc.returncode, proc.stdout, proc.stderr)

old_source = subprocess.run(['git', 'show', original_sha + ':' + production], cwd=root,
                            capture_output=True, check=True).stdout
old_tree = ast.parse(old_source)
old_node = next(n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'pond_depth_verdict')
old_function = ast.get_source_segment(old_source.decode(), old_node) + '\n'
(here / 'old_pond_depth_verdict.py').write_text(old_function)
old_ns = {}
exec(compile(ast.Module(body=[old_node], type_ignores=[]), original_sha + ':' + production, 'exec'), old_ns)

sys.dont_write_bytecode = True
sys.path.insert(0, str((root / production).parent))
spec = importlib.util.spec_from_file_location('liquid_checks', root / production)
current = importlib.util.module_from_spec(spec)
spec.loader.exec_module(current)
test_tree = ast.parse((root / selftest).read_text())
nodes = [n for n in test_tree.body if
         (isinstance(n, ast.FunctionDef) and n.name == '_P') or
         (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_pond_cases' for t in n.targets))]
assert len(nodes) == 2
fixtures = {'LC': current}
exec(compile(ast.Module(body=nodes, type_ignores=[]), selftest, 'exec'), fixtures)
rows = []
for label, reads, expected in fixtures['_pond_cases']:
    old_result = old_ns['pond_depth_verdict'](copy.deepcopy(reads))
    current_result = current.pond_depth_verdict(copy.deepcopy(reads))
    assert current_result[:2] == expected, (label, current_result, expected)
    rows.append(dict(case=label, parsed_reads=reads, expected=expected,
                     old_verdict=old_result, current_verdict=current_result,
                     old_meets_expectation=old_result[:2] == expected))
regressions = [r['case'] for r in rows if not r['old_meets_expectation']]
assert len(regressions) == 3, regressions
assert all(r['old_verdict'][:2] == ('PASS', 'MOD') and r['current_verdict'][:2] == ('FAIL', 'MOD')
           for r in rows if not r['old_meets_expectation'])
(here / 'verdict_comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
after = {p: sha256((root / p).read_bytes()) for p in before}
assert after == before, 'source changed during verification'
receipt = dict(started=started, elapsed=time.time() - started, original_git_sha=original_sha,
               current_git_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
               command=cmd, returncode=proc.returncode, source_sha256=after,
               original_production_sha256=sha256(old_source), old_extracted_function_sha256=sha256(old_function.encode()),
               fixtures='AST-extracted _P and _pond_cases from final existing selftest; parsed through current production parse_pond',
               execution='Old predicate AST from git show; current predicate imported from working source; identical deep-copied parsed inputs',
               total_pond_cases=len(rows), current_failures=0, old_failures=regressions,
               source_unchanged_during_verification=True, bridge_or_game_used=False)
(here / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
