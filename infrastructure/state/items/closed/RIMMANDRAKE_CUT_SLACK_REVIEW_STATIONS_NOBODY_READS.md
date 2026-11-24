# RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS

**Next version** (review-map work; moves no 0.1.0 bar). Gimme Some Slack. From his walk of 2026-11-20: `design/RimMandrake/validation_holding/gss_walk_20261120.md` row #7 and
its station table.

## spec

He said: delete the stations nobody uses for review, so they are not reviewed or excused again. The table in the record
lists, for each of the 31 stations of `src/RimMandrake/GimmeSomeSlack/human_review.py`, what reads it. Proposed for
deletion: **5, 8, 9, 11, 17, 18, 19, 23, 27, 30** (no check and no walk reads them by their purpose). Also delete the
"KNOWN GAP" tangle lines of stations 1-4 (visit 3 saw each tangle follow its look [guess ~70%]) and change station 16's
roof poke after RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT. Before deleting, check each candidate once more against
the generated scenes (`version/test_table.json`) and the expected refusals (`human_review.py:1696`); a station that turns out
to be the only reader of a bar stays. Renumber, rebuild the key sheet (`review/KEYSHEET.md`, `keysheet.html`) and the
sign books; `pole_shots.py` and `live_stub_joins.py` read the station list and follow it.

## verify

`python3 src/RimMandrake/GimmeSomeSlack/human_review.py --plan` and `selftest_human_review.py`.

## criteria

Acceptance test: `human_review.py --plan` lists none of the deleted stations' titles (red today: it lists all 31
[measured: `station_list()` returns 31]); `selftest_human_review.py` passes; no "KNOWN GAP" line is left in the key sheet.

## refs

file: src/RimMandrake/GimmeSomeSlack/human_review.py
file: src/RimMandrake/GimmeSomeSlack/review/KEYSHEET.md
