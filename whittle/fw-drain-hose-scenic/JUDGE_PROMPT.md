You are a fresh independent read-only Opus judge. You did not make this work and have no conversation history. Use only Read/Glob/Grep. Root: /home/mandrake/rm/scratch/BENCH/fw-drain. This is a Codex Whittle item, HOSE_SCENIC_SELFTEST_FIX_NEVER_CROSSES. Do not write files, mutate source, invoke tools beyond reading, mark code CLEAN, publish, or close anything. Your returned result will be saved unchanged as JUDGE.md with the complete JSON and extraction receipt.

Frozen statement (also read the actual STATEMENT.md and NOTES.md under whittle/fw-drain-hose-scenic):

- The ScenicRoute forced-lay fixture requires traversing costed building cells and asserts a successful hose lay across them.
- Executable controls show the original fixture misses a building-as-block regression and the repaired fixture catches it. The relevant production-linked FlowWorks selftest passes on final sources.
- Evidence identifies the exact tested source and its limits. The repair preserves shipping behavior and the approved GSS cord appearance.

Read actual source and raw evidence, not builder conclusions in DONE.md, BROADEN.md, FINDINGS.md, or past judgments. All paths below are relative to root. You may inspect other relevant production files as needed.

Actual source:
- src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs (HoseGptFix.ScenicRoute and surrounding checks)
- src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs (Lay, lead-out, Clear, relevant pose/cost rules, HoseReelRect geometry)
- src/RimMandrake/_Shared/SlackGeometry/CordWorld.cs and CordPlanner.cs (walkability, routing, costs, bounds)
- src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj
- src/RimMandrake/Utils/selftest_flowworks_stock.py and run_selftests.py

Raw evidence under whittle/fw-drain-hose-scenic/evidence/:
- source_diff.patch
- fast_probe_initial.py, probe_initial_stdout.txt, probe_initial_stderr.txt, probe_initial_receipt.json
- fast_probe.py, probe_program.cs.txt, probe_manifest.json, probe_baseline_stdout.txt, probe_baseline_receipt.json
- exact_mutant.py; original_scenic_exact.cs.txt and final_scenic_exact.cs.txt; exact_program.cs.txt and mutant_program.cs.txt
- building_block_mutant.patch; exact_stdout.txt, exact_stderr.txt, exact_receipt.json; mutant_stdout.txt, mutant_stderr.txt, mutant_receipt.json
- pre_broaden/ contains the earlier world-walkability mutant and its raw results, plus a failed Python orchestration script; instrument_failures.md identifies those failures and distinguishes captured output from a transcribed terminal error
- selftest_running.json, selftest_receipt.json, selftest_stdout.txt, selftest_stderr.txt
- csharp_stdout.txt and csharp_stderr.txt: real wrapper writes decoded from external strace. Search scenic lines and final suite counts; do not infer a pass from a Python exit code alone.
- selftest_output_writes.strace, output_extraction.json, extract_output.py, record_proof.py, process_samples.jsonl (external observer and actual runner/wrapper identities)
- integrity_before.json, post_proof_integrity.json, pre_judge_integrity.json (full source and wrapper input hashes)
- stage_after_proof.json and stage_before_judge.json (actual Windows staging identities)
- reference_remeasurement.json, reference_final_identity.json, reference_windows_readback.json; prior whittle/fw-drain-selftest-resume/evidence/reference_provenance.json and its reference/RimWorld/Pawn_NeedsTracker.cs (reference and installed engine identity)
- verification.json and verify_proof.py are derived cross-checks; check their underlying raw inputs independently.

Questions to answer independently:
1. For the current production Mouth/Outward/lead-out and CordWorld bounds, is the new crossing actually unavoidable? Can mere nozzle contact, a boundary graze, an alternate corridor, a failed/incomplete lay, or a non-costed point satisfy its success assertion?
2. Are the old and final fixtures linked to actual source and actual production C# kernels? Does the final staged mutant change only the intended cost-vs-block rule? Does it preserve nozzle origin, collision geometry, start/goal exemptions, and unrelated planner rules? Is the observed final failure exactly the crossing failure, while the old assertion still passes?
3. Does the real authorized wrapper run prove final production-linked selftests pass with actual C# stdout and staged source identity? Are there hidden failures, reference mismatch, stale evidence, source changes after proof, or evidence fabricated by extraction?
4. Are detour, uncosted, carried, shortcut and wiring checks preserved? Is the repair test-only with shipping/GSS/art behavior unchanged? State any limits or defects you find; do not infer live validation.

Give a verdict for each frozen bullet with exact source/raw evidence references, any material limitations, and actionable defects if present. End with exactly 'would show: yes' only if you independently would show this item as complete to its parent; otherwise end 'would show: no'. Do not treat the requested wording as a predetermined answer.
