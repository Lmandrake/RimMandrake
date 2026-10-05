# PIT_FILL_EFFECTS_1 — What a fluid does to a pit occupant: drowning at D=4, poison keyed to fill, burning oil with an occupant

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
- `RM_PitDrowning` keyed to F>0 at D=4 for non-swimmers (swimming-graphic test, never an "aquatic" substring).
- Poison FluidDef: toxin keyed to fill, not a comp.
- Oil: ignitable; fire on a body knows its occupants and harms them (ruling 22: very effective).
- Uses the lifted `OccupyingLiquid()` query — which must read the CELL's fluid (`LIQUID_BODY_FLUID_IDENTITY_1`'s `fluidGrid`), never a per-map fluid.
- Fluids never mix (owner Q3, 2026-10-02), so a cell holds exactly one fluid and each effect keys off that one fluid; no blended or "sludge" effect exists.

## verify
Bridge: flooding an occupied D=4 cell by opening a sluice drowns a non-swimmer and spares a swimmer; poison fill applies toxic buildup; igniting an oil-filled occupied pit burns the occupant.

## criteria
No "water/oiled/poison pit" def exists; all three effects come from the fluid.

## depends
`SUPERDEEP_HOLDER_RETIRE_1`, `LIQUID_BODY_FLUID_IDENTITY_1` (`FLOWWORKS_CHANNEL_OSCILLATION_1` closed 2026-10-02 at `ddb473416`).

## northstar
State components: hediff severity by fluid and swimmer flag; fire present + occupant damage.
**First script must prove (Q3):** two occupied D=4 cells side by side holding different fluids each apply only their own fluid's effect (drowning vs poison vs ignition), read per cell by fluid id.

## BUILT OFFLINE (FOUNDRY flowworksA, 2026-10-05) — live verify owed
- `Source/RM_PitFillEffects.cs` + Verse-free `RM_FillEffectMath.cs` (2 selftest cases, 77/77): every 250 ticks, each pawn standing in an excavated wet cell is read by the CELL's fluid (`FluidAt`). Drowning: F>0 at D=4, any fluid, non-swimmers only — swimmer = `CurKindLifeStage.swimmingGraphicData != null` (1.6's own marker), fliers skipped; `RM_PitDrowning` +24/day x F/D (~1 in-game hour at brim) with a -4/day ebb comp. All PROVISIONAL.
- Poison: `FluidDef.toxicPerDayAtBrim` (new field). `RM_Fluid_Poison` = 2.4/day at brim x F/D x (1 - ToxicEnvironmentResistance), vanilla ToxicBuildup, any depth. PROVISIONAL.
- Oil: `RM_Fluid_Oil` is a CreepingFuse (90 ticks/cell PROVISIONAL) on Phase 6's `RM_LiquidFire`, which already harms the occupant (D=4 always catches, ruling 22).
- New defs: `FlowWorks_PitFluids.xml` (oil, poison), `FlowWorks_PitFluidTerrain.xml` (their 4-tier fill ladders, cloned from tar, colour-multiply placeholder art). Neither is yet any natural LiquidDef's `canalFluid`.
- Settings: `pitDrowningEnabled`, `pitDrowningRateMultiplier`, `poisonFillEnabled` (Pits section). Census: static_call `RimMandrake.FlowWorks.RM_PitFillEffects.ProofReport`.
- First script: validation.py chain `pit_fill_effects` (water vs poison side by side, read per cell by fluid; lit oil burns its occupant) + `toggle_pit_fill_effects`. Never run live; the sluice-opening route in `## verify` is not scripted yet.
