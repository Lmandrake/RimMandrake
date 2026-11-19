# RIMMANDRAKE_READ_ONLY_FILES_THAT_FAILED_PILOT_FOUND_ZERO

## What the card said

<!-- answered 2026-11-19T21:03:33Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** [owner-asked] 'Lint' here means one small checker program. It scans pipeline code for places where 'I could not look' might be reported as zero, empty or pass. It flagged 299 places in 30 files, and it cannot be switched on as a gate until each place is fixed or has a written reason. A pilot read 148 places in the 3 biggest files and found 0 real problems. Reading the other 26 files takes about 8 more Opus runs, one at a time; the second is running now. What should happen to the remaining could-not-look reads?
**Picked:** Read only files that failed before
**Its description:** Why: spend reads where a could-not-look bug was actually seen (nine instances in the 2026-11-17 audit). Cost: a helper must first map those to files; the rest stay unread.
**Other options:** Stop reading; switch the gate on now (Recommended) · Read all 26 files, then switch on
