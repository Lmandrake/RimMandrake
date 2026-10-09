# PROMISED_GIFT_NEVER_LOST_1 — FV-2: owed deep-gifts not dequeued before ransom setting / placement checks

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` (remaining rows, helper pass 2026-10-09; owner 'Queue all' card 2026-10-08). Row FV-2 there is the spec; its 'Checked' column says what was read to confirm it is unbuilt. Re-check src before building.

| FV-2 | **A promised gift is never silently lost (hygiene).** Owed deep-gifts are removed from the queue before two things are checked: whether the ransom setting is on, and whether the gift was placed. So switching the setting off while a gift is owed cancels it for good, and a failed placement (`Grant` returns an empty list) is never retried. Pause owed gifts while the setting is off and retry a failed placement. Replacing the three parallel lists with one saved record would make this simple. | small C# change, with a save-compatible list migration | S | low | FeverWood | `RM_MapComponent_TentacleWatch.cs:182-192` (`CollectDue` removes first, then gates on `broodRansomEnabled`); `RM_BroodRansom.cs:326-344` (empty list on failure, no requeue); not in the VERDICTS FeverWood rows or any item |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

- Offline: build clean; TickPendingGifts returns before CollectDue while broodRansomEnabled is off (queue kept); an empty Grant result re-queues the gift 2500 ticks later.
- L2 (owed): switch the ransom off while a gift is owed, back on, gift arrives.
