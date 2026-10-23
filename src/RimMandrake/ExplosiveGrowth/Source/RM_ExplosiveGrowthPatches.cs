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

            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.explosivegrowth"), typeof(RM_ExplosiveGrowthRegistry).Assembly, "RimMandrake.ExplosiveGrowth");

            string selfTest = RM_ChargeSelfTest.Run();
            if (selfTest.Contains("FAIL")) Log.Error("[RM ExplosiveGrowth] " + selfTest);
            else Log.Message("[RM ExplosiveGrowth] " + selfTest);

            int[] t = RM_ExplosiveGrowthRegistry.CountByTop;
            int[] k = RM_ExplosiveGrowthRegistry.CountByArchetype;
            Log.Message(string.Format(
                "[RM ExplosiveGrowth] {0} plant defs soak (churn {1}, burst {2}, slime {3}, tinder {4}, rupture {5}, flush {6}), {7} never soak; " +
                "roster rows resolved {8}, absent {9}; rupture kinds {10}, mutation hediffs {11}. " +
                "Archetypes: dry {13}, wet {14}, fire {15}, exempt {16}, vanilla {17}; {18} stalled, {19} wet and {20} fire biome(s); " +
                "{21} natural-water terrain(s), {22} water filth(s), {23} liquid set(s), tidally locked {24}. " +
                "Scope (home mod {12}): {25} Baroque Biomes biome(s){26}. Trees (3.0+, not fungi) {27}, fungi marked {28}.",
                RM_ExplosiveGrowthRegistry.CountSoaking, t[0], t[1], t[2], t[3], t[4], t[5],
                RM_ExplosiveGrowthRegistry.CountNone, RM_ExplosiveGrowthRegistry.RosterResolved,
                RM_ExplosiveGrowthRegistry.RosterMissing, RM_ExplosiveGrowthRegistry.RupturePawnKinds.Count,
                RM_ExplosiveGrowthRegistry.RuptureMutationHediffs.Count,
                ExplosiveGrowthMod.Home?.PackageId ?? "UNKNOWN", k[0], k[1], k[2], k[3], k[4],
                RM_ExplosiveGrowthRegistry.TerminatorBiomeCount, RM_ExplosiveGrowthRegistry.WetBiomeCount,
                RM_ExplosiveGrowthRegistry.FireBiomeCount, RM_ExplosiveGrowthRegistry.NaturalWaterTerrainCount,
                RM_ExplosiveGrowthRegistry.FilthLiquidCount, RM_ExplosiveGrowthRegistry.LiquidSets.Count,
                RM_ExplosiveGrowthRegistry.TidallyLocked, RM_ExplosiveGrowthRegistry.HomeBiomes.Count,
                RM_ExplosiveGrowthRegistry.ScopeForcedBy != null ? ", every biome by roster " + RM_ExplosiveGrowthRegistry.ScopeForcedBy
                : ExplosiveGrowthSettings.nativesSameRuleInOtherBiomes ? " (our plants everywhere by the unsupported option)" : " only",
                RM_ExplosiveGrowthRegistry.CountTrees, RM_ExplosiveGrowthRegistry.CountFungi));
        }
    }

    /// <summary>
    /// THE RULED RATE (spec §2.5, D1+D2): ONE postfix multiplies vanilla's COMPOSITE GrowthRate by the plant's moisture
    /// factor r (archetype x the cell's water state x the tree ratio; setting A for vanilla plants; sealed growers x1). It
    /// REPLACES the old everyday band and soak, never stacks. The composite already holds light, temperature, fertility and
    /// drought, so a dark cell stays 0: r never lifts a zero (the 12:28 light ruling). Pure read: no writes, no allocation.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.GrowthRate), MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Ruled growth rate", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_GrowthRate_Rule
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref float __result)
        {
            if (__result <= 0f || !RM_ExplosiveGrowthRegistry.Ready || !ExplosiveGrowthSettings.On) return;
            Map map = __instance.Map;
            if (map == null) return;   // unspawned or held: vanilla
            RM_PlantProfile p = RM_ExplosiveGrowthRegistry.For(__instance.def);
            if (p == null) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null) return;
            __result *= comp.MoistureFactorFor(__instance, p);
        }
    }

    /// <summary>
    /// DORMANCY (WP2 "Yes, age at the slowed rate"; spec §5.2, D13): a PREFIX on Plant.TickLong takes (1 - r) x 2000 off
    /// the age step vanilla is about to add, so a plant below x1 ages at r. A prefix because vanilla adds ageInt += 2000 and
    /// checks Dying in the same call (RimSage RimWorld/Plant.cs:810-868): a postfix would let vanilla kill it first. Only
    /// the moisture factor slows ageing; darkness, blight, temperature and drought never do.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.TickLong))]
    [RimMandrake.Shared.PatchFeature("Dormancy (slowed ageing)", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_TickLong_Dormancy
    {
        private static readonly AccessTools.FieldRef<Plant, int> ageRef = AccessTools.FieldRefAccess<Plant, int>("ageInt");

        [HarmonyPrefix]
        public static void Prefix(Plant __instance)
        {
            if (!ExplosiveGrowthSettings.dormancyEnabled || !ExplosiveGrowthSettings.On || !RM_ExplosiveGrowthRegistry.Ready) return;
            if (!__instance.Spawned || __instance.Destroyed) return;
            RM_PlantProfile p = RM_ExplosiveGrowthRegistry.For(__instance.def);
            if (p == null) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null) return;
            float r = comp.MoistureFactorFor(__instance, p);
            int off = RM_ExplosiveGrowthKernel.AgeRemoval(r, Rand.Value);
            if (off > 0) ageRef(__instance) -= off;
        }
    }

    /// <summary>
    /// TREE LIFE (tree_burst_design_2026-10-17.md §3, §4, §6a; T3, T5): after the dormancy prefix (lower priority), a tree
    /// drinks and may burst (RM_TreeLife). A PREFIX for the dormancy prefix's reason: vanilla adds its age step and checks
    /// Dying in the same call, so a water-driven death must burst before vanilla's rot can claim it, and a natural crossing
    /// is left to vanilla. Returns false (skip vanilla) only when the tree burst and is gone.
    /// </summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.TickLong))]
    [RimMandrake.Shared.PatchFeature("Tree life (litres buy days, end-of-life burst)", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_TickLong_TreeLife
    {
        [HarmonyPrefix]
        [HarmonyPriority(Priority.Low)]
        public static bool Prefix(Plant __instance)
        {
            if (!ExplosiveGrowthSettings.On || !RM_ExplosiveGrowthRegistry.Ready) return true;
            if (!__instance.Spawned || __instance.Destroyed) return true;
            RM_PlantProfile p = RM_ExplosiveGrowthRegistry.For(__instance.def);
            if (p == null || !p.isTree) return true;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null) return true;
            return !RM_TreeLife.OnTickLong(__instance, p, comp);
        }
    }

    /// <summary>
    /// TIDAL LOCK (OQ-7 by card: "no rest; always lit means always growing"; D14). Vanilla rests every plant by the CLOCK,
    /// not the light (Resting = DayPercent &lt; 0.25 || &gt; 0.8, RimSage RimWorld/Plant.cs:277-284), so a permanently lit
    /// cell on Ash'karr would still rest 45% of each day. On a world a loaded roster marks tidallyLockedWorld, a plant with
    /// light never rests. A dark cell is untouched (its growth is 0 anyway).
    /// </summary>
    [HarmonyPatch(typeof(Plant), "Resting", MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("Tidal lock: lit plants never rest", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_Resting_TidalLock
    {
        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref bool __result)
        {
            if (!__result || !ExplosiveGrowthSettings.tidalLockNoRest || !RM_ExplosiveGrowthRegistry.TidallyLocked || !ExplosiveGrowthSettings.On) return;
            if (!__instance.Spawned) return;
            if (__instance.GrowthRateFactor_Light > 0.001f) __result = false;
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
    [RimMandrake.Shared.PatchFeature("Explosive growth overgrown print", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_Print_Overgrown
    {
        [HarmonyPrefix]
        public static void Prefix(Plant __instance, out FloatRange? __state)
        {
            __state = null;
            if (!ExplosiveGrowthSettings.On) return;
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
    [RimMandrake.Shared.PatchFeature("Explosive growth hue shift", typeof(ExplosiveGrowthSettings), "hueShiftEnabled")]
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
            if (__result == null || !ExplosiveGrowthSettings.On || !ExplosiveGrowthSettings.hueShiftEnabled) return;
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

    /// <summary>HARVEST — "the jackpot window" (§4): a swollen WILD plant (OQ-14) HARVESTED
    /// before the top yields swollen produce, up to double at full charge. CUTTING it forfeits
    /// the jackpot (§4, sprint X4, ruled S0-4 2026-10-16): a cut pays the plain yield.
    /// 🄸 INVENTED scale.</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.YieldNow))]
    [RimMandrake.Shared.PatchFeature("Harvest jackpot", typeof(ExplosiveGrowthSettings), "harvestJackpotEnabled")]
    public static class RM_Patch_Plant_YieldNow_Jackpot
    {
        /// <summary>Proof hook only (RM_ExplosiveGrowthProof): null = read the live reservation, true/false = force
        /// "a cut is in progress" so the forfeit branch can be read without a pawn.</summary>
        public static bool? ForceCutting;

        private static readonly HashSet<Pawn> reservers = new HashSet<Pawn>();

        /// <summary>The jackpot multiplier for one yield read: 1 + charge on a harvest, 1 on a cut (X4), 1 uncharged.</summary>
        public static float Multiplier(float charge, bool cutting) => charge > 0f && !cutting ? 1f + charge : 1f;

        /// <summary>True while a pawn's CUT job (JobDriver_PlantCut and subclasses, PlantDestructionMode.Cut) holds
        /// this plant. Vanilla JobDriver_PlantWork reads YieldNow inside the work toil, before PlantCollected,
        /// and the driver reserves its target first (RimSage JobDriver_PlantWork.cs), so the reserver at that
        /// moment is the actor. Only consulted for a charged wild plant, so the scan never runs on the hot path.</summary>
        public static bool CuttingNow(Plant plant)
        {
            if (ForceCutting.HasValue) return ForceCutting.Value;
            Map map = plant.MapHeld;
            if (map == null) return false;
            reservers.Clear();
            map.reservationManager.ReserversOf(plant, reservers);
            bool cut = false;
            foreach (Pawn p in reservers)
            {
                if (p?.jobs?.curDriver is JobDriver_PlantCut) { cut = true; break; }
            }
            reservers.Clear();
            return cut;
        }

        [HarmonyPostfix]
        public static void Postfix(Plant __instance, ref int __result)
        {
            if (__result <= 0 || !ExplosiveGrowthSettings.On || !ExplosiveGrowthSettings.harvestJackpotEnabled) return;
            if (!__instance.Spawned) return;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null || !comp.AnyCharging) return;
            if (__instance.IsCrop) return;   // OQ-14: a crop's harvest is exactly its full YieldNow
            float charge = comp.ChargeOf(__instance);
            if (charge <= 0f) return;
            float m = Multiplier(charge, CuttingNow(__instance));
            if (m > 1f) __result = GenMath.RoundRandom(__result * m);
        }
    }

    /// <summary>SURVIVE — cutting or harvesting a charging plant defuses it,
    /// "and the last swing is a gamble" (§4). Once it trembles, the swing can
    /// set it off instead. Ruling 7: trigger/weaponize stay unreliable, so this
    /// is a real chance, not a safe button.</summary>
    [HarmonyPatch(typeof(Plant), nameof(Plant.PlantCollected))]
    [RimMandrake.Shared.PatchFeature("Explosive growth last-swing gamble", typeof(ExplosiveGrowthSettings), "enabled")]
    public static class RM_Patch_Plant_PlantCollected_Gamble
    {
        /// <summary>The last swing's chance to set it off (0 below the tremble or with the gamble off).
        /// 🄸 INVENTED: 15% as it starts to tremble, 60% at the very top.</summary>
        public static float GambleChance(float charge)
        {
            if (!ExplosiveGrowthSettings.lastSwingGambleEnabled || charge < RM_MapComponent_ExplosiveGrowth.TrembleAt) return 0f;
            return Mathf.Lerp(0.15f, 0.6f, Mathf.InverseLerp(RM_MapComponent_ExplosiveGrowth.TrembleAt, 1f, charge));
        }

        [HarmonyPrefix]
        public static bool Prefix(Plant __instance)
        {
            if (!ExplosiveGrowthSettings.On || !__instance.Spawned) return true;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(__instance.Map);
            if (comp == null || !comp.AnyCharging) return true;
            float charge = comp.TakeCharge(__instance);
            if (charge <= 0f) return true;
            comp.Dirty(__instance.Position);
            if (__instance.IsCrop) return true;   // OQ-14: cutting a crop defuses it, never a gamble

            float chance = GambleChance(charge);
            if (chance <= 0f || !Rand.Chance(chance)) return true;

            RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(__instance.def);
            RM_TopResolver.Fire(__instance, prof, comp);
            return __instance.Spawned; // the top destroyed it; skip vanilla's collect
        }
    }
}
