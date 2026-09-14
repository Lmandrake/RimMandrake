using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FORGE_MECHANICS_1 F4 "the foundry tower dungeon shell" — placement
    // gate for RUT_FoundryTowerEntrance (forge_kit_spec.md F4: "0-2 tower
    // entrances per Volcano/LavaField-zone map, 0-1 on Pyroclastic skirts").
    //
    // Generic, not Forge-specific — exactly the extension point
    // RM_GenStep_PlacedSetPieces.cs's own header documents ("each kit writes
    // its own ScattererValidator subclass... e.g. a brine-shallow-water
    // validator"): a biome-membership gate is broadly reusable by any future
    // kit that needs its own set-piece scatterer confined to specific
    // biomes, so this lives in the shared RM_ home rather than a
    // Forge-only file.
    //
    // FORGE_MECHANICS_1.md's own F2/F5/F6 build pass already found (and
    // this pass rechecked) that BIOME_OWNERSHIP_WAVE_1 merged all three
    // donor biomes the kit spec names (Volcano/Advanced Biomes,
    // LavaField/Odyssey, AB_PyroclasticConflagration/Alpha Biomes) into one
    // owned BiomeDef, RUT_TheForge — the three donor defNames no longer
    // back any biome this campaign's maps can actually generate on. So this
    // validator is configured with RUT_TheForge only, and the spec's own
    // "0-2 Volcano/LavaField vs 0-1 Pyroclastic" split collapses to one
    // uniform count for the whole (now single) biome, same collapse F5's
    // own edge-band ring already made for the identical reason — flagged in
    // the item file as owed, not silently dropped: splitting the count by
    // sub-zone again needs an elevation or TileMutatorDef signal this def
    // does not yet carry.
    public class RM_ScattererValidator_Biome : ScattererValidator
    {
        public List<BiomeDef> allowedBiomes = new List<BiomeDef>();

        public override bool Allows(IntVec3 c, Map map)
        {
            if (allowedBiomes.NullOrEmpty())
            {
                Log.ErrorOnce(
                    "[RM EnvironmentalHazards] RM_ScattererValidator_Biome has no allowedBiomes "
                    + "configured — refusing every site rather than placing globally.",
                    1997332416);
                return false;
            }

            return map.Biome != null && allowedBiomes.Contains(map.Biome);
        }
    }
}
