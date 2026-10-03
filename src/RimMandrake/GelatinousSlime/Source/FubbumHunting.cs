using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_FUBBUM_HUNTER_1: the fubbum is a vanilla predator (race.predator,
    // maxPreyBodySize 0.6: above the gelatid's 0.55, below any adult colonist's 1.0), so vanilla
    // hunting AI does the work; nothing here drives behaviour. This only applies the Mod Settings
    // switch to the loaded def: off => race.predator false, the animal hunts nothing.
    [StaticConstructorOnStartup]
    public static class FubbumHunting
    {
        static FubbumHunting()
        {
            Apply();
        }

        public static void Apply()
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Fubbum");
            if (def == null || def.race == null) return;
            def.race.predator = SlimeSettings.fubbumHunts;
        }
    }
}
