using RimWorld;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_GENOME_ORGAN_GROWING_1 — DefOf shortcuts for the genome/organ
    // mechanic. AA_RedGoo (the host) is a soft, MayRequire="sarg.alphaanimals"
    // dependency and is looked up by defName string at call sites instead of
    // through this class, so this mod never hard-references Alpha Animals.
    [DefOf]
    public static class RM_ContagionDefOf
    {
        public static ThingDef RM_GenomeSample;
        public static HediffDef RM_AmoebaGestation;
        public static JobDef RM_InjectGenomeSample;

        static RM_ContagionDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ContagionDefOf));
        }
    }
}
