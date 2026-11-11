"""Fresh readback of exact final source/artifact/test/live inputs after cleanup; no game mutations or evidence timestamp edits."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
R=E/'raw'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((R/'source-built-identity.json').read_text())
for name,digest in source['compiled_inputs'].items():
    assert sha(ROOT/name)==digest,name
for name,key in [('RM_HugeThings.dll','dll_sha256'),('RM_HugeThings.dll.srchash','stamp_sha256')]:
    assert sha(ROOT/'src/RimMandrake/HugeThings/Assemblies'/name)==source[key]
attempts=sorted(p for p in R.glob('live-attempt*') if (p/'process-receipt.json').exists())
passed=[p for p in attempts if json.loads((p/'process-receipt.json').read_text()).get('ok')]
assert len(passed)==1,'need exactly one completed passing live round'
round=passed[0]
live=json.loads((round/'loaded-methods.json').read_text())
assert live['ok'] and live['restoration']['ok']
assert json.loads((round/'guard-after.stdout.txt').read_text())['state']=='FREE'
assert (round/'status-after.rc').read_text().strip()=='3'
report={'readback_utc':datetime.now(timezone.utc).isoformat(),'compiled_source_identity':source,
        'source_and_spec_sha256':{},'raw_input_sha256':{},'live_round':str(round.relative_to(ROOT)),
        'test_process':json.loads((R/'focused-fixture-child/process.json').read_text()),
        'build_process':json.loads((R/'build-clones.process.json').read_text()),
        'live_process':json.loads((round/'process-receipt.json').read_text()),
        'live_restore':live['restoration'],
        'actual_fresh_process_preflight':json.loads((round/'preflight-live.json').read_text()),
        'entry_before':json.loads((round/'entry-before.json').read_text()),
        'entry_after':json.loads((round/'entry-after.json').read_text()),
        'cleanup_guard':json.loads((round/'guard-after.stdout.txt').read_text()),
        'design_prompt_sha256':sha(E/'design_prompt.txt'),'design_response_sha256':sha(E/'design_raw.json')}
paths=['src/RimMandrake/HugeThings/TIERING.md','src/RimMandrake/HugeThings/northstar/juvenile_tier_live.py',
       'src/RimMandrake/HugeThings/northstar/measure_reefback_calf.py','src/RimMandrake/HugeThings/northstar/selftest_juvenile_policy_model.py',
       'src/RimMandrake/Utils/selftest_hugethings_juvenile_tier.py','infrastructure/state/items/TITAN_CAMPS_SCAVENGERS_EVENTS_1.md',
       'design/RimMandrake/hugethings_codex_2026-11-09/REEFBACK_CALF_DECISION.md','design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md']
for name in paths:
    p=ROOT/name;report['source_and_spec_sha256'][name]=sha(p)
    target=R/'final-spec-source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
for path in sorted(R.rglob('*')):
    if path.is_file() and path.name!='final-evidence.json':report['raw_input_sha256'][str(path.relative_to(ROOT))]=sha(path)
(R/'final-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'raw_files_read':len(report['raw_input_sha256']),'compiled_inputs':len(source['compiled_inputs']),'live_round':report['live_round'],'test_rc':report['test_process']['rc'],'build_rc':report['build_process']['rc']}))
