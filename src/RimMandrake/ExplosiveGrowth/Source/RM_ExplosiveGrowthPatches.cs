using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    [StaticConstructorOnStartup]
    public static class RM_ExplosiveGrowthBootstrap
    {
        static RM_ExplosiveGrowthBootstrap()
        {
            try
            {
                RM_ExplosiveGrowthRegistry.Rebuild();
            }
            catch (Exception e)
            {
                Log.Error("[RM ExplosiveGrowth] failed to build the plant table; the mechanic is OFF this session: " + e);
                return;
            }

            new Harmony("mandrake.rm.explosivegrowth").PatchAll();

            int[] t = RM_ExplosiveGrowthRegistry.CountByTop;
            Log.Message(string.Format(
                "[RM ExplosiveGrowth] {0} plant defs soak (churn {1}, burst {2}, slime {3}, tinder {4}, rupture {5}, flush {6}), {7} never soak; " +
                "roster rows resolved {8}, absent {9}; rupture kinds {10}, mutation hediffs {11}.",
                RM_ExplosiveGrowthRegistry.CountSoaking, t[0], t[1], t[2], t[3], t[4], t[5],
                RM_ExplosiveGrowthRegistry.CountNone, RM_ExplosiveGrowthRegistry.RosterResolved,
                RM_ExplosiveGrowthRegistry.RosterMissing, RM_ExplosiveGrowthRegistry.RupturePawnKinds.Count,
                RM_ExplosiveGrowthRegistry.RuptureMutationHediffs.Count));
        }
    }

    /// <summary>
    /// The EVENT tier (design doc §0): a soaked plant's composite GrowthRate is
    /// multiplied again, on top of whichever ambient band another mod applied
    /// (mandrake.rut.plantgrowth's x4 / x10 / x0.4). Postfix order between the
    /// two does not matter — both multiply. This REPLACES FloodedCanyon's own
    /// soak postfix (retired in the same change), so flooded ground is
    /// multiplied once, not twice.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRate), MethodType.Getter)]
    public static class RM_Patch_Plant_GrowthRate_Soak
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref float __result)
        {
            if (__result <= 0f || !ExplosiveGrowthSettings.enabled) return;
            Map map = __instance.Map;
            if (map == null) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null || comp.SoakedCount == 0) return;
            __result *= comp.GrowthFactorFor(__instance);
        }
    }

    /// <summary>
    /// OVERGROWN (design doc §2, §5): past natural size. Plant.Print (verified,
    /// RimWorld/Plant.cs) sizes the printed plane as
    /// drawSize.x * def.plant.visualSizeRange.LerpThroughRange(growth), with
    /// growth clamped to 1 — so past-100% needs the range itself scaled for the
    /// duration of this one print. Print runs on the main thread during section
    /// regeneration; the finalizer restores the shared def field even if the
    /// print throws.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.Print))]
    public static class RM_Patch_Plant_Print_Overgrown
    {
        [HarmonyPrefix]
        public static void Prefix(Plant __instance, out FloatRange? __state)
        {
            __state = null;
            if (!ExplosiveGrowthSettings.enabled) return;
            Map map = __instance.Map;
            RM_MapComponent_ExplosiveGrowth comp = map != null ? RM_MapComponent_ExplosiveGrowth.For(map) : null;
            if (comp == null || !comp.AnyCharging) return;
            float s = comp.VisualScaleFor(__instance);
            if (s == 1f) return;
            FloatRange r = __instance.def.plant.visualSizeRange;
            __state = r;
            __instance.def.plant.visualSizeRange = new FloatRange(r.min * s, r.max * s);
        }

        [HarmonyFinalizer]
        public static void Finalizer(Plant __instance, FloatRange? __state)
        {
            if (__state.HasValue) __instance.def.plant.visualSizeRange = __state.Value;
        }
    }

    /// <summary>
    /// "Its hue deepens and shifts wrong" (§2). Plant.Graphic (verified,
    /// override getter) is what Print reads its material from, so a tinted
    /// clone here lands in the next re-print. Only Graphic_Single and
    /// Graphic_Random implement GetColoredVersion among plant graphics
    /// (verified: the base class logs an error and returns BadGraphic), so
    /// anything else is left untinted rather than broken.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.Graphic), MethodType.Getter)]
    public static class RM_Patch_Plant_Graphic_Hue
    {
        // "Wrong": a bruised violet for ordinary plants, raw red for the
        // contaminated. 🄸 INVENTED colours.
        private static readonly Color WrongHue = new Color(0.62f, 0.45f, 0.85f);
        private static readonly Color RuptureHue = new Color(1f, 0.32f, 0.32f);

        private static readonly Dictionary<(Graphic, int, bool), Graphic> cache = new Dictionary<(Graphic, int, bool), Graphic>();

        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref Graphic __result)
        {
            if (__result == null || !ExplosiveGrowthSettings.enabled || !ExplosiveGrowthSettings.hueShiftEnabled) return;
            if (!__instance.Spawned) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null || !comp.AnyCharging) return;
            float h = comp.HueFor(__instance);
            if (h <= 0f) return;
            if (!(__result is Graphic_Single) && !(__result is Graphic_Random)) return;

            RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(__instance.def);
            bool rupture = prof != null && prof.top == RM_GrowthTop.Rupture;
            int step = Mathf.RoundToInt(h * 4f);
            var key = (__result, step, rupture);
            if (!cache.TryGetValue(key, out Graphic tinted))
            {
                Color tint = Color.Lerp(Color.white, rupture ? RuptureHue : WrongHue, h);
                tinted = __result.GetColoredVersion(__result.Shader, __result.color * tint, __result.colorTwo * tint);
                cache[key] = tinted;
            }
            __result = tinted;
        }
    }

    /// <summary>HARVEST — "the jackpot window" (§4): a swollen plant harvested
    /// before the top yields swollen produce, up to double at full charge.
    /// 🄸 INVENTED scale.</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.YieldNow))]
    public static class RM_Patch_Plant_YieldNow_Jackpot
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref int __result)
        {
            if (__result <= 0 || !ExplosiveGrowthSettings.enabled || !ExplosiveGrowthSettings.harvestJackpotEnabled) return;
            if (!__instance.Spawned) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null || !comp.AnyCharging) return;
            float charge = comp.ChargeOf(__instance);
            if (charge > 0f) __result = GenMath.RoundRandom(__result * (1f + charge));
        }
    }

    /// <summary>SURVIVE — cutting or harvesting a charging plant defuses it,
    /// "and the last swing is a gamble" (§4). Once it trembles, the swing can
    /// set it off instead. Ruling 7: trigger/weaponize stay unreliable, so this
    /// is a real chance, not a safe button.</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]
    public static class RM_Patch_Plant_PlantCollected_Gamble
    {
        [HarmonyPrefix]
        public static bool Prefix(Plant __instance)
        {
            if (!ExplosiveGrowthSettings.enabled || !__instance.Spawned) return true;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null || !comp.AnyCharging) return true;
            float charge = comp.TakeCharge(__instance);
            if (charge <= 0f) return true;
            comp.Dirty(__instance.Position);

            if (!ExplosiveGrowthSettings.lastSwingGambleEnabled || charge < RM_MapComponent_ExplosiveGrowth.TrembleAt) return true;
            // 🄸 INVENTED: 15% as it starts to tremble, 60% at the very top.
            float chance = Mathf.Lerp(0.15f, 0.6f, Mathf.InverseLerp(RM_MapComponent_ExplosiveGrowth.TrembleAt, 1f, charge));
            if (!Rand.Chance(chance)) return true;

            RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(__instance.def);
            RM_TopResolver.Fire(__instance, prof, comp);
            return __instance.Spawned; // the top destroyed it; skip vanilla's collect
        }
    }
}
