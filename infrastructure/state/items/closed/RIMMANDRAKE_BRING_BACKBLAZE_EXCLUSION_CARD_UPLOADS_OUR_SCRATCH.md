# RIMMANDRAKE_BRING_BACKBLAZE_EXCLUSION_CARD_UPLOADS_OUR_SCRATCH

## What the card said

<!-- answered 2026-11-28T01:10:21Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Backblaze is the backup program on Archmagi. It backs up D:\ClaudeWork, the folder where agents keep scratch files, builds, logs and run records. Measured just now from Backblaze's own file index: the index holds 21.2 million entries, and 7.85 million of them (37%) are under D:\ClaudeWork. The build and scratch folders alone are 6.5 million entries, and agents can make those files again. Measured earlier today: Backblaze read 410 GB of disk in one hour and held 5.9 GB of memory, on the disk and memory that our runs share. Its log showed it reading its own index at that time. Not measured: how much of that load an exclusion removes. (Hard to read? Type STE, Binding or Both for a rewrite.) What should Backblaze stop backing up under D:\ClaudeWork?
**His words:** All of claudework and make the backups only run once a day rather than regularly.
**Other options:** Only what agents can remake (Recommended) · All of D:\ClaudeWork · Keep all, back up nightly · Leave it as it is
