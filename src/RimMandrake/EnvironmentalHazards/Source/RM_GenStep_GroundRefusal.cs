using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F5 build — see RM_GroundRefusalBiomeExtension.cs
    // for the full gap this closes (hard ban 4, "no heavy structures on the
    // ground") and why reusing vanilla MarshyTerrain via a GenStep — not a
    // bespoke TerrainDef, not a terrainsByFertility edit — is the chosen
    // fix.
    //
    // Ordered AFTER RUT_GenStep_RootCauseways (228, which as of
    // FEVERWOOD_BOUGH_SOIL_TERRAIN_1 also runs the third bough-soil pass
    // within that same GenStepDef/order) and after RUT_GenStep_ScatterPools
    // (226) — see this class's own GenStepDef order value in the
    // MapGeneration registration XML. Every lane/pool/crown-soil cell those
    // earlier steps painted is no longer Soil/SoilRich by the time this
    // step runs, so a plain "convert whatever is still in
    // convertFromTerrains" sweep naturally leaves every previously-painted
    // special cell alone — no cross-extension bookkeeping needed, just
    // ordering, same idiom RM_GenStep_ScatterPools's own header already
    // documents for the pool/causeway relationship.
    //
    // Deliberately blanket, not chance-gated or footprint-limited: hard ban
    // 4 is absolute ("No heavy structures on the ground"), not a rarity
    // dial, so every remaining eligible cell converts, every time.
    //
    // Generic on purpose, not Fever-Wood-specific, same idiom as every
    // other BiomeDef-modExtension-gated GenStep in this assembly: a no-op
    // on any biome without RM_GroundRefusalBiomeExtension.
    public class RM_GenStep_GroundRefusal : GenStep
    {
        public override int SeedPart => 1804662230;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_EnvironmentalHazardsSettings.groundRefusalEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: WORLDGEN-AFFECTING master toggle
            }

            RM_GroundRefusalBiomeExtension ext = map.Biome?.GetModExtension<RM_GroundRefusalBiomeExtension>();
            if (ext == null)
            {
                return;
            }

            if (ext.refusalTerrain == null || ext.convertFromTerrains == null || ext.convertFromTerrains.Count == 0)
            {
                Log.Error("[RM EnvironmentalHazards] RM_GenStep_GroundRefusal: biome " + map.Biome.defName
                    + "'s RM_GroundRefusalBiomeExtension has no refusalTerrain/convertFromTerrains — skipping.");
                return;
            }

            HashSet<TerrainDef> convertFrom = new HashSet<TerrainDef>(ext.convertFromTerrains);
            int converted = 0;

            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef current = map.terrainGrid.TerrainAt(c);
                if (current != null && convertFrom.Contains(current))
                {
                    map.terrainGrid.SetTerrain(c, ext.refusalTerrain);
                    converted++;
                }
            }

            if (converted == 0)
            {
                Log.Warning("[RM EnvironmentalHazards] RM_GenStep_GroundRefusal: converted 0 cells on "
                    + map.Biome.defName + " — every convertFromTerrains entry was already absent from the map.");
            }
        }
    }
}
