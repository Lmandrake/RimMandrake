using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.TerminalBiomes
{
    // HAZARD_CLOCK_INSPECT_LINES_1 (TB-4). Three numbers that already exist, shown where the player already looks:
    //   a bright Grey Sea lamp  -> how long it has burned steadily (the burn clock; the threshold is NOT shown,
    //                              the watcher at the rim stays the warning),
    //   a twilight well         -> opening / standing / waning and time left,
    //   a grav engine           -> crust cells still on the deck (Grey Sea only).
    // Text only. One postfix on ThingWithComps.GetInspectString (Building overrides call down into it); every branch
    // is gated on the setting and returns at once for anything that is not one of the three.
    [HarmonyPatch(typeof(ThingWithComps), nameof(ThingWithComps.GetInspectString))]
    public static class RM_Patch_HazardClockInspect
    {
        [HarmonyPostfix]
        public static void Postfix(ThingWithComps __instance, ref string __result)
        {
            if (!RM_TerminalBiomesSettings.hazardClockInspectEnabled || __instance == null || !__instance.Spawned)
            {
                return;
            }
            string line = RM_HazardClockInspect.LineFor(__instance);
            if (!line.NullOrEmpty())
            {
                __result = __result.NullOrEmpty() ? line : __result + "\n" + line;
            }
        }
    }

    public static class RM_HazardClockInspect
    {
        public static string LineFor(Thing t)
        {
            Map map = t.Map;
            if (map == null)
            {
                return null;
            }
            if (t.def.defName == "RM_Skylight")
            {
                return WellLine(t, map);
            }
            if (t is Building_GravEngine engine)
            {
                return CrustLine(engine, map);
            }
            if (t is Building && map.Biome != null && map.Biome.defName == RM_GreyCrust.GreyBiome)
            {
                return LampLine(t, map);
            }
            return null;
        }

        public static string LampLine(Thing t, Map map)
        {
            if (!RM_TerminalBiomesSettings.GreyLampGiantActive || !RM_MapComponent_GreyLampWatch.IsWorklightClass(t, out CompGlower glower) || !glower.Glows)
            {
                return null;
            }
            RM_MapComponent_GreyLampWatch watch = map.GetComponent<RM_MapComponent_GreyLampWatch>();
            if (watch == null)
            {
                return null;
            }
            int ticks = watch.LitTicksOf(t);
            return "RM_HazardClockLamp".Translate(ticks.ToStringTicksToPeriod());
        }

        public static string WellLine(Thing t, Map map)
        {
            RM_MapComponent_WellLedger ledger = RM_MapComponent_WellLedger.GetFor(map);
            if (ledger == null || !ledger.TryGetWellOf(t, out WellStage stage, out int remaining))
            {
                return null;
            }
            switch (stage)
            {
                case WellStage.Opening: return "RM_HazardClockWellOpening".Translate();
                case WellStage.Waning: return "RM_HazardClockWellWaning".Translate(remaining.ToStringTicksToPeriod());
                case WellStage.Standing: return "RM_HazardClockWellStanding".Translate(remaining.ToStringTicksToPeriod());
                default: return null;
            }
        }

        public static string CrustLine(Building_GravEngine engine, Map map)
        {
            if (!RM_GreyCrust.Active || map.Biome == null || map.Biome.defName != RM_GreyCrust.GreyBiome)
            {
                return null;
            }
            RM_MapComponent_GreyHullCrust crust = map.GetComponent<RM_MapComponent_GreyHullCrust>();
            if (crust == null)
            {
                return null;
            }
            return "RM_HazardClockCrust".Translate(crust.CountCrust(engine));
        }
    }
}
