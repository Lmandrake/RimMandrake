# FlowWorks settings — full-file review (BENCH, 2026-10-14)

Files (every line read, not the diff):
- `src/RimMandrake/FlowWorks/Source/RimMandrakeFlowWorksMod.cs` (1,492 lines at review start)
- `src/RimMandrake/FlowWorks/Source/Hose/RM_HoseSettings.cs` (336 lines)

Both reachable: the settings class is FlowWorks' `Mod`; the hose section is drawn and Scribed from it.

## Master -> dependent pairs (inert when master off?)

Every consumer of every declared dependent was read (grep `RimMandrakeFlowWorksSettings.<key>` / `RM_HoseSettings.<key>` across `src/`, then the code around each read).

| master | dependents | verdict |
|---|---|---|
| depthEngineEnabled | flowPerPulse, maxNetworkCells, networkSeamsMoveEnabled | inert: only set on the kernel in `DoPulse`, which returns early with the engine off |
| sourceBudgetEnabled | sourceBudgetMultiplier | **NOT inert (F2)**: `RM_LiquidStock.FormBody -> CapacityOf` reads it whenever a body first forms (`BodyAt` from the pulse, pumps, fire), budget on or off; the capacity is baked into the body forever |
| refillEnabled | refillRateMultiplier | inert: `Refill` only called under `refillEnabled` |
| rainFillsExcavationsEnabled | rainFillPerPulse | inert: `ApplyRain` returns first |
| viscosityEnabled | thickCreepEnabled | inert: `creepEnabled = viscosity && thickCreep` |
| liquidHeatPushEnabled | liquidHeatStrength | inert: `RM_LiquidHeat.Tick` returns before `Push` |
| canalFireEnabled | burn days x2, front speed, source reach, explosion/foam/rain | inert: every entry (NotifyFireAt, IgniteNow, NotifyExplosionAt, Tick, BurnPulse) gates on it; `IsSmothered`/`RainDouses` only reached from gated paths; Tick ExtinguishAll when off |
| pitDrowningEnabled | pitDrowningRateMultiplier | inert (read only when `drown`) |
| pitExposureEnabled | narrowing, coupling, resistance loss | inert: Tick and the coupling patch gate first |
| fallDamageEnabled | fallDamageMultiplier | inert |
| spikesEnabled | spikeDamageMultiplier | inert |
| pitDepthDrawOffsetEnabled | pitSinkPerLevel, pitLipOcclusionEnabled, pitSinkClampEnabled, pitHidesShadowEnabled | inert: draw postfix, lip MapComponentUpdate and shadow prefix all gate on it (`RM_PromotionProofs` reads pitSinkPerLevel: proof surface only) |
| pitLipOcclusionEnabled | pitLipOcclusion, pitLipOccupantCutEnabled | inert |
| pitLipOccupantCutEnabled | pitLipOccupantCutWidth | inert |
| excavationWallFacesEnabled | excavationWallMaterialEnabled, pitOutlineEnabled | inert: `Regenerate` returns, layer invisible |
| pitScorchEnabled | pitScorchFadeDays | effectively inert: `RM_PitScorch.MapComponentTick` keeps ageing marks laid before the switch with the kept value, but nothing is drawn or marked while off. Left as declared (nothing a player can see depends on it) |
| liquidBubblesEnabled | liquidBubbleDensity | inert |
| trapTriggerEnabled | trapSensitivityMultiplier | inert (`RunScan` returns) |
| superdeepRoomsEnabled | captureDownEnabled | inert (`&& RoomsOn` at both reads) |
| digFindsEnabled | local-only, chance, budget %, letter | inert: `OnCut` returns first; `MapBudget` only from `Ensure` after it |
| liquidDrillingEnabled | drillUnitsPerCycle | inert (TickRare returns) |
| swaleEnabled | swaleRateMultiplier | inert |
| hose `enabled` | tint, wobble, handling time, wind speed, auto-resume | inert: draw returns at `MapComponentUpdate`, work giver/float menu refuse, both jobs `FailOn(!enabled)` |
| hose tankModesEnabled | tankUnitsPerCycle | inert (`RM_LiquidNet` returns at line 675) |
| hose hoseHoldsLiquid | hoseUnitsPerCell | inert (`HeldCap`) |

Every `using (Dependent(...))` scope lists exactly its declared dependents; nested scopes (lip occlusion -> cut -> width) are correct.

Not declared but unreachable with the depth engine off (rain, refill, recession and others run inside `DoPulse`): a UX choice, not wrong behaviour. Not changed.

## Reset all

- **F1 (defect, fixed)**: Reset-all's work runs in the confirmation dialog's callback, OUTSIDE this window's frame. The rebuild/redraw/apply hooks used per-frame snapshots taken before `Section()` (built for the same-frame section reset), so a confirmed Reset-all that flipped `pondBedHollowEnabled`, `pitRelativeClimbEnabled`, climb multiplier, ramps, ramp span, `superdeepRoomsEnabled`, wall faces/material/outline/scorch, `liquidLooksEnabled` or `liquidSeeThroughEnabled` changed the setting but never re-pocketed the climb grid, never rebuilt pit rooms, never redrew walls and never applied/reverted the liquid looks. Fix: one `ApplyChangedSettings()` compare against last-applied values, run at the start and end of every frame; it also catches `PatchApplier.ReforceOff` and bridge writes (the old code left looks applied when ReforceOff forced the switch back off).
- Scope otherwise correct: every public static bool/float/int of the class (snapshotted at type init, below every field) plus `disabledFluids`; the sub-screens are not touched, as the summary says. Hose Reset-all: every hose field except the migration flag.
- Hose: `ResetToDefaults` (HoseProbe "defaults") was a hand-kept copy of every default; now calls `ResetAllFields` so a new setting cannot be missed.

## ExposeData round-trip

Scripted check: 112 declared fields, 112 Scribed, key == field name, every default argument equals its initialiser (`pitExposureNarrowing` uses `RM_PitExposureMath.DefaultNarrowing` = 8f = the literal). No key collisions across the main, Rivers, Machinery, sluice gate, kit, quarry and hose sections. Hose: defaults match; the `hose_tanksFeedHoses` legacy read and the maxLength migration are correct.

## Static per-game state

None. The statics are the session-wide settings themselves plus UI state (scroll, search, collapsed sections, measured height) and the new last-applied mirror of the settings. No table is keyed by thing, pawn or map.

## Other findings

- Hose: the comment said `shippedDefaults` "MUST stay the LAST static field initialiser", but two private UI initialisers come after it. Harmless; reworded to "below every public setting field".

## Fixes / commits

- F1 + F2 + hose tidy, with two source-shape selftests updated (`ReviewBatch56Checks.Settings_pit_section_reset_reruns_rebuild_redraw_apply`, `PondReturnChecks`). F2: `sourceBudgetMultiplier` is now Independent (live slider).
- Build: `winbuild.py FlowWorks`, 0 warnings, 0 errors. Selftests (`--only`): settings_screens, settings_kit, flowworks_stock, flowworks_rivers, 4/4 GREEN.
- Live check owed (not done, no bridge): confirm Reset-all with "Pits trap by relative height" off, then read `RM_PocketGrid` state for a re-pocket.

## CLEAN status

Re-reviewed after the edits (the changed regions in full; the rest was unchanged since the full read). No findings left in either file, so both are marked clean.
