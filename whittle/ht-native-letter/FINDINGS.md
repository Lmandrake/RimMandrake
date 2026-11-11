# PASSAGE_LETTER_FIX_SAYS_FOREIGN_WHEN_NATIVE — parent report

The text-only working-tree fix is ready for the parent to publish and register at L0. The parent retains all publication, ledger and closing work. Base git SHA: `f5df8f2217d5bc40e89d72738a60f4063d984507`. Nothing was committed, published, marked CLEAN or submitted to the ledger.

Changed paths only:
- `src/RimMandrake/HugeThings/Languages/English/Keyed/RM_TitanicCreatures.xml`: remove the false foreign-biome claim; retain direction and destructive crossing; clarify approach from beyond the map.
- `src/RimMandrake/HugeThings/Languages/English/Keyed/RM_HugeThings.xml`: explain own-biome passage-list precedence and own-roster fallback; preserve warning/damage/largest-tier/off explanations.
- `src/RimMandrake/HugeThings/northstar/titan_events_live.py`: correct only the stale module-docstring phrase to sea/land matching. Executable Python AST is unchanged; C# is unchanged.

Raw final XML, callsite, eligibility, kernel and settings snapshots: `evidence/source/`. Full source hashes and git SHA: `evidence/source_manifest.json`. Actual diff: `evidence/source.diff` (and `evidence/tracked.diff`). Compatibility and four-direction plus warning-hours string-format inspections: `evidence/compatibility.json`. Static player-case traces: `evidence/player_cases.txt`. No bridge, game, other clone, FlowWorks/GSS, art, setting numbers, acceptance bars or frozen task files were touched. No live acceptance is claimed.

Focused check only: `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_hugethings_titanic_lint.py --workers 1`. Final result PASS 1/1, failures/crashes/skips 0, exit 0, no cached PASS. Raw stdout/stderr and receipt with final source hashes: `evidence/selftest.stdout.txt`, `evidence/selftest.stderr.txt`, `evidence/selftest.receipt.json`. The earlier passing run before the broaden-driven wording refinements is preserved under `evidence/pre_broaden_wording/` and is not the final check.

Different-model consultation: one fresh bounded Opus print session, no tools/MCP/history, WHITTLE=0, returned 0. The list-versus-roster case and incoming-versus-resident warning case were acted on as described in `BROADEN.md`. Raw prompt, response, stderr and process receipt: `evidence/broaden_prompt.txt`, `evidence/broaden_raw.json`, `evidence/broaden_stderr.txt`, `evidence/broaden_call.json`.

One fresh independent Codex judge, no model override, stdin exactly JUDGE_PROMPT.md: all three statement bullets true; `JUDGE.md` ends `would show: yes`. Raw events, last output, usage and process receipt: `evidence/judge.events.jsonl`, `evidence/judge.last.txt`, `evidence/judge.spend.json`, `evidence/judge.process.json`. No further judge was run after the valid yes. The judge independently inspected source, XML/arguments, diffs, AST and hashes; it did not rerun the temporary-copy lint harness or claim runtime/UI/gameplay proof.

Actual workflow: imported `/home/mandrake/dev/MandrakeWorkflows-dev/whittle/run.py` and called `validate(cwd)`. Final workflow rc 0, with empty validator stdout/stderr: `evidence/workflow.receipt.json`, `evidence/workflow.stdout.txt`, `evidence/workflow.stderr.txt`. One real refusal found three DONE citations missing the Source directory component. Added directory aliases to the existing reviewed snapshots; unchanged content and target mtimes were verified. Repair receipt: `evidence/evidence_path_repair.json`. The untouched refused validation is retained under `evidence/validation_attempt1/`; DONE, source, judge and snapshot target mtimes were not rewritten to clear it. The earlier inherited failed Windows launch receipts remain untouched as `evidence/launch-win-failed.*`.

Agent: nested Codex builder; own token usage UNMEASURED until the outer runner finishes. Judge usage from its raw envelope: input 411194, output 4956. Opus raw envelope: input 2, cache creation 4410, cache read 649, output 2525; recorded model claude-opus-5-5. Hook refusals: 1, repaired; compactions: 0. Owner acceptance: not claimed; parent publishes, registers L0 and closes.

NEXT: Parent reviews the recorded diff/verdict, publishes the three source changes and Whittle artifacts, then records L0 and closes the item. No remaining builder blocker.
