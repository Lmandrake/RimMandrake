using RimWorld;
using Verse;

namespace RimMandrake.Warcasket
{
    [DefOf]
    public static class RM_WarcasketDefOf
    {
        public static HediffDef RM_TerrainImmersionHazard;
        public static HediffDef RM_WarcasketBreach;
        public static StatDef RM_HazardousTerrainProtection;
        public static JobDef RM_CrackSarcophagus;

        static RM_WarcasketDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_WarcasketDefOf));
        }
    }
}
