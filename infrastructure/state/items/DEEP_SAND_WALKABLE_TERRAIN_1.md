# DEEP_SAND_WALKABLE_TERRAIN_1 — deep sand is walkable-slow, and it is a whole terrain type

Owner ruling 2026-09-27, typed into the sand-predator card's free text, verbatim:

> "Deep sand pools are NOT unwalkable, just very slowly. And they should be an
> entire terrain type, not just small pools. Some in the Long Shade, Muchly in
> the Stillsand."

This supersedes the closed `SAND_SWIMMERS_MOD_1` spec's "impassable like deep
water" line (which quoted his 2026-09-06 intent — the 09-27 ruling is newer and
wins).

## What is wrong today

`src/RimMandrake/FlowWorks/Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml` line 65:
`<passability>Impassable</passability>` (pathCost 300). The def's own comment
says impassability rides the Water tag — untangle that when changing it.

## spec

1. `RM_DeepSand` becomes passable at a punishing pathCost ("just very slowly" —
   tune against Marsh/water shallows; FOUNDRY's call, note the chosen value).
   Check what else follows from the Water tag before flipping passability.
2. Deep sand is an ENTIRE terrain type painted across desert maps, not
   occasional pools: present in the Long Shade ("some"), dominant presence in
   the Stillsand ("muchly"). Map-generation weighting per biome.
3. Sand fishing survives the change — the old hook was "fishable water you
   can't walk on"; now it is fishable ground you cross at a crawl. Re-check the
   fishing terrain requirements under the new passability.
4. The qorrax (ex-`JOE_Cephalope`, renamed by card 2026-09-27, our own
   recreated art owed) is the terrain's deadly sand-swimming predator; BENCH's
   reading is that its spawn ties to this terrain across both deserts rather
   than to one biome roster — that reading is recorded on
   `LONGSHADE_DESIGN_SITTING_1`, confirm against its rulings before wiring.

## verify

Quicktest: a pawn crosses deep sand slowly but does cross; the terrain reads as
a region of the map, not decoration; fishing still works on it.
