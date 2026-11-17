# RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD

## spec

Land the judge prompt changes proposed in `D:\ClaudeWork\rimmandrake\conductor\role_prompt_upgrades_20261116.md`
section 7, closing paragraph ("What I would now propose for the judges"), with the owner's four card answers of
2026-11-16 11:36 PM PST (ledger notes on RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY):

- Point 11, picked "Keep: it reads as PASS": "Why: a doubt the judge cannot put into words gives the builder nothing to fix. Buys: no unanswerable refusals, and no change to the frozen checker. Costs: a real but badly worded doubt slips through to the in-game visit. Recommended because your refusal rule needs a path to pass, and this one has none."
- Point 14, picked "Open search in round 1 only": "Why: catch what the Designer left off the list, but only once. Buys: round 1 looks everywhere; later rounds only check that named gaps were repaired, so the loop ends. Costs: something missed in round 1 waits for the in-game visit or your look. Recommended: it ends the Pyrelands loop without GPT's hole."
- Point 19, picked "Leave them, re-judge at next version": "Why: two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens. Costs: a design gap the old judge missed is found later, in game. Recommended: live failures beat predictive review."
- Point 26, picked "Only if a second reader agrees": "Why: stop real defects without reopening the goalpost loop. Buys: a late gap blocks only when it is a Problem a player would reject and the judge's second reader confirms it. Costs: a small code and prompt change plus a re-test of the judge. Recommended: serious defects are cheaper to fix on paper."

Work owed: J3 in GPT's words (checker FAIL text and lane-1 FAIL rows carry a path to pass); J1 as GPT's checker
`measurement:` rewording only (rewording, inside the Relentless freeze); J2 coverage line in GPT's words plus "Hunt
parameter regimes and regions, not examples."; J4 completion condition in GPT's words, with the open search in round 1
only; J6 rows split into experience and number, only the number waived; point 26's late-gap rule in prompt and code;
point 27's two art-brief fixes; then J5: one calibration batch on the exact final coverage brief (and the art brief),
including planted cases for routing, a mixed experience-and-number row, and a serious late gap. Dropped: J2 and J6
checker lines, J1 art line, `PINNED:`, every percentage. The three flagged signatures are left; the re-judge at each
mod's next Design Version is recorded where the next version's opening reads it.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate` reads the coverage judge CALIBRATED
at its final brief (today, base: UNTESTED, measured 2026-11-16 by `calibrate --no-run`); new selftests for the
late-gap rule (blocks only when serious and reader-confirmed; four cases: serious+confirmed, serious+unconfirmed,
minor+confirmed, round-1 gap) and the round-1-only open search fail on the base and pass after. Not watched failing at
filing; the builder writes and watches them first.

## criteria

- The coverage judge has a finish line: open search in round 1, repairs only after.
- A serious late gap confirmed by the second reader blocks; any other late gap is advisory.
- Every FAIL names what would pass.
- The coverage brief is CALIBRATED at the landed text.

## refs

file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/bar_rule.py
file: src/RimMandrake/rimflow/relentless_wall.py
file: design/RimMandrake/art_judge_brief.md
