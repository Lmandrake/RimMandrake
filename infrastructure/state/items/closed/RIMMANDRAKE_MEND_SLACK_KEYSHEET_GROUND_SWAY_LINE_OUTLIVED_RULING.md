# RIMMANDRAKE_MEND_SLACK_KEYSHEET_GROUND_SWAY_LINE_OUTLIVED_RULING

## spec
The review generator `src/RimMandrake/GimmeSomeSlack/human_review.py:244` writes station 1's U_motion_look note as "the live end's drip / spark rhythm, the sway in the wind". The owner ruled 2026-11-16 that wind moves no ground cord (RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT; b560ff91e8 removed ground sway). Station 1 is ground cords, so the note asks him to judge a motion that the mod no longer has. The next `human_review.py --build` writes the false line back into `review/KEYSHEET.md`, `review/keysheet.html` and the station's sign book.

Found by the Stage 7 walk-brief reader (RIMMANDRAKE_STEWARD_GIMMESOMESLACK_PRE_HUMAN_STAGE, 2026-11-20). That run corrected the committed `review/KEYSHEET.md` and `review/keysheet.html` (both in `.hashignore`). It did not edit the generator: `human_review.py` is in the mod hash, and an edit before his walk would make the walk build's rows read stale. The sign book inside `GSS_VISIT3_WALK_20261120.rws` still carries the old line; the walk brief tells him.

Fix: in `human_review.py:244`, replace "the sway in the wind" with "(wind moves no ground cord, owner 2026-11-16; only pole wires sway, stations 6 and 21)", the same text as the corrected key sheet. Do it after his walk, or in the next rebuild of the mod.

## criteria
Acceptance test: `! grep -q 'the sway in the wind' src/RimMandrake/GimmeSomeSlack/human_review.py` exits 0. Watched it fail on 73f0359aa8 (grep finds line 244). Expected: 1 check, PASS.

## verify
offline: ! grep -q 'the sway in the wind' src/RimMandrake/GimmeSomeSlack/human_review.py

## refs
file: src/RimMandrake/GimmeSomeSlack/human_review.py
