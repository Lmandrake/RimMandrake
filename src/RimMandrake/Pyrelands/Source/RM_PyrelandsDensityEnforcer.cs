using RimWorld;
using Verse;

namespace RimMandrake.StarWars.FireEcology
{
    // Owner order 2026-09-17: "Make the plant density three times that. I mean
    // it. No more small nudges."
    //
    // MEASURED the same night: Pyrelands.xml declared plantDensity 1.55 /
    // wildPlantRegrowDays 9, yet the RUNNING game read plantDensity 1.0 and
    // wildPlantRegrowDays 5.806452 (= 9 / 1.55). Culprit BISECTED 2026-09-18
    // on minimal-list add-one-mod loads: Map Designer (zylle.mapdesigner) —
    // its startup pass caps BiomeDef.plantDensity at 1.0 and folds the ratio
    // into wildPlantRegrowDays (with density 16 it wrote 1.0 / 0.5625 = 9/16;
    // GeologicalLandforms core and BiomeTransitions both cleared). This
    // enforcer runs after it and wins; every previous density nudge was
    // silently eaten, which is why 1.15 -> 1.55 read "still too bare".
    //
    // So the XML is not authority enough here. This enforcer re-asserts OUR
    // numbers after every other mod has run: once when startup long events
    // finish (after all static ctors), and again on every game load/new game
    // (GameComponent.FinalizeInit — Verse.Game.FillComponents auto-instantiates
    // every GameComponent subclass). It logs whenever it finds the values
    // eaten, so the rewriter stays visible in Player.log.
    [StaticConstructorOnStartup]
    public static class RM_PyrelandsDensityStartup
    {
        static RM_PyrelandsDensityStartup()
        {
            LongEventHandler.ExecuteWhenFinished(RM_PyrelandsDensityEnforcer.Enforce);
        }
    }

    public class RM_PyrelandsDensityEnforcer : GameComponent
    {
        // Keep equal to Defs/BiomeDefs/Pyrelands.xml. The XML states intent;
        // this class is what makes it stick.
        // Desired cover per cell is min(plantDensity * fertility^2, 1) — 16
        // saturates every terrain down to light ash (0.25 fert); owner approved
        // the resulting ~96%-of-plantable look live, 2026-09-18.
        public const float PlantDensity = 16f;
        public const float WildPlantRegrowDays = 9f; // the XML's own value, un-eaten

        public RM_PyrelandsDensityEnforcer(Game game)
        {
        }

        public override void FinalizeInit()
        {
            Enforce();
        }

        public static void Enforce()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Pyrelands");
            if (biome == null)
            {
                return;
            }
            if (biome.plantDensity != PlantDensity || biome.wildPlantRegrowDays != WildPlantRegrowDays)
            {
                Log.Message(string.Format(
                    "[Pyrelands] density enforcer: plantDensity {0} -> {1}, wildPlantRegrowDays {2} -> {3} (something rewrote the XML values after load)",
                    biome.plantDensity, PlantDensity, biome.wildPlantRegrowDays, WildPlantRegrowDays));
                biome.plantDensity = PlantDensity;
                biome.wildPlantRegrowDays = WildPlantRegrowDays;
            }
        }
    }
}
