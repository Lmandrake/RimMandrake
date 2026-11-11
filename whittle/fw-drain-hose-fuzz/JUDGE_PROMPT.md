# Independent Whittle judgment

You are a fresh independent Opus judge. Use only Read, Glob and Grep. Read actual source and raw execution evidence. Make your own assessment from these files. The working directory is neutral and the repository is `/home/mandrake/rm/scratch/BENCH/fw-drain`.

## Frozen statement

- The hose fuzz family proves meaningful successful lay coverage and cannot pass when every generated hose lay is refused.
- Executable production-linked controls demonstrate the old false pass and repaired failure, while legitimate individual refusals and supported single-seed/debug modes remain usable. The relevant FlowWorks selftest passes on final sources.
- Evidence identifies the exact tested source and its limits. The repair preserves shipping behavior and the approved GSS cord appearance.

Read `whittle/fw-drain-hose-fuzz/STATEMENT.md`, `NOTES.md` and `PROMPT.md` for the complete task and boundaries. The parent retains publication, ledger writes and closure. The maker must not mark its code CLEAN.

## Actual source

Read these paths under the repository root.

- `src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs`, especially MakeHose, RunHose, Report and Run.
- `src/RimMandrake/FlowWorks/Source/SelfTest/HoseChecks.cs`, especially Check, RunHoseFuzzOnly and RunHoseSuites.
- `src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs`, especially the CLI parser, --hose-fuzz branch and ordinary RunHoseSuites call.
- `src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj` and `src/RimMandrake/Utils/selftest_flowworks_stock.py`.
- `src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs`, especially Lay, CheckInstall and HoseReelRect.Outward. Read complete production dependencies under `_Shared/SlackGeometry` and `Source/Hose` as needed.
- `whittle/fw-drain-hose-fuzz/evidence/original_HoseFuzz.cs` and `evidence/source_diff.patch`.

## Raw execution evidence

All following relative paths are under `whittle/fw-drain-hose-fuzz/evidence/`.

Read `fast_probe.py`, `run_fast_matrix.py`, `run_broaden_controls.py`, `record_proof.py`, `extract_output.py`, `integrity.py` and `check_proof.py` to understand how the evidence was produced. Read actual stdout and receipts, using summary records to locate additional inputs.

- `fast_original_total/stdout.txt`, `receipt.json`, `HoseMath.diff`, and the saved whole `inputs/src/RimMandrake/FlowWorks/Source/Hose/HoseMath.cs` in that directory.
- `fast_original_total_full/stdout.txt`, `receipt.json`, and the corresponding whole saved kernel.
- `fast_final_repaired_total/stdout.txt`, `receipt.json`, and its saved kernel and HoseFuzz source.
- `fast_final_total_full/stdout.txt` and `receipt.json`.
- `fast_final_refuse_outlet/stdout.txt` and `receipt.json`, and the same two files under `fast_final_refuse_free/`.
- The stdout and receipt pairs under `fast_final_positive_tiny/`, `fast_final_positive_g2/` and `fast_final_positive_g2off/`.
- The stdout and receipt pairs under `fast_final_debug_refusal/`, `fast_final_debug_partial_refusal/`, `fast_final_debug_positive/`, `fast_final_debug_mutant/`, `fast_final_disabled/`, `fast_final_trail_only/` and `fast_final_both_families/`.
- The stdout and receipt pairs under `fast_entry_g2_retry/`, `fast_entry_g2off/`, `fast_entry_refusal/` and `fast_entry_total/`. These use the actual C# project and entry point.
- `control_overlap.json` and the actual timestamps and stage paths in the entry-control and wrapper receipts. Assess their overlapping execution against the measured input identities and raw outputs.
- `entry_g2_console.txt` and `entry_g2_preparation_failure.json`. This earlier failed staging attempt must remain visible.
- `selftest_stdout.txt`, `selftest_stderr.txt`, `selftest_receipt.json`, `csharp_stdout.txt`, `csharp_stderr.txt`, `selftest_output_writes.strace` and `output_extraction.json`. Inspect the actual full-wrapper C# output for the coverage line and suite result.
- `integrity_baseline.json` is the pre-edit source/wrapper subset manifest. `integrity_original.json` is the first full-mod/tool/media snapshot, taken after the final source edit. Use `integrity_before.json`, `integrity_after_test.json`, `integrity_before_review.json`, `stage_identity.json`, `reference_identity.json` and `proof_checks.json` to inspect tested and staged identities. The filenames do not substitute for inspecting their timestamps and hashes.
- The unchanged whole observer trace is external at `/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-fuzz-raw/selftest_writes.strace`, with whole runner logs beside it. Read `output_extraction.json` for its hash and the extraction method. The smaller preserved strace file contains the complete runner/wrapper writes selected by PID.
- `broaden_report.md`, `broaden_raw.json`, `broaden_call.json`, `broaden_extraction.json`, and the parent `BROADEN.md`. The broaden and judge calls are separate fresh processes.

## Questions

Does the coverage check fail in the hose family's existing assertion and diagnostics when all lays refuse, and when just the actual outlet or free mode refuses? Do the witnesses pass the real RunHose invariant checks, including the relevant non-fallback checks? Are case/step/laid summaries clear about sampled and witness coverage?

Does the implementation honor --fuzz-scale, --fuzz-only and legitimate individual refusals? Evaluate the explicit single-seed debug exception against the user's instruction to preserve refusal-only debugging. Does its output state the coverage limitation honestly?

Does the actual wrapper entry point execute the guard? Are raw stdout, the original reproduction, final mutant failure, controls and staged identities sufficient? Did any instrument failure become mislabeled as a mod failure or a PASS? Are shipping/GSS/art changes absent from the measured work?

Read DONE.md after the source and raw evidence, and judge each frozen bullet independently. Identify material flaws and unverified limits. Return your complete assessment as your response text. Finish with exactly `would show: yes` only if you would show this item to the parent with the reported limits. Otherwise finish with `would show: no` and name the required repair or proof. Do not edit files.
