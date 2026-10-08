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
            ApplyRoil(biome);
        }

        // GREENTIDE_BASE_PORT_BUILD_1: the Roil toggle. Adds or removes RM_RoilLock in the biome's
        // biomeMapConditions and RM_RoilWeather's weather-table row, idempotently, so a settings change
        // reaches the next generated map.
        private static void ApplyRoil(BiomeDef biome)
        {
            GameConditionDef roilLock = DefDatabase<GameConditionDef>.GetNamedSilentFail("RM_RoilLock");
            WeatherDef roilWeather = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_RoilWeather");
            if (roilLock == null || roilWeather == null)
            {
                return;
            }
            if (biome.biomeMapConditions == null)
            {
                biome.biomeMapConditions = new System.Collections.Generic.List<GameConditionDef>();
            }
            // Mirror the biome into the kernel's three facts, apply the rule, and write the answer back.
            var state = new RM_RulesKernel.RoilBiome
            {
                HasLock = biome.biomeMapConditions.Contains(roilLock),
                HasRecord = biome.baseWeatherCommonalities.Exists(r => r.weather == roilWeather),
                HaveStash = roilWeatherRecord != null,
            };
            state.Apply(RM_GreentideSettings.roilEnabled);
            if (state.HasLock && !biome.biomeMapConditions.Contains(roilLock))
            {
                biome.biomeMapConditions.Add(roilLock);
            }
            if (!state.HasLock)
            {
                biome.biomeMapConditions.Remove(roilLock);
            }
            WeatherCommonalityRecord rec = biome.baseWeatherCommonalities.Find(r => r.weather == roilWeather);
            if (state.HasRecord && rec == null && roilWeatherRecord != null)
            {
                biome.baseWeatherCommonalities.Add(roilWeatherRecord);
            }
            else if (!state.HasRecord && rec != null)
            {
                roilWeatherRecord = rec;
                biome.baseWeatherCommonalities.Remove(rec);
            }
        }

        private static WeatherCommonalityRecord roilWeatherRecord;
    }
}
