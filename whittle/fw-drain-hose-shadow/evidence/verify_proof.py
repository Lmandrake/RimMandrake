"""Substantive fresh content verification, without touching mtimes or rerunning passed tests."""
import hashlib,json,subprocess,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((h/'identity_preproof.json').read_text())
after=json.loads((h/'identity_after.json').read_text())
assert pre['sha256']==after['sha256']
initial=json.loads((h/'identity_before.json').read_text())
changes=[p for p,v in initial['sha256'].items() if after['sha256'].get(p)!=v]
changes+=sorted(set(after['sha256'])-set(initial['sha256']))
expected={'src/RimMandrake/FlowWorks/Source/SelfTest/'+p for p in ('HoseShadowHarness.cs','HoseShadowHarness.targets','Program.cs','RimMandrakeFlowWorks.SelfTest.csproj')}
assert set(changes)==expected,changes
r=json.loads((h/'selftest_receipt.json').read_text())
assert r['returncode']==0 and r['source_test_hashes_unchanged']
for p,v in r['sha256_after'].items(): assert sha(root/p)==v,p
stdout=(h/'selftest_stdout.txt').read_text()
cs=(h/'csharp_stdout.txt').read_text()
assert 'PASS 1/1  FAIL 0/1  UNMEASURED 0/1  CRASH 0/1  SKIPPED 0/1' in stdout
assert 'cache: 0 CACHED PASS' in stdout
assert cs.count('ok    HS_')==9 and '\nFAIL' not in cs
neg=json.loads((h/'negative_controls.json').read_text())
assert neg['restored_byte_exact'] and len(neg['records'])==8
assert all(v['returncode']!=0 and v['compiled'] and v['failures'] for v in neg['records'])
stage=json.loads((h/'stage_identity.json').read_text())
assert stage['all_inputs_match'] and len(stage['exact_production_methods'])==7
for p,v in stage['compile_inputs'].items(): assert sha(root/p)==v['expected'],p
assert pre['shipping_dll_sha256']==after['shipping_dll_sha256']==initial['shipping_dll_sha256']
assert pre['shipping_stamp_sha256']==after['shipping_stamp_sha256']==initial['shipping_stamp_sha256']
assert pre['installed_assembly_sha256']==after['installed_assembly_sha256']
# Freshly read every recorded source/artifact byte, not a timestamp refresh.
readback={p:sha(root/p) for p in after['sha256']}
assert readback==after['sha256']
record=dict(time=time.time(),frozen_statement_sha256=sha(h.parent/'STATEMENT.md'),source_inputs_freshly_read=len(readback),all_before_after_inputs_equal=True,shipping_stamp_rows=len(after['shipping_stamp_rows']),shipping_dll_sha256=after['shipping_dll_sha256'],shipping_stamp_sha256=after['shipping_stamp_sha256'],installed_assembly_sha256=after['installed_assembly_sha256'],source_manifest_evidence='identity_before.json, identity_preproof.json, identity_after.json, integrity_before.json, stage_identity.json',stage_compiled_inputs=len(stage['compile_inputs']),exact_extracted_production_methods=list(stage['exact_production_methods']),focused='focused3.json: 10/10 Cases including 9 HS behaviours, HoseCarryChecks41/41 assertions',standard_runner_stdout=stdout,standard_csharp_summary=[line for line in cs.splitlines() if 'passed' in line or line.startswith('  HoseCarryChecks:') or line.startswith('ok    HS_')],negative_controls=[dict(name=v['name'],failures=v['failures']) for v in neg['records']],changed_paths=sorted(expected),other_changes='Parent-existing own-seat reassignment ledger modification and unit scaffold are preserved; worker made no ledger writes',limits=['offline complete-method extraction against explicit engine doubles, not the whole Verse class','upper-first iteration can retain one stale frame; budget can retain old shadow while pending until a later scan','retracting entire lower strand is omitted including visible clipped remainder','LegacyFrame opt-in intentionally retains original carry/null/retract comparison behavior','actual live rendered behavior, Unity lifecycle, natural jobs/scheduling and full mod list unverified'],shipping_source_changed=False,shipping_build_run=False,art_changes=False,bridge_or_deploy_or_game_or_modlist_actions=False)
assert not (h/'verification.json').exists()
(h/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
