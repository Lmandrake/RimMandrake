using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// RAIN_FIX_FORCED_WEATHER_SKIPS_THE_LIST, bar no_ordinary_rain ("Ordinary rain never falls on a Pyrelands map; its only wet
    /// weather is black rain"). The biome's baseWeatherCommonalities hold no ordinary rain, but WeatherDecider.ChooseNextWeather
    /// has two roads off that list: a game condition's ForcedWeather (Royalty's weather controller, GameCondition_ForceWeather /
    /// CompCauseGameCondition_ForceWeather.RandomizeSettings, picks any isBad weather with canOccurAsRandomForcedEvent, which
    /// includes RainyThunderstorm and FoggyRain), and a tile mutator's MutateWeatherCommonalityFor (Odyssey's WetClimate adds 10 to
    /// Rain, RainyThunderstorm and FoggyRain whatever the biome lists). Every weather change and the loaded-game initial weather go
    /// through ChooseNextWeather, so one postfix there turns an ordinary rain into black rain on a map whose biome carries the
    /// ordinaryRainFallsBlack trait (RM_PyrelandsBiomeTraits, biome data: Patches/RM_Pyrelands_BiomeTraits.xml).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsNoOrdinaryRain
    {
        private static WeatherDef blackRain;

        static PyrelandsNoOrdinaryRain()
        {
            try
            {
                new Harmony("mandrake.rm.pyrelands.noordinaryrain").Patch(AccessTools.Method(typeof(WeatherDecider), "ChooseNextWeather"),
                    postfix: new HarmonyMethod(typeof(PyrelandsNoOrdinaryRain), nameof(Postfix_ChooseNextWeather)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] no ordinary rain: patch FAILED, a forced or mutator rain can fall on the Pyrelands: " + e.Message);
            }
        }

        public static void Postfix_ChooseNextWeather(Map ___map, ref WeatherDef __result)
        {
            try
            {
                if (__result == null || ___map?.Biome == null) return;
                // Weather data: the biome's own trait (RM_PyrelandsBiomeTraits.ordinaryRainFallsBlack), as its weather table is.
                bool black = RM_PyrelandsBiomeTraits.OrdinaryRainFallsBlack(___map.Biome);
                if (!RM_FireEcoKernel.RainBecomesBlackRain(__result.defName, black, PyrelandsMechanicsGate.On)) return;
                if (blackRain == null) blackRain = DefDatabase<WeatherDef>.GetNamedSilentFail(RM_FireEcoKernel.BlackRainDefName);
                if (blackRain != null) __result = blackRain;
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] no ordinary rain: " + e.Message, 0x46E21);
            }
        }
    }
}
