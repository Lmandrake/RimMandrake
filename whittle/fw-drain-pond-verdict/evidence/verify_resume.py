"""Fresh old/current predicate replay after sync; reuse the one actual resume selftest.

Never rewrite original verification files or mutate production/test source.
"""
import ast
import copy
import hashlib
import importlib.util
import json
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
resume = json.loads((here / 'resume_integrity.json').read_text())
assert resume['returncode'] == 0 and resume['source_unchanged_during_selftest']
assert before == resume['source_sha256']
assert before == json.loads((here / 'final_integrity.json').read_text())['source_sha256']
old_source = subprocess.check_output(['git', 'show', original_sha + ':' + production], cwd=root)
old_node = next(n for n in ast.parse(old_source).body
                if isinstance(n, ast.FunctionDef) and n.name == 'pond_depth_verdict')
old_function = ast.get_source_segment(old_source.decode(), old_node) + '\n'
assert old_function.encode() == (here / 'old_pond_depth_verdict.py').read_bytes()
old_ns = {}
exec(compile(ast.Module(body=[old_node], type_ignores=[]), original_sha + ':' + production, 'exec'), old_ns)
sys.dont_write_bytecode = True
sys.path.insert(0, str((root / production).parent))
spec = importlib.util.spec_from_file_location('liquid_checks', root / production)
current = importlib.util.module_from_spec(spec)
spec.loader.exec_module(current)
nodes = [n for n in ast.parse((root / selftest).read_text()).body
         if (isinstance(n, ast.FunctionDef) and n.name == '_P') or
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
assert len(regressions) == 3
assert all(r['old_verdict'][:2] == ('PASS', 'MOD') and r['current_verdict'][:2] == ('FAIL', 'MOD')
           for r in rows if not r['old_meets_expectation'])
after = {p: sha256((root / p).read_bytes()) for p in before}
assert after == before
comparison = json.dumps(rows, indent=2) + '\n'
with (here / 'resume_verdict_comparison.json').open('x') as stream:
    stream.write(comparison)
patch = subprocess.check_output(['git', 'diff', '--', production, selftest], cwd=root)
with (here / 'resume.patch').open('xb') as stream:
    stream.write(patch)
receipt = dict(started=started, elapsed=time.time() - started,
               original_git_sha=original_sha,
               current_git_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
               source_sha256=after,
               original_production_sha256=sha256(old_source),
               old_extracted_function_sha256=sha256(old_function.encode()),
               selftest_command=resume['command'], selftest_returncode=resume['returncode'],
               selftest_evidence='resume_selftest.txt', selftest_process_receipt='resume_integrity.json',
               selftest_output_sha256=sha256((here / 'resume_selftest.txt').read_bytes()),
               selftest_run_count_this_resume=1,
               fixtures='AST-extracted _P and _pond_cases from final existing selftest; parsed through current production parse_pond',
               execution='Fresh execution of git-show AST-extracted original predicate and imported current predicate on identical deep-copied parsed inputs',
               total_pond_cases=len(rows), current_failures=0, old_failures=regressions,
               comparison_sha256=sha256(comparison.encode()),
               fresh_results_equal_original_recorded_results=json.loads(comparison) == json.loads((here / 'verdict_comparison.json').read_text()),
               source_unchanged_during_verification=True, bridge_or_game_used=False)
with (here / 'resume_verification.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt, indent=2))
