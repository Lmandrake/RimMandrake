# BOUNDARY: exam_errors and the verdict word of a scenario's expect, Design Version 0.1.0

Code: `exam_errors` in `src/RimMandrake/rimflow/designer_stage.py`. Item: `RIMMANDRAKE_REQUIRE_EXAM_EXPECT_VERDICT_WORD_492_ALREADY_DO`.

## ACCEPTS
- A scenario `expect` whose text before the first `:` (or the whole text, with no `:`) is `accept` or `reject`, any case, any spacing. Measured 2026-11-19: all 492 scenarios in the 12 exam.json files on disk (338 reject, 154 accept).

## DOES NOT SURVIVE
- An expect with another leading word ("maybe: ..."): refused, naming the scenario and both words. (A non-string was already refused as "needs expect".)

## PROMISES (tests of the same name in `src/RimMandrake/rimflow/selftest_designer_stage.py`)
- **expect-carries-a-verdict-word**: "maybe: ..." is refused naming the scenario id, 'accept' and 'reject'; " Reject : wall" is not refused.
