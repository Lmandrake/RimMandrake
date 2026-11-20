# RIMMANDRAKE_SPLIT_PIT_LOOK_EXIT_UNMEASURED_READ_AS_FAIL

Caused by RIMMANDRAKE_DRIVE_FLOWWORKS_IN_GAME_VISIT_TWO.

## spec

`src/RimMandrake/FlowWorks/northstar/pit_look_1114_live.py` ended with `sys.exit(1 if bad else 0)`, where `bad` holds every row that is not
True, UNMEASURED (None) included. Visit 2's run on SITTING_20261114_PIT_FIXES read 19 PASS, 0 FAIL, 1 UNMEASURED (body_cover_is_a_look,
UNMEASURED by design) and exited 1, so the visit runner recorded FAIL. Fixed: exit 1 only for a FAIL, 2 when a row could not look or no
row ran, 0 when all PASS. The first visit-2 row was re-derived to UNMEASURED with a `verdict_corrected` note.

## verify

python3 src/RimMandrake/FlowWorks/northstar/selftest_pit_look_exit_codes.py: red before the fix (cases 'one unmeasured', 'empty'), green after.

## criteria

The selftest above, 4 cases PASS.
