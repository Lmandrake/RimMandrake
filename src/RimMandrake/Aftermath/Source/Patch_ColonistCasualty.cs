using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.Aftermath
{
    // Same choke point RimMandrake.Ninefold's own Patch_BattleResolved.cs
    // already cites (Pawn.Kill -- verified there, re-verified here since this
    // is a separate assembly): every pawn death passes through
    // `Pawn.Kill(DamageInfo? dinfo, Hediff exactCulprit)`. Unlike Ninefold's
    // hook (which only counts VIOLENT deaths for Sh'kaar), doc Part 2's LOST
    // classification says plainly "colonist deaths ... >= 1" with no violence
    // qualifier, so this one does not filter on dinfo.HasValue.
    //
    // Does NOT duplicate Ninefold's per-death Sh'kaar delta -- this patch
    // writes only to an open BattleRecord's ColonistCasualty flag, never
    // calls ApplyDelta itself.
    [HarmonyPatch(typeof(Pawn), nameof(Pawn.Kill))]
    public static class Patch_ColonistCasualty
    {
        [HarmonyPostfix]
        public static void Postfix(Pawn __instance)
        {
            if (__instance?.Faction != Faction.OfPlayer) return;
            if (__instance.Map == null) return;

            MapComponent_BattleRecorder.For(__instance.Map)?.Notify_ColonistCasualty();
        }
    }
}
