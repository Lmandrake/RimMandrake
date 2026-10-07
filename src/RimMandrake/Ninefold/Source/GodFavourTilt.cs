using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Ninefold
{
    // ════════════════════════════════════════════════════════════════════
    // NINEFOLD_FAVOUR_ODDS_BUILD_1 — god favour shows only as ODDS.
    // Spec: design/Jawa/nine_faults_permanent_rite_2026-10-01.md §4 + §5.
    //
    // A god's band tilts the chance of a few incidents and weathers in his
    // domain on the clan's home maps. Nothing is labelled: no letter, no
    // tooltip, no hediff, no stat. The tilts are data
    // (Defs/RM_GodFavourTilts.xml), one RM_GodFavourTiltDef per row of the
    // §4 table, so BENCH tunes them without C#.
    //
    // Size (§4): per band, a multiplier on the incident's chance —
    // Exalted ×1.35, Content ×1.15, Neutral ×1, Slighted ×0.85,
    // Wrathful ×0.7. A `Less` row uses the RECIPROCAL (Exalted ×1/1.35):
    // "Where the row says the reverse, the factor is inverted." Several
    // rows on one def multiply (Eclipse: Ishko more, Sh'kaar less).
    // Mod Settings' strength slider scales the distance from ×1.
    //
    // Nothing new is Scribed here: the tilt reads the live band from
    // GameComponent_Ninefold.GetBand every call.
    // ════════════════════════════════════════════════════════════════════

    public enum FavourDirection
    {
        More,
        Less,
    }

    public class RM_GodFavourTiltDef : Def
    {
        public God god;
        public IncidentDef incident;
        public WeatherDef weather;
        public FavourDirection direction = FavourDirection.More;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
                yield return e;
            if (incident == null && weather == null)
                yield return "RM_GodFavourTiltDef needs an <incident> or a <weather>.";
            if (incident != null && weather != null)
                yield return "RM_GodFavourTiltDef takes ONE of <incident> or <weather>, not both.";
        }
    }

    public static class GodFavourTilts
    {
        private static Dictionary<IncidentDef, List<RM_GodFavourTiltDef>> byIncident;
        private static Dictionary<WeatherDef, List<RM_GodFavourTiltDef>> byWeather;

        public static float BandFactor(SatiationBand band)
        {
            switch (band)
            {
                case SatiationBand.Exalted: return 1.35f;
                case SatiationBand.Content: return 1.15f;
                case SatiationBand.Slighted: return 0.85f;
                case SatiationBand.Wrathful: return 0.7f;
                default: return 1f;
            }
        }

        private static void EnsureIndex()
        {
            if (byIncident != null) return;
            byIncident = new Dictionary<IncidentDef, List<RM_GodFavourTiltDef>>();
            byWeather = new Dictionary<WeatherDef, List<RM_GodFavourTiltDef>>();
            foreach (RM_GodFavourTiltDef t in DefDatabase<RM_GodFavourTiltDef>.AllDefsListForReading)
            {
                if (t.incident != null)
                {
                    if (!byIncident.TryGetValue(t.incident, out var l))
                        byIncident[t.incident] = l = new List<RM_GodFavourTiltDef>();
                    l.Add(t);
                }
                else if (t.weather != null)
                {
                    if (!byWeather.TryGetValue(t.weather, out var l))
                        byWeather[t.weather] = l = new List<RM_GodFavourTiltDef>();
                    l.Add(t);
                }
            }
        }

        private static bool Active(Map map, out GameComponent_Ninefold comp)
        {
            comp = null;
            if (!RM_NinefoldSettings.engineEnabled || !RM_NinefoldSettings.favourOddsEnabled) return false;
            if (map == null || !map.IsPlayerHome) return false;
            comp = GameComponent_Ninefold.Instance;
            return comp != null;
        }

        private static float Combine(List<RM_GodFavourTiltDef> rows, GameComponent_Ninefold comp)
        {
            float f = 1f;
            float strength = RM_NinefoldSettings.favourStrength;
            for (int i = 0; i < rows.Count; i++)
            {
                RM_GodFavourTiltDef t = rows[i];
                float band = BandFactor(comp.GetBand(t.god));
                if (t.direction == FavourDirection.Less) band = 1f / band;
                f *= 1f + (band - 1f) * strength;
            }
            return f < 0f ? 0f : f;
        }

        public static float IncidentFactor(IncidentDef def, IIncidentTarget target)
        {
            if (def == null || !(target is Map map)) return 1f;
            if (!Active(map, out var comp)) return 1f;
            EnsureIndex();
            return byIncident.TryGetValue(def, out var rows) ? Combine(rows, comp) : 1f;
        }

        public static float WeatherFactor(WeatherDef def, Map map)
        {
            if (def == null) return 1f;
            if (!Active(map, out var comp)) return 1f;
            EnsureIndex();
            return byWeather.TryGetValue(def, out var rows) ? Combine(rows, comp) : 1f;
        }
    }

    // §5: "a Harmony postfix on StorytellerComp.IncidentChanceFinal(
    // IncidentDef, IIncidentTarget)". RimSage-verified 2026-10-06: protected,
    // non-virtual, returns Mathf.Max(0, chance) — patched by name.
    [HarmonyPatch(typeof(StorytellerComp), "IncidentChanceFinal")]
    public static class Patch_FavourIncidentChance
    {
        [HarmonyPostfix]
        public static void Postfix(IncidentDef def, IIncidentTarget target, ref float __result)
        {
            if (__result <= 0f) return;
            __result *= GodFavourTilts.IncidentFactor(def, target);
        }
    }

    // §5: "a postfix on WeatherDecider.CurrentWeatherCommonality(WeatherDef)".
    // RimSage-verified 2026-10-06: private, reads the decider's private
    // `map` field — patched by name, map read through a field ref.
    [HarmonyPatch(typeof(WeatherDecider), "CurrentWeatherCommonality")]
    public static class Patch_FavourWeatherCommonality
    {
        private static readonly AccessTools.FieldRef<WeatherDecider, Map> MapRef =
            AccessTools.FieldRefAccess<WeatherDecider, Map>("map");

        [HarmonyPostfix]
        public static void Postfix(WeatherDecider __instance, WeatherDef weather, ref float __result)
        {
            if (__result <= 0f) return;
            __result *= GodFavourTilts.WeatherFactor(weather, MapRef(__instance));
        }
    }
}
