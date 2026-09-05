using System.Collections.Generic;
using Verse;
using Verse.AI.Group;
using HarmonyLib;

namespace RimMandrake.Aftermath
{
    // Verified against 1.6 source (RimSage): Verse/AI/Group/LordMaker.cs:8
    // `public static Lord MakeNewLord(Faction faction, LordJob lordJob, Map map,
    // IEnumerable<Pawn> startingPawns = null)` is the single choke point every
    // Lord in the game is created through -- not raid-specific. See
    // MapComponent_BattleRecorder.TryCorrelateLord's own header for the
    // correlation heuristic this postfix feeds.
    [HarmonyPatch(typeof(LordMaker), nameof(LordMaker.MakeNewLord))]
    public static class Patch_LordCreated
    {
        [HarmonyPostfix]
        public static void Postfix(Lord __result, Map map, IEnumerable<Pawn> startingPawns)
        {
            if (__result == null || map == null) return;
            MapComponent_BattleRecorder.For(map)?.TryCorrelateLord(__result, startingPawns);
        }
    }

    // Verified against 1.6 source (RimSage): Verse/AI/Group/LordManager.cs:141
    // `public void RemoveLord(Lord oldLord)` -- the single removal path (also
    // called from LordManager.LordManagerTick's own toil-failure sweep).
    [HarmonyPatch(typeof(LordManager), nameof(LordManager.RemoveLord))]
    public static class Patch_LordRemoved
    {
        [HarmonyPostfix]
        public static void Postfix(LordManager __instance, Lord oldLord)
        {
            if (oldLord == null || __instance?.map == null) return;
            MapComponent_BattleRecorder.For(__instance.map)?.TryCloseByLordRemoval(oldLord);
        }
    }
}
