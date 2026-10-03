# FLIGHT_STATE_READ_TOOL_1

## spec
The flight-state read tool ALREADY EXISTS: `jawa/pawn_flight` (commit f707e69f1, 2026-09-21), in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlightTools.cs`, and its name is present in the
committed `artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`. Do NOT add a second tool (a duplicate
alias kills the whole jawa-bench provider). `action=report` (default) is read-only; select by `pawn` (id/name)
or `kind` (PawnKindDef or ThingDef defName, all maps). Each row: flying, flightState, hasTracker, canEverFly
(= MaxFlightTime stat > 0), canFlyNow, maxFlightTicks, maxFlightTimeStat, flightCooldownStat, flyingTicks,
flightCooldownTicks, lerpTick, current job + tryStartFlying. No match returns a named error, not silence.
This item's remaining work is the live PROOF of that tool on the flyers (Krizzak, Firehawk, Murmuration).
No rect selector exists; select by kind or pawn id.

## verify
After the next deploy, on a test map spawn `RM_Krizzak` (or Locust): `jawa/pawn_flight kind=<defName>` reads
canEverFly=true and maxFlightTimeStat>0. Spawn a walking animal (e.g. Muffalo): canEverFly=false,
maxFlightTimeStat=0 (or flight tracker per row). Record each as a `rimflow verify` run. Never a visual hunt.

## criteria
- Krizzak and Firehawk (and Locust as control) read canEverFly=true; a walker reads false.
- Read-only `report` changes nothing (flightState unchanged before/after).
- Empty selection returns an error naming the unmatched kind, not success.
