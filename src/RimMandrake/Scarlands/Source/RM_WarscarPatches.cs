using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_FREE_TIER_BODY_1: the tetchik "spawn-cell validator".
    // WildAnimalSpawner weights kinds by CommonalityOfAnimalNow(kind, loc) for
    // a random loc, so zeroing a kind there unless glower is near loc means a
    // tetchik herd is only ever picked where glower grows.
    [HarmonyPatch(typeof(WildAnimalSpawner), "CommonalityOfAnimalNow")]
    public static class RM_WarscarPatches_TetchikGlowerGate
    {
        private const int GlowerRadius = 6;
        private static ThingDef glowerDef;

        public static void Postfix(ref float __result, PawnKindDef def, IntVec3 loc, Map ___map)
        {
            if (__result <= 0f || def == null || def.defName != "RM_Tetchik") return;
            if (___map == null) return;
            if (glowerDef == null) glowerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Glower");
            if (glowerDef == null) { __result = 0f; return; }

            foreach (IntVec3 c in GenRadial.RadialCellsAround(loc, GlowerRadius, true))
            {
                if (!c.InBounds(___map)) continue;
                Plant p = c.GetPlant(___map);
                if (p != null && p.def == glowerDef) return;
            }
            __result = 0f;
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
