using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using HarmonyLib;

namespace RimMandrake.Ninefold
{
    // design/Jawa/divine_satiation_engine.md §8b.B: "A colonist has a MENTAL
    // BREAK (berserk/daze/binge) -> ▲Zizzik (large -- the wrong spark in a
    // mind, §⑦), ↓Oomo if a food/water binge wastes stores."
    //
    // The ↓Oomo/binge half is NOT implemented here -- it needs the binge-
    // specific MentalStateDef, not any break, and is out of scope for this
    // hook (which only reads whether a break started, not which resources
    // it wasted).
    //
    // Verified against decompiled source (RimSage): `MentalStateHandler.
    // TryStartMentalState` (Source/Verse/AI/MentalStateHandler.cs:91) is the
    // single call site every mental STATE passes through -- not just breaks.
    // `Pawn_InteractionsTracker.TryInteractWith` starts `SocialFighting`
    // through the same method on both participants, and `LordToil_PanicFlee`
    // starts `PanicFlee` the same way; §8b gives social fights their OWN row
    // (▲Zizzik, ↓Mob'Unloo -- a bond damaged, not this hook's pair), so both
    // are excluded here rather than double-counted under the wrong gods.
    // `BreakStateDefs` is built once from every `MentalBreakDef.mentalState`
    // in the database, which covers every real break EXCEPT the ones that
    // drive a `workerClass` instead of a `mentalState` -- `Catatonic` is the
    // one reachable by a player humanlike (`RunWild` is animal-only, already
    // excluded by the Humanlike filter below). `MentalBreakWorker_Catatonic.
    // TryStart` never calls `TryStartMentalState` at all (it applies
    // `HediffDefOf.CatatonicBreakdown` directly and returns true
    // unconditionally), so it needs its own patch below rather than a
    // `BreakStateDefs` entry.
    //
    // Filtered to the player's own humanlike colonists only -- a wild
    // animal's manhunter state or a hostile raider's berserk is not the
    // clan's "wrong spark," it is theirs.
    [HarmonyPatch(typeof(MentalStateHandler), nameof(MentalStateHandler.TryStartMentalState))]
    public static class Patch_MentalBreakStarted
    {
        private static HashSet<MentalStateDef> breakStateDefs;

        private static HashSet<MentalStateDef> BreakStateDefs =>
            breakStateDefs ??= new HashSet<MentalStateDef>(
                DefDatabase<MentalBreakDef>.AllDefs
                    .Select(b => b.mentalState)
                    .Where(s => s != null));

        [HarmonyPostfix]
        public static void Postfix(bool __result, MentalStateDef stateDef, Pawn ___pawn)
        {
            if (!__result) return;
            if (stateDef == null || !BreakStateDefs.Contains(stateDef)) return;

            MentalBreakUtility.ApplyBreakDelta(___pawn, stateDef.defName);
        }
    }

    // `MentalBreakWorker_Catatonic.TryStart` bypasses `TryStartMentalState`
    // entirely (Verse.AI/MentalBreakWorker_Catatonic.cs:16-21) -- a direct
    // `AddHediff(HediffDefOf.CatatonicBreakdown)` with an unconditional
    // `return true`. Patched separately (not via the base virtual
    // `MentalBreakWorker.TryStart`, which every `mentalState`-carrying break
    // also runs through and would double-count).
    [HarmonyPatch(typeof(MentalBreakWorker_Catatonic), nameof(MentalBreakWorker_Catatonic.TryStart))]
    public static class Patch_CatatonicBreakStarted
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, Pawn pawn)
        {
            if (!__result) return;

            MentalBreakUtility.ApplyBreakDelta(pawn, "Catatonic");
        }
    }

    internal static class MentalBreakUtility
    {
        public static void ApplyBreakDelta(Pawn pawn, string breakLabel)
        {
            if (pawn == null || !pawn.RaceProps.Humanlike) return;
            if (pawn.Faction != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Zizzik, EventMagnitude.Large,
                "mental break: " + pawn.LabelShortCap + " -> " + breakLabel);
        }
    }
}
