"""Inspect the actual authorized run and exact inputs, without invoking a suite."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
output_path = here / 'csharp_stdout.txt'
output = output_path.read_text()
runner = (here / 'selftest_stdout.txt').read_text()
receipt = json.loads((here / 'selftest_receipt.json').read_text())
before = json.loads((here / 'integrity_before.json').read_text())
stage = json.loads((here / 'stage_identity.json').read_text())
main = re.search(r'^(\d+)/(\d+) passed$', output, re.M)
hose = re.search(r'hose: (\d+)/(\d+) assertions passed', output)
cases = re.findall(r'^ok\s+(PipeSpan_P3_.*)$', output, re.M)
expected = [
    'PipeSpan_P3_edge_joins_two_60pct_components_cap_after_join_refused',
    'PipeSpan_P3_edge_joins_two_40pct_components_accepted_as_one',
    'PipeSpan_P3_one_logical_edge_no_duplicate_cardinal_or_reverse_span',
    'PipeSpan_P3_ring_of_two_pole_routes_cut_in_turn',
    'PipeSpan_P3_cut_span_splits_the_net_once',
    'PipeSpan_P3_production_wiring_adapter_callback_join_order',
    'PipeSpan_P3_callback_guard_rejects_normalized_counter_only',
    'PipeSpan_P3_callback_guard_scopes_changed_bump',
]
changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=root, text=True).splitlines()
diff = subprocess.check_output(['git', 'diff', '--', *changed], cwd=root)
(here / 'source_diff.patch').write_bytes(diff)
sha_after = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in before['sha256']}
groups = {}
for label, prefix in [('flowworks_source', 'src/RimMandrake/FlowWorks/Source/'),
                      ('gss_source', 'src/RimMandrake/GimmeSomeSlack/Source/'),
                      ('shared', 'src/RimMandrake/_Shared/')]:
    values = {p: v for p, v in sha_after.items() if p.startswith(prefix)}
    groups[label] = dict(files=len(values), sha256=hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest())
reference = json.loads((here / 'reference_identity.json').read_text())
reference_after = {k: hashlib.sha256((root / reference['prior'][p]).read_bytes()).hexdigest()
                   for k, p in [('assembly_sha256', 'assembly'), ('source_sha256', 'source')]}
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
original = json.loads((here / 'original_guard_reproduction.json').read_text())
scope = (here / 'scope_reconciliation.md').read_text()
record = dict(time=time.time(), HEAD=head, tested_HEAD=receipt['tested_HEAD'],
              main_counts=list(map(int, main.groups())) if main else None,
              hose_counts=list(map(int, hose.groups())) if hose else None,
              exact_pipe_span_case_passes={name: name in cases for name in expected},
              actual_pipe_span_cases=cases, failing_lines=re.findall(r'^FAIL.*$', output, re.M),
              wrapper_pass='PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in runner,
              receipt_returncode=receipt['returncode'],
              unmeasured_phrase_present='UNMEASURED, not a pass or a fail' in output,
              source_hashes_unchanged=sha_after == before['sha256'] == receipt['sha256_after'],
              input_groups=groups, stage_all_inputs_match=stage['all_inputs_match'],
              reference_remeasured_after=reference_after,
              reference_identity_matches=reference_after == reference['remeasured'],
              changed_paths=changed, source_diff_sha256=hashlib.sha256(diff).hexdigest(),
              raw_output_sha256=hashlib.sha256(output_path.read_bytes()).hexdigest(),
              original_guard_reproduction_readback=original,
              scope_reconciliation=scope,
              negative_callback_controls=14,
              limitations=['Offline source-shape and linked production math proof.',
                           'Source guard pins current internal signature, parameter names and braced Changed block.',
                           'Existing brace matcher does not lex strings or preprocessor directives.',
                           'GSS AerialSelfTest and separate FlowWorks Replay project were outside the requested wrapper.'])
path = here / 'verification.json'
assert not path.exists()
path.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: v for k, v in record.items() if k not in ('scope_reconciliation', 'original_guard_reproduction_readback')}, indent=2))
assert main and main[1] == main[2] and hose and hose[1] == hose[2]
assert all(record['exact_pipe_span_case_passes'].values())
assert record['wrapper_pass'] and receipt['returncode'] == 0 and not record['failing_lines']
assert not record['unmeasured_phrase_present']
assert record['source_hashes_unchanged'] and record['reference_identity_matches'] and stage['all_inputs_match']
assert head == receipt['tested_HEAD']
assert changed == ['src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs',
                   'src/RimMandrake/FlowWorks/Source/SelfTest/RiverSwitchFlipChecks.cs']
