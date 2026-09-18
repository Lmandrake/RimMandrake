using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F1 build (fever_wood_kit_spec.md F1, "registered
    // pool terrain"). Closes the gap the F1/F6 build passes both flagged and
    // declined to guess through: RUT_FeverWoodMirrorPool was real and
    // reachable via dev-mode placement but never painted by any GenStep.
    // Blocked on an owner ruling on count/size/distribution; ruled
    // 2026-09-18 (ledger event on this item): "3-6 small pools per generated
    // map, scattered with a minimum spacing between them, never a single
    // large landmark-sized pool." That ruling is this class's
    // poolCountRange/poolRadiusRange defaults.
    //
    // Same idiom as RM_LivingBoleBiomeExtension / RM_RootCausewayBiomeExtension:
    // a BiomeDef opts in by carrying this extension; RM_GenStep_ScatterPools
    // reads it and is a harmless no-op on any biome that doesn't. Generic, not
    // Fever-Wood-specific — nothing below names the Fever Wood.
    //
    // Deliberately no marker Thing and no discrete pool-identity list: the
    // only consumer that cares whether a cell is a "pool" is
    // RUT_MapComponent_TheTenant, and it already finds pools by scanning the
    // terrain grid for RM_LurkingWaterExtension (TerrainDef.GetModExtension)
    // rather than by reading any registry this GenStep would populate — see
    // RUT_MapComponent_TheTenant.IsRegisteredWater/NearRegisteredWater. So
    // painting poolTerrain (itself already carrying RM_LurkingWaterExtension,
    // e.g. RUT_FeverWoodMirrorPool.xml) is the WHOLE job; there is nothing
    // else to wire.
    //
    //   <BiomeDef>
    //     <defName>RUT_FeverWood</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_MirrorPoolBiomeExtension">
    //         <poolTerrain>RUT_FeverWoodMirrorPool</poolTerrain>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_MirrorPoolBiomeExtension : DefModExtension
    {
        // What gets painted. Required.
        public TerrainDef poolTerrain;

        // OWNER RULING 2026-09-18 (FEVER_WOOD_MECHANICS_1 ledger): "3-6 small
        // pools per generated map".
        public IntRange poolCountRange = new IntRange(3, 6);

        // Each pool is painted as a GenRadial blob around its center — the
        // same radial-footprint idiom RM_GenStep_TerrainChannels/
        // RM_GenStep_RootCauseways already paint with, rather than inventing
        // a second rectangle-painting routine. Radius 1.0 reads as a ~2x2
        // pool, radius 2.0 as a ~4x4 pool — the owner's own "roughly 2x2 to
        // 4x4" band. INVENTED: the exact radius-to-tile-count mapping (the
        // ruling gave a tile-count band, not a radius).
        public FloatRange poolRadiusRange = new FloatRange(1f, 2f);

        // OWNER RULING 2026-09-18: "scattered with a minimum spacing between
        // them - unpredictable and eerie, not a landmark". INVENTED number:
        // the ruling names the requirement, not the distance. Kept well
        // below RM_LivingBoleBiomeExtension's 30 and
        // RM_RootCausewayBiomeExtension's fallback 25 on purpose — several
        // SMALL pools scattered across a 43-tile-region-sized map need
        // tighter packing than the one-or-two-per-map Greatbole/anchor
        // spacing those siblings tune for.
        public float minSpacing = 18f;

        public int edgeMargin = 8;

        // Placement attempts per pool before giving up on that one slot
        // (rejection sampling against spacing/edge/standable, same shape as
        // RM_GenStep_RootCauseways.PickFallbackAnchors). Not spec-given —
        // just a generous ceiling so a crowded or small map degrades to
        // fewer pools instead of looping forever.
        public int placementAttemptsPerPool = 60;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (poolTerrain == null)
            {
                yield return "RM_MirrorPoolBiomeExtension has no poolTerrain — RM_GenStep_ScatterPools would have nothing to paint.";
            }

            if (poolCountRange.max <= 0)
            {
                yield return "RM_MirrorPoolBiomeExtension.poolCountRange has no positive count — it would place nothing.";
            }
        }
    }
}
