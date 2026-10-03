# STILLSAND_CAVE_TIER_ROWS_1 — the krayt den, the sarlacc seep and the debt cave rows

Split from `STILLSAND_PRECIOUS_CAVES_1` spec 3. The precious table is data: each row is a
`RimMandrake.Stillsand.RM_PreciousCaveDef` whose `<elements>` are `RM_SetPieceElement` subclasses.
The Stillsand's cave elements are `RM_CaveElement_Terrain`, `RM_CaveElement_Things` and
`RM_CaveElement_Pawns`, and the shipped EnvironmentalHazards elements work there too. The RM tier
ships five rows. The other three belong to other tiers, so they arrive as defs in those tiers' mods.
Each such mod must declare `mandrake.rm.stillsand`.

## spec

1. **Krayt den (RSW):** a greater krayt, or its old den with skull and pearl (`RSW_KraytDragonSkull`,
   `RSW_KraytPearl`). This is the quest set piece in `STILLSAND_EVENT_CREATURES_1` §5.
2. **Sarlacc seep (RSW):** an `RSW_DeepDesertSeep` marker in the Sarlacc mod.
3. **Debt cave (Utinni):** a worn debt stone with Return lines, a mummified priest and sealed water
   jars. This depends on `STILLSAND_RETURN_RITUAL_1`'s debt stone.

## criteria

- With all three tiers loaded, the Stillsand Mod Settings list eight rows, and each new row can
  roll on a quicktest map.
