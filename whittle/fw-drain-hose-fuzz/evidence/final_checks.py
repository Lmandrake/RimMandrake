"""Read-only final identity, review and workflow checks. No suite rerun."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

here=Path(__file__).resolve().parent
root=here.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda name:json.loads((here/name).read_text())
after=load('integrity_after_final_review.json')
before=load('integrity_before.json')
assert after['sha256']==before['sha256']
assert after['same_as_test_input'] and not after['staged']['missing'] and not after['staged']['mismatch']
assert sha(root/'src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs')=='577c4429c424506d94cadabb8d536d0a801f446905d656848fd0a3fb5019b788'
reviews={}
for mode,target in [('broaden',here/'broaden_report.md'),('judge',here/'JUDGE_first.md'),('judge_final',here.parent/'JUDGE.md')]:
    raw=load(mode+'_raw.json')
    call=load(mode+'_call.json')
    assert call['returncode']==0 and not raw.get('is_error')
    assert target.read_bytes()==raw['result'].encode()
    reviews[mode]=dict(raw_sha256=sha(here/(mode+'_raw.json')),report_sha256=sha(target),model_usage=raw['modelUsage'],last_line=raw['result'].strip().splitlines()[-1],fresh_call=True)
assert reviews['judge_final']['last_line']=='would show: yes'
reference=json.loads((root/'whittle/fw-drain-selftest-resume/evidence/reference_provenance.json').read_text())
reference_now={k:sha(Path(reference[k])) for k in ('assembly','source')}
assert all(reference_now[k]==reference[k+'_sha256'] for k in reference_now)
extraction=load('output_extraction.json')
raw_trace=Path(extraction['original_observer_path'])
assert sha(raw_trace)==extraction['original_observer_sha256']
for name in ('selftest_stdout.txt','selftest_stderr.txt'):
    assert (raw_trace.parent/name).read_bytes()==(here/name).read_bytes()
workflow=load('workflow_after_judge.json')
assert workflow['need_judge'] and workflow['need_broaden']
assert workflow['done_problems']==[] and workflow['full_validator_returncode']==0
assert subprocess.run(['git','diff','--check'],cwd=root,capture_output=True).returncode==0
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==before['HEAD']
record=dict(time=time.time(),all_checks_pass=True,source_and_tool_and_media_files=len(after['sha256']),staged_inputs=len(after['staged']['sha256']),post_review_matches_test_input=True,review_outputs_unchanged=True,reviews=reviews,reference_remeasured_after_final_review=reference_now,whole_observer_preserved=dict(path=str(raw_trace),sha256=sha(raw_trace),bytes=raw_trace.stat().st_size),external_raw_runner_logs_match_saved=True,workflow_receipt='workflow_after_judge.json',workflow_returncode=0,done_problems=[],git_diff_check=0,status=subprocess.check_output(['git','status','--short'],cwd=root,text=True),source_HEAD_unchanged=True)
assert not (here/'final_checks.json').exists()
(here/'final_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='reviews'},indent=2))
