# RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE

## spec

Owed by the owner's card of 2026-11-17 ("Judge ruling -> Adopt the four rules (Recommended)"; its cost line: "unproven
until recalibrated and one mod runs"). Spec: design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md.

ORDER (each step only after the one before it):
1. Wait for RIMMANDRAKE_WRITE_JUDGE_FOUR_RULES_TWO_LOOK_LIMIT to land (and the two bug fixes,
   RIMMANDRAKE_UNBLOCK_POLISH_GAPS_EVERY_LOOK_NOT_LATE_ONLY and RIMMANDRAKE_CLOSE_CARRIED_GAPS_REPAIRED_WITHOUT_CLAIM_FORM).
   Any edit to coverage_judge.py, bar_rule.py, roles/designer_lock.md or roles/designer_scene_contract.md changes
   refusal_contract.brief_hash, so the coverage judge is UNTESTED: its refusals do not bind and covered does not sign.
2. Add three calibration cases to the coverage judge's calibration set and recalibrate it:
   - Pyrelands look 8 (design/specs/2026-11-17-judge-flaws-not-polish/tickets/look8_replay.json) must CLOSE;
   - the fire-immunity test where the beast never touches fire must be REFUSED (nobody would notice the promise broken);
   - "test the giant against every roster kind" must NOT block (advice: "test more cases").
3. Only then: restamp Pyrelands and run its one-entry look under the new rules.
4. In Pyrelands' paperwork, mark "most of the map" and "wind off must flood" as examples (rule 3: a number or line binds
   only if the owner said it), not bars.

## criteria

- Calibration record shows the new brief hash TESTED, with the three cases passing as stated.
- Pyrelands' look after the restamp is judged by the calibrated brief, in at most two looks.

## refs

file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/refusal_contract.py
file: design/specs/2026-11-17-judge-flaws-not-polish/6_proposed_ruling_plain.md
