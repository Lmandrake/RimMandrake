# RIMMANDRAKE_WIRE_FRIDAY_JUDGE_TO_EXAMINE_FLAGGED_FILES_WEEKLY

## spec

The owner's card of 2026-11-19 5:54 PM PST (item `RIMMANDRAKE_ENACT_REVIEWER_FIXES_ONE_REREAD_THEN_FLAG`) says:
*"Flagged files are examined to see if we need to change the definition of significant or there is a real
instability, but this is done infrequently, say weekly or so."*

The rule text (`design/RimMandrake/standing_rulings.md` §Code is clean when its promises are tested) proposes that
the Friday run of `rm-findings-judge.timer` does this examination. The Friday run is a weekly Opus `claude -p`
(`src/RimMandrake/Utils/findings_judge.sh`). It already reads patterns across runs and files rule candidates
(`src/RimMandrake/Utils/findings_judge_friday.md`). Until this item closes, the Conductor examines the flagged files.

Add one step to `findings_judge_friday.md`:

1. Run `python3 src/RimMandrake/Utils/code_review_status.py list --flagged`. Exit 3 means a flag shard is
   unreadable: report that, and examine nothing.
2. For each flagged file, answer one question: must the definition of significant change, or is this code really
   unstable? Read the flag's why and `git log` of the file since the flag.
3. A definition answer: file one rule candidate (one per source event) that quotes the flags.
   An instability answer: leave the flag and write one line in the run's report.
   When the examination ends a flag: `code_review_status.py unflag <path> --why "<the answer>"`.
4. Count the examined files in the run record (`flagged=`).

## verify

`grep -c "list --flagged" src/RimMandrake/Utils/findings_judge_friday.md` prints 1 or more, and a Friday run
(`FINDINGS_JUDGE_FRIDAY=1 src/RimMandrake/Utils/findings_judge.sh`) with one planted flag in a throwaway root reports it.

## criteria

Acceptance test: `grep -q "code_review_status.py list --flagged" src/RimMandrake/Utils/findings_judge_friday.md`.
Expected: exit 0 (1 check passes). Watched failing on the base b57a0b2520 (exit 1), 2026-11-19.
The live Friday run is UNRUN: the first real Friday after the change is the live test.
