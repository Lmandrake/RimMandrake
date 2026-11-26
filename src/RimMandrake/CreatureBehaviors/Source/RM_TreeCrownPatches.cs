using System;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// TREE_SHADE_BUILD_CROWNS_ON_STILTS (design/RimMandrake/tree_shade_model_2026-10-19.md §4.3, §4.5):
    /// - Plant.DeSpawn: a shade tree leaving the map (felled, burned, eaten, crushed) asks its map's shade grid for a
    ///   recompute, so its crown shade goes with it (RM_MapComponent_ShadeGrid.RequestPlantRecompute).
    /// - The lower-left cell readout: the light line ("Lit") gains what Direct Sun does on that cell and what shades it,
    ///   "Lit · Direct Sun: shaded (veluthar canopy)" or "Lit · Direct Sun: full sun, +39 °C". Vanilla calls
    ///   MouseoverUtility.GetGlowLabelByValue for that line; the postfix appends only while the readout is drawing, so
    ///   the cell inspector's own light row is unchanged. No layout change, no transpiler.
    /// - PlaySettings: the shade overlay button in the bottom-right row (RM_ShadeOverlay).
    /// Each part is patched on its own; a missing target logs once and leaves that part off.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_TreeCrownPatches
    {
        [ThreadStatic] private static bool inReadout;

        static RM_TreeCrownPatches()
        {
            Harmony h = new Harmony("mandrake.rm.creaturebehaviors.treecrowns");
            Try("tree despawn clears its shade", () => h.Patch(AccessTools.Method(typeof(Plant), nameof(Plant.DeSpawn)),
                prefix: new HarmonyMethod(typeof(RM_TreeCrownPatches), nameof(Prefix_PlantDeSpawn))));
            Try("Direct Sun in the cell readout", () =>
            {
                h.Patch(AccessTools.Method(typeof(MouseoverReadout), nameof(MouseoverReadout.MouseoverReadoutOnGUI)),
                    prefix: new HarmonyMethod(typeof(RM_TreeCrownPatches), nameof(Prefix_Readout)),
                    finalizer: new HarmonyMethod(typeof(RM_TreeCrownPatches), nameof(Finalizer_Readout)));
                h.Patch(AccessTools.Method(typeof(MouseoverUtility), nameof(MouseoverUtility.GetGlowLabelByValue)),
                    postfix: new HarmonyMethod(typeof(RM_TreeCrownPatches), nameof(Postfix_GlowLabel)));
            });
            Try("shade overlay button", () => h.Patch(
                AccessTools.Method(typeof(PlaySettings), nameof(PlaySettings.DoPlaySettingsGlobalControls)),
                postfix: new HarmonyMethod(typeof(RM_ShadeOverlay), nameof(RM_ShadeOverlay.Postfix_PlaySettings))));
        }

        private static void Try(string what, Action patch)
        {
            try
            {
                patch();
            }
            catch (Exception e)
            {
                Log.Warning("[RM CreatureBehaviors] tree crowns: could not patch " + what + "; that part is off. " + e.Message);
            }
        }

        public static void Prefix_PlantDeSpawn(Plant __instance)
        {
            try
            {
                if (__instance.Spawned && RM_MapComponent_ShadeGrid.IsShadeTree(__instance.def))
                {
                    RM_MapComponent_ShadeGrid.For(__instance.Map)?.RequestPlantRecompute();
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] tree crowns despawn: " + e, 0x7C20A11);
            }
        }

        public static void Prefix_Readout()
        {
            inReadout = true;
        }

        public static Exception Finalizer_Readout(Exception __exception)
        {
            inReadout = false;
            return __exception;
        }

        public static void Postfix_GlowLabel(ref string __result)
        {
            if (!inReadout)
            {
                return;
            }
            try
            {
                Map map = Find.CurrentMap;
                string line = map != null ? ReadoutLine(map, UI.MouseCell()) : null;
                if (line != null)
                {
                    __result = __result + " · " + line;
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] tree crowns readout: " + e, 0x7C20A12);
            }
        }

        /// <summary>The readout's Direct Sun / shade words for this cell, or null where there is nothing to say (no
        /// grid, off the map, no Direct Sun and no shade). Under Direct Sun it gives the felt heat of a size-1 creature
        /// in the open (weather and the strength dial in it) or names the shade; elsewhere it names strong shade only.</summary>
        public static string ReadoutLine(Map map, IntVec3 c)
        {
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            if (grid == null || !c.InBounds(map) || !RM_CreatureBehaviorsSettings.shadeGridEnabled
                || !RM_CreatureBehaviorsSettings.shadeOverlayButton)
            {
                return null;
            }
            string cause = grid.ShadeCauseAt(c);
            if (grid.SunHeatActive)
            {
                float ex = grid.ExposureAt(c);
                if (RM_CreatureBehaviorsSettings.directSunWeatherDims)
                {
                    ex *= RM_WeatherSenseExtension.SunFactor(map);
                }
                float felt = RM_DirectSun.FeltOffsetC(ex, grid.EffectiveHeatOffsetC, RM_CreatureBehaviorsSettings.sunHeatStrength, 1f);
                if (felt < 0.5f)
                {
                    return "Direct Sun: shaded" + (cause != null ? " (" + cause + ")" : "");
                }
                string heat = "+" + felt.ToString("0") + " °C";
                return cause != null && ex < 0.999f
                    ? "Direct Sun: part shade (" + cause + "), " + heat
                    : "Direct Sun: full sun, " + heat;
            }
            return cause != null && grid.ShadeAt(c) >= 0.5f ? "Shade (" + cause + ")" : null;
        }
    }
}
