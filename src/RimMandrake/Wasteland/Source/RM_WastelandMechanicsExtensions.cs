using System.Collections.Generic;
using Verse;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_MECHANICS_BUILD_1 §4 — the two DefModExtensions the storm
    // layer reads. Both live in THIS assembly, so a def in this mod can carry
    // them inline with no load-order or missing-type risk.
    //
    // Biome opt-in (RM_WastelandStormBiomeExtension): the storm MapComponent
    // is instantiated on EVERY map (vanilla builds one of each MapComponent
    // subclass per map), so it gates on this extension being present on the
    // map's BiomeDef and does nothing anywhere else. RM_Wasteland carries it
    // inline; any other biome may opt in by patch — the feature-gating the
    // Mod Settings ruling asks for ("biome-kit mechanics enabled in other
    // biomes without the biome").
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Marks a BiomeDef whose maps run the Wasteland storm layer
    /// (storm dose, ash-fall pollution, aftermath germination).</summary>
    public class RM_WastelandStormBiomeExtension : DefModExtension
    {
    }

    /// <summary>
    /// What a Wasteland weather does to the ground and the people under it while
    /// it runs. Read by <see cref="RM_MapComponent_WastelandStorms"/> — only on an
    /// opted-in biome's map. The dose rides vanilla's Biotech-era toxic mechanism
    /// (ToxicUtility / ToxicBuildup), per the 2026-09-28 ruling: "radiation AND
    /// pollution, ridden mostly on the Biotech pollution mechanism" — no parallel
    /// radiation system.
    /// </summary>
    public class RM_WeatherDoseExtension : DefModExtension
    {
        /// <summary>extraFactor passed to ToxicUtility.DoAirbornePawnToxicDamage every
        /// ToxicUtility.CheckInterval ticks for every unroofed spawned pawn. 1.0 = the
        /// vanilla toxic-fallout dose rate. 0 = no airborne dose.</summary>
        public float airborneToxicFactor;

        /// <summary>Unroofed cells that receive fall per in-game day on a 250x250 map
        /// (scaled by map area). Each is Biotech-polluted if it can be, and remembered
        /// as fresh fall for the aftermath plant. 0 = no fall.</summary>
        public float fallCellsPerDay;

        /// <summary>Plant germinated on this storm's fresh fall when the weather ends
        /// (the Cinderfelt). Null = no aftermath.</summary>
        public ThingDef aftermathPlant;

        /// <summary>Fraction of remembered fresh-fall cells that germinate the
        /// aftermath plant when the storm ends.</summary>
        public float aftermathSeedFraction = 0.35f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (airborneToxicFactor < 0f)
            {
                yield return "airborneToxicFactor must be >= 0.";
            }
            if (fallCellsPerDay < 0f)
            {
                yield return "fallCellsPerDay must be >= 0.";
            }
            if (aftermathPlant != null && aftermathPlant.plant == null)
            {
                yield return "aftermathPlant " + aftermathPlant.defName + " is not a plant.";
            }
            if (aftermathPlant != null && fallCellsPerDay <= 0f)
            {
                yield return "aftermathPlant is set but fallCellsPerDay is 0 — no fresh fall is ever "
                    + "recorded, so nothing can germinate.";
            }
            if (aftermathSeedFraction < 0f || aftermathSeedFraction > 1f)
            {
                yield return "aftermathSeedFraction must be in [0,1].";
            }
        }
    }
}
