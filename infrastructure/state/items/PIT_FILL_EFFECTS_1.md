# PIT_FILL_EFFECTS_1 — What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burning oil with an occupant

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- `RM_PitDrowning` keyed to F>0 at D=4 for non-swimmers (swimming-graphic test, never an "aquatic" substring).
- Poison FluidDef: toxin keyed to fill, not a comp.
- Oil: ignitable; fire on a body knows its occupants and harms them (ruling 22: very effective).
- Uses the lifted `OccupyingLiquid()` query.

## verify
Bridge: flooding an occupied D=4 cell by opening a sluice drowns a non-swimmer and spares a swimmer; poison fill applies toxic buildup; igniting an oil-filled occupied pit burns the occupant.

## criteria
No "water/oiled/poison pit" def exists; all three effects come from the fluid.

## depends
`SUPERDEEP_HOLDER_RETIRE_1`, `LIQUID_BODY_FLUID_IDENTITY_1`, **`FLOWWORKS_CHANNEL_OSCILLATION_1`**.

## northstar
State components: hediff severity by fluid and swimmer flag; fire present + occupant damage.
