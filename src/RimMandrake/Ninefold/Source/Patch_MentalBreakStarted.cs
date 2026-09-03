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
    // single call site every mental break (and manhunter/panic-flee state)
    // passes through, `bool __result` tells us whether it actually started
    // (many calls no-op: already in a state, tutorial mode, blocked by a
    // hediff), and the owning pawn is the handler's private `pawn` field,
    // reachable via Harmony's `___pawn` convention.
    //
    // Filtered to the player's own humanlike colonists only -- a wild
    // animal's manhunter state or a hostile raider's berserk is not the
    // clan's "wrong spark," it is theirs.
    [HarmonyPatch(typeof(MentalStateHandler), nameof(MentalStateHandler.TryStartMentalState))]
    public static class Patch_MentalBreakStarted
    {
        [HarmonyPostfix]
        public static void Postfix(bool __result, MentalStateDef stateDef, Pawn ___pawn)
        {
            if (!__result) return;
            if (___pawn == null || !___pawn.RaceProps.Humanlike) return;
            if (___pawn.Faction != Faction.OfPlayer) return;

            GameComponent_Ninefold comp = GameComponent_Ninefold.Instance;
            if (comp == null) return;

            comp.ApplyDelta(God.Zizzik, EventMagnitude.Large,
                "mental break: " + ___pawn.LabelShortCap + " -> " + stateDef?.defName);
        }
    }
}
