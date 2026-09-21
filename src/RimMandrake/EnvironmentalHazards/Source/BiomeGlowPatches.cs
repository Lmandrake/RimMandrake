using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 3, the mechanism. Two postfixes, both
    // no-ops unless a BiomeDef somewhere carries a
    // BiomeGlowMultiplierExtension — so this assembly is inert in a game
    // whose mods never opt in, which is what makes it safe to ship at RM
    // tier alongside anything.
    [StaticConstructorOnStartup]
    public static class EnvironmentalHazardsMod
    {
        internal const string HarmonyId = "mandrake.rm.environmentalhazards";

        // Keyed by BiomeDef, not by Map: a Map-keyed cache leaks every map
        // the player ever leaves, and the answer only ever depends on the
        // biome anyway.
        private static readonly Dictionary<BiomeDef, BiomeGlowMultiplierExtension> ExtensionCache =
            new Dictionary<BiomeDef, BiomeGlowMultiplierExtension>();

        // True when no BiomeDef in the whole load order opts in. Lets both
        // postfixes bail on a field read instead of a dictionary lookup in
        // what is one of the hottest methods in the game.
        private static bool anyBiomeOptsIn;

        // GREENTIDE_MECHANICS_2 M5. True when no GameConditionDef in the
        // whole load order carries RM_GlowMultiplierOverrideExtension — lets
        // CurCelestialSunGlow_Postfix skip scanning a map's ActiveConditions
        // entirely on every other install, the same hot-path bail
        // anyBiomeOptsIn already gives the biome-side check. Unlike
        // ExtensionCache above this cannot be a BiomeDef/Map-keyed cache at
        // all — which condition is active changes at runtime, not per biome
        // or per map identity — so the per-call cost this flag guards is a
        // short linear scan of ActiveConditions, not a dictionary lookup.
        private static bool anyGlowOverrideOptsIn;

        static EnvironmentalHazardsMod()
        {
            BuildCache();

            Harmony harmony = new Harmony(HarmonyId);

            Apply(harmony,
                  AccessTools.Method(typeof(GenCelestial), nameof(GenCelestial.CurCelestialSunGlow), new[] { typeof(Map) }),
                  AccessTools.Method(typeof(BiomeGlowPatches), nameof(BiomeGlowPatches.CurCelestialSunGlow_Postfix)),
                  "biome-glow-multiplier");

            Apply(harmony,
                  AccessTools.Method(typeof(ConditionalStatAffecter_InSunlight), nameof(ConditionalStatAffecter_InSunlight.Applies)),
                  AccessTools.Method(typeof(BiomeGlowPatches), nameof(BiomeGlowPatches.InSunlightApplies_Postfix)),
                  "biome-sunlight-suppression");

            // VENOMVINE_FORTRESS_PASSABILITY_1. Both targets are resolved by
            // explicit parameter types rather than by name alone: each has an
            // overload beside it, and AccessTools.Method would otherwise pick
            // whichever the reflection order happens to hand it.
            Apply(harmony,
                  AccessTools.Method(typeof(Verse.PathFinder), nameof(Verse.PathFinder.CreateRequest), new[]
                  {
                      typeof(Verse.IntVec3),
                      typeof(Verse.LocalTargetInfo),
                      typeof(Verse.IntVec3?),
                      typeof(Verse.TraverseParms),
                      typeof(Verse.PathFinderCostTuning?),
                      typeof(Verse.AI.PathEndMode),
                      typeof(Verse.Pawn),
                      typeof(Verse.PathRequest.IPathGridCustomizer)
                  }),
                  AccessTools.Method(typeof(RM_BodySizeBarrierPatches), nameof(RM_BodySizeBarrierPatches.CreateRequest_Prefix)),
                  "body-size-barrier-routing",
                  asPrefix: true);

            Apply(harmony,
                  AccessTools.Method(typeof(Verse.AI.Pawn_PathFollower), nameof(Verse.AI.Pawn_PathFollower.GetPawnCellBaseCostOverride), new[]
                  {
                      typeof(Verse.Pawn),
                      typeof(Verse.IntVec3)
                  }),
                  AccessTools.Method(typeof(RM_BodySizeBarrierPatches), nameof(RM_BodySizeBarrierPatches.GetPawnCellBaseCostOverride_Postfix)),
                  "body-size-barrier-move-cost");
        }

        private static void Apply(Harmony harmony, MethodBase target, MethodInfo patch, string rule, bool asPrefix = false)
        {
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] " + rule + ": target method not found — rule NOT armed. "
                          + "The engine signature this patch was written against has moved.");
                return;
            }

            if (patch == null)
            {
                Log.Error("[RM EnvironmentalHazards] " + rule + ": patch method not found — rule NOT armed.");
                return;
            }

            try
            {
                if (asPrefix)
                {
                    harmony.Patch(target, prefix: new HarmonyMethod(patch));
                }
                else
                {
                    harmony.Patch(target, postfix: new HarmonyMethod(patch));
                }
            }
            catch (Exception e)
            {
                Log.Error("[RM EnvironmentalHazards] " + rule + ": patch failed, rule NOT armed. " + e);
            }
        }

        private static void BuildCache()
        {
            ExtensionCache.Clear();
            anyBiomeOptsIn = false;

            List<BiomeDef> biomes = DefDatabase<BiomeDef>.AllDefsListForReading;
            for (int i = 0; i < biomes.Count; i++)
            {
                BiomeGlowMultiplierExtension ext = biomes[i].GetModExtension<BiomeGlowMultiplierExtension>();
                if (ext == null)
                {
                    continue;
                }

                ExtensionCache[biomes[i]] = ext;
                anyBiomeOptsIn = true;
            }

            // GREENTIDE_MECHANICS_2 M5. GameConditionDefs opting into
            // RM_GlowMultiplierOverrideExtension can't be cached by def the
            // way biomes are above (which one is ACTIVE is runtime state,
            // not load-order state) — this only records whether the feature
            // is used anywhere at all, so ActiveGlowOverrideFor can bail
            // without touching a map's GameConditionManager on every install
            // that never uses it.
            anyGlowOverrideOptsIn = false;
            List<GameConditionDef> conditions = DefDatabase<GameConditionDef>.AllDefsListForReading;
            for (int i = 0; i < conditions.Count; i++)
            {
                if (conditions[i].GetModExtension<RM_GlowMultiplierOverrideExtension>() != null)
                {
                    anyGlowOverrideOptsIn = true;
                    break;
                }
            }
        }

        internal static BiomeGlowMultiplierExtension ExtensionFor(Map map)
        {
            if (!anyBiomeOptsIn || map == null)
            {
                return null;
            }

            BiomeDef biome = map.Biome;
            if (biome == null)
            {
                return null;
            }

            return ExtensionCache.TryGetValue(biome, out BiomeGlowMultiplierExtension ext) ? ext : null;
        }

        // GREENTIDE_MECHANICS_2 M5. First active condition on the map whose
        // def carries RM_GlowMultiplierOverrideExtension, or null. Order
        // among ActiveConditions is registration order, same list
        // WeatherDecider.ForcedWeather already walks for the identical
        // "most recently registered wins" reason — a rare incident-fired
        // clearing condition is always registered after a biome's own
        // permanent lock, so it is the one this finds first in the common
        // case of exactly one override condition active at a time. Two
        // such conditions active simultaneously (not something this kit
        // creates) would resolve to whichever comes first in that list —
        // an accepted, undocumented-further edge case, same posture as
        // WeatherDecider's own "last one wins" resolution it mirrors.
        internal static RM_GlowMultiplierOverrideExtension ActiveGlowOverrideFor(Map map)
        {
            if (!anyGlowOverrideOptsIn || map?.gameConditionManager == null)
            {
                return null;
            }

            List<GameCondition> active = map.gameConditionManager.ActiveConditions;
            for (int i = 0; i < active.Count; i++)
            {
                GameCondition condition = active[i];
                if (condition?.def == null)
                {
                    continue;
                }

                RM_GlowMultiplierOverrideExtension ext = condition.def.GetModExtension<RM_GlowMultiplierOverrideExtension>();
                if (ext != null)
                {
                    return ext;
                }
            }

            return null;
        }
    }

    public static class BiomeGlowPatches
    {
        // Postfix on GenCelestial.CurCelestialSunGlow(Map). Everything that
        // reads "how light is it outside right now" goes through here, so
        // scaling the result darkens the biome for shooting accuracy, mood,
        // plant growth and light-gated work all at once — none of which this
        // assembly touches directly.
        public static void CurCelestialSunGlow_Postfix(Map map, ref float __result)
        {
            if (!RM_EnvironmentalHazardsSettings.biomeGlowMultiplierEnabled)
            {
                return; // mod option: biome darkness multiplier disabled
            }

            // GREENTIDE_MECHANICS_2 M5: an active "clearing event" condition
            // (e.g. Breaklight) takes priority over the biome's own permanent
            // darkening — checked first and, when present, applied INSTEAD
            // of ext.glowMultiplier below, never stacked with it.
            RM_GlowMultiplierOverrideExtension overrideExt = EnvironmentalHazardsMod.ActiveGlowOverrideFor(map);
            if (overrideExt != null)
            {
                __result *= overrideExt.glowMultiplier;
                return;
            }

            BiomeGlowMultiplierExtension ext = EnvironmentalHazardsMod.ExtensionFor(map);
            if (ext == null)
            {
                return;
            }

            __result *= ext.glowMultiplier;
        }

        // Postfix on ConditionalStatAffecter_InSunlight.Applies(StatRequest).
        // Only ever forces the answer to FALSE — never to true — so an opted
        // -in biome can remove a sunlight-gated effect but can never invent
        // one where vanilla says there is no sun.
        public static void InSunlightApplies_Postfix(StatRequest req, ref bool __result)
        {
            if (!RM_EnvironmentalHazardsSettings.biomeGlowMultiplierEnabled)
            {
                return; // mod option: biome darkness multiplier disabled
            }
            if (!__result)
            {
                return;
            }

            if (!req.HasThing || req.Thing == null || !req.Thing.Spawned)
            {
                return;
            }

            BiomeGlowMultiplierExtension ext = EnvironmentalHazardsMod.ExtensionFor(req.Thing.Map);
            if (ext == null || !ext.suppressSunlightStatAffecter)
            {
                return;
            }

            __result = false;
        }
    }
}
