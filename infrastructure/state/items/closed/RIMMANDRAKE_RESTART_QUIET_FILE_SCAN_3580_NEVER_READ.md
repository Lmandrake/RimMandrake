# RIMMANDRAKE_RESTART_QUIET_FILE_SCAN_3580_NEVER_READ

## spec

The owner's card of 2026-11-19 5:54 PM PST (item `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG`). Question:
should a standing scan run again? He picked *"Quiet files only, when idle (Recommended)"*. The option's description:
*"A helper reads files unchanged for 7 days or more, mod content first, when no mod step needs the machine."* His words:
*"(1) yes, on Sonnet 5.5, and the Python to visualize the clean/dirty codebase is ressurrected and included on the
standard suite of Desktop visualizations to track. (perhaps this should become tabs in a standing browser actually,
along with FLEET_NOW and MATURATION_NOW in their own windows)."* The card marked this work "Owed: needs the machine".

Measured on 2026-11-19 (`D:\ClaudeWork\rimmandrake\conductor\review_loop_three_gaps_20261119.md`): the old scan
converged on quiet files (median 0.75 commits in the week before a review) and failed on files being rewritten (11.3).
The card says 3,580 code files have never been reviewed, and no scan job exists.

Build, in this order:

1. A scan job. It picks files unchanged for 7 days or more, mod content first, and never a FLAGGED file
   (`code_review_status.py list` already counts FLAGGED apart from review debt). It runs only when no mod step needs
   the machine. Each read follows the method in `design/RimMandrake/standing_rulings.md` §Code is clean when its
   promises are tested: significant findings only, the reader fixes with a test seen failing, one blind reread, flag
   on a second fix. A read that finds nothing significant records READ-CLEAN (`mark-clean`). The model is his word:
   Sonnet 5.5.
2. The 7-day line names its danger and evidence beside the number (CLAUDE.md §No limit without the danger it guards):
   the churn measurement above.
3. The clean/dirty view (`src/RimMandrake/Utils/codebase_health.py`, `rm-codebase-health.*`) returns to the standard
   Desktop visualizations. It shows PAGE-CLEAN and READ-CLEAN apart (see the note on
   `RIMMANDRAKE_SWITCH_HEALTH_BOARDS_TO_PAGE_CLEAN_RECORD_LINGERS`), and FLAGGED. His idea of tabs in one standing
   browser beside FLEET_NOW and MATURATION_NOW is a "perhaps": propose it to the Conductor, do not build it unasked.

## verify

The scan job runs once on an idle machine and records READ-CLEAN or a fix on at least one quiet mod file. The Desktop
view shows the three states.

## criteria

Acceptance test: none, live-app behaviour. The pass depends on the machine-idle signal, a live scheduled job and a
Desktop view he looks at. The builder writes the scan picker's offline selftest (quiet line, mod first, FLAGGED
skipped) with the picker, by the rule "The test is built with the item".
