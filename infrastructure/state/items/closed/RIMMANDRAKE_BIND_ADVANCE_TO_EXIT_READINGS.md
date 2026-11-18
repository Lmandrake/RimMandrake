# RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS

## spec
`maturation.py evaluate`/`advance` moves a mod past the blind (Stage 4/5), in-game (Stage 6) and pre-human (Stage 7)
exits on `bool(steward)` alone: any non-empty `--steward-confirms` advances it, whatever the exit reader says.
`selftest_maturation.py` lines 253-258 assert that behaviour. Source: skeptical review 2026-11-15
(`D:\ClaudeWork\rimmandrake\conductor\maturation_gpt_review_20261115\claims_checked.md` A1-A2;
`design/RimMandrake/maturation_pipeline.md` §9 items 2 and 8). Build after RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES.

## decision (2026-11-15, Evidence-for-Ask, delegated)
Taken under RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME (no evidence against the obvious answer).

1. `advance` refuses a forward move whose exit reading is not met. A steward confirmation alone no longer moves a mod
   past Stage 4/5, 6 or 7.
2. The only override is an OWNER event of his (ownerSaid / byCard / perRuling) on the mod's item, newer than the
   refused reading, the same pattern `advance --to passed` already uses (`OWNER:<tsn>`). The refusal names the
   reading that failed and the override it would take.
3. A reader that is itself wrong is fixed as a Convergent repair of the reader, never waved past by an override.

Sources: spec `design/specs/2026-11-13-maturation-pipeline.md` §4 Stage 6 "a site is asserted, never hoped" (rule 6,
his 2026-11-12); CARRIED "Scripts decide"; rule 4 "Nothing reaches him unread"; his Stage 4/5 words "send it back to
just before Stage 4 again for a new blind judgement pass" (a not-met exit goes back, it does not go forward).
Evidence against: none found. The spec marks the exits PROPOSAL, but every recorded word of his points the same
way, and no ruling of his lets a mod pass an unmet reading.

Builder also owes: update `design/RimMandrake/maturation_pipeline.md` §9 items 2 and 8 and the spec's Stage 4/5, 6, 7
exit marks from PROPOSAL to the built rule, in the same commit (this decision did not edit those docs).

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/rimflow/selftest_maturation.py` with lines
253-258 inverted: advance with a not-met reading refuses; with his OWNER override event it moves; a steward confirm
alone does not.
