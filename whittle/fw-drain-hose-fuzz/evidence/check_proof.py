"""Verify raw control outputs, exact source identities and the one authorized wrapper."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
from integrity import snapshot, staged_hashes

here=Path(__file__).resolve().parent
root=here.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hose='src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs'
kernel='src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs'
original=here/'original_HoseFuzz.cs'
checks={}
controls={
 'original_total':0, 'original_total_full':0,
 'final_total_full':1, 'final_repaired_total':1,
 'final_positive_tiny':0, 'final_positive_g2off':0, 'final_positive_g2':0,
 'final_refuse_outlet':1, 'final_refuse_free':1,
 'final_debug_refusal':0, 'final_debug_partial_refusal':0,
 'final_debug_positive':0, 'final_debug_mutant':0,
 'final_disabled':0, 'final_trail_only':0, 'final_both_families':0,
 'entry_g2_retry':0,'entry_g2off':0,'entry_refusal':0,'entry_total':1,
}
for label, expected in controls.items():
    d=here/('fast_'+label)
    receipt=json.loads((d/'receipt.json').read_text())
    output=(d/'stdout.txt').read_text()
    assert receipt['returncode']==expected and receipt['staged_inputs_match_saved'], label
    for p, digest in receipt['staged_sha256'].items():
        assert sha(d/'inputs'/p)==digest, (label,p)
        assert sha(Path(receipt['stage'])/'inputs'/p)==digest, (label,p,'external stage drift')
    saved=d/'inputs'/hose
    assert saved.read_bytes()==(original if receipt['version']=='original' else root/hose).read_bytes()
    if receipt['mutant']=='production':
        assert (d/'inputs'/kernel).read_bytes()==(root/kernel).read_bytes()
    lines=[l for l in output.splitlines() if l.startswith(('FAIL ','PASS fuzz hose','  fuzz hose','  HoseFuzz:','hose fuzz total:','FAILED checks:'))]
    checks[label]=dict(returncode=receipt['returncode'],expected=expected,raw_stdout='fast_'+label+'/stdout.txt',receipt='fast_'+label+'/receipt.json',targeted_lines=lines,inputs_verified=True)
    if label in ('original_total','original_total_full'):
        assert 'PASS fuzz hose:' in output and '(0 laid,' in output and 'FAIL ' not in output
    elif expected==1:
        assert 'FAIL fuzz hose:' in output
        if receipt['mutant']=='total':
            assert '0/2 successful checked coverage witnesses' in output
            assert 'hose coverage [outlet] seed 2:' in output and 'hose coverage [free] seed 2:' in output
        else:
            assert '1/2 successful checked coverage witnesses' in output
            assert 'hose coverage ['+receipt['mutant']+'] seed 2:' in output
    elif label in ('final_debug_refusal','entry_refusal'):
        assert '0 random laid' in output and 'single-seed debug' in output
    elif label.startswith('final_positive') or label in ('entry_g2_retry','entry_g2off','final_both_families'):
        assert '2/2 successful checked coverage witnesses' in output and 'FAIL ' not in output
    elif label=='final_disabled':
        assert 'coverage witnesses' not in output and 'fuzz hose' not in output
    elif label=='final_trail_only':
        assert 'PASS fuzz trail:' in output and 'coverage witnesses' not in output and 'fuzz hose' not in output
# Both total-refusal comparisons use byte-identical mutated whole production kernels.
for old,new in [('original_total','final_repaired_total'),('original_total_full','final_total_full')]:
    assert (here/('fast_'+old)/'inputs'/kernel).read_bytes()==(here/('fast_'+new)/'inputs'/kernel).read_bytes()
checks['same_total_refusal_mutant_verified']=True
checks['full_scale_original_false_pass']='2798 cases, 8200 steps, 0 failures, 0 laid'
assert '2798 cases, 8200 steps, 0 failure(s)' in (here/'fast_original_total_full/stdout.txt').read_text()
assert '2798 cases, 8200 steps, 2 failure(s)' in (here/'fast_final_total_full/stdout.txt').read_text()
current=snapshot()
baseline=json.loads((here/'integrity_baseline.json').read_text())['sha256']
changed=[p for p,digest in baseline.items() if current['sha256'][p]!=digest]
assert changed==[hose],changed
checks['changed_since_pre_edit_source_manifest']=changed
full_before=json.loads((here/'integrity_original.json').read_text())['sha256']
assert current['sha256']==full_before
checks['full_mod_tool_media_snapshot_stable_since_final_change']=True
tracked=subprocess.check_output(['git','diff','--name-only','HEAD','--','src/RimMandrake/FlowWorks','src/RimMandrake/GimmeSomeSlack','src/RimMandrake/_Shared','src/RimMandrake/Utils','src/Directory.Build.props','src/Directory.Build.targets'],cwd=root,text=True).splitlines()
assert tracked==[hose],tracked
checks['tracked_mod_tool_changes_vs_HEAD']=tracked
receipt=json.loads((here/'selftest_receipt.json').read_text())
assert receipt['returncode']==0 and receipt['source_test_hashes_unchanged']
assert receipt['sha256_after']==current['sha256']
staged=staged_hashes()
assert not staged['missing'] and not staged['mismatch'] and staged['artifacts']
checks['staged_inputs_match_test_input']=True
checks['stage']=staged['stage']
wrapper=(here/'selftest_stdout.txt').read_text()
output=(here/'csharp_stdout.txt').read_text()
assert 'PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in wrapper
assert 'FAIL ' not in output
assert '2/2 successful checked coverage witnesses' in output
assert 'HoseFuzz: 4/4' in output
checks['wrapper']=dict(returncode=0,elapsed=receipt['elapsed'],stdout=wrapper,targeted_lines=[l for l in output.splitlines() if 'fuzz hose ' in l or 'HoseFuzz:' in l or 'fuzz trail ' in l or 'assertions passed' in l or 'passed,' in l])
reference=json.loads((root/'whittle/fw-drain-selftest-resume/evidence/reference_provenance.json').read_text())
checks['reference_after_test']={k:sha(Path(reference[k])) for k in ('assembly','source')}
assert all(checks['reference_after_test'][k]==reference[k+'_sha256'] for k in checks['reference_after_test'])
extraction=json.loads((here/'output_extraction.json').read_text())
raw=Path(extraction['original_observer_path'])
assert raw.is_file() and sha(raw)==extraction['original_observer_sha256']
checks['whole_observer_preserved']=dict(path=str(raw),sha256=sha(raw),bytes=raw.stat().st_size)
checks['preparation_failure']=json.loads((here/'entry_g2_preparation_failure.json').read_text())
checks['final_source_sha256']=sha(root/hose)
checks['original_source_sha256']=sha(original)
checks['time']=time.time()
(here/'source_diff.patch').write_bytes(subprocess.check_output(['git','diff','--',hose],cwd=root))
assert not (here/'proof_checks.json').exists()
(here/'proof_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in checks.items() if k not in controls},indent=2))
