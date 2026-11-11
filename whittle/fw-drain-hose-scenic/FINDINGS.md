# HOSE_SCENIC_SELFTEST_FIX_NEVER_CROSSES — worker findings

Ready for the parent’s publication/ledger/closure work. No commit, publish, ledger write, CLEAN mark, bridge lease, game launch, deployment, ModsConfig edit, shipping/GSS source edit or art edit was performed.

## Exact change

Only tracked source edit: `src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs`, `HoseGptFix.ScenicRoute`, lines 444–466. Final SHA-256: `80815870cdb9b0ead575d526d960dd3ae5387d71238c79e712817d4bc9f1a588`. Tested HEAD: `fea33f6a8cad7b1c002776b495e2c9bc455d7ec3` plus this uncommitted test-file change. Full patch: `whittle/fw-drain-hose-scenic/evidence/source_diff.patch`.

The measured mouth is (20.026,8.773), facing west; OutletLead is 4 at MinBendRadius 1.2, so its plan starts near x=16.026. The old target (14,9) reached no remote rig. The repair adds a costed HoseReelRect at (12,8), width/height 2, spanning both open rows between full-width walls z=7/10. Target (8,9) lies beyond it. Success requires forced.Ok and interior points in both costed columns in both poses, away from all source-nozzle contact. A permanent identical-footprint Device-blocked control must return `no route`. Existing detour, uncosted, carried, shortcut and wiring checks remain unchanged.

## Executed proof

- Fast production reproduction first: `python3 whittle/fw-drain-hose-scenic/evidence/fast_probe.py`; raw `probe_baseline_stdout.txt`/`probe_baseline_receipt.json` and `probe_manifest.json` under the same evidence directory. It compiled full actual production C# files; the original fixture laid without remote hits, while the remote costed footprint laid across (13,8) and (12,8). The initial missing-dependency compile failure is preserved separately in `probe_initial_*` and `fast_probe_initial.py`.
- Exact fixture controls after the final source change: `python3 whittle/fw-drain-hose-scenic/evidence/exact_mutant.py`. Both command receipts rc=0 (the mutant FAIL is the expected control result). Complete actual ScenicRoute methods were extracted from HEAD/current source, not retyped. Eleven full actual production dependencies were hash-checked and compiled in isolated D-drive staging. `exact_stdout.txt` has every original/final check passing. `mutant_stdout.txt` keeps every original check passing, with exactly one Final FAIL: the new crossing, `no route`. All other Final checks pass. The mutant changes only the staged production `CordPlanner.Walk` cost gate, preserving start/goal exceptions, nozzle origin, CordWorld, collision geometry, shaping and other planner rules. Exact patch, input/stage hashes, extracted fixtures and programs are in `building_block_mutant.patch`, `exact_receipt.json`, `mutant_receipt.json`, `*_scenic_exact.cs.txt`, and `*_program.cs.txt`. The broader preliminary CordWorld mutant remains intact under `evidence/pre_broaden/`.
- Exactly one final authorized wrapper run: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1`. PASS 1/1, FAIL/UNMEASURED/CRASH/SKIPPED 0; actual C# main 1240/1240, HoseGptFix 27/27, hose assertions 457/457. Test time 470.9 s, external observation 483.4 s. `selftest_receipt.json`, `selftest_stdout.txt`, `csharp_stdout.txt`, `selftest_output_writes.strace`, `output_extraction.json`, and `process_samples.jsonl` preserve execution and actual wrapper-PID writes. No unchanged suite rerun or global runner modification.
- Suite TMPDIR: `/home/mandrake/.seat-tmp/fw-hose-scenic` (ext4). Existing external strace observer hash is recorded. Installed Assembly-CSharp.dll and the preserved Pawn_NeedsTracker reference were remeasured before reuse and again after the source change; assembly `5cf1b5be399d5b1c9c56ca72c9d35b4ecf307feacf5859d04ac5a1aa5926356a`, reference `fa58868173d778dd1f0f596eb062c6c14af87f74293cf5f171aab08269a394d2`, matching prior provenance. Windows reference readback, Windows RIMWORLD_DECOMPILED and WSLENV are recorded.
- Full relevant FlowWorks/GSS/shared source and core wrapper/build-input hashes match before/after proof and before/after review: `integrity_before.json`, `post_proof_integrity.json`, `pre_judge_integrity.json`, `post_judge_integrity.json`. All 730 required staged C#/project/build/XML identities match: `stage_after_proof.json`, `stage_before_judge.json`, `stage_after_judge.json`. Supplemental full Utils Python inventory also stayed unchanged (`wrapper_support_*`, `final_review_integrity.json`).

## Frozen bullets and independent review

1. Forced costed traversal: maker evidence is the exact-source baseline/geometry and hard-block control; fresh Opus judge: MET; parent/owner acceptance pending.
2. Old false-pass, repaired mutant failure, final selftest pass: maker evidence is raw mutant output and actual C# stdout; fresh Opus judge: MET; parent/owner acceptance pending.
3. Exact identity/limits and shipping/GSS preservation: maker evidence is source/stage hashing and test-only diff; fresh Opus judge: MET; parent/owner acceptance pending. No visual or live acceptance is claimed.

`BROADEN.md` records actual suggestions/actions. Broaden and judge were separate fresh `claude -p --model opus --effort high` calls, Read/Glob/Grep-only, no history/fork/project settings/MCP, neutral ext4 cwd. Acted on the planner-only mutant and permanent hard-block suggestions. Complete JSON and transport/extraction receipts: `evidence/broaden_raw.json`, `broaden_call.json`, `broaden_extraction.json`, `judge_raw.json`, `judge_call.json`, `judge_extraction.json`. The unmodified extracted judge report is `whittle/fw-drain-hose-scenic/JUDGE.md`; it returned `would show: yes`, no actionable defects. `final_review_integrity.json` verifies the report equals the returned JSON result byte-for-byte. No source was changed after that review or the wrapper proof.

## Limits and retained failures

This is offline planned Lay, seed 7, no relay endpoint. It does not certify live LayFromOn, CheckInstall’s separate search, all carried paths, the stray-rig shaping fallback, or pixels. Plump can fall back to Flat; distinct shape is not asserted. Source/GSS appearance preservation follows the absence of shipping/source/art changes. The suite retains its existing G4 fuzz note: seed 46, plump length 17.99 versus flat 17.43, outside this fixture/item.

The mutant runs an isolated eleven-production-file probe, not the whole mutated SelfTest project; the unmutated final source runs in the real wrapper. The full strace was filtered per the existing observer pattern and removed; the retained wrapper/runner writes and decoded stdout are raw evidence, but the recorded original full-trace hash cannot now be recomputed. The judge did not recompute hashes under its read-only tool constraints; the maker independently remeasured source and stage identities after judgment.

The runner refused cache admission. The latest matching refusal rows name absent-input folder mtimes (/etc and /home/mandrake), wall-clock use, and Windows external paths. Those rows have no timestamps, so attribution to this run is circumstantial; independently measured repo inputs are unchanged. The fresh executable PASS is not a cache PASS. See `cache_record_refusal.json`. No cache admission or runner state was forced.

Instrument failures are preserved in `evidence/instrument_failures.md`: initial missing production dependencies; an orchestration Path/string TypeError; and a derived verifier wrongly expecting individual PASS messages where Program.Check prints only suite totals. Actual compile stdout/stderr/receipt and failed script versions remain. No three consecutive genuine nonpasses occurred; successful production runs separate the faults. Expected mutant FAIL is a passing negative-control experiment.

## Workflow result

Actual repository `.claude/hooks/whittle_stop.py` `done_problems` returned `[]`; actual `/home/mandrake/dev/MandrakeWorkflows/whittle/run.py validate(root)` returned 0, with judge and broaden both required. Receipt: `evidence/workflow_after_judge.json`.

The pre-judge check refused two things, both inspected: no judge yet, and a reference identity receipt older than final source. The old receipt/refusal is preserved (`workflow_before_judge.json`); a new actual assembly/reference measurement (`reference_final_identity.json`) replaced its citation in DONE, then the fresh judge was obtained. No mtimes were manipulated. Final evidence cited by DONE is after the final source change.

Agent: Codex Whittle maker; source remains uncommitted for parent. Owner/parent has not accepted or closed the item. Maker token count: UNMEASURED. Compactions: 0. Independent model use follows below, taken from the raw receipts.

| call | actual model | output tokens (incl. thinking) | cost USD | elapsed s |
|---|---|---:|---:|---:|
| broaden | claude-opus-5-5 | 18584 | 1.2145074 | 231.0 |
| judge | claude-opus-5-5 | 25456 | 2.4376430000000004 | 339.4 |
