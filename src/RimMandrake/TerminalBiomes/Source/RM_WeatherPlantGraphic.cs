using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // GREYSEA_FLOOR_PASS_1 — the brine crown's retraction. Owner, by card 2026-10-18: "Picture only" —
    // during salt snow (RM_GreySaltSnow) the crown shows a pulled-in, spines-only form; NO gameplay effect
    // (its venom contact, path cost, beauty and hit points are untouched).
    //
    // The shape is the Cauldron's dewfall saturation (src/RimMandrake/Cauldron/Source/RM_CauldronDewfallVisuals.cs,
    // RM_DewfallSaturation) made weather-generic: a plant carrying RM_WeatherGraphicExtension shows its variant
    // texture while its map's current weather is the named WeatherDef. A postfix on Plant.Graphic returns the
    // variant only where vanilla would return the def's own graphic, so sowing / polluted / leafless / immature
    // keep their own look. Plants are printed into the section mesh, so a map component remeshes Things once
    // when the weather flips into or out of a trigger weather.
    //
    // DORMANT until art is installed: a variant whose texture is not on disk is skipped (logged once), and with
    // no variant on disk nothing is swapped and the map component does nothing.
    // Setting: greyCrownRetractionEnabled (Grey Sea group). Off: the crown always shows its open form.
    public class RM_WeatherGraphicExtension : DefModExtension
    {
        public WeatherDef weather;
        public string texPath;
        public System.Type graphicClass;    // null = the plant's own graphic class

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (weather == null) yield return "RM_WeatherGraphicExtension has no weather";
            if (texPath.NullOrEmpty()) yield return "RM_WeatherGraphicExtension has no texPath";
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_WeatherPlantGraphics
    {
        private static readonly Dictionary<ThingDef, (WeatherDef weather, Graphic graphic)> table =
            new Dictionary<ThingDef, (WeatherDef, Graphic)>();
        private static readonly HashSet<WeatherDef> triggers = new HashSet<WeatherDef>();

        public static bool Ready => table.Count > 0;
        public static bool IsTrigger(WeatherDef w) => w != null && triggers.Contains(w);

        static RM_WeatherPlantGraphics()
        {
            var missing = new List<string>();
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.plant == null || d.graphicData == null) continue;
                var ext = d.GetModExtension<RM_WeatherGraphicExtension>();
                if (ext == null || ext.weather == null || ext.texPath.NullOrEmpty()) continue;
                System.Type cls = ext.graphicClass ?? d.graphicData.graphicClass;
                bool onDisk = cls == typeof(Graphic_Random)
                    ? ContentFinder<Texture2D>.GetAllInFolder(ext.texPath).Any()
                    : ContentFinder<Texture2D>.Get(ext.texPath, false) != null;
                if (!onDisk) { missing.Add(d.defName); continue; }
                var gd = new GraphicData();
                gd.CopyFrom(d.graphicData);
                gd.texPath = ext.texPath;
                gd.graphicClass = cls;
                table[d] = (ext.weather, gd.Graphic);
                triggers.Add(ext.weather);
            }
            if (missing.Count > 0)
                Log.Message("[RM TerminalBiomes] weather plant variants not on disk yet (no swap for): " + string.Join(", ", missing));
        }

        public static bool TryVariant(Plant plant, Graphic vanillaResult, out Graphic variant)
        {
            variant = null;
            if (!table.TryGetValue(plant.def, out var row)) return false;
            WeatherDef cur = plant.MapHeld?.weatherManager?.curWeather;
            if (!RM_TerminalMiscKernel.WeatherVariantShows(RM_TerminalBiomesSettings.GreyCrownRetractionActive,
                    vanillaResult == plant.def.graphic, cur != null && cur == row.weather)) return false;
            variant = row.graphic;
            return true;
        }
    }

    [HarmonyPatch(typeof(Plant), nameof(Plant.Graphic), MethodType.Getter)]
    public static class RM_Patch_PlantWeatherGraphic
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref Graphic __result)
        {
            if (!RM_WeatherPlantGraphics.Ready) return;
            if (RM_WeatherPlantGraphics.TryVariant(__instance, __result, out Graphic v)) __result = v;
        }
    }

    // Remeshes Things once when the weather crosses into or out of a trigger weather. Nothing saved: the mesh
    // is built fresh on load, already in the current weather.
    public class RM_MapComponent_WeatherPlantGraphic : MapComponent
    {
        private const int CheckInterval = 250;
        private bool lastTrigger;
        private bool initialised;

        public RM_MapComponent_WeatherPlantGraphic(Map map) : base(map) { }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            lastTrigger = RM_WeatherPlantGraphics.IsTrigger(map.weatherManager?.curWeather);
            initialised = true;
        }

        public override void MapComponentTick()
        {
            if (!RM_WeatherPlantGraphics.Ready || Find.TickManager.TicksGame % CheckInterval != 0) return;
            bool now = RM_WeatherPlantGraphics.IsTrigger(map.weatherManager?.curWeather);
            if (RM_TerminalMiscKernel.WeatherVariantRemesh(initialised, lastTrigger, now))
                map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Things);
            lastTrigger = now;
            initialised = true;
        }
    }
}
