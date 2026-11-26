A check that reads Archmagi's D:\ClaudeWork state (testq queue, evidence) and runs in a session on SteveDesktop reads SteveDesktop's own D:\ClaudeWork: the folder exists and is empty, so it prints a confident 0 instead of COULD NOT LOOK. Read the lane queue over ssh archmagi-wsl, and make such a check say COULD NOT LOOK on a folder with no records.
item: RIMMANDRAKE_PUT_STEVEDESKTOP_ON_NON_MOD_WORK_ALL_DAY_HE_ASKED
home: infrastructure/state/facts/instrument_traps.md
