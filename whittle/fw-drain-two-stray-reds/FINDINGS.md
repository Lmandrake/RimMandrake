# FLOWWORKS_SELFTEST_FIX_TWO_STRAY_REDS — verification blocked

Changed repository paths: only `whittle/fw-drain-two-stray-reds/` (verification documents, JUDGE_PROMPT path/tool clarification, evidence and recording scripts). Production, tests, other completed Whittle units, ledger, bridge/game/deploy, ModsConfig and art were not changed. No commit, publication, closure or CLEAN marking was performed.

Exact tested and final HEAD: `14b5a573688a293511f8a64ea2cac4d90410ff2c`. The pre-existing two-file test repair `4e9da327df7ba0a60b50837e200efb711fcbfef1` is unchanged here and is an ancestor of HEAD and published main. A post-review fetch confirmed ancestry against `origin/main` at `662e8278ce19d0d9b30bf599fd8d38cfdae4d494`; HEAD did not move (`evidence/publication_followup.json`). The exact repair diff and earlier production changes are in `evidence/git_provenance.json` and `evidence/production_history.json`.

One actual execution of the requested relevant runner, with no cache answer or repeat: **both named cases PASS; main cases 1233/1238; hose assertions 455/455; runner exit 1, RED**. The wrapper took 593.5 s; the enclosing process receipt took 608.7 s. Five other failures are named with exact details in `evidence/verification.json` and complete raw output in `evidence/csharp_stdout.txt`. `BLOCKED.md` names the next source pairings to investigate. Five subsystems require further triage, so no unrelated guard was rewritten to obtain green.

Build identity: the authorized wrapper staged this clone and built only the standalone SelfTest project. `evidence/BUILD_SOURCE.json` records clean src snapshots at the tested HEAD. All 497 tracked FlowWorks Source files match the stage, and all 253 explicit Compile inputs match. DLL/runtime hashes are retained in `evidence/stage_artifacts.json`. Production math is directly compiled; the shipping FlowWorks DLL was not rebuilt or deployed. The external strace observer captured raw wrapper output without test/runner injection. Its exact kept writes and decoding receipt remain; redundant source-transfer syscall dumps were omitted to keep evidence compact.

Original Codex verifier's DONE assessment (superseded by parent review below): the named checks retain the original capacity sequence and inspected three resizing sites, and the riser caller plus shared westward swap; full-suite-green is false. Fresh independent Opus judgment: the published repair fixes both stale failures without weakening the intended checks, but **would show: no**. It also qualifies bullet 1: the global regex count covers three unit-times-beds resizing occurrences, not every formation/migration capacity assignment or method identity. This qualification remains explicit in BLOCKED.md; the frozen statement was not rewritten or treated as independently approved.

The judge received only JUDGE_PROMPT.md in a fresh no-history/no-MCP/no-project-settings CLI process, with Read/Glob/Grep and Write restricted to JUDGE.md, no shell/live access, 360 s bound; it completed in 147.8 s. CLI Write was denied. `evidence/judge_raw.json` preserves that refusal and complete report; `evidence/judge_recovery.json` proves exact denied-payload recovery, with no new reviewer. JUDGE.md remains the judge's words, including its uncertainties. Post-review integrity and remote ancestry checks address the hash/publication uncertainties separately, without rewriting that report.

Broaden: one real fresh Opus tools-disabled call, completed in 23.6 s; audited production history and staged/full-run identity as suggested. Prompt/result/process receipts and actions are in BROADEN.md and `evidence/broaden_*`. No mutation test was added. Both model calls resolved to `claude-opus-5-5`.

Actual final workflow checks set WHITTLE_DIR and explicitly require judge+broaden: `done_problems` refuses the false green-suite claim and negative judge; full `whittle/run.py validate(root)` returns **2 (BLOCKED)**. `evidence/workflow_initial.json`, `workflow_before_judge.json`, and `workflow_final.json` preserve the real refusal progression. No mtimes were manufactured. The result-cache refusal is also preserved: clock/external SDK inputs and changing absent-input folders/__pycache__ prevented caching; the summary names the test receiving that refusal, not a demonstrated source edit. No cache answered; hashes below agree.

Source/test integrity: all 501 recorded files have identical SHA-256 values before proof, after proof and after review; canonical manifest hash `daa90ebaa4bd465bc28cc55af4534a5d25f7e3069ffb3825af11255d4e5c1dc9`. Full before/after maps are in `evidence/integrity_before.json` and `evidence/selftest_receipt.json`; final comparison is `evidence/final_integrity.json`.

| Source/test path | SHA-256, unchanged throughout |
| --- | --- |
| `FlowWorks/Source/RM_LiquidStock.cs` | `8bf7480c35d837b5a2d01d15e86530bdbe54189d8da1fb71b9ae4458670e7f79` |
| `FlowWorks/Source/RM_BedMath.cs` | `6be6956039f5c672ee17838409234d5b314bb3c952c6ac1d834fed66617701e6` |
| `FlowWorks/Source/Machinery/RM_LiquidJoins.cs` | `38ffadae34b9bf27e1c96912bc0e2d25a3f833b7ef22e2043888e6fbd83c54ea` |
| `FlowWorks/Source/Machinery/LiquidJoinRule.cs` | `2d04b40cf202fb25463a834f6f888685217b5afc29d1384a36b53fc233dde3a9` |
| `FlowWorks/Source/SelfTest/DeepBedChecks.cs` | `c395a7200dc4478e11e1ab6d2fcf155611b4e65043abe4c8c5f4d81147ee1871` |
| `FlowWorks/Source/SelfTest/ReelRiserShadowChecks.cs` | `b0dc180e8d23dad02ac80c722e84ce394fa18fb8b9145d9686928a48efb942bd` |
| `FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj` | `ef4fde6dcb5dc65bc83a6ea223f9f74fcdfcd11df0f03fd519776166cfbec26b` |
| `Utils/selftest_flowworks_stock.py` | `1c4bc152045d3af048e3cb9588ac8048aae461d466605a7f5aa8f80793908a8e` |
| `Utils/run_selftests.py` | `651f5e82fbed5f98b812f60451f515aaf118759514209110236bb01e709ebf90` |

Limits: source-wiring guards plus real production-linked math, not live rendering, in-game pond operations, exhaustive order coverage, deployment or full-mod integration proof. No new production defect was established for the two reported failures; the five further failures remain unaccepted work. Parent alone publishes, records ledger and decides closure/scope.

Owner authority: the task authorized verification; the parent drafted the specific statement, without separate owner approval of its wording; no later owner acceptance. Compactions: 0. Codex token usage is not exposed here; both Opus calls' exact usage/cost fields remain in their raw JSON receipts.

Parent review after runner exit 2: the independent rejection stands. The first DONE bullet is now false because its all-sizing-sites wording is not supported; the original claim is preserved. The second named test passes with source-guard limits, and the full suite is RED. This is a published diagnostic unit, not an accepted item. No extra test or judge run is warranted by this correction to an already rejected claim. Source hashes and exact raw independent judge payload were checked again by the parent before publication.
