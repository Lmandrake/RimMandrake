# RIMMANDRAKE_BUILD_ACCOUNT_END_WARN_SAVE_PAUSE_SWITCH_SIZED_BY_BURN

## What the card said

<!-- answered 2026-11-24T19:16:33Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** At 1% left, every run gets the order "record your state immediately and prepare for termination". Then the machine pauses, then it switches accounts, and the switch stops every Claude process. The pause must be long enough for runs to save, and short enough that the account does not reach 0%, where every window errors and you cannot talk to a seat. Measured today with about 12 runs live: the account lost 1 point every 15 minutes. The meter shows whole percents, so a reading of 1% can mean 0.5% is left, which is about 7 minutes from zero at that rate. A "saved signal" below means a small file that each run writes when its state is on disk. (Hard to read? Type STE, Binding or Both for a rewrite.) How long should the pause at 1% be?
**Picked:** Sized from the burn rate (Recommended)
**Its description:** Why: the safe pause depends on how many runs are spending. The machine reads the current burn and pauses for a fifth of the time to zero, 3 minutes at most. Buys: safe at any load, long when few runs are live. Costs: one more calculation that can be wrong if the burn reading is stale. Recommended: it is the only option that holds your under-10% chance at every load.
**His words:** (1) and that may also initiate the "no new work / save now" warning up at 3% as well if the burn is going crazy fast. Scale both 3/2% (initiate saves) warning and the time-constant post 1% based on load. If the reading is believed to be stale, default to safe values. TELL THE PROCESSES these numbers. Estimate how long they have to complete their saves. It may influence their choices.
**Other options:** Fixed 2 minutes · Until every run says saved
