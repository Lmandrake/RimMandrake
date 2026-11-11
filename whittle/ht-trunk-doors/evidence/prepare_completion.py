"""Prepare exact claims and a neutral file inventory only after accepted raw audits exist."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[3];u=root/'whittle/ht-trunk-doors';raw=u/'evidence/raw';attempt=sys.argv[1]
assert json.loads((raw/attempt/'process-receipt.json').read_text())['ok']
assert json.loads((raw/'final-proof-audit.json').read_text())['ok']
assert (raw/'final-audit-v7.json').is_file()
assert not (u/'DONE.md').exists() and not (u/'JUDGE_SCOPE_READY.md').exists()
bullets=[x[2:] for x in (u/'STATEMENT.md').read_text().splitlines() if x.startswith('- ')]
assert len(bullets)==3
refs='`whittle/ht-trunk-doors/evidence/raw/final-audit-v7.json` `whittle/ht-trunk-doors/evidence/raw/final-proof-audit.json`'
(u/'DONE.md').write_text('# Done\n\n'+'\n'.join('- true: '+b+' | evidence: '+refs for b in bullets)+'\n')
paths=['whittle/ht-trunk-doors/STATEMENT.md','whittle/ht-trunk-doors/NOTES.md',
'design/RimMandrake/hugethings_codex_2026-11-09/ANSWERS_OWNER.md','whittle/ht-trunk-doors/evidence/item-before.txt',
'whittle/ht-trunk-doors/PARENT_METHOD_SCOPE.md','whittle/ht-trunk-doors/PARENT_SITE_ACTOR_SCOPE.md',
'whittle/ht-trunk-doors/SOURCE_COMMITTED.json','whittle/ht-trunk-doors/SOURCE_READY_INPUTS.json']
paths += [r['path'] for r in json.loads((u/'SOURCE_READY_INPUTS.json').read_text()) if r['exists']]
paths += [r['path'] for r in json.loads((raw/'source-ready-v9-compiled-inputs.json').read_text())['inputs']]
for name in ['DEPENDENCY_APPROVED.json','DEPENDENCY_PROPOSAL.json','LUMINOUS_DEPENDENCY_AUTHORIZATION.json','LUMINOUS_DEPENDENCY_READY.json','ARCHIVE_POLICY_DECISION.md']:
 if (u/name).is_file():paths.append(str((u/name).relative_to(root)))
for name in ['final-audit-v7.json','final-proof-audit.json','source-ready-v9-inputs.json','source-ready-v9-compiled-inputs.json','candidate7-persistence-checker-v2.json','candidate9-python-check.json','engine-load-tick-contract.json','engine-native-load-tick.json']:
 if (raw/name).is_file(): paths.append(str((raw/name).relative_to(root)))
for stem in ['build-candidate7','tests-after5','planner-before-replay','planner-after-replay','planner-before','planner-after']:
 for p in sorted(raw.glob(stem+'.*')):paths.append(str(p.relative_to(root)))
for folder in ['planner-before-inputs','planner-after-inputs']:
 paths += [str(p.relative_to(root)) for p in sorted((raw/folder).rglob('*')) if p.is_file()]
for p in sorted((raw/attempt).iterdir()):
 if p.is_file():paths.append(str(p.relative_to(root)))
paths += [str(p.relative_to(root)) for p in sorted(raw.glob('accepted-cleanup-*')) if p.is_file()]
for name in ['run_live.py','verify_deploy.py','sanitize_old_log.py','final_audit_v7.py','final_proof_audit.py','build_candidate7.py']:
 paths.append(str((u/'evidence'/name).relative_to(root)))
for ext in ['dll','dll.srchash']:
 build=json.loads((raw/'build-candidate7.receipt.json').read_text());paths.append(build[ext]['path'])
paths=list(dict.fromkeys(paths))
text='# Neutral judge scope ready\n\nParent: please supply exact JUDGE_PROMPT.md. Worker has not authored it or JUDGE.md. Scope identifies source and raw records for independent review and replay; it supplies no verdict. Parent owns final full-file source review, publication and ledger lifecycle.\n\nSource deletion: src/RimMandrake/HugeThings/northstar/p1_live.py. Its prior bytes are evidence/raw/source-before/src/RimMandrake/HugeThings/northstar/p1_live.py within this unit. Read current source files in full, including the read-only TrunkDoorValidationHooks observer and functional script, and inspect exact runtime/build/script commit provenance. Runtime manifest has54 inputs.\n\nAll listed paths are relative to this clone. Attempt raw calls, script inputs, strict log gates, preflight rows, lease/guard/Steam/deploy records and restoration are separate evidence. Prior failures remain retained and are not accepted attempts. No old gameplay claim is made; PARENT_METHOD_SCOPE names the L0 method authority. No flight/art/L4/full-mod/first-touch claim. Companion missing-stamp and cached-effective-lint scope caveats must remain.\n\nJudge should receive frozen criteria and these neutral source/raw records, excluding builder DONE/BROADEN/FINDINGS/PROGRESS and pilot narratives. Only judge writes JUDGE.md. No game operation, ledger mutation or source edit is authorized for judgment. Read-only replay may use exact retained inputs without overwriting raw artifacts.\n\nFiles:\n\n'+'\n'.join('- `'+p+'`' for p in paths)+'\n'
(u/'JUDGE_SCOPE_READY.md').write_text(text)
print('exact DONE and neutral judge scope prepared; parent prompt and fresh judge/real validator still owed')
