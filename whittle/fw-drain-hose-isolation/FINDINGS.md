# Parent inspection delivery

Item: HOSE_NET_SELFTEST_FIX_VACUOUS_ISOLATION. Work stayed in the parent's clone `/home/mandrake/rm/scratch/BENCH/fw-drain`, with `WHITTLE_DIR=whittle/fw-drain-hose-isolation`. Parent retains publication, ledger and closure.

Agent: Codex Whittle, sole source writer; no other builder. This worker's session token usage is UNMEASURED here; the parent runner may record it. Zero compactions.
Broaden: fresh independent read-only Opus, `claude -p --model opus --effort high`, no history/fork or persistence; Read/Glob/Grep only. Cost $0.6972006. Full usage/model metadata in `evidence/broaden_raw.json` and `evidence/broaden_recovery.json`.
Judge: separate fresh independent read-only Opus call after DONE, same bounded transport. Cost $1.1470554000000002. Full usage/model metadata in `evidence/judge_raw.json` and `evidence/judge_recovery.json`. Unchanged report `JUDGE.md` ends `would show: yes`.
Owner: the supplied frozen statement and task instructions set scope; no later ruling or acceptance was inferred.

## Source and intended rule

Only `src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs` changed: 13 insertions, 6 deletions, all within TankEndpoints g3. Names `cA1`/`cB1` are recognized pipes; there are no adjacency, touch-table or hose shortcuts. The pump must return exactly T with an empty hose route. A second check positively requires two distinct non-null components, shared T, far-only TV, and exactly two components attached to T. The inaccurate old comment about a hose in this fixture was corrected.

The production rule comes from `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs`: RM_NetComponents is in that file, not in a separate RM_LiquidNetComponents.cs. Seeds filters pipe roles; Build attaches tanks without visiting their other conductors. Design `design/RimMandrake/liquid_network_semantics_design_2026-10-11.md` §3.1 states that members attach without conducting. Current kernel/adapter tank adjacency is 8-way under the later ruling; the fixture does not prove adjacency geometry.

Tested base HEAD: `40f1b06c765e73e7f19b03e86cfe8c0bef3d817c`, plus the recorded working-tree patch `evidence/source_diff.patch`.
Final HoseNetChecks SHA256: `5b647005f48bad7972488653809ef1c61d5236e4648d92d0f3de802df7b66954`.
Unchanged production kernel SHA256: `738d600b5db245bb9c1938920bb40c24c6bccd761c5bca15f8c16ef166e1593d`.

## Executed proof

`evidence/fast_probe.py` compiles the whole production kernel and HoseNetChecks in isolated Windows staging with a failure-counting Program.Check reporter. Complete inputs, stdout, stderr, diffs and receipts are preserved under each `evidence/fast_*` directory.

- `fast_reproduce`: before the fix, the real kernel measured a1=None, b1=None and tanks=[]. The old exclusion passed; the repaired near-plus-exclusion predicate failed. C# exit 1, intentional reproduction.
- `fast_final`: exact final source and unchanged whole kernel; all 40 checks pass, C# exit 0.
- `fast_old_fixture`: only cA1/cB1 revert to a1/b1; unchanged production kernel. Both new g3 checks fail and the other 38 pass, C# exit 1.
- `fast_tank_conduction`: exact final HoseNetChecks; isolated kernel mutant makes pipe-tank contacts visit every pipe attached to that tank, recording traversal steps for canonical replay. Both new g3 checks fail and the other 38 pass, C# exit 1. The repository kernel was never mutated.

The only full wrapper invocation was:

`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1`

It passed: PASS 1/1, FAIL 0/1, UNMEASURED 0/1, CRASH 0/1, SKIPPED 0/1, exit 0. Reported test time 469.1 seconds; the observer receipt spans 481.96 seconds. Raw C# reports 1240/1240 main cases, HoseNetChecks 40/40, and 456/456 hose assertions. Individual passing assertions are silent in the full harness; the exact-source fast run prints their names. No unchanged suite was rerun. The three intentional red reproducer/control processes are discriminating controls, not unexpected mod/site/harness failures; unexpected nonpasses measured zero.

Raw full proof: `evidence/selftest_stdout.txt`, `evidence/selftest_stderr.txt`, `evidence/selftest_receipt.json`, `evidence/csharp_stdout.txt`, `evidence/csharp_stderr.txt`. External observer: `evidence/selftest_writes.strace` (complete), `evidence/selftest_output_writes.strace`, `evidence/output_extraction.json`, and `evidence/process_samples.jsonl`. The global runner was not modified.

TMPDIR was `/home/mandrake/.seat-tmp/fw-hose-isolation`. `evidence/reference_remeasurement.json` remeasured installed Assembly-CSharp.dll and the prior Pawn_NeedsTracker reference against the preserved prior provenance; both matched. The reference and assembly were rechecked after the run. Windows RIMWORLD_DECOMPILED and WSLENV are recorded in the run receipt. No replacement reference was necessary.

Full tracked FlowWorks/GSS files (including media), shared sources, Utils inputs and build props/targets were hashed in `evidence/integrity_original.json`, `integrity_before.json`, `integrity_after_test.json`, `integrity_before_review.json`, and `integrity_after_review.json`. Only HoseNetChecks changed from the original snapshot. Every stageable input matches; normal media/bin/obj exclusions are explicitly listed. The selftest DLL has a build-window mtime. Before/after review source, staged input and binary hashes agree in `evidence/post_review_checks.json`. `evidence/proof_checks.json` verifies actual raw failure names/counts, identities and run results.

The cache-recording refusal remains visible. `evidence/cache_record_refusal.json` preserves the latest matching raw refusal row and the pre-existing malformed line's location. External .NET paths, wall-clock reads and absent-input folder changes prevent cache recording even though the actual source manifests are stable. This is a cacheability bookkeeping limitation; no cache acceptance is claimed.

## Review and workflow

`BROADEN.md` records the acted-on suggestions: exact near-tank result with empty route, explicit both-component existence/isolation, and a focused whole-kernel mutant that records canonical replay steps. The unchanged broaden report, complete JSON and receipts remain under evidence.

`JUDGE_PROMPT.md` supplied the frozen bullets, actual source/raw proof paths and questions, without builder conclusions. The judge found every bullet true and no material defect. Complete JSON and report-extraction hash receipt are preserved. Its phrase "both directions" concerns near reachability plus far exclusion; this fixture does not add a second pump-origin traversal.

The actual repository `.claude/hooks/whittle_stop.py` done_problems and `/home/mandrake/dev/MandrakeWorkflows/whittle/run.py` validate(root) ran with judge and broaden required. `evidence/workflow_initial.json` preserves the missing-DONE refusal; `workflow_before_judge.json` preserves the missing-judge refusal. Both were inspected and resolved by real proof and a fresh judge. `workflow_reviewed.json` reports done_problems=[] and validator exit 0. The final post-FINDINGS invocation is saved as `evidence/workflow_final.json`. No mtimes were manipulated. All DONE-cited evidence postdates the final source change.

## Limits and boundaries

This is offline fake-graph endpoint coverage using two single-cell runs. The mutant targets pipe-tank-pipe conduction; existing TU checks cover other endpoint behavior. Negative controls use the fast reporter, not the full wrapper. No adapter geometry, live transfer/game behavior, fresh visuals, separate GSS suite or general end-to-end acceptance is claimed. Shipping behavior and approved GSS cord appearance are preserved by unchanged file hashes, not visually re-approved.

No commit, publication, ledger write, closure, bridge lease, game launch, deployment, ModsConfig change, art edit or shipping/GSS source change was made. No shipping DLL rebuild was requested; the wrapper built its selftest. Code-review CLEAN status remains unassigned by this worker. Earlier Whittle evidence was preserved.
