"""Read the final actual run, exact source diff, publication ancestry and immutable inputs."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

here = Path(__file__).resolve().parent
root = here.parents[2]
proof = here / 'final'
output = (proof / 'csharp_stdout.txt').read_text()
runner = (proof / 'selftest_stdout.txt').read_text()
receipt = json.loads((proof / 'selftest_receipt.json').read_text())
main = re.search(r'^(\d+)/(\d+) passed$', output, re.M)
hose = re.search(r'hose: (\d+)/(\d+) assertions passed', output)
names = ['Pond_capacity_dug_out_and_back_in_any_order',
         'PipeTankRiser_wiring_link_stops_layer_prints_flange_follows', 'RiverSwitchFlip_weirWhiteWater',
         'PitCapture_follows_a_held_pawn_that_moves', 'PipePole_P3_sag_at_the_slider_extremes',
         "LW1 a lay depends on the world's content only: fresh clone = reused pooled clone = rebuilt world (bit hash); TakeLayWorld uses World(LayWorldMaxAge)",
         'Thirst_small_pond_drink_admitted', 'Thirst_harmony_target_and_call_sites']
cases = {name: bool(re.search(r'^ok\s+' + re.escape(name) + r'$', output, re.M)) for name in names}
changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=root, text=True).splitlines()
diff = subprocess.check_output(['git', 'diff', '--', *changed], cwd=root)
(here / 'source_diff.patch').write_bytes(diff)
original = '4e9da327df7ba0a60b50837e200efb711fcbfef1'
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
ref = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=root, text=True).strip()
ancestry = {target: subprocess.run(['git', 'merge-base', '--is-ancestor', original, target], cwd=root).returncode == 0
            for target in ['HEAD', 'origin/main']}
original_diff = subprocess.check_output(['git', 'show', original, '--',
                                        'src/RimMandrake/FlowWorks/Source/SelfTest/DeepBedChecks.cs',
                                        'src/RimMandrake/FlowWorks/Source/SelfTest/ReelRiserShadowChecks.cs'], cwd=root, text=True)
before = json.loads((proof / 'integrity_before.json').read_text())
groups = {}
for group, prefix in [('flowworks_source', 'src/RimMandrake/FlowWorks/Source/'),
                      ('gss_source', 'src/RimMandrake/GimmeSomeSlack/Source/'),
                      ('shared', 'src/RimMandrake/_Shared/')]:
    entries = {p:v for p,v in before['sha256'].items() if p.startswith(prefix)}
    groups[group] = dict(files=len(entries), sha256=hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest())
record = dict(time=time.time(), HEAD=head, origin_main=ref, tested_HEAD=receipt['tested_HEAD'],
              main_counts=list(map(int, main.groups())) if main else None,
              hose_counts=list(map(int, hose.groups())) if hose else None,
              exact_case_passes=cases, failing_lines=re.findall(r'^FAIL.*$', output, re.M),
              unmeasured_phrase_present='UNMEASURED, not a pass or a fail' in output,
              wrapper_pass='PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in runner,
              receipt_returncode=receipt['returncode'], source_hashes_unchanged=receipt['source_test_hashes_unchanged'],
              changed_paths=changed, source_diff_sha256=hashlib.sha256(diff).hexdigest(), input_groups=groups,
              original_repair=original, original_repair_ancestor=ancestry, original_repair_diff=original_diff,
              raw_output_sha256=hashlib.sha256((proof / 'csharp_stdout.txt').read_bytes()).hexdigest(),
              supporting_tests_not_executed=['GSS AerialSelfTest and SittingChecks', 'separate FlowWorks Replay project'],
              limitations=['No live job/map/pixel proof', 'pond count pins three occurrences without method identity'])
assert not (here / 'verification.json').exists()
(here / 'verification.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k:v for k,v in record.items() if k != 'original_repair_diff'}, indent=2))
assert main and main[1] == main[2] and hose and hose[1] == hose[2]
assert all(cases.values()) and not record['failing_lines'] and not record['unmeasured_phrase_present']
assert record['wrapper_pass'] and receipt['returncode'] == 0 and receipt['source_test_hashes_unchanged']
assert all(ancestry.values()) and head == receipt['tested_HEAD']
assert all('/Source/SelfTest/' in p for p in changed)
