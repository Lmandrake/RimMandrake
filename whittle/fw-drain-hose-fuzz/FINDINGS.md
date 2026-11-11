# Findings

## Item and deliverable

HOSE_FUZZ_HARDEN_ZERO_LAID_PASSES was handled by the Codex maker in `/home/mandrake/rm/scratch/BENCH/fw-drain`. The evidence directory is `/home/mandrake/rm/scratch/BENCH/fw-drain/whittle/fw-drain-hose-fuzz/evidence`.

The sole source edit is `src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs`, starting at line 485. Final SHA256 is `577c4429c424506d94cadabb8d536d0a801f446905d656848fd0a3fb5019b788`. The saved original hashes to `62b6fff3cc26d89d509b1ab81d172c51e9db1816631523525174f9efc706ff53`.

Positive-scale hose-family runs without `--fuzz-seed` require two deterministic seed-2 witnesses through the actual RunHose checks. They exercise a real nozzled outlet and a free lay, require non-fallback success, and feed failures into the existing family assertion and grouped diagnostics. Sample counts stay separate from witness coverage. The explicit single-seed debugger permits refusal-only PASS and labels successful-lay coverage optional. This debug exception was a maker decision to preserve the requested refusal-only debugging workflow.

Parent retains publication, ledger updates, closure and source-review status. This handoff contains uncommitted source and evidence.

## Executable proof

All test kernels are complete actual production files selected by the SelfTest project. The fast harness stages byte copies and isolated mutations of those files. The actual-entry controls stage the real complete C# project, including its original generated-source target. Their receipts retain source hashes, staged hashes, commands, return codes and raw stdout/stderr.

| Control | Observation | Raw evidence under evidence/ |
|---|---|---|
| Original total refusal, full scale | False PASS, 2798 cases, 8200 steps, zero lays | `fast_original_total_full/stdout.txt`, `receipt.json` |
| Repaired identical total mutant, full scale | Family FAIL with two coverage faults | `fast_final_total_full/stdout.txt`, `receipt.json` |
| Tiny-scale old PASS and final FAIL | The same whole mutated HoseMath is byte-identical | `fast_original_total/`, `fast_final_repaired_total/` |
| Outlet-only refusal | Family FAIL, one outlet coverage fault | `fast_final_refuse_outlet/` |
| Free-only refusal | Family FAIL, one free coverage fault | `fast_final_refuse_free/` |
| Production tiny scale, g2 and g2off | PASS, 2/2 witnesses | `fast_final_positive_tiny/`, `fast_final_positive_g2/`, `fast_final_positive_g2off/` |
| Refusal-only seed 18 and partial-refusal seed 7 | PASS with explicit debug coverage limit | `fast_final_debug_refusal/`, `fast_final_debug_partial_refusal/` |
| Positive seed and total-refusal debug mutant | Debug behavior recorded explicitly | `fast_final_debug_positive/`, `fast_final_debug_mutant/` |
| Scale zero, trail-only and both families | Existing selection/skip behavior preserved | `fast_final_disabled/`, `fast_final_trail_only/`, `fast_final_both_families/` |
| Actual C# CLI | g2, g2off and refusal debug pass, total refusal fails | `fast_entry_g2_retry/`, `fast_entry_g2off/`, `fast_entry_refusal/`, `fast_entry_total/` |

`proof_checks.json` verifies 20 final or reproduction controls and their saved and external staged input identities. Earlier prototype controls remain in their original directories.

The sole full-wrapper invocation was `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1`. Its wrapper duration was 504.3 seconds, outer runner wall time 505.8 seconds, and observer receipt elapsed 519.733 seconds. It returned zero and reported PASS 1/1, FAIL 0/1, UNMEASURED 0/1, CRASH 0/1 and SKIPPED 0/1. Actual captured C# stdout includes 1240/1240 passed, hose 457/457 assertions, HoseFuzz 4/4, 2409 random lays and 2/2 successful checked witnesses. See `selftest_stdout.txt`, `selftest_receipt.json` and `csharp_stdout.txt`.

The complete original observer trace and runner logs remain under `/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-fuzz-raw/`, equivalent to `D:\ClaudeWork\rimmandrake\codex_wsl\fw-drain\hose-fuzz-raw\`. The whole trace SHA256 is `1afe04c97a02cdd801a9d22877c7b5fa30b21ba4503c662a1e5c9093446c80c4`. `output_extraction.json` records its identity and the PID-based decoding into `csharp_stdout.txt`, `csharp_stderr.txt` and `selftest_output_writes.strace`.

## Identities, failures and limitations

`integrity_baseline.json` was captured before the edit and covers the relevant source/wrapper subset. The first full mod/tool/media snapshot, named `integrity_original.json`, was captured after the final edit. Subsequent test and review snapshots cover 6009 files. The staged source/tool comparison covers 3968 files and records 2040 deliberate media/build exclusions. The engine-reference file travels through RIMWORLD_DECOMPILED. `stage_identity.json` and the review snapshots retain stage paths, build provenance and artifact identities. The tracked source/tool/art diff against HEAD contains only HoseFuzz.cs.

The installed Assembly-CSharp.dll was remeasured against `whittle/fw-drain-selftest-resume/evidence/reference_provenance.json` before reuse. Its hash is `5cf1b5be399d5b1c9c56ca72c9d35b4ecf307feacf5859d04ac5a1aa5926356a`. The engine-reference hash is `fa58868173d778dd1f0f596eb062c6c14af87f74293cf5f171aab08269a394d2`. The Windows reference path and WSLENV are recorded in the wrapper receipt. The proof checker remeasured both after the test.

One staging attempt failed before any C# compilation. It treated the generated ReleaseRect.g.cs Compile entry as a literal static path. The exact console, partial inputs and diagnosis remain in `entry_g2_console.txt`, `fast_entry_g2/` and `entry_g2_preparation_failure.json`. The retry used a new label and the actual project generation target. This was an instrument failure. Expected mutant failures were checked against explicit expected outcomes. The three-genuine-nonpass diagnosis threshold was never reached.

Known-results cache recording was refused because of changed absent-input parent-directory mtimes, a wall-clock read and Windows external inputs. `cache_record_refusal.json` preserves the latest matching raw refusal. The actual wrapper PASS and stable source hashes are separate observations. The global runner received no edits.

Three focused actual-entry builds overlapped the authorized wrapper interval in separate scratch stages. They bypassed its dotnet lock. `control_overlap.json` preserves exact intervals and stage paths. The full wrapper output and staged identities establish its production result. DONE.md discloses the concurrent build load. The source stayed fixed throughout.

The guard provides one deterministic positive seed in each actual lay mode. It establishes no minimum random-sample success rate. A future legitimate planner or generator change can require selecting another positive seed. Explicit single-seed debugging can pass even under a total-refusal mutant, with its coverage limit printed. Witness failures enter the family failure count while the case count describes the sample, so tiny runs can show more failures than sampled cases. Grouped coverage diagnostics identify those witness faults. The ShippedMatrixProbe VV_HOSE entry was reviewed in source and was outside the executed controls. The original false-pass reproduction used the lightweight Program.Check adapter. Actual Program.cs controls independently exercised the repaired failure. This is an offline kernel/selftest proof. Live gameplay and fresh visual acceptance are outside its scope. Shipping, GSS and approved media identity are measured by the retained hashes.

## Independent review and workflow

Fresh read-only Opus broaden and judge calls used `claude -p --model opus --effort high`, neutral ext4 working directories, empty MCP configuration, Read/Glob/Grep-only tools, and independent print processes without history or session persistence. Complete JSON and transport/extraction receipts are preserved. BROADEN.md records suggestions and actions. The first judge returned `would show: yes` and identified the concurrent-build disclosure gap. Its complete response remains unchanged in `evidence/JUDGE_first.md`, with raw JSON in `evidence/judge_raw.json`.

The second fresh judge also returned `would show: yes` after DONE disclosed the overlap. Its complete JSON is `evidence/judge_final_raw.json`, its transport receipt is `evidence/judge_final_call.json`, and its unchanged extracted response is JUDGE.md, bound by `evidence/judge_final_extraction.json`.

The actual `.claude/hooks/whittle_stop.py` done_problems check returned an empty list and `/home/mandrake/dev/MandrakeWorkflows/whittle/run.py validate(root)` returned zero with judge and broaden required. `evidence/workflow_after_judge.json` preserves that result. Initial workflow refusals required the missing per-bullet claim and judge. The pre-judge refusal required the pending fresh judge. Those receipts remain in `evidence/workflow_initial.json` and `evidence/workflow_before_judge.json`. Every refusal was inspected.

`evidence/integrity_after_final_review.json` and `evidence/final_checks.json` reverify source, stage, media and wrapper identity after the final review. They also remeasure the installed assembly and engine reference, verify both unchanged judge extractions and the broaden extraction, and confirm retention of the whole external trace and runner logs. All final checks passed. The final workflow check is also retained in `evidence/workflow_final.json`.

Maker token usage is UNMEASURED by this interface. Opus usage and costs are preserved in each raw JSON modelUsage object. Compactions were zero. The parent drafted this unit’s frozen statement under the user’s drain instruction and retained publication/closure. No subsequent owner ruling was received.

Parent measured the completed native Codex runner usage in evidence/runner_spend.json: {'input_tokens': 10082496, 'output_tokens': 53449}. The runner and full orchestrator exited zero.
