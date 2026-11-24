# RIMMANDRAKE_CORRECT_SLACK_TWO_FALSE_LINES_AFTER_HIS_WALK

Gimme Some Slack **0.1.1**, current version (a false statement in the mod's own files). Merged by the ticket sweep of 2026-11-22
(`design/concepts/GimmeSomeSlack/ticket_sweep_2026-11-22.md`) from:
- `RIMMANDRAKE_MEND_SLACK_KEYSHEET_GROUND_SWAY_LINE_OUTLIVED_RULING` (filed 2026-11-20 by the walk-brief reader);
- `RIMMANDRAKE_CORRECT_GSS_DRIPLOOPS_COMMENT_SAYS_ON_SHIPS_OFF` (blind cycle 4 lane 2 code read, 2026-11-16).
Neither carried an owner quote. The ruling the first one enforces is his card of 2026-11-16 (in `RIMMANDRAKE_CLEAN_SLACK_SWAY_POLE_WIRES_ONLY_NOT_CONDUIT`):
*"Oh wow, there's been some confusion. Wires swaying in the wind were supposed to be about power pole wires. Wind wasn't supposed to mess with conduit-based wiring at all, nor about terminal wires in walls extending cable hanging out. Let's clean that up."*

## spec

Two lines in hashed Gimme Some Slack files say something false:
1. `src/RimMandrake/GimmeSomeSlack/human_review.py:244` writes station 1's U_motion_look note as "... the live end's drip / spark
   rhythm, the sway in the wind." Wind moves no ground cord since 0a0fd8343b (his card above). The committed `review/KEYSHEET.md`
   was already corrected; the generator would put the false line back on the next review-map save.
2. `src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialSettings.cs:76` says dripLoops is "Default ON (owner by card 2026-10-15 ...)";
   the default is `AerialMath.DripLoopsDefault = false` since his 2026-11-08 sitting.

Fix: delete "the sway in the wind" from line 1's note; make line 2's summary state the real default (OFF) and its date.

## Why not now

Both files are in the mod hash (`src/RimMandrake/GimmeSomeSlack/.hashignore` does not list `human_review.py` or `Source/`). Gimme Some
Slack 0.1.1 is at Stage 8, his live walk on ArchBig (since 2026-11-21 10:32 PM PST). A hash move under his walk is what sent the mod
back to Stage 6 on 2026-11-21 7:02 PM PST (journal, Conductor decision). So this lands the moment his walk ends (pass or road back),
together with whatever else moves the hash then. It needs no live check: neither line changes what the game does.

## criteria

Acceptance test (red today, watched 2026-11-22 by the sweep: prints `1` and `1`):

    grep -c "the sway in the wind" src/RimMandrake/GimmeSomeSlack/human_review.py; grep -c "Default ON" src/RimMandrake/GimmeSomeSlack/Source/Aerial/AerialSettings.cs

passes when both print `0`, and `python3 src/RimMandrake/GimmeSomeSlack/selftest_human_review.py` still passes.

## verify

Run the acceptance test under ## criteria; cite its output on the close.
