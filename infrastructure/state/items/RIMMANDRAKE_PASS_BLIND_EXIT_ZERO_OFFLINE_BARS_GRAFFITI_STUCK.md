# RIMMANDRAKE_PASS_BLIND_EXIT_ZERO_OFFLINE_BARS_GRAFFITI_STUCK

## spec
Pipeline defect (CRITERION FLAW), found by the steward on Graffiti's blind cycle 1. `maturation.py read_exit` added
"the test table names no offline bar (proves_at 2 or 4-5)" to its not-met reasons whenever a version's test table has
zero offline bars. Graffiti 0.1.0 is locked with 47 bars, all proving at Stage 6 (the only such mod today: Explosive
Knockback 2, FlowWorks 5, Gimme Some Slack 2, Pyrelands 6, Leaning Scrub 3 offline bars), so its blind exit could never
read met, however clean the record. The exit both the spec (§Stages 4 and 5, Exit: "Every bar tagged offline is
green. A blind judge found nothing that is a Problem.") and FORMAT_NOTES ("every offline bar green, no Problem found")
state holds with nothing to rerun when no bar is offline; the judge certificate already passes such a table.

Refusal record: evidence: the line in read_exit, Graffiti's next reading of 2026-11-16; would_pass: a clean cycle record
on a table with no offline bar reads met; smallest_fix: drop the block, keep the count visible as
`checks.offline_bars`. No bar changed: this is the reader, not a mod's or a north-star bar.

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_maturation.py --blind` (exit 0, ALL PASS). Its new case
"a table with no offline bar: a clean record reads met, and the reading counts 0 offline bars" FAILED on the base
(reason: "the test table names no offline bar"), and passes with the fix; the companion case (an open Problem on such a
table still reads not met) passes on both.

## criteria
- A clean blind record on a table with zero offline bars reads met; an open Problem on it still reads not met.
- The reading reports the offline-bar count in `checks.offline_bars`.
