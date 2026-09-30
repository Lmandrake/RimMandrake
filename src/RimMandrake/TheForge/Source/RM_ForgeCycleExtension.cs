using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_CYCLE_MECHANICS_1. The XML surface of the six-phase grand cycle,
    // carried on the pulse GameConditionDef (RM_ForgePulse) next to its
    // WeatherPulseExtension. Any biome that lists a condition carrying this
    // extension gets the cycle, which is how the kit mechanic can be enabled
    // outside the Forge (settings law: biome-kit mechanics are not bound to
    // the biome).
    //
    // Every number here is an INVENTED tuning value, not a ruling: the item
    // fixes the ORDER and the CONTENT of the phases, not their lengths.
    public class RM_ForgeCycleExtension : DefModExtension
    {
        // Phase lengths, in in-game hours.
        public FloatRange stillHours = new FloatRange(48f, 72f);
        public FloatRange gasWashHours = new FloatRange(2f, 3f);
        public FloatRange rainHours = new FloatRange(6f, 9f);
        public FloatRange freezeHours = new FloatRange(10f, 14f);
        public FloatRange growthHours = new FloatRange(54f, 66f);
        public FloatRange cracksHours = new FloatRange(6f, 8f);
        public FloatRange meltHours = new FloatRange(1.5f, 2.5f);

        // Telegraph: the hiss letter lands this long before the gas wash.
        public float hissLeadHours = 1.5f;

        // Phase 2, gas wash.
        public IntRange gasWashWaves = new IntRange(2, 4);
        public float gasWashRadius = 7f;
        public float gasWashCellChance = 0.3f;
        public FloatRange gasWashFireSize = new FloatRange(0.3f, 0.7f);

        // Phase 3, flooding (FlowWorks water releases).
        public IntRange floodReleases = new IntRange(2, 4);
        public int floodTilesPerRelease = 45;

        // Phase 4, the freeze. Only cells whose terrain is in this list AND
        // carry no temporary terrain already are frozen; the crust is laid
        // on the temp layer, so melting is removing it and the lava beneath
        // was never touched.
        public List<TerrainDef> freezableTerrains = new List<TerrainDef>();
        public TerrainDef basaltTerrain;
        public TerrainDef pumiceTerrain;
        public float pumiceChance = 0.3f;
        public int maxFrozenCells = 6000;
        public WeatherDef freezeWeather;

        // Phase 5, the growth.
        public ThingDef gardenDef;
        public IntRange gardenCount = new IntRange(5, 10);
        public float gardenStartGrowth = 0.05f;

        // Phase 6, glowing cracks then melt-back.
        public TerrainDef crackTerrain;
        public float meltPawnBurn = 18f;
        public int meltPawnBurnHits = 4;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (basaltTerrain != null && !basaltTerrain.temporary)
            {
                yield return "RM_ForgeCycleExtension.basaltTerrain " + basaltTerrain.defName + " must be temporary (it is laid on the temp-terrain layer).";
            }
            if (pumiceTerrain != null && !pumiceTerrain.temporary)
            {
                yield return "RM_ForgeCycleExtension.pumiceTerrain " + pumiceTerrain.defName + " must be temporary.";
            }
            if (crackTerrain != null && !crackTerrain.temporary)
            {
                yield return "RM_ForgeCycleExtension.crackTerrain " + crackTerrain.defName + " must be temporary.";
            }
        }
    }
}
