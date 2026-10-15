# ASHWALLOW_HEAT_DOME_WIRE_CURLS_UP_LATE

Owner, Ashwallow art sheet note (2026-10-11): "have its legs curl inward along its body to help it seal up into a dome
when it's half-buried ... plus the behavior to assume the defensive stance when under heat attack."

Built 2026-10-15 (BENCH): `src/RimMandrake/Pyrelands/Source/RM_BurrowHeatReaction.cs` - a heat-category hit domes an
RM_BurrowOnFireExtension race at once (RM_Burrow, InterruptForced) with a 600-tick heat hold; the burrow driver surfaces
only when no fire is near and the hold has run out; the Body node draws `domeTexPath` while RM_Burrowed holds. Setting
`burrowDomeOnHeatHit`. The dome ART is its own item: ASHWALLOW_DOME_SKETCH_AWAITS_ITS_NEW_BODY.

## criteria

- O1 L0: FireEcologyHook builds; pyrelands fuzz covers DomeOnHeatHit (256-row table), BurrowHeatHoldUntil and BurrowMayEmerge boundaries; pyrelands lint 0 ERROR
- A1 L2: `heat_dome` chain, `ashwallow_domes_on_heat_hit`: a 2-point Burn on a wild ashwallow with no ground fire near leaves it burrowed in RM_Burrow with the hold running 5 ticks later, unharmed, and surfaced 900 ticks later
- A2 L2: `heat_dome` chain, `ashwallow_heat_dome_toggle_off`: with burrowDomeOnHeatHit off the same hit does not dome it
- A3 L2: once the dome art is installed, ProbeDome's bodyGraphic reads the domeTexPath while burrowed (same chain)
