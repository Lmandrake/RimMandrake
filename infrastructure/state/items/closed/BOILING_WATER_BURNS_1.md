# BOILING_WATER_BURNS_1 — boiling water that burns you

Owner's ask, 2026-08-31: "Boiling water that burns you." Spec by BENCH,
mechanism MEASURED from 1.6 source: **pure defs, zero C# expected.**

## spec
Vanilla ships the whole pipeline: `TerrainDef.burnDamage` +
`burnIntervalTicks` + `ignitePawnsIntervalTicks`, consumed by
`HediffGiver_Terrain` — this is exactly how Odyssey lava burns
(`GameCondition_LavaFlow` + the lava TerrainDefs carry only these fields).

1. **`RUT_BoilingWater`** TerrainDef family (shallow/deep): water-colored
   steam-wreathed terrain with `burnDamage` tuned well below lava (painful,
   survivable crossing — a deterrent, not a wall) and no ignite (wet pawns
   don't catch fire; burns only).
2. **Placement:** the Scald's 30 near-volcanic lake tiles already carry
   `SteamGeysers_Increased`/`VEE_SulfuricLake` mutators — boiling water is
   the map-level expression on THOSE tiles' generated maps; plus vent-garden
   tiles in the Depths (`depths_concept.md` §6's vent gardens: heat + light +
   danger in one tile, now literal).
3. `heatPerTick` on the terrain pushes local ambient heat — the shore of a
   boiling pool is a warm room outdoors, which the colony can exploit
   (Zizzik-flavored free heating with a burn risk).
4. Start from `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md` (B64 lineage)
   for names/art notes; this item supersedes its mechanism section with the
   measured vanilla fields.

## verify
ONE unknown to settle first (source read left it open): whether
`HediffGiver_Terrain` is active on pawns by default or needs a carrier
hediff — test by spawning a pawn onto Odyssey lava in a quicktest BEFORE
authoring; if lava burns, our terrain burns. Then: pawn walked across
`RUT_BoilingWater` takes the predicted burn per interval; a pawn beside it
takes none. LIES: heatstroke from `heatPerTick` mimics burn damage in the
health tab — read the hediff type, not the red number.

## criteria
Crossing hurts on the predicted curve; shoreline is warm; no fire hediff ever
appears from water; art reads as boiling (steam motes) at display size.
