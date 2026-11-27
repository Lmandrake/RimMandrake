# Polish for the bridge order waits (beside `boundary.md`)

One line per finding. No line is a ticket. The next Work Bundle that changes the named file takes the line.

- `src/RimMandrake/bridgetools/selftest_order_wait.py` (flight case): the harness gives `HoldInWindow` the core's own
  named constants. So an edit that swaps `JawaBenchFlightCore.TakingOff` and `Landing` still passes. Pin the engine's
  literal values in the harness (`TakingOff` = 2 is held, `Landing` = 3 is not; read from `Pawn_FlightTracker.FlightState`).
- `boundary.md` (this page) has no LIMITS section, but `PawnFlight` in
  `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlightTools.cs` refuses `maxPawns` > 2000 and
  `maintainTicks` > 60000. These limits name no danger (CLAUDE.md §No limit without the danger it guards). Give each one
  its danger and its evidence, or remove it. `timeoutSeconds` is a hang guard and stays.
