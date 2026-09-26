using RimWorld;
using Verse;

namespace RimMandrake.Greentide
{
    // GREENTIDE_DENSITY_SETTINGS_1. RM_Greentide_Biome.xml states the shipped
    // plantDensity/movementDifficulty intent (GREENTIDE_BIOME_DENSITY_1); this
    // writes whatever Mod Settings currently holds onto the live BiomeDef
    // instance. BiomeDef has no settings hook of its own, so direct field
    // assignment on the runtime object is the mechanism — the same shape as
    // src/RimMandrake/Pyrelands/Source/RM_PyrelandsDensityEnforcer.cs, reused
    // here rather than guessed at cold (that item confirmed a mod can rewrite
    // another mod's BiomeDef fields after load and have it stick; here we are
    // only ever rewriting our own).
    //
    // Runs at startup (after all static ctors, via LongEventHandler), on every
    // game/save load (GameComponent.FinalizeInit), and the instant the Mod
    // Settings window closes (RM_GreentideMod.WriteSettings) so a slider change
    // is felt without needing a restart.
    [StaticConstructorOnStartup]
    public static class RM_GreentideDensityStartup
    {
        static RM_GreentideDensityStartup()
        {
            LongEventHandler.ExecuteWhenFinished(RM_GreentideDensityApplier.Apply);
        }
    }

    public class RM_GreentideDensityApplier : GameComponent
    {
        public RM_GreentideDensityApplier(Game game)
        {
        }

        public override void FinalizeInit()
        {
            Apply();
        }

        public static void Apply()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Greentide");
            if (biome == null)
            {
                return;
            }
            biome.plantDensity = RM_GreentideSettings.plantDensity;
            biome.movementDifficulty = RM_GreentideSettings.movementDifficulty;
        }
    }
}
