## spec

Found by Codex reviewing RIMMANDRAKE_SPLIT_UNREADABLE_LEDGER_FROM_FORGED_SOURCE_CITATION (2026-11-18), read and
confirmed by line: `designer_stage.result_errors` resolves `artifact_repo = clone_of(d) or repo` ("Dispatcher closes
a package written in another clone. Resolve its artifacts beside the concept") and stage 3 passes it to
`scene_errors` and `showcase_check` (~line 1378). Stage 5 passes plain `repo` to both (~lines 1397-1398). When the
Dispatcher closes a stage-5 result written in the Designer's clone, a scene's proof script present in that clone but
not yet in the Dispatcher's tree reads as missing (`entry_point_exists`), refusing a good result.

Fix: stage 5 uses `artifact_repo`, as stage 3 does.

## verify

python3 src/RimMandrake/rimflow/selftest_designer_stage.py

## criteria

- A1: a stage-5 result whose scene entry point exists only in the concept's own clone is not refused for it.
- A2: one whose entry point exists in neither clone is still refused.

## acceptance

Acceptance test: a case in selftest_designer_stage.py with the concept in a second fixture clone (clone_of(d) != repo),
a stage-5 scenes.json naming a proof script present only in that clone: on base it FAILS (the result is refused with
entry_point_exists); after the fix it passes, and a script in neither clone is still refused. Not yet written or
watched failing: this run ran out of scope for it (it needs the two-clone stage-5 fixture).
