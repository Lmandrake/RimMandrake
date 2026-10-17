using RimWorld;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    [DefOf]
    public static class RM_ExplosiveGrowthDefOf
    {
        // Defs/SoundDefs/RM_ExplosiveGrowth_Sounds.xml — vanilla tree clips
        // re-pitched; no new audio commissioned.
        public static SoundDef RM_EG_Creak;
        public static SoundDef RM_EG_Split;
        public static SoundDef RM_EG_Pop;
        public static SoundDef RM_EG_Rupture;

        // Defs/ThingDefs_Filth/RM_WaterFilth.xml: standing water that is a water source (D6, D7).
        public static ThingDef RM_Filth_WaterSpill;
        public static ThingDef RM_Filth_RainPuddle;

        static RM_ExplosiveGrowthDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_ExplosiveGrowthDefOf));
        }
    }
}
