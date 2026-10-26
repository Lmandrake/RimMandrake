using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // DEAD_OR_INERT_SETTINGS (2026-10-08): the rarity slider was a label with no reader. RM_Warscar keeps the
    // vanilla BiomeWorker_Scarlands (shared with the vanilla twin), so the slider acts here, on RM_Warscar only:
    // 0 never; below 1 a tile-seeded chance keeps the score; above 1 the score is multiplied (wins more ties against
    // biomes scoring the same tile). PROVISIONAL numbers: the multiplier form is a guess, the 0 and 1 ends are exact.
    [HarmonyPatch(typeof(BiomeWorker_Scarlands), nameof(BiomeWorker_Scarlands.GetScore))]
    public static class RM_WarscarPatches_Rarity
    {
        private const int GateSeedSalt = 0x57415253; // "WARS"

        public static void Postfix(ref float __result, BiomeDef biome, RimWorld.Planet.PlanetTile planetTile)
        {
            if (biome == null || biome.defName != "RM_Warscar" || __result <= 0f) return;
            float rarity = RM_WarscarSettings.biomeRarityFactor;
            if (rarity <= 0.001f) { __result = -100f; return; }
            if (rarity < 1f) { if (!Rand.ChanceSeeded(rarity, planetTile.tileId ^ GateSeedSalt)) __result = 0f; return; }
            __result *= rarity;
        }
    }

    // WARSCAR_FREE_TIER_BODY_1 / TETCHIK_GLOWERGATE_WIDEN_EDGE_ENTRY: tetchik come where glower grows.
    // WildAnimalSpawner weights kinds by CommonalityOfAnimalNow(kind, loc). At map generation loc is the interior
    // cell the herd is placed on, and glower near it is the gate. For ongoing arrivals loc is the map-edge entry
    // cell, where glower almost never grows, so there the gate asks whether the map holds a glower stand
    // (RM_TetchikGateKernel.MinMapGlower plants anywhere). The rule itself is RM_TetchikGateKernel.Allow.
    [HarmonyPatch(typeof(WildAnimalSpawner), "CommonalityOfAnimalNow")]
    public static class RM_WarscarPatches_TetchikGlowerGate
    {
        private static ThingDef glowerDef;

        public static void Postfix(ref float __result, PawnKindDef def, IntVec3 loc, Map ___map)
        {
            if (__result <= 0f || def == null || def.defName != "RM_Tetchik") return;
            if (___map == null) return;
            if (glowerDef == null) glowerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Glower");
            if (glowerDef == null) { __result = 0f; return; }

            bool entry = RM_TetchikGateKernel.IsEntryCell(loc.x, loc.z, ___map.Size.x, ___map.Size.z);
            int mapGlower = entry ? ___map.listerThings.ThingsOfDef(glowerDef).Count : 0;
            if (RM_TetchikGateKernel.Allow(entry, false, mapGlower)) return;   // cheap map-wide answer first
            if (RM_TetchikGateKernel.Allow(entry, GlowerNear(loc, ___map), mapGlower)) return;
            __result = 0f;
        }

        private static bool GlowerNear(IntVec3 loc, Map map)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(loc, RM_TetchikGateKernel.GlowerRadius, true))
            {
                if (!c.InBounds(map)) continue;
                Plant p = c.GetPlant(map);
                if (p != null && p.def == glowerDef) return true;
            }
            return false;
        }
    }

    // WARSCAR_FREE_TIER_BODY_1: chatrak plate cannot be dyed. Dyeing at a
    // styling station sets CompColorable.DesiredColor, which queues the dye
    // job; refusing it for chatrak-plate apparel means no job and no dye spent.
    [HarmonyPatch(typeof(CompColorable), nameof(CompColorable.DesiredColor), MethodType.Setter)]
    public static class RM_WarscarPatches_ChatrakPlateNoDye
    {
        public static bool Prefix(CompColorable __instance, Color? value)
        {
            if (!value.HasValue) return true;
            ThingDef stuff = __instance.parent?.Stuff;
            return stuff == null || stuff.defName != "RM_ChatrakPlate";
        }
    }
}
