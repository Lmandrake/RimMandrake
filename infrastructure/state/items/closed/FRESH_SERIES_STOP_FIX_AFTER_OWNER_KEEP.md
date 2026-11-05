# FRESH_SERIES_STOP_FIX_AFTER_OWNER_KEEP

On owner_escalations_leaningscrub_1 (2026-10-24) he kept the live in-game art for RM_Crustweevil, RM_Dustflutter and
RM_Fuzzrunner. The fresh series (COPY_DAMAGED_FAUNA_REDRAW_OWNER_PROMPTS, s1r1 done, round 2 filed in fddd6879f1)
still continues for all three, and `fauna_drive.py install` (~line 236) may replace owner-kept art when the first
pass was REALLY_BAD, which it was for all three. Risk: the series overwrites the picture he just chose.

## Wanted
Question for the main window: stop s1 for these three? Code: fauna_drive install/rows refuse a subject whose live art
has an owner keep ruling newer than the series reset, unless he re-asks.
