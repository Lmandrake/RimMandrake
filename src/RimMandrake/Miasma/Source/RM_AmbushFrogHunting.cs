using Verse;

namespace RimMandrake.Miasma
{
    // MIASMA_AMBUSH_FROG_REMAKE_1: the bozzuga is a vanilla predator (race.predator, maxPreyBodySize 0.6),
    // so vanilla hunting AI does the work. This only applies the Mod Settings switch to the loaded def:
    // off => race.predator false, the animal hunts nothing.
    [StaticConstructorOnStartup]
    public static class RM_AmbushFrogHunting
    {
        static RM_AmbushFrogHunting()
        {
            Apply();
        }

        public static void Apply()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Bozzuga");
            if (def == null || def.race == null) return;
            def.race.predator = RM_MiasmaSettings.ambushFrogHunts;
        }
    }
}
