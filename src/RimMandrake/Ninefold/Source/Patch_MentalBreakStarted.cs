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
    // in the database, which is exactly the set of states a real break can
    // start (as opposed to manhunter/panic-flee/social-fighting, none of
    // which is a `MentalBreakDef`).
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
            if (___pawn == null || !___pawn.RaceProps.Humanlike) return;
            if (___pawn.Faction != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Zizzik, EventMagnitude.Large,
                "mental break: " + ___pawn.LabelShortCap + " -> " + stateDef.defName);
        }
    }
}
