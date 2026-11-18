# RIMMANDRAKE_MEND_CERTIFICATE_SUMMARY_BAR_REFUSAL_CRASHED_IT

## spec
`judge_certificate.summary()` joined each refused clause's test ids; a bar-level `decided` refusal (an offline bar naming
no offline decider) carries `test: None`, so the join raised `TypeError` and `maturation.evaluate` (which calls
`JC.summary` outside the certificate's own try) crashed on any such mod. Found by Codex reviewing
RIMMANDRAKE_DRYRUN_SCENES_ON_EMPTY_GAME_THREE_PASSED, 2026-11-18. Fix: the summary names such a refusal "(bar <id>)".

## refs
file: src/RimMandrake/rimflow/judge_certificate.py
new: src/RimMandrake/rimflow/selftest_asks_on_empty_game.py

## verify
python3 src/RimMandrake/rimflow/selftest_asks_on_empty_game.py

## criteria
- A1: the selftest exits 0 with its bar-level-refusal summary case passing.

## acceptance
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_asks_on_empty_game.py` exits 0 (case "a bar-level refusal
(test None) reads in the summary"). Watched failing on 79a1728271: base `summary()` on a `decided` row with test None
raises `TypeError('sequence item 0: expected str instance, NoneType found')`.
