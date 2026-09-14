using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // MIASMA_MECHANICS_1 M1 build (miasma_kit_spec.md M1: "Terrain painting
    // at gen time: the GenStep assigns the water/muck TerrainDefs by
    // salinity band"). Generic on purpose, per the spec's own words: "the
    // Webwork/Scald never need it, but any future two-water biome does."
    //
    //   <BiomeDef>
    //     <defName>RUT_Miasma</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_GradientAxisExtension">
    //         <waterBands>
    //           <li> <!-- fresh: no terrain named, leaves vanilla water untouched -->
    //             <max>0.34</max>
    //           </li>
    //           <li>
    //             <max>0.66</max>
    //             <terrainShallow>RM_WaterBrackishShallow</terrainShallow>
    //             <terrainDeep>RM_WaterBrackishDeep</terrainDeep>
    //           </li>
    //           <li>
    //             <max>1</max>
    //             <terrainShallow>RM_WaterBrineShallow</terrainShallow>
    //             <terrainDeep>RM_WaterBrineDeep</terrainDeep>
    //           </li>
    //         </waterBands>
    //         <landRepaintMinSalinity>0.85</landRepaintMinSalinity>
    //         <landRepaintSource><li>Mud</li><li>AB_FertileMud</li></landRepaintSource>
    //         <landTerrain>RUT_Jawa_SaltCrust</landTerrain>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    public class RM_GradientAxisExtension : DefModExtension
    {
        // Ordered fresh -> brine by ascending `max` (0..1, the upper
        // salinity bound each band covers). A band whose terrainShallow/
        // terrainDeep are both null is a genuine no-op — how "fresh" stays
        // whatever vanilla map-gen already painted, with no def to name.
        // Only cells whose CURRENT terrain carries the vanilla Water tag
        // (TerrainDef.IsWater) are ever considered for repaint here.
        public List<RM_GradientAxisWaterBand> waterBands = new List<RM_GradientAxisWaterBand>();

        // Non-water cells (the "muck" half of the spec's "water/muck
        // TerrainDefs by salinity band") at or above this salinity are
        // repainted to landTerrain — but ONLY when their current terrain is
        // listed in landRepaintSource, so this can never touch rock, stone
        // floors, or anything the biome's own terrainsByFertility didn't
        // put there. >= 1 (the default) disables land repainting entirely.
        public float landRepaintMinSalinity = 1f;
        public List<TerrainDef> landRepaintSource = new List<TerrainDef>();
        public TerrainDef landTerrain;

        // Perlin-noise wander added to the signed-distance axis before
        // banding (spec M1: "a signed-distance gradient with noise so the
        // salt line is a wandering front, not a ruler"). Amplitude is the
        // +/- salinity swing; cellScale is the noise frequency in map cells
        // (smaller = broader wander features).
        public float noiseAmplitude = 0.12f;
        public float noiseCellScale = 0.045f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (waterBands.NullOrEmpty() && landTerrain == null)
            {
                yield return "RM_GradientAxisExtension has no waterBands and no landTerrain — it would paint nothing.";
            }

            float lastMax = -1f;
            for (int i = 0; i < waterBands.Count; i++)
            {
                RM_GradientAxisWaterBand band = waterBands[i];
                if (band == null)
                {
                    yield return "RM_GradientAxisExtension.waterBands has a null entry at index " + i + ".";
                    continue;
                }

                if (band.max <= lastMax)
                {
                    yield return "RM_GradientAxisExtension.waterBands must be ordered by strictly ascending max (band " + i + " has max " + band.max + " <= previous " + lastMax + ").";
                }

                lastMax = band.max;
            }

            if (!waterBands.NullOrEmpty() && lastMax < 1f)
            {
                yield return "RM_GradientAxisExtension.waterBands' last band has max " + lastMax + " < 1 — salinity above it would never be repainted.";
            }

            if (landTerrain != null && landRepaintSource.NullOrEmpty())
            {
                yield return "RM_GradientAxisExtension has landTerrain set but no landRepaintSource — it would never fire (by design: it must never touch terrain it wasn't told about).";
            }
        }
    }

    public class RM_GradientAxisWaterBand
    {
        public float max = 1f;
        public TerrainDef terrainShallow;
        public TerrainDef terrainDeep;
    }
}
