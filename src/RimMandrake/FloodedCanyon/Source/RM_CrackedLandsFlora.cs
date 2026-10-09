using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FloodedCanyon
{
    // ════════════════════════════════════════════════════════════════════
    // CRACKEDLANDS_FLORA_EXPANSION_BUILD_1 — the zennaq draws lightning.
    //
    // MEASURED (RimSage, decompiled 1.6): a random strike is chosen inside
    // WeatherEvent_LightningStrike.DoStrike(IntVec3 strikeLoc, Map map, ref Mesh),
    // a public static that every strike event funnels through (the plain and the
    // delayed event both call it). When strikeLoc is Invalid the engine rolls a
    // random standable unroofed cell. A forced location (flashstorm, debug tool)
    // is left alone: this only bends the random roll.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ZennaqLightning
    {
        // How far from the rolled cell a zennaq still pulls the bolt onto itself.
        public const int PullRange = 30;

        /// <summary>The cell the bolt should land on given the engine's own rolled cell.
        /// Returns the nearest zennaq within PullRange of it, else the rolled cell.</summary>
        public static IntVec3 Redirect(IntVec3 rolled, Map map, ThingDef zennaq)
        {
            if (map == null || zennaq == null || !rolled.IsValid)
            {
                return rolled;
            }
            Thing best = null;
            float bestDist = PullRange * PullRange + 1;
            var list = map.listerThings.ThingsOfDef(zennaq);
            for (int i = 0; i < list.Count; i++)
            {
                Thing t = list[i];
                if (!t.Spawned || map.roofGrid.Roofed(t.Position))
                {
                    continue;
                }
                float d = (t.Position - rolled).LengthHorizontalSquared;
                if (d < bestDist)
                {
                    bestDist = d;
                    best = t;
                }
            }
            return best != null ? best.Position : rolled;
        }
    }

    [RimMandrake.Shared.PatchFeature("RM_ZennaqLightningPatch", typeof(RM_FloodedCanyonSettings), "zennaqLightningPullEnabled")]
    [HarmonyPatch(typeof(WeatherEvent_LightningStrike), nameof(WeatherEvent_LightningStrike.DoStrike))]
    public static class RM_ZennaqLightningPatch
    {
        private static ThingDef zennaqDef;

        public static void Prefix(ref IntVec3 strikeLoc, Map map)
        {
            if (!RM_FloodedCanyonSettings.zennaqLightningPullEnabled || strikeLoc.IsValid || map == null)
            {
                return;
            }
            if (zennaqDef == null)
            {
                zennaqDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Zennaq");
                if (zennaqDef == null)
                {
                    return;
                }
            }
            if (map.listerThings.ThingsOfDef(zennaqDef).Count == 0)
            {
                return;
            }
            // Same roll the engine would make, then bend it.
            IntVec3 rolled = CellFinderLoose.RandomCellWith(sq => sq.Standable(map) && !map.roofGrid.Roofed(sq), map);
            strikeLoc = RM_ZennaqLightning.Redirect(rolled, map, zennaqDef);
        }
    }

    /// <summary>With the setting off, the expansion plants leave the wild roster at startup (applies next launch).</summary>
    [StaticConstructorOnStartup]
    public static class RM_CrackedLandsFloraGate
    {
        private static readonly string[] Expansion =
            { "RM_Nabbuq", "RM_Ruqqal", "RM_Sevvuq", "RM_Zennaq", "RM_Luqqim", "RM_Harrovaq" };

        static RM_CrackedLandsFloraGate()
        {
            if (RM_FloodedCanyonSettings.floraExpansionEnabled)
            {
                return;
            }
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_FloodedCanyon");
            if (biome != null)
            {
                biome.wildPlants.RemoveAll(r => r.plant != null && Array.IndexOf(Expansion, r.plant.defName) >= 0);
            }
        }
    }
}
