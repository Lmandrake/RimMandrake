using Verse;

namespace RimMandrake.FlowWorks.ManyWaters
{
    // DEEP_SAND_FIX_READS_AS_FRESHWATER: a terrain that carries vanilla's "Water" tag but holds no liquid. RM_DeepSand
    // keeps the tag because fishing reads it (TerrainDef.IsWater is HasTag("Water")); this marker tells FlowWorks' one
    // natural-liquid read, RM_MapComponent_Excavation.IsNaturalLiquid, that the ground is sand: no water source, no
    // lake square, no pond body, nothing for a pit dug beside it to fill from. Empty on purpose (a marker).
    // Checked by SelfTest/DeepSandSourceChecks.cs.
    public class RM_NotLiquidExtension : DefModExtension
    {
    }
}
