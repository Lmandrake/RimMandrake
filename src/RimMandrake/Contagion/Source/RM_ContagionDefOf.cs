using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1 — DefOf shortcuts for the genome/organ
    // mechanic. The host (RM_BloodyMess) is matched by defName string in
    // AmoebaHostUtility rather than through this class.
    [DefOf]
    public static class RM_ContagionDefOf
    {
        public static ThingDef RM_GenomeSample;
        public static HediffDef RM_AmoebaGestation;
        public static JobDef RM_InjectGenomeSample;

        // CONTAGION_GENOME_LIMB_AND_MATCH_BONUS_1
        public static ThoughtDef RM_GenomeMatchedInstall;

        static RM_ContagionDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ContagionDefOf));
        }
    }
}
