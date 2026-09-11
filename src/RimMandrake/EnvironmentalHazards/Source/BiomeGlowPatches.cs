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
        }

        private static void Apply(Harmony harmony, MethodBase target, MethodInfo postfix, string rule)
        {
            if (target == null)
            {
                Log.Error("[RM EnvironmentalHazards] " + rule + ": target method not found — rule NOT armed. "
                          + "The engine signature this patch was written against has moved.");
                return;
            }

            try
            {
                harmony.Patch(target, postfix: new HarmonyMethod(postfix));
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
