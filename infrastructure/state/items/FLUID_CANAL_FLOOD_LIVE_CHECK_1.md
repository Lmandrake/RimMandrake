## spec

`FLUID_CANAL_FLOOD_TUNING_GAPS_1` findings 1/2/3 were fixed in code and
compile clean, but the mod is NOT deployed and nobody has watched a flood
recede or a floor come back. This is that watch — a quicktest, not the
campaign, and not a cold load: the 13-mod minimal list is enough. Requires
Odyssey active and `mandrake.rm.fluidcanals` deployed.

Setup: place `RM_FluidSpring_Test`, build a concrete floor on a cell next to
it, then `Actions\RMFluidCanals\Instant-dig canal at cell` adjacent to the
spring. Read cells with `Actions\RMFluidCanals\Report cell (RAW)`.

## verify

1. **Recoverable (the owner's ruling, finding 1).** A flooded cell reports
   `terrain=ShallowFloodwater tempTerrain=ShallowFloodwater underneath=<the
   cell's real terrain>`. On the concrete cell `underneath=Concrete` is the
   whole proof. FAIL if `tempTerrain=none` (the fluid went to the permanent
   layer) or `underneath` reads the floodwater. Then let it drain
   (`floodedTicks` 300000 — dev-mode tick advance) and confirm the concrete
   is back and the cell is re-diggable.
2. **Rate (finding 3).** The flood advances ~1 tile per 60 ticks: a 60-volume
   spring covers ~60 tiles in ~1.5 in-game hours. FAIL if it is one tile per
   in-game hour (the old rate-divisor behaviour).
3. **Boxed-in expiry (finding 2).** Wall a spring in so the flood is boxed
   after a few tiles. The `Flood_FluidCanal` must be GONE by the
   `expiresAtTick` its own report prints (the report also prints `nowTick`),
   and the tiles it did place must still drain on schedule afterwards — the
   removals live on the map's `TempTerrainManager`, not on the flood.

## note 2026-09-03 (BENCH)

Deploy state measured: `FluidCanals` repo↔game **in sync (9 files)** but
`mandrake.rm.fluidcanals` is **not in the active ModsConfig** — the live session
(full 578 list, gravship_scratch_b) cannot run this. Rides the next game-DOWN:
swap to the minimal list WITH Odyssey + fluidcanals enabled (`modset_builder.py`),
22 s load, then the three verify steps. Do not spend a full-list session on it.

## criteria

All three read as expected on a live map, or the reading that failed is
written back into `FLUID_CANAL_FLOOD_TUNING_GAPS_1`'s own record with what it
actually did.
