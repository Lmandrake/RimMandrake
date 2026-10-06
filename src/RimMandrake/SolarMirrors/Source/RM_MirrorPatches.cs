using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using Unity.Collections;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.3 / §2.4, done from THIS mod. The design's P0 is a public
    // light-source hook inside CreatureBehaviors; this build could not edit that mod, so the
    // same composition order is applied by postfix:
    //   base exposure (CreatureBehaviors, unchanged) -> lit exposure = max(base, min(1, light))
    //   -> path cost from lit exposure -> (patch graph reads the same cached array).
    // Cover (parasols, living casters) is applied by ExposureAt after the cache, so a parasol
    // still shades you in a beam. ShadeAt is cut to (1 - light) but never below that cover.
    // When CreatureBehaviors gains the P0 hook, these three patches are what it replaces.

    [HarmonyPatch(typeof(RM_MapComponent_ShadeGrid), "RebuildHeatLayers")]
    public static class RM_Patch_ShadeGrid_RebuildHeatLayers
    {
        private static readonly AccessTools.FieldRef<RM_MapComponent_ShadeGrid, float[]> ExposureRef =
            AccessTools.FieldRefAccess<RM_MapComponent_ShadeGrid, float[]>("exposure");

        private static readonly AccessTools.FieldRef<RM_MapComponent_ShadeGrid, RM_SunPathCustomizer> CustomizerRef =
            AccessTools.FieldRefAccess<RM_MapComponent_ShadeGrid, RM_SunPathCustomizer>("pathCustomizer");

        public static void Postfix(RM_MapComponent_ShadeGrid __instance)
        {
            if (!RM_SolarMirrorsSettings.shadeEffect)
            {
                return;
            }
            float[] exposure = ExposureRef(__instance);
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(__instance.map);
            if (exposure == null || comp == null || !comp.AnyLight)
            {
                return;
            }
            // Under ambient heat (steam, volcanic) light does nothing for heat, as shade does nothing.
            if (__instance.EffectiveHeatKind == RM_HeatKind.ambient)
            {
                return;
            }
            RM_SunHeatExtension ext = __instance.HeatExtension;
            RM_SunPathCustomizer cust = CustomizerRef(__instance);
            // The customizer was created a moment ago inside RebuildHeatLayers and no path request
            // has seen it yet, so writing its grid here is the same as writing it before creation.
            NativeArray<ushort> cost = cust != null ? cust.GetOffsetGrid() : default;
            bool writeCost = cust != null && cost.IsCreated && ext != null;
            float strength = RM_CreatureBehaviorsSettings.sunPathCostMultiplier;
            var cells = comp.LitCells;
            for (int k = 0; k < cells.Count; k++)
            {
                int i = cells[k];
                if (i < 0 || i >= exposure.Length)
                {
                    continue;
                }
                float lit = Mathf.Max(exposure[i], Mathf.Min(1f, comp.LightAtIndex(i)));
                if (lit <= exposure[i])
                {
                    continue;
                }
                exposure[i] = lit;
                if (writeCost && i < cost.Length)
                {
                    cost[i] = RM_SunHeatMath.PathCost(lit, ext.sunPathCostPerCell, strength);
                }
            }
        }
    }

    [HarmonyPatch(typeof(RM_MapComponent_ShadeGrid), nameof(RM_MapComponent_ShadeGrid.ShadeAt))]
    public static class RM_Patch_ShadeGrid_ShadeAt
    {
        public static void Postfix(RM_MapComponent_ShadeGrid __instance, IntVec3 cell, ref float __result)
        {
            if (__result <= 0f || !RM_SolarMirrorsSettings.shadeEffect)
            {
                return;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(__instance.map);
            if (comp == null || !comp.AnyLight)
            {
                return;
            }
            float l = comp.LightAt(cell);
            if (l <= 0f)
            {
                return;
            }
            float cover = __instance.GearShadeAt(cell);
            if (RM_CreatureBehaviorsSettings.movingShadeEnabled)
            {
                cover = Mathf.Max(cover, __instance.MovingShadeAt(cell));
            }
            __result = Mathf.Max(Mathf.Min(__result, 1f - Mathf.Min(1f, l)), cover);
        }
    }

    /// <summary>Design §2.4: the one funnel for gameplay glow (plant growth, sowing, work in the
    /// dark). It never brightens the rendered ground; RM_MapComponent_MirrorLight draws that.
    /// PROVISIONAL: glow + light, capped at 1, so the Long Shade's 0.8 sky reads 1.0 in a beam.</summary>
    [HarmonyPatch(typeof(GlowGrid), nameof(GlowGrid.GroundGlowAt))]
    public static class RM_Patch_GlowGrid_GroundGlowAt
    {
        public static void Postfix(IntVec3 c, bool ignoreSky, Map ___map, ref float __result)
        {
            if (ignoreSky || __result >= 1f || !RM_SolarMirrorsSettings.glowEffect)
            {
                return;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(___map);
            if (comp == null || !comp.AnyLight)
            {
                return;
            }
            float l = comp.LightAt(c);
            if (l > 0f)
            {
                __result = Mathf.Min(1f, __result + l);
            }
        }
    }

    /// <summary>Design §5 E1: a light-gated bench (the solar furnace) takes bills only while
    /// concentrated mirror light falls on it. WorkGiver_DoBill and Building_WorkTable's
    /// CurrentlyUsableForBills both go through UsableForBillsAfterFueling.</summary>
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsableForBillsAfterFueling))]
    public static class RM_Patch_WorkTable_UsableForBills
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            RM_CompLightReceiver r = __instance.GetComp<RM_CompLightReceiver>();
            if (r != null && r.Props.gatesBills && !r.BillsAllowed)
            {
                __result = false;
            }
        }
    }
}
