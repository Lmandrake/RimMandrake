using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // SOLAR_HEAT_EXPOSURE_1 — the three engine seams, one Harmony id.
    // (This assembly already references Harmony — RM_SightBlockPatches,
    // RM_PinnedSunPatches — so no new dependency.)
    //
    // §1 HEAT. Postfix on Thing.AmbientTemperature (getter), pawns only: a
    //    spawned pawn on a sun-heat biome FEELS its cell's sun as extra
    //    degrees. That property is the one input vanilla's whole heat path
    //    reads — HediffGiver_Heat (Heatstroke, and burns past +150 over the
    //    comfort max), ThoughtWorker_Hot, sleep comfort — so apparel
    //    insulation, the comfortable range and heatstroke keep exactly their
    //    vanilla meaning (MEASURED via RimSage: HediffGiver_Heat.
    //    OnIntervalPassed reads pawn.AmbientTemperature against
    //    SafeTemperatureRange). No new heat hediff. The offset is scaled by
    //    body size (RM_SunHeatMath.BodySizeFactor), which is what makes how
    //    long a pawn can stay in the open a function of its size.
    //
    // §4 PATHING. Postfix on Pawn_PathFollower.GenerateNewPathRequest (the
    //    ONE path patch): vanilla passes no IPathGridCustomizer for ordinary
    //    movement, so we attach the map's shared sun-cost grid to undrafted
    //    pawns' requests. Every vanilla job — eat, haul, flee, hunt, wander —
    //    then prefers shade-to-shade routes, with no job giver rewritten.
    //    Drafted pawns go where the player sends them.
    //
    // §6 LEGIBILITY. Postfix on Pawn.GetGizmos adds the sun-load bar
    //    (RM_Gizmo_SunLoad) for a selected pawn on a sun-heat map.
    //
    // All three are inert on every map whose biome carries no
    // RM_SunHeatExtension (only those maps are registered) and when the
    // settings turn the feature off.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class RM_SunHeatPatches
    {
        private static readonly Dictionary<Map, RM_MapComponent_ShadeGrid> heatMaps =
            new Dictionary<Map, RM_MapComponent_ShadeGrid>();

        static RM_SunHeatPatches()
        {
            Harmony harmony = new Harmony("mandrake.rm.creaturebehaviors.sunheat");
            TryPatch(harmony, AccessTools.PropertyGetter(typeof(Thing), nameof(Thing.AmbientTemperature)),
                nameof(Postfix_AmbientTemperature), "sun heat (felt temperature)");
            TryPatch(harmony, AccessTools.Method(typeof(Pawn_PathFollower), "GenerateNewPathRequest"),
                nameof(Postfix_GenerateNewPathRequest), "sun-cost pathing");
            TryPatch(harmony, AccessTools.Method(typeof(Pawn), nameof(Pawn.GetGizmos)),
                nameof(Postfix_GetGizmos), "sun-load bar");
        }

        private static void TryPatch(Harmony harmony, MethodInfo target, string postfix, string what)
        {
            try
            {
                if (target == null)
                {
                    Log.Warning("[RM CreatureBehaviors] sun heat: target for " + what + " not found; that part is off.");
                    return;
                }
                harmony.Patch(target, postfix: new HarmonyMethod(typeof(RM_SunHeatPatches), postfix));
            }
            catch (Exception e)
            {
                Log.Error("[RM CreatureBehaviors] sun heat: patch for " + what + " failed; that part is off: " + e);
            }
        }

        /// <summary>Called by every shade grid on FinalizeInit; only maps
        /// whose biome carries RM_SunHeatExtension are kept.</summary>
        public static void Register(Map map, RM_MapComponent_ShadeGrid grid)
        {
            if (map != null && grid != null && grid.HeatExtension != null)
            {
                heatMaps[map] = grid;
            }
        }

        public static void Unregister(Map map)
        {
            if (map != null)
            {
                heatMaps.Remove(map);
            }
        }

        /// <summary>The active sun-heat grid for a pawn's map, or null.</summary>
        public static RM_MapComponent_ShadeGrid ActiveGridFor(Pawn pawn)
        {
            if (heatMaps.Count == 0 || pawn == null || !pawn.Spawned)
            {
                return null;
            }
            if (!heatMaps.TryGetValue(pawn.Map, out RM_MapComponent_ShadeGrid grid) || !grid.SunHeatActive)
            {
                return null;
            }
            return grid;
        }

        /// <summary>Degrees C of sun this pawn feels where it stands now.</summary>
        public static float SunOffsetFor(Pawn pawn, RM_MapComponent_ShadeGrid grid)
        {
            RM_SunHeatExtension ext = grid.HeatExtension;
            float exposure = grid.ExposureAt(pawn.Position);
            if (ext == null || exposure <= 0f)
            {
                return 0f;
            }
            float sizeFactor = RM_SunHeatMath.BodySizeFactor(pawn.BodySize, ext.bodySizeExponent,
                ext.minBodySizeFactor, ext.maxBodySizeFactor);
            return RM_SunHeatMath.HeatOffset(exposure, ext.heatOffsetC, RM_CreatureBehaviorsSettings.sunHeatStrength,
                sizeFactor, ext.maxHeatOffsetC);
        }

        public static void Postfix_AmbientTemperature(Thing __instance, ref float __result)
        {
            if (heatMaps.Count == 0 || !(__instance is Pawn pawn))
            {
                return;
            }
            try
            {
                RM_MapComponent_ShadeGrid grid = ActiveGridFor(pawn);
                if (grid != null)
                {
                    __result += SunOffsetFor(pawn, grid);
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] sun heat: " + e, 0x5A17E47);
            }
        }

        public static void Postfix_GenerateNewPathRequest(Pawn ___pawn, PathRequest __result)
        {
            if (heatMaps.Count == 0 || __result == null || __result.customizer != null)
            {
                return;
            }
            try
            {
                if (___pawn == null || ___pawn.Drafted)
                {
                    return;
                }
                RM_MapComponent_ShadeGrid grid = ActiveGridFor(___pawn);
                RM_SunPathCustomizer customizer = grid?.PathCustomizer;
                if (customizer != null)
                {
                    __result.customizer = customizer;
                }
            }
            catch (Exception e)
            {
                Log.ErrorOnce("[RM CreatureBehaviors] sun-cost pathing: " + e, 0x5A17E48);
            }
        }

        public static IEnumerable<Gizmo> Postfix_GetGizmos(IEnumerable<Gizmo> __result, Pawn __instance)
        {
            foreach (Gizmo g in __result)
            {
                yield return g;
            }
            if (heatMaps.Count == 0 || !RM_CreatureBehaviorsSettings.sunLoadBarEnabled)
            {
                yield break;
            }
            RM_MapComponent_ShadeGrid grid = ActiveGridFor(__instance);
            if (grid == null || Find.Selector == null || Find.Selector.NumSelected != 1)
            {
                yield break;
            }
            yield return new RM_Gizmo_SunLoad(__instance, grid);
        }
    }
}
