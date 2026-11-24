# BOUNDARY: bridge order waits

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWaitCore.cs`,
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchWait.cs`,
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchJobTools.cs` (`OrderedJob`, `DoBillNow`),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTerrainTools.cs` (`OrderPawn`),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchZoneTools.cs` (`PrioritizedWork`),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchAbilityTools.cs` (`PawnUseAbility`, `PawnUseVerb`),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlightTools.cs` (`PawnFlight`),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchMapCompTiming.cs` (`MapCompTiming`).
Selftest: `src/RimMandrake/bridgetools/selftest_order_wait.py`.

The tools wait for a game tick count under a wall-clock limit. They poll on the game thread. The caller's cancellation
still interrupts the wait. Pre-wait refusals, including an empty pawn selection, keep their existing replies.

## PROMISES

- **paused-wait-stops.** If the call did not set a speed, two consecutive polls that see the game paused at the
  same tick end an otherwise unfinished wait with `waitEnded: "paused"`. A stationary tick counter while unpaused
  waits for `"timeout"`, as does a stalled game after the call set its speed. Reaching the requested tick count
  (or requesting zero ticks) returns `"ticks"`. Where reported, `pausedDuringWait` means a poll saw the game paused
  and can be true even if some ticks passed.
- **arrival-requires-opt-in.** `order_pawn` takes optional `stopOnArrival` (default false). With it on, a poll that
  finds every ordered pawn on the destination cell or gone from the order map ends the wait with `waitEnded: "arrived"`,
  including when the result is already true at the first poll. Arrival wins if a limit is reached in the same poll.
  The reply still reads back each pawn and requires every pawn to stand on the destination after ticks elapsed for
  `success`. With the option off, arrival has no effect on the wait.

## DOES NOT SURVIVE

- A game thread that cannot answer a poll can delay the return until the thread responds or the caller cancels.
- A pawn can visit the destination between polls and leave before the next read. Arrival is an observation at a poll.
