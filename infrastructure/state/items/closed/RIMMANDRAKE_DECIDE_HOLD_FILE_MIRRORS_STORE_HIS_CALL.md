# RIMMANDRAKE_DECIDE_HOLD_FILE_MIRRORS_STORE_HIS_CALL

## What the card said

<!-- answered 2026-11-19T14:52:59Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** [owner-asked] A run is changing how your mod holds are stored. Today a file and the control store (the database behind ./pipe) both record a hold. The run makes the control store the only writer, and the file becomes a copy. Only your lift command can lift a hold, before and after. A ticket had marked this change as your decision. I started the run at 6:45 AM because you said "Commission all unfinished work proposals". Did you mean to include this change?
**Picked:** Yes, let it finish (Recommended)
**Its description:** Why: one writer means the file and the store cannot disagree about a hold. Buys: the change lands today with its tests. Costs: it lands before you read it. Recommended because the run must prove that the list of held mods is the same before and after.
**His words:** (1) yes... but Conductor should also be able to lift a Hold. We work together, don't use me as a bottleneck alone.
**Other options:** Build it, but show me first · No, stop the run
