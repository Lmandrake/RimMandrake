You are a fresh independent Opus judge for this one Codex Whittle item. You did not build it and have no history or fork. Read-only Read/Glob/Grep only. Your only brief is this prompt. Inspect actual source and raw proof directly. Evaluate each frozen bullet and report any material failure, missing discriminating control or misleading claim. Return a complete report in your response. Do not edit files, run suites or contact anyone.

Repository root is /home/mandrake/rm/scratch/BENCH/fw-drain. Resolve the relative paths below from that root.

## Frozen statement

# Make the pipe-span callback regression guard useful

- The pipe-span selftest rejects the retired counter-only OnSpansChanged callback even after source whitespace is collapsed, and accepts the current callback that invalidates the liquid net when the span set changes.
- Meaningful negative controls demonstrate the repaired guard can fail; the existing production net-bump, listener registration and join-order checks remain effective, and the relevant FlowWorks selftest passes on the final sources.
- Evidence identifies the exact tested source and reconciles the later triage note with the actual callback contract. Shipping behavior and the approved GSS cord appearance are preserved.

## Actual source to read

- src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs
- src/RimMandrake/FlowWorks/Source/SelfTest/RiverSwitchFlipChecks.cs, especially Src and Flat
- src/RimMandrake/FlowWorks/Source/SelfTest/DrawbridgeChecks.cs, especially Body
- src/RimMandrake/FlowWorks/Source/SelfTest/TransferChecks.cs, especially StripComments
- src/RimMandrake/FlowWorks/Source/Machinery/RM_PipePoles.cs, especially OnSpansChanged, registration and JoinCells
- src/RimMandrake/FlowWorks/Source/Machinery/RM_PipeSpanNetMath.cs
- src/RimMandrake/Utils/selftest_flowworks_stock.py and run_selftests.py as needed for interpreting captured output

## Raw proof and provenance to read

- whittle/fw-drain-pipe-span/evidence/csharp_stdout.txt and csharp_stderr.txt
- whittle/fw-drain-pipe-span/evidence/selftest_stdout.txt and selftest_stderr.txt
- whittle/fw-drain-pipe-span/evidence/selftest_receipt.json
- whittle/fw-drain-pipe-span/evidence/selftest_output_writes.strace and output_extraction.json. The full original observer file remains in selftest_writes.strace. Inspect raw write records as needed alongside decoded stdout.
- whittle/fw-drain-pipe-span/evidence/integrity_before.json, post_proof_integrity.json, pre_judge_integrity.json, stage_identity.json and BUILD_SOURCE.json
- whittle/fw-drain-pipe-span/evidence/reference_identity.json and reference_windows_readback.json
- whittle/fw-drain-pipe-span/evidence/source_diff.patch
- whittle/fw-drain-pipe-span/evidence/original_guard_reproduction.json, item.txt and history.txt
- whittle/fw-drain-pipe-span/NOTES.md

## Questions

1. Does the actual guard accept the real callback and reject the retired counter-only callback after the exact whitespace normalizer called by Src? Are mutant replacements required to change the real source, and do positive controls discriminate genuine failures from a predicate that always rejects?
2. Do the controls cover expression-body borrowing of adjacent braces, moved bump code, missing/renamed callbacks, whitespace variation, comment spoofing and unrelated counter text? Is the use of existing helpers proportionate? Identify remaining source-shape limitations and decide whether they materially defeat this narrow item.
3. Are the production net-bump, GSS listener-registration and join-order checks retained, and are the linked production net/edge math cases still executed?
4. What do the actual raw stdout and wrapper receipt show? Compare executed case names to actual source. Are there any failures, crashes, skipped or UNMEASURED checks hidden by a wrapper PASS? Do the recorded source/stage/reference identities support the exact tested sources?
5. Compare the original finding and history in item.txt/history.txt with actual production code. Does the later triage sentence describe the proper guard intent? The owner's quoted words are in the raw item. Derive the reconciliation yourself.
6. Is the change confined to the item, and does its evidence support the frozen bullets at offline scope? State any remaining gap for the parent, who alone handles publication, ledger and closure.

Read actual source and raw evidence before deciding. Builder narratives in DONE.md, BROADEN.md, FINDINGS.md and verification.json are not your proof. Cite the actual source lines and raw evidence values you used. End with exactly one final line, `would show: yes` or `would show: no`, according to your independent verdict.
