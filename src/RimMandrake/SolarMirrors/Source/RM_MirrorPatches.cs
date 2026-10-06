using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.4 / §5 E1: the two vanilla patches. Shade, exposure and sun
    // path cost are NOT patched: the light reaches CreatureBehaviors' shade grid through its public
    // light-source hook (IRM_LightLayer / RegisterLightSource), implemented by
    // RM_MapComponent_MirrorLight.

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
