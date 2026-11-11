# PIPE_SPAN_SELFTEST_FIX_COLLAPSED_WHITESPACE

Codex completed the offline instrument repair in `/home/mandrake/rm/scratch/BENCH/fw-drain`. Parent controls publication, ledger updates and closure. The tested working tree is based on `b24bb1cae88888b6cf0c6c02c91e40152bca5795`.

## Source changes

- `src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs:60` replaces the vacuous counter-only substring assertion with a callback-scoped Changed/NetBumps/Bump check. Existing comment stripping runs before whitespace collapse. The declaration must include its own opening brace, and the existing DrawbridgeChecks.Body helper bounds the nested body. The positive Changed condition is required.
- `src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs:199` exercises five counter-only variants after the same whitespace normalizer called by Src. Every mutant must change the real source. Positive controls accept the current callback raw, normalized and with CRLF/tab re-indentation.
- `src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs:225` exercises nine further mutations covering absent/renamed callbacks, bump work moved into a sibling method, expression-body brace borrowing, commented-out work, deleted bump operations, unconditional work and negated Changed. Added comment, method and string decoys preserve acceptance.
- `src/RimMandrake/FlowWorks/Source/SelfTest/RiverSwitchFlipChecks.cs:47` factors the existing whitespace Regex.Replace into Flat. Src and normalized mutants share that implementation.

The tracked source diff contains these two SelfTest files. The production net/edge math, registration and join-order checks execute in the retained pipe-span cases. `evidence/source_diff.patch` records the exact patch. `DONE.md` maps evidence to every frozen bullet.

## Intent reconciliation for the parent’s ledger note

The original finding FE_cs_selftests_2.4 identifies a rejection guard that always accepts because Src removes the searched newline/tab characters. Its assertion message says “the callback is no longer only a counter”. History records the retired expression-bodied counter in `1e681b935e` and the changed-set invalidation callback introduced by `5f54729885`. The current production callback counts calls and bumps the liquid net only when the per-map span signature changes. RM_PipeSpanNetMath.Changed also admits the first observed set and rejects equal repeated signatures.

The agent-drafted 2026-10-29 phrase “fails when the callback body gains a statement” inverts that contract. The attached owner quote requests assessment and routing of ancient queue items. It supplies no callback-semantics instruction. The repair therefore rejects loss of the changed-set bump, including the retired counter-only callback, and accepts the current callback. Raw item text and source history are preserved in `evidence/item.txt` and `evidence/history.txt`. The detailed reconciliation is in `evidence/scope_reconciliation.md` and is independently derived in `JUDGE.md`.

## Executed proof

The single requested wrapper ran after the final source edit.

```sh
python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1
```

- Actual C# stdout reports 1240/1240 main cases, 188/188 hose checks and 455/455 hose assertions. All eight PipeSpan_P3 cases pass, including both new control cases and all retained net/edge/signature/wiring cases.
- The wrapper reports PASS 1/1, FAIL 0/1, UNMEASURED 0/1, CRASH 0/1 and SKIPPED 0/1. The outer observer elapsed time is 496.739 seconds. There were zero genuine suite nonpasses.
- `evidence/selftest_receipt.json`, `selftest_stdout.txt` and `selftest_stderr.txt` preserve the actual invocation and wrapper result. `csharp_stdout.txt` and `csharp_stderr.txt` contain the decoded wrapper writes. The external strace observer’s complete original file, selected raw writes, sampled PIDs and extraction hashes are retained in `selftest_writes.strace`, `selftest_output_writes.strace`, `process_samples.jsonl` and `output_extraction.json`.
- `evidence/original_guard_reproduction.json` preserves the pre-change reproduction showing that the original predicate accepted a normalized counter-only callback. The final executable controls reject those mutants. The judge accepted this in-test red-first demonstration.

## Identity and environment

`evidence/integrity_before.json` and the post-run/review manifests cover 753 inputs, including all 497 FlowWorks Source files, 107 GSS Source files, 27 shared files, relevant Defs/About files, the primary wrapper/staging inputs and the engine reference. All measured input hashes match before and after the test and review. `evidence/stage_identity.json` and `stage_identity_verified.json` verify the staged bytes and test artifacts. The staged callback and guard source have LF line endings, with zero CRLF sequences.

Final SHA-256 values include the following.

| File | SHA-256 |
|---|---|
| PipeSpanNetChecks.cs | `66e32015a7525be952612bba434e1e1551bcad8a41ccc2c1f31e18754964ef66` |
| RiverSwitchFlipChecks.cs | `c502478a4ba22531c010c353444fce9bf39935e4cb602802054327ef9d38855b` |
| RM_PipePoles.cs | `df06e2bc3db66e65f661fce4480424b9860db1a76858ca7f56ab31e9135c7132` |
| RM_PipeSpanNetMath.cs | `e0d02bdb5be7a61a3d42640b6e17978cf1b543f23f91fece07fe48ab521e7c01` |

The installed Assembly-CSharp.dll and existing Pawn_NeedsTracker reference were remeasured against the prior provenance. Both hashes match. The assembly hash is `5cf1b5be399d5b1c9c56ca72c9d35b4ecf307feacf5859d04ac5a1aa5926356a`. The reference hash is `fa58868173d778dd1f0f596eb062c6c14af87f74293cf5f171aab08269a394d2`. Windows readback agrees. The run used ext4 TMPDIR `/home/mandrake/.seat-tmp/fw-pipe-span`, a Windows RIMWORLD_DECOMPILED path and WSLENV export, as recorded in the receipt.

Four additional cache/evidence helper modules are checked in `evidence/supplemental_wrapper_identity.json`. Their baseline bytes are derived after the test from the recorded immutable HEAD and clean pre-run status for those paths. Those bytes match current and staged hashes. `final_readback.json` rechecks the source inputs, supplemental modules, exact judge extraction and git diff whitespace check.

## Refusals and recovered instrument faults

- The initial observer setup attempted to hash failreport.py at the wrong location and exited before launching the wrapper. The actual traceback and receipt are preserved in `evidence/proof_setup_failure_stderr.txt` and `proof_setup_failure.json`. Resolving the pulse/ and telemetry/ paths repaired that observer setup.
- A copied validator initially retained the previous item’s WHITTLE_DIR. Its stale-evidence refusal is preserved in `evidence/workflow_initial.json`. That call exercised the prior item’s ignored hook bookkeeping. Historical statement, notes, reviews and proof files have no tracked diff. The corrected invocation is preserved in `workflow_initial_corrected.json` and reports the expected missing DONE. `workflow_before_judge.json` reports the expected missing fresh judge.
- The wrapper refused cache admission. Its raw refusal names absent-input folder changes under `/etc` and `/home/mandrake`, a clock read and external Windows dotnet paths. `evidence/cache_record_refusal.json` preserves the newest matching raw refusal row and an existing malformed-line location. The executed C# result and independently measured input identities provide this item’s proof. The global runner and cache policy retain their existing implementations.

## Independent review and workflow

Fresh read-only Opus broaden and judge calls used `claude -p --model opus --effort high`, neutral ext4 working directories, Read/Glob/Grep-only tools, empty settings/MCP configuration and separate session IDs. Complete JSON and unchanged extracted reports have transport and extraction receipts. `BROADEN.md` records the suggestions acted on.

The judge read actual source and raw evidence and returned the final line `would show: yes`. `JUDGE.md` is an unchanged UTF-8 extraction of the complete result string. `evidence/judge_recovery.json` records equality and matching hashes. Both reviews report zero permission denials.

| Review | Input tokens | Cache creation tokens | Cache read tokens | Output tokens | Reported cost |
|---|---|---|---|---|---|
| Broaden, claude-opus-5-5 | 14 | 42628 | 138749 | 9975 | $0.5683298 |
| Judge, claude-opus-5-5 | 56 | 139188 | 2693282 | 17411 | $2.0006044 |

At worker handoff, maker token usage was unavailable inside the worker. The completed parent runner receipt measures 7,016,790 input and 38,887 output tokens, state done and returncode 0; it is preserved in `evidence/runner_spend.json`. The worker had zero compactions. Parent holds the owner-facing acceptance and ledger decisions.

The actual `.claude/hooks/whittle_stop.py` done_problems call returned an empty list, and `/home/mandrake/dev/MandrakeWorkflows/whittle/run.py` validate(root) returned 0 with judge and broaden required. `evidence/workflow_after_judge.json` records that result. `evidence/workflow_final.json` records the final invocation after this findings file.

## Limits

This evidence covers the offline source guard and linked production math. Runtime GSS callback delivery, rendered cord appearance and live liquid transport require their own acceptance evidence. The tracked diff and source hashes establish the preserved shipping implementation for this repair.

The source guard pins the current internal signature, parameter names and braced Changed block. Existing brace matching treats string-literal braces as code, and source-shape matching can accept an unreachable correct-looking block. Renames or equivalent helper refactors can produce a false alarm. These bounds are recorded by the independent judge.

The judge also noted that the positive whitespace rewrite lacks an in-test inequality assertion. `evidence/final_readback.json` confirms that this exact positive rewrite changes the callback text and changes only whitespace. Each negative mutant already has the in-test inequality assertion. The final source and the single executed suite were retained through review.
