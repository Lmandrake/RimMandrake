# Gimme Some Slack: next version (after 0.1.0)

Divergent work: anything that shifts or extends the 0.1.0 vision (`../vision.md`). Each entry is a pre-written ticket with its acceptance test, who proposed it, when, and why it was not taken now. **Protected: append-only for agents; removing an entry is his call.** Nothing here changes a 0.1.0 bar.

*Empty at entry on 2026-11-13: no open judge gap sorted as next version.*

## Re-judge coverage under a calibrated brief when the next version opens

- **What:** this mod's coverage signature was made before the coverage brief read CALIBRATED (`coverage_judge.unproven_signatures` flags it; flagged, never voided). When its next Design Version opens, its coverage is judged again by a coverage brief that reads CALIBRATED at that time.
- **Who, when, why not now:** owner, by question card 2026-11-16 11:36 PM PST (point 19), picked "Leave them, re-judge at next version": "two of the three are already in live in-game visits, which find real failures better than a paper re-read. Buys: no spend or delay now; each gets a tested judge when its next Design Version opens." Filed by RIMMANDRAKE_LAND_JUDGE_PROMPT_CALLS_FOUR_ANSWERED_BY_CARD.
- **Acceptance test:** `python3 src/RimMandrake/rimflow/refusal_contract.py calibrate --no-run` reads `coverage_judge` CALIBRATED, and `python3 -c "import sys; sys.path.insert(0, 'src/RimMandrake/rimflow'); import coverage_judge as C; print([u['concept'] for u in C.unproven_signatures('.')])"` no longer lists `design/concepts/GimmeSomeSlack`.
