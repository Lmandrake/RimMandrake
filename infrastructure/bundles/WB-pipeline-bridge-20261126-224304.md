# WB-pipeline-bridge-20261126-224304 (onboarding run of pipeline:bridge)

State: ENDED. Every member has an outcome.

| member | class | outcome |
|---|---|---|
| RIMMANDRAKE_PROVE_FLIGHT_MAINTAIN_HOLDS_ONLY_STARTED_PAWNS | keep | offline fault fixed (15b98dd078, polish 7e83b15205); live state read waits (until 2026-12-03) on the owner's act 1 |

- Fault found offline: StartFlying() leaves flightState TakingOff, and the c10.F1 maintain rule held only raw Flying, so
  `jawa/pawn_flight action=start maintainTicks>0` held no pawn. Rule now in `JawaBenchFlightCore.HoldInWindow`;
  promise `flight-maintain-holds-started` in `design/specs/2026-11-24-bridge-order-waits/boundary.md`.
- The companion DLL is NOT deployed by this run. The flight sitting deploys it first.
- Owed: fresh read of the fix, filed as RIMMANDRAKE_READ_FLIGHT_HOLD_RULE_FRESH_ONE_LINE_TWO_STATES.
