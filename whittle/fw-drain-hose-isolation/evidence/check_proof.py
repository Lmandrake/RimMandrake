"""Inspect saved raw outputs and byte identities. No tests are rerun."""
from pathlib import Path
import hashlib, json, subprocess, time
from integrity import snapshot, staged_hashes
here=Path(__file__).resolve().parent
root=here.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
messages=['two pipe runs touching one tank stay two nets: pump reaches T over pipe, never TV',
          'can-fail: both pipe runs exist, T attaches to both, TV only to the far run']
for mode in ('reproduce','final','old_fixture','tank_conduction'):
    d=here/('fast_'+mode)
    receipt=json.loads((d/'receipt.json').read_text()); output=(d/'stdout.txt').read_text()
    passes=[l for l in output.splitlines() if l.startswith('PASS ')]
    failures=[l for l in output.splitlines() if l.startswith('FAIL ')]
    assert receipt['returncode']==receipt['expected_returncode']
    assert receipt['staged_inputs_match_saved']
    assert {p:sha(d/p) for p in receipt['evidence_sha256']}==receipt['evidence_sha256']
    if mode=='final':
        assert not failures and len(passes)==40
    if mode in ('old_fixture','tank_conduction'):
        assert failures==['FAIL hosenet: '+m for m in messages] and len(passes)==38
    checks[mode]=dict(returncode=receipt['returncode'],passes=len(passes),failures=failures,source_sha256=receipt['source_sha256'],saved_inputs_match_receipt=True)
assert 'MEASURED roles a1=None b1=None tanks=[]' in (here/'fast_reproduce/stdout.txt').read_text()
checks['reproduction_exclusion_was_vacuous']=True
kernel='src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs'
hose='src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs'
assert (here/'fast_final/HoseNetChecks.cs').read_bytes()==(root/hose).read_bytes()
assert (here/'fast_tank_conduction/HoseNetChecks.cs').read_bytes()==(root/hose).read_bytes()
assert (here/'fast_final/Kernel.cs').read_bytes()==(root/kernel).read_bytes()
assert (here/'fast_old_fixture/Kernel.cs').read_bytes()==(root/kernel).read_bytes()
assert not (here/'fast_old_fixture/kernel.diff').read_text()
assert not (here/'fast_tank_conduction/hose.diff').read_text()
assert (here/'fast_old_fixture/HoseNetChecks.cs').read_text()==(root/hose).read_text().replace('"cA1"','"a1"').replace('"cB1"','"b1"')
assert (here/'fast_tank_conduction/Kernel.cs').read_bytes()!=(root/kernel).read_bytes()
checks['final_source_sha256']={p:sha(root/p) for p in (hose,kernel)}
checks['isolated_controls_have_intended_source_differences']=True
original=json.loads((here/'integrity_original.json').read_text())
current=snapshot()
changed=[p for p,h in current['sha256'].items() if original['sha256'].get(p)!=h]
assert changed==[hose],changed
checks['changed_tracked_mod_or_tool_inputs']=changed
receipt=json.loads((here/'selftest_receipt.json').read_text())
assert receipt['returncode']==0 and receipt['source_test_hashes_unchanged'] and receipt['staged_matches_test_input']
assert current['sha256']==receipt['sha256_after']
wrapper=(here/'selftest_stdout.txt').read_text(); output=(here/'csharp_stdout.txt').read_text()
assert 'PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in wrapper
# Production Program.Check prints failures only; the exact suite count proves all checks ran.
# Individual PASS messages are preserved by the independently staged fast Program.Check stub.
assert 'HoseNetChecks: 40/40' in output
assert 'FAIL ' not in output
checks['wrapper']=dict(returncode=receipt['returncode'],elapsed=receipt['elapsed'],stdout=wrapper,source_test_hashes_unchanged=receipt['source_test_hashes_unchanged'],staged_matches_test_input=receipt['staged_matches_test_input'],targeted_lines=[l for l in output.splitlines() if any(m in l for m in messages) or 'HoseNetChecks:' in l],summary_lines=[l for l in output.splitlines() if 'passed' in l or 'assertions' in l])
reference=json.loads((here/'reference_remeasurement.json').read_text())
checks['reference_rechecked_after_test']={p:sha(root/p) if not Path(p).is_absolute() else sha(Path(p)) for p in [reference['assembly'],reference['source']]}
assert checks['reference_rechecked_after_test'][reference['assembly']]==reference['assembly_sha256']
assert checks['reference_rechecked_after_test'][reference['source']]==reference['source_sha256']
checks['limitation']='Offline fake-graph endpoint isolation; no geometry, live-map/game or visual re-approval. Mutant covers pipe–tank–pipe traversal, not every form of tank conduction. Media unchanged by hash; wrapper intentionally excludes media from staging.'
checks['time']=time.time()
checks['raw_output_sha256']={p:sha(here/p) for p in ['csharp_stdout.txt','csharp_stderr.txt','selftest_stdout.txt','selftest_stderr.txt','selftest_output_writes.strace']}
(here/'source_diff.patch').write_bytes(subprocess.check_output(['git','diff','--',hose],cwd=root))
assert not (here/'proof_checks.json').exists()
(here/'proof_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
