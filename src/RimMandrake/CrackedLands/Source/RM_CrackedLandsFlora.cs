using System;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CrackedLands
{
    /// <summary>With the setting off, the expansion plants leave the wild roster at startup (applies next launch).</summary>
    [StaticConstructorOnStartup]
    public static class RM_CrackedLandsFloraGate
    {
        private static readonly string[] Expansion =
            { "RM_Nabbuq", "RM_Ruqqal", "RM_Sevvuq", "RM_Zennaq", "RM_Luqqim", "RM_Harrovaq" };

        static RM_CrackedLandsFloraGate()
        {
            if (RM_CrackedLandsSettings.floraExpansionEnabled)
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
