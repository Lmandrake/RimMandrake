using System.Collections.Generic;
using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Aftermath
{
    // Verified against 1.6 source (RimSage): RimWorld/IncidentWorker_Raid.cs:70
    // `public bool TryGenerateRaidInfo(IncidentParms parms, out List<Pawn> pawns,
    // bool debugTest = false)` is the single method both IncidentWorker_RaidEnemy
    // and IncidentWorker_RaidFriendly funnel through (line 135 calls it with the
    // 2-arg overload). The HostileTo(Faction.OfPlayer) guard inside
    // MapComponent_BattleRecorder.OpenBattle is what actually scopes this to
    // hostile raids -- this postfix fires for either.
    [HarmonyPatch(typeof(IncidentWorker_Raid), nameof(IncidentWorker_Raid.TryGenerateRaidInfo))]
    public static class Patch_RaidGenerated
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, IncidentParms parms, List<Pawn> pawns)
        {
            if (!__result || pawns == null || pawns.Count == 0) return;

            Map map = parms.target as Map;
            if (map == null) return;

            MapComponent_BattleRecorder.For(map)?.OpenBattle(parms.faction, pawns, parms.points, Find.TickManager.TicksGame);
        }
    }
}
