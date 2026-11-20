# RIMMANDRAKE_TRACE_FLOWWORKS_GEYSER_PALE_RING_NOT_STEAM

From his FlowWorks walk of 2026-11-20: `design/RimMandrake/validation_holding/flowworks_walk_20261120.md` row #4 (his words, the picture, the station).

## spec

A ring of pale whole squares (about radius 6) round the native steam geyser above stations 20-22, with paler squares even over station 21's water sheet (queue 2449), so it is an overlay drawn late, not a terrain [guess ~70%]. Not steam (round drifting puffs). Not FlowWorks: no FlowWorks code touches undug ground round a geyser [measured]. Same size as EnvironmentalHazards' vapor-column field (`src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_VaporColumns.cs:59`), which has no drawer [measured]. Another of the 316 mods is the likely source [guess ~60%].

## verify

On the review save: hover one ring square and one inside it (terrain line); list the overlays toggled on; if none, list the map components and mods that draw per cell there.

## criteria

Acceptance test: the live read names the drawer; after the fix (or a ruling that it is another mod's and is switched off on review maps), no pale ring shows round that geyser.
