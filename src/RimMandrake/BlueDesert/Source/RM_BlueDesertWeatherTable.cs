// BLUEDESERT_MECHANICS_BUILD_1 §4 — the Mod Settings seam for the three
// ruled weathers (RM_Haze, RM_IceSandDrift, RM_IceFog).
//
// WeatherDecider.CurrentWeatherCommonality reads
// map.Biome.baseWeatherCommonalities[i].commonality LIVE on every decision
// (RimSage, decompiled 1.6), so zeroing a record's commonality takes effect
// at the next weather change with no restart and no cache to bust. The
// XML-authored values are captured once and restored when the toggle is
// turned back on. Only RM_BlueDesert's own records are touched — the gate
// is on the BIOME, never on the weather defs globally.

using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.BlueDesert
{
    [StaticConstructorOnStartup]
    public static class RM_BlueDesertWeatherTable
    {
        private static readonly string[] RuledWeathers = { "RM_Haze", "RM_IceSandDrift", "RM_IceFog" };

        private static Dictionary<WeatherCommonalityRecord, float> authored;

        static RM_BlueDesertWeatherTable()
        {
            Apply();
        }

        public static void Apply()
        {
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_BlueDesert");
            if (biome?.baseWeatherCommonalities == null)
            {
                return;
            }
            if (authored == null)
            {
                authored = new Dictionary<WeatherCommonalityRecord, float>();
                foreach (WeatherCommonalityRecord rec in biome.baseWeatherCommonalities)
                {
                    if (rec?.weather != null && System.Array.IndexOf(RuledWeathers, rec.weather.defName) >= 0)
                    {
                        authored[rec] = rec.commonality;
                    }
                }
            }
            bool on = RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.ruledWeathersEnabled;
            foreach (KeyValuePair<WeatherCommonalityRecord, float> kv in authored)
            {
                kv.Key.commonality = RM_BlueKernel.WeatherCommonality(on, kv.Value);
            }
        }
    }
}
