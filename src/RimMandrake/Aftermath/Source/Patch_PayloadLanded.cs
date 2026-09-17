using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Aftermath
{
    // AFTERMATH_DEAD_LETTERS_1: the seam where a queued aftermath rule's
    // payload actually lands. Verified against 1.6 source (RimSage):
    // RimWorld/IncidentWorker.cs:183 `public bool TryExecute(IncidentParms
    // parms)` is the single method every IncidentDef of every category
    // funnels a successful fire through (unlike IncidentWorker_Raid.
    // TryGenerateRaidInfo, which Patch_RaidGenerated already patches for a
    // different purpose and which only raid-shaped incidents call) - this
    // item's own eight rules span both RaidEnemy and ShortCircuit, so the
    // base-class seam is the one that covers all of them without caring
    // which subclass fired.
    [HarmonyPatch(typeof(IncidentWorker), nameof(IncidentWorker.TryExecute))]
    public static class Patch_PayloadLanded
    {
        [HarmonyPostfix]
        public static void Postfix(IncidentWorker __instance, bool __result, IncidentParms parms)
        {
            if (!__result) return;
            Map map = parms.target as Map;
            if (map == null) return;

            AftermathRuleRunner.Instance?.OnPayloadLanded(__instance.def, parms.faction, map);
        }
    }
}
