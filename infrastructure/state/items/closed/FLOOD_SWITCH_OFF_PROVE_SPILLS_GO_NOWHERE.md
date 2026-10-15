# FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE

Found by the independent P4-P8 review: `Transient/flowworks_review_P4_P8_20261011.md` (P6a section).

## What is true now (origin/main 9272c1344)
- P6a (57b4b4120) made an excavated cell HandsOff for a FlowWorks spill when `legacyFloodViaEngineEnabled`
  ("Spilled liquid fills channels properly") is OFF. That fix is right for the race: vanilla's queued temp-terrain
  removal strips whatever temp terrain is there (`TempTerrainManager.Tick` -> `RemoveTempTerrain`), engine fill included.
- But `Flood_FlowWorks.CanFloodInto` only admits a cell where `CanLiquidEnter` holds (`DepthAt > Surface`): an excavated
  cell, or natural liquid read-through (water refused by `IsWater`). So with OFF a release places NOTHING except over
  natural non-water liquid, its frontier empties and it is destroyed with its volume unspent. Every spill caller
  (TarPitBelch, ForgeCycle, HotLiquid kits) goes inert.
- The settings text added by P6a ("Off: a spill never enters a dug channel, so it never clashes with the channel's own
  liquid") reads as if spills still happen elsewhere.

Default is ON, so shipped behaviour is unaffected.

## verify
With the switch OFF, a spill next to a dug channel either places what the settings text promises, or the text says it places nothing.

## Decide
Either (a) accept OFF = spills do nothing, and make the settings line say so; or (b) give OFF a real meaning (e.g.
surface temp-terrain puddles beside channels, which needs CanFloodInto to admit surface cells when OFF).

NEXT: pick (a) or (b); for (a) correct the CheckboxLabeled text in RimMandrakeFlowWorksMod.cs (~line 741) and rebuild.
