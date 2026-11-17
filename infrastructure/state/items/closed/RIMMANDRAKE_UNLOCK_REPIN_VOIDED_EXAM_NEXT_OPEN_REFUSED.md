## spec

`designer_stage.py repin` on a concept whose stage.json reads `status: locked` (stage 5 signed) leaves stage 4 stale
when the change moves the exam's tree or sheet, and writes "the next open retakes it". But a locked status refuses every
open (`open_run`: "LOCKED: changing a locked tree is his word only") and `reopen_if_stale` returns early on it, and
`maturation_autonomy.chain_owed` returns None for a locked status, so no chain steward is owed either. The retake that
the repin promises can never happen. Seen 2026-11-17 on Pyrelands and Graffiti after the bars-card repin (7e59c0c1ba):
preview `open_run(commit=False)` refused LOCKED on both, and `chain_owed` was None on both.

Fix: when repin voids a stage on a locked concept, set the status to `ready` (his card is the word that unlocks it) and
say so in the `locked_change` history row; the next open reopens stage 4 through `reopen_if_stale`, and stage 5's
coverage signature locks it again. Repair the two concepts written by the defective repin the same way.

## criteria

- a repin that voids the exam of a locked concept leaves it openable (no LOCKED refusal) and owing the maturation chain.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/selftest_designer_repin.py` prints `all checks passed` (case 5 now
starts from `status: locked`). Watched it fail on the base before the fix: `FAIL 5 a voided exam unlocks the concept
for its retake got: 'locked'`, `FAIL 5 the next open is not refused as LOCKED`, `FAIL 5 the maturation chain is owed
for the locked change got: None` (3 checks failed).

## refs

file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/selftest_designer_repin.py
file: design/concepts/Pyrelands/stage.json
file: design/concepts/Graffiti/stage.json
